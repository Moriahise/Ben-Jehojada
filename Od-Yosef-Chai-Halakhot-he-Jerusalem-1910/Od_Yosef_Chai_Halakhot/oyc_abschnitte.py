# -*- coding: utf-8 -*-
"""
Schritt 1 — Abschnittsliste aus dem Sefaria-JSON und Abgleich mit dem NLI-Scan.

Quellen
    JSON  Sefaria "Od Yosef Chai; Halakhot - he - Jerusalem, 1910"
          (versionSource = NLI NNL_ALEPH990019337340205171)
    Scan  NLI-Digitalisat derselben Ausgabe, Seitenbilder NNNN_FLxxxxxxxxx.jpg
          (ZIP oder Ordner; mehrere Angaben moeglich, z. B. 1-25 und 26-400)

Der Abgleich laeuft ueber die Scan-Konkordanz (scan_konkordanz.tsv): je
Scanseite Art (Halakhot, Derashot, Titelblatt ...), Abschnitt (JSON-Schluessel
wie "Bereshit"), erste und letzte Ot auf der Seite und die Kolumnentitel.
Die Konkordanz ist Lektoratsarbeit; das Skript prueft sie gegen JSON und
Scaninventar und erzeugt dafuer einen Pruefbogen mit den Kopfzeilen jeder Seite.
Optional schlaegt Tesseract (-l heb) Kolumnentitel vor; die Konkordanz selbst
wird nie automatisch ueberschrieben.

Aufrufe
    python3 oyc_abschnitte.py --scan scan.zip --out out
    python3 oyc_abschnitte.py --scan scan.zip --scan-gesamt 412 --ocr --out out
    python3 oyc_abschnitte.py --laden-sefaria --vergleiche-sefaria --out out
    python3 oyc_abschnitte.py --iiif-manifest <URL> --seiten 26-120 --laden-nach scan_pages/
"""
import argparse
import collections
import html
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import oyc_common as C

SCAN_NAME_RE = re.compile(r'(?:^|/)(\d{3,5})_(FL\d+)\.(?:jpe?g|png|tiff?)$', re.I)
ARTEN = ['Einband', 'Vorsatz', 'Kontrollaufnahme', 'Titelblatt', 'Titelrueckseite',
         'Vorspann', 'Derashot', 'Anhang', 'Halakhot', 'Kuntres', 'Register', 'Leer', 'Unklar']
HALACHA_ARTEN = {'Halakhot', 'Kuntres'}
KONK_HEADER = ['seq', 'fl_id', 'art', 'abschnitt', 'ot_von', 'ot_bis',
               'kopf_rechts', 'kopf_mitte', 'kopf_links', 'bemerkung']


# --- Abschnittsliste ---------------------------------------------------------
def incipit(html_text, n_words=8):
    t = re.sub(r'\s+', ' ', C.strip_tags(html_text)).strip()
    return ' '.join(t.split(' ')[:n_words])


def stichwort(html_text):
    m = re.match(r'\s*<b>(.*?)</b>', html_text or '', re.S)
    return C.strip_tags(m.group(1)).strip() if m else ''


def abschnittsliste(werk):
    rows, summary = [], []
    for a in werk['abschnitte']:
        n_hal = sum(1 for h in a['halachot'] if not h['leer'])
        leer = [h['n'] for h in a['halachot'] if h['leer']]
        chars = 0
        n_abs = 0
        for h in a['halachot']:
            first = next((p for p in h['absaetze'] if C.strip_tags(p['html']).strip()), None)
            seg_chars = C.visible_length(C.segment_he(h)) if not h['leer'] else 0
            nabs = sum(1 for p in h['absaetze'] if C.strip_tags(p['html']).strip())
            chars += seg_chars
            n_abs += nabs
            hinweis = []
            if h['leer']:
                hinweis.append('LEER in Sefaria – im Scan pruefen')
            if seg_chars > C.BATCH_MAX_CHARS:
                hinweis.append('Segment > {} Zeichen (Batch-Kontingent)'.format(C.BATCH_MAX_CHARS))
            if first and not stichwort(first['html']) and a['tiefe'] == 2:
                hinweis.append('kein fettes Stichwort')
            rows.append([a['ord'], a['key'], a['he_title'], h['n'], h['ref'], nabs, seg_chars,
                         stichwort(first['html']) if first else '',
                         incipit(first['html']) if first else '', '; '.join(hinweis)])
        summary.append({'ord': a['ord'], 'key': a['key'], 'he': a['he'],
                        'he_title': a['he_title'], 'tiefe': a['tiefe'],
                        'parascha': a['parascha'], 'halachot': n_hal,
                        'hoechste_ot': max((h['n'] for h in a['halachot']), default=0),
                        'leer': leer, 'absaetze': n_abs, 'zeichen': chars})
    return rows, summary


def schema_pruefung(werk):
    m = werk['meta']
    befunde = []
    if m['schema_reihenfolge'] and m['schema_reihenfolge'] != m['text_reihenfolge']:
        befunde.append('Schema-Reihenfolge weicht von der Textreihenfolge ab.')
    bekannt = [a['key'] for a in werk['abschnitte'] if a['parascha']]
    pos = [C.PARASHOT.index(k) for k in bekannt]
    if pos != sorted(pos):
        befunde.append('Paraschot nicht in Tora-Reihenfolge: ' + ', '.join(bekannt))
    sonder = [a['key'] for a in werk['abschnitte'] if not a['parascha']]
    if sonder:
        befunde.append('Sonderabschnitte (keine Parascha): ' + ', '.join(sonder))
    for a in werk['abschnitte']:
        if a['tiefe'] == 1:
            befunde.append('{}: Tiefe 1 (Absaetze ohne Ot-Gliederung, {} Absaetze)'.format(
                a['key'], len(a['halachot'])))
    for p in (p for _, _, p in C.iter_absaetze(werk)):
        if re.match(r'\s*\[\d+\]', C.strip_tags(p['html'])):
            befunde.append('{}: Absatz beginnt mit [Zahl] – stoert die [n]-Zuordnung im '
                           'Buchmanager'.format(p['ref']))
    return befunde


# --- Sefaria-Fassungen vergleichen -------------------------------------------
def vergleiche_werke(a, b):
    """Strukturvergleich zweier JSON-Fassungen (z. B. Upload gegen aktuelle
    Sefaria-Fassung). Liefert Liste von Befundzeilen."""
    out = []
    ka = [x['key'] for x in a['abschnitte']]
    kb = [x['key'] for x in b['abschnitte']]
    for k in ka:
        if k not in kb:
            out.append('nur in A: Abschnitt ' + k)
    for k in kb:
        if k not in ka:
            out.append('nur in B: Abschnitt ' + k)
    ia, ib = C.absatz_index(a), C.absatz_index(b)
    changed = [r for r in ia if r in ib and ia[r][2]['html'] != ib[r][2]['html']]
    only_a = [r for r in ia if r not in ib]
    only_b = [r for r in ib if r not in ia]
    for r in changed[:40]:
        out.append('Absatz geaendert: ' + r)
    if len(changed) > 40:
        out.append('… {} weitere geaenderte Absaetze'.format(len(changed) - 40))
    for r in only_a[:20]:
        out.append('Absatz nur in A: ' + r)
    for r in only_b[:20]:
        out.append('Absatz nur in B: ' + r)
    out.insert(0, 'Absaetze: A {} · B {} · geaendert {} · nur A {} · nur B {}'.format(
        len(ia), len(ib), len(changed), len(only_a), len(only_b)))
    return out


# --- Scaninventar -------------------------------------------------------------
class TeilDatei(io.RawIOBase):
    """Liest ein in Teile zerlegtes ZIP (name.zip.001, .002 …) wie eine Datei."""

    def __init__(self, teile):
        self.teile = [Path(t) for t in teile]
        self.groessen = [t.stat().st_size for t in self.teile]
        self.gesamt = sum(self.groessen)
        self.pos = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.gesamt + off)
        return self.pos

    def readinto(self, b):
        n, start, rest, i, out = len(b), self.pos, len(b), 0, bytearray()
        while rest > 0 and self.pos < self.gesamt:
            acc = 0
            for i, g in enumerate(self.groessen):
                if self.pos < acc + g:
                    break
                acc += g
            with open(self.teile[i], 'rb') as fh:
                fh.seek(self.pos - acc)
                chunk = fh.read(min(rest, acc + self.groessen[i] - self.pos))
            out += chunk
            self.pos += len(chunk)
            rest -= len(chunk)
        b[:len(out)] = out
        return len(out)


def teil_zips(p):
    """Ordner oder name.zip.001 -> Liste von Teilgruppen."""
    p = Path(p)
    if p.is_file() and re.search(r'\.zip\.0*1$', p.name):
        stamm = re.sub(r'\.0*1$', '', p.name)
        return [sorted(p.parent.glob(glob_escape(stamm) + '.[0-9][0-9][0-9]'))]
    if p.is_dir():
        gruppen = collections.OrderedDict()
        for f in sorted(p.glob('*.zip.[0-9][0-9][0-9]')):
            gruppen.setdefault(f.name.rsplit('.', 1)[0], []).append(f)
        return list(gruppen.values())
    return []


def glob_escape(s):
    return re.sub(r'([\[\]*?])', r'[\1]', s)


class ScanQuelle:
    """Seitenbilder aus ZIP-Dateien (auch geteilt: .zip.001 …) oder Ordnern,
    Schluessel = Sequenznummer."""

    def __init__(self, pfade):
        self.seiten = {}
        for p in pfade or []:
            p = Path(p)
            gruppen = teil_zips(p)
            if gruppen:
                for teile in gruppen:
                    z = zipfile.ZipFile(io.BufferedReader(TeilDatei(teile), 1 << 20))
                    for info in z.infolist():
                        m = SCAN_NAME_RE.search(info.filename)
                        if m:
                            self._add(int(m.group(1)), m.group(2), info.filename, info.file_size,
                                      ('teile', tuple(map(str, teile)), info.filename))
                if p.is_dir() and not any(SCAN_NAME_RE.search(f.name) for f in p.rglob('*')):
                    continue
                if not p.is_dir():
                    continue
            if p.is_file() and zipfile.is_zipfile(p):
                z = zipfile.ZipFile(p)
                for info in z.infolist():
                    m = SCAN_NAME_RE.search(info.filename)
                    if m:
                        self._add(int(m.group(1)), m.group(2), info.filename, info.file_size,
                                  ('zip', p, info.filename))
            elif p.is_dir():
                for f in sorted(p.rglob('*')):
                    m = SCAN_NAME_RE.search(f.name)
                    if m and f.is_file():
                        self._add(int(m.group(1)), m.group(2), f.name, f.stat().st_size,
                                  ('file', f, None))
            else:
                raise SystemExit('Scanquelle nicht gefunden oder kein ZIP/Ordner: ' + str(p))

    def _add(self, seq, fl, name, size, ref):
        if seq in self.seiten and self.seiten[seq]['fl_id'] != fl:
            raise SystemExit('Scanseite {} doppelt mit verschiedenen FL-IDs'.format(seq))
        self.seiten[seq] = {'seq': seq, 'fl_id': fl, 'datei': name, 'bytes': size, '_ref': ref}

    def bytes_of(self, seq):
        kind, path, member = self.seiten[seq]['_ref']
        if kind == 'teile':
            with zipfile.ZipFile(io.BufferedReader(TeilDatei(path), 1 << 20)) as z:
                return z.read(member)
        if kind == 'zip':
            with zipfile.ZipFile(path) as z:
                return z.read(member)
        return Path(path).read_bytes()

    def image(self, seq):
        from PIL import Image
        return Image.open(io.BytesIO(self.bytes_of(seq)))


def scaninventar(scan):
    import hashlib
    rows = []
    for seq in sorted(scan.seiten):
        s = scan.seiten[seq]
        data = scan.bytes_of(seq)
        w = h = ''
        try:
            im = scan.image(seq)
            w, h = im.size
        except Exception:
            pass
        rows.append([seq, s['fl_id'], s['datei'], s['bytes'], hashlib.sha256(data).hexdigest(), w, h])
    return rows


def kopfzeile(scan, seq, anteil=0.09, breite=900):
    im = scan.image(seq).convert('L')
    w, h = im.size
    c = im.crop((0, 0, w, int(h * anteil)))
    return c.resize((breite, max(1, int(breite * c.size[1] / w))))


# --- OCR-Vorschlag (optional) ------------------------------------------------
def tesseract_vorhanden():
    return shutil.which('tesseract') is not None


def ocr_woerter(img, psm=6, timeout=90):
    """Tesseract (heb) auf ein PIL-Bild -> Wortliste mit Position und Konfidenz."""
    import csv
    import os
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    env = dict(os.environ, OMP_THREAD_LIMIT='1')
    try:
        r = subprocess.run(['tesseract', 'stdin', 'stdout', '-l', 'heb', '--psm', str(psm), 'tsv'],
                           input=buf.getvalue(), capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return []
    rows = csv.DictReader(io.StringIO(r.stdout.decode('utf-8', 'replace')), delimiter='\t',
                          quoting=csv.QUOTE_NONE)
    out = []
    for x in rows:
        if x.get('level') == '5' and (x.get('text') or '').strip():
            out.append({'t': x['text'].strip(), 'x': int(x['left']), 'y': int(x['top']),
                        'w': int(x['width']), 'h': int(x['height']), 'conf': float(x['conf']),
                        'zeile': (x['block_num'], x['par_num'], x['line_num'])})
    return out


TITEL_RE = re.compile(r'^[^א-ת]*עו[דר]')


def _sauber(w):
    return re.sub(r'[^א-ת"\' ]', '', w['t']).strip()


def _gut(w):
    return len(re.sub(r'[^א-ת]', '', _sauber(w))) >= 2 and w['conf'] >= 30


def _titel_dict(rechts, links, titel, notiz=''):
    clean = lambda L: ' '.join(_sauber(w) for w in sorted(L, key=lambda w: -w['x'])).strip()
    konf = [w['conf'] for w in titel + rechts + links] or [0]
    return {'rechts': clean(rechts), 'mitte': 'עוד יוסף חי', 'links': clean(links),
            'konfidenz': round(sum(konf) / len(konf), 1), 'notiz': notiz}


def kolumnentitel(woerter, breite=None):
    """Findet die Zeile mit dem Mitteltitel 'עוד יוסף חי' und teilt sie in
    rechts / mitte / links. Ist der Mitteltitel unleserlich, genuegt eine Zeile
    mit 'הלכות'/'פרשת'/'קונטרס'; geteilt wird dann an der Seitenmitte.
    -> dict oder None (Seite ohne Kolumnentitel)."""
    zeilen = collections.OrderedDict()
    for w in woerter:
        zeilen.setdefault(w['zeile'], []).append(w)
    for ws in zeilen.values():
        ws = sorted(ws, key=lambda w: -w['x'])
        heb = [re.sub(r'[^א-ת"\']', '', w['t']) for w in ws]
        for i, t in enumerate(heb):
            if TITEL_RE.match(t) and i + 1 < len(heb) and heb[i + 1].startswith('יוס'):
                titel = [ws[i], ws[i + 1]] + ([ws[i + 2]] if i + 2 < len(ws) and heb[i + 2].startswith('חי') else [])
                rechts_x = max(w['x'] + w['w'] for w in titel)
                links_x = min(w['x'] for w in titel)
                rechts = [w for w in ws if w['x'] >= rechts_x and _gut(w)]
                links = [w for w in ws if w['x'] + w['w'] <= links_x and _gut(w)]
                return _titel_dict(rechts, links, titel)
    if breite:
        for ws in list(zeilen.values())[:4]:
            txt = ' '.join(_sauber(w) for w in ws)
            if any(_ratio(t, z) >= 0.7 for t in _tokens(txt) for z in ('הלכות', 'פרשת', 'קונטרס', 'המשולש')):
                rechts = [w for w in ws if w['x'] >= 0.6 * breite and _gut(w)]
                links = [w for w in ws if w['x'] + w['w'] <= 0.4 * breite and _gut(w)]
                if rechts or links:
                    return _titel_dict(rechts, links, [], 'Mitteltitel unleserlich')
    return None


def kopf_bild(im, anteil=0.11, rand=0.04, breite=1600):
    """Kopfstreifen fuer die OCR: Falzstreifen am Rand weg, verkleinert, binarisiert."""
    im = im.convert('L')
    w, h = im.size
    c = im.crop((int(w * rand), 0, int(w * (1 - rand)), int(h * anteil)))
    c = c.resize((breite, max(1, int(breite * c.size[1] / c.size[0]))))
    return c.point(lambda v: 255 if v > 150 else 0)


def ocr_kopf(scan, seq, anteil=0.11):
    im = scan.image(seq)
    k = kolumnentitel(ocr_woerter(kopf_bild(im, anteil)), 1600)
    if k is None:                                   # zweiter Versuch: hoeherer Streifen, ohne Schwelle
        b = kopf_bild(im, anteil + 0.04)
        k = kolumnentitel(ocr_woerter(b), 1600)
    if k is None:
        g = im.convert('L')
        w, h = g.size
        c = g.crop((int(w * 0.04), 0, int(w * 0.96), int(h * anteil)))
        k = kolumnentitel(ocr_woerter(c.resize((1600, int(1600 * c.size[1] / c.size[0])))), 1600)
    if k is not None:
        k['blatt'] = blattzahl(k)
    return k


HEB_ZAHL = {'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
            'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90, 'ק': 100}


def blattzahl(k):
    """Blattzahl am aeusseren Rand (letztes Token links: 'מא', 'מב' …) oder ''."""
    toks = _tokens(k.get('links', ''))
    if not toks:
        return ''
    t = toks[-1]
    if 1 <= len(t) <= 3 and t not in ('ש', 'שר', 'הלכות') and all(c in HEB_ZAHL for c in t):
        vals = [HEB_ZAHL[c] for c in t]
        if vals == sorted(vals, reverse=True):
            return t
    return ''


def _ratio(a, b):
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio()


def _tokens(text):
    t = re.sub(r'[^א-ת ]', ' ', C.strip_nikud(text or ''))
    return [x for x in t.split() if x]


def _hat_wort(text, wort, schwelle=0.6):
    return any(_ratio(t, wort) >= schwelle for t in _tokens(text))


def kandidaten():
    """Abschnitte in Druckreihenfolge: Paraschot (Tora-Reihenfolge), dazu
    Kuntres nach Vayeshev und Purim nach Tetzaveh."""
    out = []
    for key, he in zip(C.PARASHOT, C.PARASHOT_HE):
        out.append((key, he))
        if key == 'Vayeshev':
            out.append(('Kuntres Chut HaMeshulash', 'חוט המשולש'))
        if key == 'Tetzaveh':
            out.append(('Purim', 'פורים'))
    return out


KANDIDATEN = kandidaten()


def finde_paraschot(text, pos, fenster=60, schwelle=0.6):
    """Paraschanamen im Kolumnentitel, nur vorwaerts ab Index pos (Druckreihenfolge).
    Bei gleicher Aehnlichkeit gewinnt die naechstliegende. -> [Index …]"""
    w = _tokens(text)
    found, i = [], 0
    while i < len(w):
        best = None
        for j in range(pos, min(len(KANDIDATEN), pos + fenster)):
            name = KANDIDATEN[j][1]
            n = len(name.split())
            r = _ratio(' '.join(w[i:i + n]), name)
            wert = r - 0.01 * (j - pos)                  # naechstliegende bevorzugt
            # weite Spruenge brauchen eindeutigere Lesung
            if r >= schwelle + 0.02 * (j - pos) and (best is None or wert > best[3] + 0.05):
                best = (r, j, n, wert)
        if best:
            found.append(best[1])
            pos = best[1]
            i += best[2]
        else:
            i += 1
    return found


def ist_halakhot(k):
    toks = (k or {}).get('links', '').split()
    return bool(k) and (_hat_wort(k['links'], 'הלכות') or
                        any(re.fullmatch(r'["\']*ש["\'י]?[רף]["\']*', t) for t in toks))


def ist_kuntres(k):
    return bool(k) and (_hat_wort(k['links'], 'המשולש') or _hat_wort(k['rechts'], 'קונטרס', 0.55))


def ist_derashot(k):
    return bool(k) and (_hat_wort(k['rechts'], 'פרשת', 0.7) or _hat_wort(k['rechts'], 'פתיחה', 0.7))


def deute_kolumnentitel(k, werk, pos=0):
    """Kolumnentitel -> (art, abschnitt, notiz).
    Halakhot:  rechts = Parascha(ot) der Seite, links = 'הלכות ש"ר'
    Kuntres:   rechts = 'קונטרס', links = 'חוט המשולש'
    Derashot:  rechts = 'פרשת' bzw. 'פתיחה', links = Parascha bzw. Ordnungszahl
    Anhang:    'מראות יחזקאל'"""
    if not k:
        return '', '', 'kein Kolumnentitel erkannt'
    k = dict(k)
    if ist_halakhot({'links': k['rechts'], 'rechts': ''}) and not ist_halakhot(k):
        k['rechts'], k['links'] = k['links'], k['rechts']      # vertauschte Seiten
    if ist_derashot(k):
        return 'Derashot', '', ' '.join(_tokens(k['rechts'])[:1] + _tokens(k['links']))
    if ist_kuntres(k):
        return 'Kuntres', 'Kuntres Chut HaMeshulash', ''
    if ist_halakhot(k):
        idx = finde_paraschot(k['rechts'], pos)
        if not idx:
            return 'Halakhot', '', 'Parascha nicht erkannt: "{}"'.format(k['rechts'])
        keys = []
        for j in idx:
            if KANDIDATEN[j][0] not in keys:
                keys.append(KANDIDATEN[j][0])
        return 'Halakhot', '+'.join(keys), ''
    if ist_derashot(k):
        return 'Derashot', '', ' '.join(_tokens(k['rechts'])[:1] + _tokens(k['links']))
    if _hat_wort(k['rechts'], 'מראות') or _hat_wort(k['links'], 'יחזקאל'):
        return 'Anhang', '', 'מראות יחזקאל'
    toks = _tokens(k['links'])
    for n in C.PARASHOT_HE:                      # 'פרשת' rechts unleserlich, Parascha links lesbar
        m = len(n.split())
        if any(_ratio(' '.join(toks[i:i + m]), n) >= 0.8 for i in range(len(toks))):
            return 'Derashot', '', 'פרשת ' + n + ' (פרשת unleserlich)'
    return 'Unklar', '', 'Kolumnentitel: {} · {}'.format(k['rechts'], k['links'])


def deute_kopfzeile(text, werk):
    """Freitext eines Kolumnentitels in Lesereihenfolge -> (art, abschnitt)."""
    t = re.sub(r'\s+', ' ', re.sub(r'[^א-ת"\' ]', ' ', C.strip_nikud(text or ''))).strip()
    m = re.search(r'עו[דר]\s+יוס\S*\s+חי', t)
    k = {'rechts': t[:m.start()].strip(), 'links': t[m.end():].strip()} if m else {'rechts': t, 'links': ''}
    art, ab, _ = deute_kolumnentitel(k, werk)
    return art, ab


def _ocr_job(args):
    pfade, seq = args
    scan = ScanQuelle(pfade)
    return seq, ocr_kopf(scan, seq)


def ocr_vorschlag(scan, scan_pfade, werk, prozesse=4):
    """Kolumnentitel aller Seiten -> Konkordanzzeilen (Vorschlag)."""
    from multiprocessing import Pool
    seqs = sorted(scan.seiten)
    with Pool(prozesse) as pool:
        res = dict(pool.map(_ocr_job, [(list(map(str, scan_pfade)), s) for s in seqs], chunksize=4))
    zeilen, pos, aktuell = [], 0, ''
    index = {key: j for j, (key, he) in enumerate(KANDIDATEN)}
    vorher = ''
    for seq in seqs:
        k = res.get(seq)
        if vorher not in HALACHA_ARTEN and vorher != '':
            pos, aktuell = 0, ''                   # neuer Block: Reihenfolge von vorn
        art, ab, notiz = deute_kolumnentitel(k, werk, pos)
        if art:
            vorher = art
        if art == 'Halakhot' and not ab and aktuell:
            ab, notiz = aktuell, 'Parascha aus Vorseite (Kolumnentitel unleserlich: "{}")'.format(k['rechts'])
        if ab:
            pos = index[ab.split('+')[-1]]
            aktuell = ab.split('+')[-1]
        zeilen.append({'seq': seq, 'fl_id': scan.seiten[seq]['fl_id'], 'art': art, 'abschnitt': ab,
                       'ot_von': '', 'ot_bis': '',
                       'kopf_rechts': (k or {}).get('rechts', ''), 'kopf_mitte': (k or {}).get('mitte', ''),
                       'kopf_links': (k or {}).get('links', ''),
                       'bemerkung': 'OCR {}{}{}{}'.format(
                           'Konfidenz {}'.format(k['konfidenz']) if k else 'ohne Kolumnentitel',
                           (' · Blatt ' + k['blatt']) if k and k.get('blatt') else '',
                           (' · ' + k['notiz']) if k and k.get('notiz') else '',
                           (' · ' + notiz) if notiz else '')})
    return zeilen


# --- Belege des Buches ueber seinen Umfang -------------------------------------
BUECHER = [('Bereshit', 0, 11), ('Shemot', 12, 22), ('Vayikra', 23, 32),
           ('Bamidbar', 33, 42), ('Devarim', 43, 53)]


def buch_der_parascha(key):
    i = C.PARASHOT.index(key)
    return next(b for b, lo, hi in BUECHER if lo <= i <= hi)


def buecher_der_abschnitte(werk):
    """Buch je Abschnitt; Sonderabschnitte (Purim, Kuntres) gehoeren zum Buch
    der folgenden Parascha (Kuntres: 'קודם שאכתוב הלכות ... לפרשת מקץ')."""
    keys = [a['key'] for a in werk['abschnitte']]
    out = {}
    for i, a in enumerate(werk['abschnitte']):
        if a['parascha']:
            out[a['key']] = buch_der_parascha(a['key'])
            continue
        nxt = next((k for k in keys[i + 1:] if k in C.PARASHOT), None)
        prv = next((k for k in reversed(keys[:i]) if k in C.PARASHOT), None)
        out[a['key']] = buch_der_parascha(nxt or prv) if (nxt or prv) else ''
    return out


def lade_belege(path):
    if not path or not Path(path).exists():
        return []
    return json.loads(Path(path).read_text(encoding='utf-8')).get('belege', [])


def pruefe_belege(werk, summary, belege):
    """-> {key: hinweis} und Befundzeilen fuer Abschnitte ausserhalb des
    vom Buch selbst angegebenen Umfangs."""
    buch = buecher_der_abschnitte(werk)
    hinweise, befunde = {}, []
    for b in belege:
        if b.get('art') != 'umfang':
            continue
        erlaubt = set(b.get('buecher') or [])
        aus = [s for s in summary if buch.get(s['key']) and buch[s['key']] not in erlaubt]
        for s in aus:
            hinweise[s['key']] = 'laut Scan S. {} nur {} – Abschnitt gehoert zu {}'.format(
                b['seq'], '/'.join(sorted(erlaubt)), buch[s['key']])
        if aus:
            befunde.append('Umfang laut Buch (Scan S. {}, {}): nur Halakhot zu {}. Im JSON ausserhalb: '
                           '{} ({} Halachot, {} Zeichen) – Herkunft im Scan pruefen'.format(
                               b['seq'], b.get('stelle', ''), ' und '.join(b.get('buecher') or []),
                               ', '.join(s['key'] for s in aus), sum(s['halachot'] for s in aus),
                               sum(s['zeichen'] for s in aus)))
    return hinweise, befunde, buch


# --- Konkordanz ---------------------------------------------------------------
def lade_konkordanz(path):
    if not path or not Path(path).exists():
        return []
    rows = C.read_tsv(path)
    for r in rows:
        r['seq'] = int(r['seq'])
        for k in ('ot_von', 'ot_bis'):
            r[k] = int(r[k]) if (r.get(k) or '').strip().isdigit() else None
    return rows


def abschn(r):
    """Abschnitte einer Konkordanzzeile; 'Noach+Lech Lecha' = Wechsel auf der Seite."""
    return [x.strip() for x in (r.get('abschnitt') or '').split('+') if x.strip()]


def scanabgleich(werk, summary, scan, konk, scan_gesamt=None, belege=None):
    befunde = collections.OrderedDict((k, []) for k in
                                      ('FEHLER', 'PRUEFEN', 'HINWEIS'))
    umfang_hinweis, umfang_befunde, buch = pruefe_belege(werk, summary, belege or [])
    befunde['PRUEFEN'].extend(umfang_befunde)
    for b in belege or []:
        if b.get('art') == 'umfang' and b.get('befund_scan'):
            befunde['PRUEFEN'].append('Scan S. {}: {}'.format(b['seq'], b['befund_scan']))
        if b.get('art') == 'befund':
            befunde['HINWEIS'].append('Scan S. {}: {}'.format(b['seq'], b['text']))
    inv = scan.seiten if scan else {}
    keys = {s['key']: s for s in summary}
    erfasst = set()
    for r in konk:
        erfasst.add(r['seq'])
        if r['art'] and r['art'] not in ARTEN:
            befunde['FEHLER'].append('Konkordanz Seite {}: unbekannte Art "{}"'.format(r['seq'], r['art']))
        if inv:
            if r['seq'] not in inv:
                befunde['PRUEFEN'].append('Konkordanz Seite {}: Bild nicht im Scaninventar'.format(r['seq']))
            elif r['fl_id'] and r['fl_id'] != inv[r['seq']]['fl_id']:
                befunde['FEHLER'].append('Konkordanz Seite {}: FL-ID {} ≠ Inventar {}'.format(
                    r['seq'], r['fl_id'], inv[r['seq']]['fl_id']))
        if r['art'] in HALACHA_ARTEN:
            if not abschn(r):
                befunde['FEHLER'].append('Konkordanz Seite {}: Halakhot-Seite ohne Abschnitt'.format(r['seq']))
            for ab in abschn(r):
                if ab not in keys:
                    befunde['PRUEFEN'].append('NUR IM SCAN: Seite {} Abschnitt "{}" fehlt im JSON'.format(
                        r['seq'], ab))
        if r['ot_von'] and r['ot_bis'] and r['ot_von'] > r['ot_bis']:
            befunde['FEHLER'].append('Konkordanz Seite {}: ot_von > ot_bis'.format(r['seq']))
    nicht_erfasst = sorted(set(inv) - erfasst)

    vorhanden = len(inv)
    vollstaendig = bool(scan_gesamt) and vorhanden >= scan_gesamt and not nicht_erfasst
    abschnitte = []
    letzte_seite = 0
    for s in summary:
        seiten = sorted(r['seq'] for r in konk if r['art'] in HALACHA_ARTEN and s['key'] in abschn(r))
        gewicht = sum(1.0 / len(abschn(r)) for r in konk if r['art'] in HALACHA_ARTEN and s['key'] in abschn(r))
        ots = [r['ot_bis'] for r in konk if abschn(r) == [s['key']] and r['ot_bis']]
        ots += [r['ot_von'] for r in konk if abschn(r) == [s['key']] and r['ot_von']]
        status, notiz = '', []
        if seiten:
            status = 'IM SCAN'
            if seiten[0] < letzte_seite:
                status = 'REIHENFOLGE ABWEICHEND'
                befunde['PRUEFEN'].append('{}: beginnt im Scan (S. {}) vor dem Ende des vorigen '
                                          'JSON-Abschnitts (S. {})'.format(s['key'], seiten[0], letzte_seite))
            letzte_seite = max(letzte_seite, seiten[-1])
            luecken = [x for x in range(seiten[0], seiten[-1] + 1) if x not in seiten
                       and x in {r['seq'] for r in konk if r['art'] in HALACHA_ARTEN}]
            if luecken:
                notiz.append('unterbrochen durch Seiten anderer Abschnitte: ' + ','.join(map(str, luecken)))
            if ots and s['tiefe'] == 2:
                scan_max = max(ots)
                if scan_max != s['hoechste_ot']:
                    status = 'ANZAHL ABWEICHEND'
                    befunde['PRUEFEN'].append('{}: hoechste Ot im Scan {} · im JSON {}'.format(
                        s['key'], scan_max, s['hoechste_ot']))
                else:
                    notiz.append('Ot-Zahl stimmt ({})'.format(scan_max))
            elif s['tiefe'] == 2:
                notiz.append('Ot-Zahl im Scan noch nicht erfasst (ot_von/ot_bis)')
        else:
            status = 'FEHLT IM SCAN' if vollstaendig else 'NOCH NICHT IM SCANBEREICH'
            if vollstaendig:
                befunde['FEHLER'].append('{}: im vollstaendigen Scan nicht gefunden'.format(s['key']))
        if s['key'] in umfang_hinweis:
            if status == 'IM SCAN':
                notiz.append('im Scan vorhanden, obwohl ausserhalb des angegebenen Umfangs')
            else:
                status = 'AUSSERHALB DES ANGEGEBENEN UMFANGS'
            notiz.append(umfang_hinweis[s['key']])
        if s['leer']:
            bestaetigt = set()
            for b in belege or []:
                if b.get('abschnitt') == s['key']:
                    bestaetigt |= set(b.get('ot_leer_bestaetigt') or [])
            offen = [n for n in s['leer'] if n not in bestaetigt]
            if offen:
                befunde['PRUEFEN'].append('{}: Ot {} ist in Sefaria leer – Text im Scan suchen'.format(
                    s['key'], ','.join(map(str, offen))))
            notiz.append('leere Ot im JSON: {}{}'.format(','.join(map(str, s['leer'])),
                                                       ' (Zaehlung des Drucks, belegt)' if not offen else ''))
        abschnitte.append({'ord': s['ord'], 'key': s['key'], 'he_title': s['he_title'],
                           'buch': buch.get(s['key'], ''), 'status': status, 'scanseiten': seiten,
                           'erste_seite': seiten[0] if seiten else None,
                           'halachot_json': s['halachot'], 'hoechste_ot_json': s['hoechste_ot'],
                           'seiten_scan': round(gewicht, 1), 'zeichen_json': s['zeichen'],
                           'notiz': '; '.join(notiz)})
    pruefe_umfang(abschnitte, befunde)
    aus = [a for a in abschnitte if a['key'] in umfang_hinweis]
    if aus and all(a['scanseiten'] for a in aus):
        for b in list(umfang_befunde):
            befunde['PRUEFEN'].remove(b)
            befunde['HINWEIS'].insert(0, b.replace('Herkunft im Scan pruefen',
                                                   'im Scan dennoch gedruckt (S. {}–{})'.format(
                                                       aus[0]['scanseiten'][0], aus[-1]['scanseiten'][-1])))
        for b in list(befunde['PRUEFEN']):
            if 'Trotz der Vorrede' in b:
                befunde['PRUEFEN'].remove(b)
    if nicht_erfasst:
        befunde['HINWEIS'].append('Scanseiten ohne Konkordanzeintrag: ' + kurzliste(nicht_erfasst))
    if not scan_gesamt:
        befunde['HINWEIS'].append('Gesamtseitenzahl des Digitalisats nicht angegeben (--scan-gesamt); '
                                  '"fehlt" wird deshalb nicht festgestellt.')
    arten = collections.Counter(r['art'] for r in konk)
    hal_seiten = sum(1 for r in konk if r['art'] in HALACHA_ARTEN)
    return {'scanseiten_vorhanden': vorhanden, 'scan_gesamt': scan_gesamt,
            'scanseiten_von_bis': [min(inv), max(inv)] if inv else None,
            'konkordanz_seiten': len(konk), 'arten': dict(arten),
            'halakhot_seiten': hal_seiten, 'vollstaendig': vollstaendig,
            'nicht_erfasst': nicht_erfasst, 'abschnitte': abschnitte,
            'befunde': befunde}


def pruefe_umfang(abschnitte, befunde, toleranz=0.35, min_diff=1.5):
    """Seitenzahl im Scan gegen Textmenge im JSON (mittlere Zeichen je Druckseite).
    Grobe Plausibilitaet: fehlender oder zusaetzlicher Text faellt als Ausreisser auf."""
    im = [a for a in abschnitte if a['seiten_scan'] > 0 and a['zeichen_json'] > 0]
    if len(im) < 3:
        return None
    zps = sum(a['zeichen_json'] for a in im) / sum(a['seiten_scan'] for a in im)
    for a in im:
        erw = a['zeichen_json'] / zps
        a['seiten_erwartet'] = round(erw, 1)
        if abs(a['seiten_scan'] - erw) >= min_diff and not (1 - toleranz) <= a['seiten_scan'] / erw <= (1 + toleranz):
            befunde['PRUEFEN'].append('{}: Umfang im Scan {} Seiten, nach JSON-Textmenge erwartet {:.1f} '
                                      '({:.0f} Zeichen je Druckseite)'.format(a['key'], a['seiten_scan'], erw, zps))
            a['notiz'] = '; '.join(x for x in [a['notiz'], 'Umfang auffaellig'] if x)
    return zps


def kurzliste(nums):
    nums = sorted(nums)
    out, start, prev = [], None, None
    for n in nums + [None]:
        if start is None:
            start = prev = n
        elif n is not None and n == prev + 1:
            prev = n
        else:
            out.append(str(start) if start == prev else '{}-{}'.format(start, prev))
            start = prev = n
    return ','.join(out)


def vorschlag_uebernehmen(konk_path, vorschlag_path):
    """OCR-Vorschlag in die Konkordanz uebernehmen.

    Vorhandene Zeilen ohne 'OCR' am Anfang der Bemerkung sind Lektoratsstand und
    bleiben unberuehrt; fruehere OCR-Zeilen werden erneuert. Seiten ohne
    Kolumnentitel erhalten Art/Abschnitt der Nachbarseiten, wenn beide Nachbarn
    uebereinstimmen (vermerkt), sonst 'Unklar'. -> (neu, erneuert, geschuetzt)"""
    alt = {r['seq']: r for r in C.read_tsv(konk_path)} if Path(konk_path).exists() else {}
    vor = {int(r['seq']): r for r in C.read_tsv(vorschlag_path)}
    seqs = sorted(vor)
    for i, seq in enumerate(seqs):
        r = vor[seq]
        if r['art']:
            continue
        prev = next((vor[x] for x in reversed(seqs[:i]) if vor[x]['art']), None)
        nxt = next((vor[x] for x in seqs[i + 1:] if vor[x]['art']), None)
        if prev and nxt and prev['art'] == nxt['art'] and prev['abschnitt'] == nxt['abschnitt']:
            r['art'], r['abschnitt'] = prev['art'], prev['abschnitt']
            r['bemerkung'] += ' · Art/Abschnitt aus Nachbarseiten'
        else:
            r['art'] = 'Unklar'
            r['bemerkung'] += ' · Abschnittsgrenze oder Sonderseite – ansehen'
    neu = erneuert = geschuetzt = 0
    zeilen = []
    for seq in sorted(set(vor) | {int(k) for k in alt}):
        a = alt.get(str(seq)) or alt.get(seq)
        if a and not (a.get('bemerkung') or '').startswith('OCR'):
            zeilen.append(a)
            geschuetzt += 1
            continue
        if seq in vor:
            zeilen.append(vor[seq])
            erneuert += 1 if a else 0
            neu += 0 if a else 1
    kopf = [l for l in Path(konk_path).read_text(encoding='utf-8-sig').splitlines()
            if l.startswith('#')] if Path(konk_path).exists() else []
    lines = kopf + ['\t'.join(KONK_HEADER)]
    for z in zeilen:
        lines.append('\t'.join(re.sub(r'[\t\r\n]+', ' ', str(z.get(k, '') or '')) for k in KONK_HEADER))
    Path(konk_path).write_text('\r\n'.join(lines) + '\r\n', encoding='utf-8')
    return neu, erneuert, geschuetzt


# --- Ausgabe ------------------------------------------------------------------
def bericht_text(werk, summary, schema, abgl, vergleich=None):
    m = werk['meta']
    L = ['OD YOSEF CHAI · HALAKHOT · ABSCHNITTSLISTE UND SCANABGLEICH', '',
         'JSON:  {} · {}'.format(m['title'], m['versionTitle']),
         '       {} · sha256 {}'.format(Path(m['datei']).name, m['sha256']),
         'Quelle laut JSON: {}'.format(m['versionSource']),
         'Lizenz laut JSON: {}'.format(m['license']), '',
         'ABSCHNITTE (JSON-Reihenfolge)',
         '{:>3}  {:<26} {:<20} {:<9} {:>5} {:>6} {:>8}  {}'.format('Nr', 'Schluessel', 'Titel', 'Buch', 'Ot', 'Abs.', 'Zeichen', 'Scan')]
    st = {a['key']: a for a in abgl['abschnitte']}
    for s in summary:
        a = st[s['key']]
        scan = a['status'] + (' S.{}–{}'.format(a['scanseiten'][0], a['scanseiten'][-1]) if a['scanseiten'] else '')
        if a.get('seiten_erwartet'):
            scan += ' ({:.1f} S., erwartet {:.1f})'.format(a['seiten_scan'], a['seiten_erwartet'])
        L.append('{:>3}  {:<26} {:<20} {:<9} {:>5} {:>6} {:>8}  {}'.format(
            s['ord'], s['key'], s['he_title'], a['buch'], s['halachot'], s['absaetze'], s['zeichen'], scan))
    L += ['', 'Summe: {} Abschnitte · {} Halachot/Segmente · {} Absaetze · {} Zeichen'.format(
        len(summary), sum(s['halachot'] for s in summary), sum(s['absaetze'] for s in summary),
        sum(s['zeichen'] for s in summary)), '', 'STRUKTUR DES JSON']
    L += ['  - ' + b for b in schema] or ['  ohne Befund']
    L += ['', 'SCAN',
          '  Seiten im Inventar: {}{}'.format(abgl['scanseiten_vorhanden'],
                                              ' (Seq. {}–{})'.format(*abgl['scanseiten_von_bis']) if abgl['scanseiten_von_bis'] else ''),
          '  Gesamtseiten Digitalisat: {}'.format(abgl['scan_gesamt'] or 'nicht angegeben'),
          '  Konkordanz: {} Seiten erfasst · Arten: {}'.format(
              abgl['konkordanz_seiten'], ', '.join('{} {}'.format(k, v) for k, v in sorted(abgl['arten'].items()))),
          '  Halakhot-/Kuntres-Seiten im erfassten Bereich: {}'.format(abgl['halakhot_seiten']),
          '  Abgleich vollstaendig: {}'.format('ja' if abgl['vollstaendig'] else 'nein')]
    for k, v in abgl['befunde'].items():
        L += ['', '{} ({})'.format(k, len(v))] + ['  - ' + x for x in v]
    if vergleich is not None:
        L += ['', 'VERGLEICH MIT AKTUELLER SEFARIA-FASSUNG'] + ['  - ' + x for x in vergleich]
    return '\n'.join(L) + '\n'


def pruefbogen_html(path, werk, summary, abgl, konk, scan, bilder_dir):
    konk_by = {r['seq']: r for r in konk}
    st = {a['key']: a for a in abgl['abschnitte']}
    first_ot = {}
    for a in werk['abschnitte']:
        h = next((h for h in a['halachot'] if not h['leer']), None)
        if h:
            p = next(p for p in h['absaetze'] if C.strip_tags(p['html']).strip())
            first_ot[a['key']] = (h['n'], incipit(p['html'], 14))
    e = html.escape
    out = ['<!doctype html><html lang="de"><head><meta charset="utf-8">',
           '<title>OYC Scanabgleich</title><style>',
           'body{font-family:system-ui,sans-serif;margin:16px;color:#222;background:#fff}',
           'table{border-collapse:collapse;width:100%;margin:12px 0}td,th{border:1px solid #ccc;padding:4px 6px;vertical-align:top;font-size:13px}',
           '.he{direction:rtl;font-family:"Frank Ruhl Libre","Times New Roman",serif;font-size:15px}',
           '.ok{background:#e8f5e9}.warn{background:#fff8e1}.bad{background:#ffebee}.todo{background:#f3f3f3}',
           'img{max-width:100%;height:auto;display:block}h2{margin-top:28px}',
           '</style></head><body>',
           '<h1>Od Yosef Chai · Halakhot · Scanabgleich</h1>',
           '<p>JSON {} · {} Abschnitte · Scan {} Seiten im Inventar · Konkordanz {} Seiten</p>'.format(
               e(werk['meta']['versionTitle']), len(summary), abgl['scanseiten_vorhanden'], len(konk)),
           '<h2>Abschnitte</h2><table><tr><th>Nr</th><th>Abschnitt</th><th>Titel</th><th>Ot (JSON)</th>'
           '<th>Status</th><th>Scanseiten</th><th>Beginn Ot 1 (JSON)</th><th>Notiz</th></tr>']
    for s in summary:
        a = st[s['key']]
        cls = {'IM SCAN': 'ok', 'NOCH NICHT IM SCANBEREICH': 'todo', 'FEHLT IM SCAN': 'bad'}.get(a['status'], 'warn')
        fo = first_ot.get(s['key'], ('', ''))
        out.append('<tr class="{}"><td>{}</td><td>{}</td><td class="he">{}</td><td>{}</td><td>{}</td><td>{}</td>'
                   '<td class="he">[{}] {}</td><td>{}</td></tr>'.format(
                       cls, s['ord'], e(s['key']), e(s['he_title']), s['halachot'], e(a['status']),
                       e(kurzliste(a['scanseiten'])), fo[0], e(fo[1]), e(a['notiz'])))
    out.append('</table><h2>Scanseiten · Kolumnentitel</h2><table><tr><th>Seq</th><th>FL</th>'
               '<th>Konkordanz</th><th>Kopfzeile (Ausschnitt)</th></tr>')
    for seq in sorted(scan.seiten if scan else konk_by):
        r = konk_by.get(seq, {})
        kopf = ' · '.join(r.get(k, '') for k in ('kopf_rechts', 'kopf_mitte', 'kopf_links') if r.get(k))
        info = '<b>{}</b> {}{}<br><span dir="auto">{}</span>'.format(
            e(r.get('art', '–')), e(r.get('abschnitt', '')),
            '<br><span class="he">{}</span>'.format(e(kopf)) if kopf else '', e(r.get('bemerkung', '')))
        if r.get('ot_von') or r.get('ot_bis'):
            info += '<br>Ot {}–{}'.format(r.get('ot_von') or '?', r.get('ot_bis') or '?')
        img = ''
        if bilder_dir and (Path(bilder_dir) / '{:04d}_kopf.jpg'.format(seq)).exists():
            rel = Path(bilder_dir).name + '/{:04d}_kopf.jpg'.format(seq)
            img = '<img src="{}" alt="Kopfzeile Seite {}">'.format(e(rel), seq)
        fl = scan.seiten[seq]['fl_id'] if scan and seq in scan.seiten else r.get('fl_id', '')
        out.append('<tr class="{}"><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            'todo' if not r else '', seq, e(fl), info, img))
    out.append('</table></body></html>')
    Path(path).write_text('\n'.join(out), encoding='utf-8')


# --- IIIF-Download ----------------------------------------------------------
def iiif_seiten(manifest):
    """[(seq, fl_id, bild_url)] aus einem IIIF-Manifest v2 oder v3."""
    out = []
    if 'sequences' in manifest:
        canvases = manifest['sequences'][0].get('canvases', [])
        for i, c in enumerate(canvases, start=1):
            res = c['images'][0]['resource']
            svc = res.get('service') or {}
            if isinstance(svc, list):
                svc = svc[0]
            sid = (svc.get('@id') or svc.get('id') or '').rstrip('/')
            url = sid + '/full/full/0/default.jpg' if sid else res.get('@id')
            out.append((i, (sid or res.get('@id', '')).rstrip('/').split('/')[-1], url))
    else:
        for i, c in enumerate(manifest.get('items', []), start=1):
            body = c['items'][0]['items'][0]['body']
            svc = body.get('service') or []
            svc = svc[0] if isinstance(svc, list) and svc else (svc or {})
            sid = (svc.get('id') or svc.get('@id') or '').rstrip('/')
            url = sid + '/full/max/0/default.jpg' if sid else body.get('id')
            out.append((i, (sid or body.get('id', '')).rstrip('/').split('/')[-1], url))
    return out


def iiif_laden(manifest_url, ziel, seiten=None):
    manifest = json.loads(C.http_get(manifest_url).decode('utf-8'))
    liste = iiif_seiten(manifest)
    wahl = set(C.parse_range(seiten, len(liste))) if seiten else None
    Path(ziel).mkdir(parents=True, exist_ok=True)
    n = 0
    for seq, fl, url in liste:
        if wahl and seq not in wahl:
            continue
        f = Path(ziel) / '{:04d}_{}.jpg'.format(seq, re.sub(r'[^A-Za-z0-9_-]', '_', fl))
        if f.exists() and f.stat().st_size > 0:
            continue
        f.write_bytes(C.http_get(url, timeout=180))
        n += 1
    return len(liste), n


# --- Hauptablauf ---------------------------------------------------------------
def run(json_path=None, scan_pfade=None, konkordanz=None, out='out', scan_gesamt=None,
        ocr=False, kopfbilder=True, vergleich_json=None, quiet=False, belege=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    werk = C.load_werk(json_path)
    rows, summary = abschnittsliste(werk)
    C.write_tsv(out / (C.WERK_TAG + '_Abschnittsliste.tsv'),
                ['abschnitt_nr', 'abschnitt', 'he_title', 'ot', 'sefaria_ref', 'absaetze',
                 'he_zeichen', 'stichwort', 'incipit', 'hinweis'], rows)
    schema = schema_pruefung(werk)
    scan = ScanQuelle(scan_pfade) if scan_pfade else None
    konk_path = Path(konkordanz) if konkordanz else C.HERE / 'scan_konkordanz.tsv'
    konk = lade_konkordanz(konk_path)
    if scan:
        C.write_tsv(out / 'scan' / (C.WERK_TAG + '_Scaninventar.tsv'),
                    ['seq', 'fl_id', 'datei', 'bytes', 'sha256', 'breite', 'hoehe'], scaninventar(scan))
    bilder_dir = None
    if scan and kopfbilder:
        bilder_dir = out / 'scan' / 'kopfzeilen'
        bilder_dir.mkdir(parents=True, exist_ok=True)
        for seq in sorted(scan.seiten):
            f = bilder_dir / '{:04d}_kopf.jpg'.format(seq)
            if not f.exists():
                kopfzeile(scan, seq).save(f, quality=50)
    if scan and ocr:
        if not tesseract_vorhanden():
            print('HINWEIS: tesseract nicht gefunden – OCR-Vorschlag uebersprungen.')
        else:
            vorschlag = ocr_vorschlag(scan, scan_pfade, werk)
            C.write_tsv(out / 'scan' / 'scan_konkordanz_vorschlag.tsv', KONK_HEADER,
                        [[z[k] for k in KONK_HEADER] for z in vorschlag])
    belege_path = Path(belege) if belege else C.HERE / 'scan_belege.json'
    abgl = scanabgleich(werk, summary, scan, konk, scan_gesamt, lade_belege(belege_path))
    vergleich = None
    if vergleich_json:
        vergleich = vergleiche_werke(werk, C.load_werk(vergleich_json))
    txt = bericht_text(werk, summary, schema, abgl, vergleich)
    (out / (C.WERK_TAG + '_Scanabgleich.txt')).write_text(txt, encoding='utf-8')
    C.write_json(out / (C.WERK_TAG + '_Scanabgleich.json'),
                 {'meta': werk['meta'], 'konkordanz': str(konk_path), 'abschnitte': summary,
                  'schema': schema, 'abgleich': abgl, 'vergleich_sefaria': vergleich})
    pruefbogen_html(out / 'scan' / (C.WERK_TAG + '_Scan_Pruefbogen.html'), werk, summary, abgl,
                    konk, scan, bilder_dir)
    if not quiet:
        print(txt)
    return {'werk': werk, 'summary': summary, 'abgleich': abgl, 'schema': schema,
            'vergleich': vergleich}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--json', default=str(C.SOURCE_JSON), help='Sefaria-JSON (Vorgabe: source/)')
    ap.add_argument('--scan', nargs='*', default=[], help='Scan-ZIP(s) oder -Ordner')
    ap.add_argument('--konkordanz', default=str(C.HERE / 'scan_konkordanz.tsv'))
    ap.add_argument('--belege', default=str(C.HERE / 'scan_belege.json'))
    ap.add_argument('--scan-gesamt', type=int, help='Gesamtseitenzahl des NLI-Digitalisats')
    ap.add_argument('--ocr', action='store_true', help='Kolumnentitel per tesseract vorschlagen')
    ap.add_argument('--ohne-kopfbilder', action='store_true')
    ap.add_argument('--vorschlag-uebernehmen', metavar='TSV',
                    help='OCR-Vorschlag in die Konkordanz uebernehmen (Lektoratszeilen bleiben)')
    ap.add_argument('--out', default=str(C.HERE / 'out'))
    ap.add_argument('--laden-sefaria', action='store_true',
                    help='aktuelle Sefaria-Fassung laden (nach out/sefaria_aktuell.json)')
    ap.add_argument('--vergleiche-sefaria', action='store_true',
                    help='geladene aktuelle Fassung mit --json vergleichen')
    ap.add_argument('--sefaria-url', default=C.SEFARIA_URL)
    ap.add_argument('--iiif-manifest', help='IIIF-Manifest des NLI-Digitalisats')
    ap.add_argument('--seiten', help='Seitenauswahl fuer den IIIF-Download, z. B. 26-200')
    ap.add_argument('--laden-nach', help='Zielordner fuer IIIF-Seitenbilder')
    a = ap.parse_args(argv)

    if a.vorschlag_uebernehmen:
        n, e, g = vorschlag_uebernehmen(a.konkordanz, a.vorschlag_uebernehmen)
        print('Konkordanz {}: {} Seiten neu, {} erneuert, {} Lektoratszeilen unveraendert'.format(
            a.konkordanz, n, e, g))
        return 0
    if a.iiif_manifest:
        if not a.laden_nach:
            ap.error('--laden-nach fehlt')
        total, neu = iiif_laden(a.iiif_manifest, a.laden_nach, a.seiten)
        print('IIIF: {} Seiten im Manifest, {} neu geladen nach {}'.format(total, neu, a.laden_nach))
        return 0
    aktuell = None
    if a.laden_sefaria:
        aktuell = Path(a.out) / 'sefaria_aktuell.json'
        C.download_sefaria(a.sefaria_url, aktuell)
        print('Sefaria geladen: {} · sha256 {}'.format(aktuell, C.sha256_file(aktuell)))
    if a.vergleiche_sefaria and not aktuell:
        aktuell = Path(a.out) / 'sefaria_aktuell.json'
        if not aktuell.exists():
            ap.error('keine aktuelle Fassung vorhanden – zuerst --laden-sefaria')
    run(a.json, a.scan, a.konkordanz, a.out, a.scan_gesamt, a.ocr, not a.ohne_kopfbilder,
        aktuell if a.vergleiche_sefaria else None, belege=a.belege)
    return 0


if __name__ == '__main__':
    sys.exit(main())
