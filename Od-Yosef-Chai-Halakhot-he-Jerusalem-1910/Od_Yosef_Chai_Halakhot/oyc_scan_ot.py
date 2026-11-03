# -*- coding: utf-8 -*-
"""
Schritt 1b — Halachot (Ot) des JSON den Scanseiten zuordnen.

Im Druck beginnt jede Halacha mit Ordnungsbuchstabe + fettem Stichwort in
Quadratschrift, jeder weitere Absatz mit einem fetten Stichwort; jede Parascha
mit der Ueberschrift "פרשה …". Der Fliesstext ist Raschi-Schrift.

Bei halber Aufloesung und binarisiert liest Tesseract (heb) die Quadratschrift
sicher (Konfidenz meist > 85), die Raschi-Schrift nicht (< 70). Daraus:

    1  je Halakhot-Seite: fette Woerter (Konfidenz >= 80) und Ueberschriften,
       in Lesereihenfolge (Baender zwischen Ueberschriften, rechte Spalte vor
       linker, oben nach unten)
    2  globale Ausrichtung dieser Wortfolge an der Folge der Stichwoerter aller
       JSON-Absaetze (dynamische Programmierung, Konsonantenvergleich)
    3  je Absatz: Scanseite (falls gefunden); je Seite: Abschnitte und Ot-Bereich

Ergebnis ist ein Vorschlag fuer die Konkordanz (ot_von/ot_bis, Abschnitte je
Seite) und eine Liste je Ot, ob und wo ihr Stichwort im Scan steht.

Aufruf
    python3 oyc_scan_ot.py --scan scan.zip --seiten 322-412 --vorschlag out/scan/scan_konkordanz_vorschlag.tsv
"""
import argparse
import collections
import difflib
import io
import os
import re
import subprocess
import sys
from pathlib import Path

import oyc_common as C
import oyc_abschnitte as A

SKALA = 0.5
SCHWELLE = 140
MIN_KONF = 80


def _ocr(img, psm=3):
    import csv
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    try:
        r = subprocess.run(['tesseract', 'stdin', 'stdout', '-l', 'heb', '--psm', str(psm), 'tsv'],
                           input=buf.getvalue(), capture_output=True, timeout=240,
                           env=dict(os.environ, OMP_THREAD_LIMIT='1'))
    except subprocess.TimeoutExpired:
        return []
    rows = csv.DictReader(io.StringIO(r.stdout.decode('utf-8', 'replace')), delimiter='\t',
                          quoting=csv.QUOTE_NONE)
    return [x for x in rows if x.get('level') == '5' and (x.get('text') or '').strip()]


def nur_buchstaben(t):
    return re.sub(r'[^א-ת]', '', C.norm_quotes(t or ''))


def seite_roh(pfade, seq, cache=None):
    """OCR einer ganzen Seite (halbe Aufloesung, binarisiert), mit Cache."""
    import json as _json
    cf = Path(cache) / '{:04d}.json'.format(seq) if cache else None
    if cf and cf.exists():
        return _json.loads(cf.read_text(encoding='utf-8'))
    scan = A.ScanQuelle(pfade)
    im = scan.image(seq).convert('L')
    w, h = im.size
    klein = im.resize((int(w * SKALA), int(h * SKALA))).point(lambda v: 255 if v > SCHWELLE else 0)
    roh = {'W': klein.size[0], 'H': klein.size[1],
           'w': [{'t': x['text'].strip(), 'x': int(x['left']), 'y': int(x['top']), 'w': int(x['width']),
                  'h': int(x['height']), 'conf': float(x['conf'])} for x in _ocr(klein)]}
    if cf:
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text(_json.dumps(roh, ensure_ascii=False), encoding='utf-8')
    return roh


def seite_lesen(pfade, seq, cache=None, streng=False):
    """-> {'seq', 'woerter': [(text, band, spalte, y, konf)], 'ueberschriften': [{'y','name','x'}]}

    Kandidaten fuer fette Stichwoerter: Woerter mit Konfidenz >= MIN_KONF
    (Quadratschrift; Raschi-Schrift liegt meist darunter). Mit streng=True nur
    solche, die deutlich groesser sind oder am Zeilenanfang stehen – im Test
    (S. 322–412) senkte das die Trefferquote, daher nicht Vorgabe."""
    import statistics
    roh = seite_roh(pfade, seq, cache)
    W, H = roh['W'], roh['H']
    alle = [x for x in roh['w'] if x['y'] >= H * 0.055 and len(nur_buchstaben(x['t'])) >= 1]
    med = statistics.median([x['h'] for x in alle]) if alle else 15
    mitte = W / 2.0
    kanten = {}
    for sp in (0, 1):
        r = sorted(x['x'] + x['w'] for x in alle if ((x['x'] + x['w'] / 2.0) > mitte) == (sp == 0))
        kanten[sp] = r[int(len(r) * 0.95) - 1] if r else W
    woerter, ueber = [], []
    for x in alle:
        bu = nur_buchstaben(x['t'])
        if x['conf'] < MIN_KONF or len(bu) < 2:
            continue
        sp = 0 if x['x'] + x['w'] / 2.0 > mitte else 1
        off = kanten[sp] - (x['x'] + x['w'])
        gross = x['h'] >= 1.6 * med
        anfang = off <= 0.09 * (W / 2.0) and x['h'] >= 1.15 * med
        if not streng or gross or anfang:
            woerter.append(dict(x, b=bu, sp=sp))
    for wd in woerter:
        if A._ratio(wd['b'], 'פרשה') >= 0.75 or A._ratio(wd['b'], 'פרשת') >= 0.75:
            zeile = [v for v in woerter if abs(v['y'] - wd['y']) < wd['h'] and v['x'] < wd['x']]
            name = ' '.join(v['b'] for v in sorted(zeile, key=lambda v: -v['x']))
            ueber.append({'y': wd['y'], 'name': name, 'x': wd['x']})
    grenzen = sorted(u['y'] for u in ueber)
    aus = []
    for wd in woerter:
        if any(abs(wd['y'] - u['y']) < wd['h'] and wd['x'] <= u['x'] + 5 for u in ueber):
            continue
        band = sum(1 for g in grenzen if wd['y'] > g)
        aus.append((wd['b'], band, wd['sp'], wd['y'], wd['conf']))
    aus.sort(key=lambda v: (v[1], v[2], v[3]))
    return {'seq': seq, 'woerter': aus, 'ueberschriften': ueber}


def _job(args):
    return seite_lesen(*args)


def lese_seiten(pfade, seqs, prozesse=4, cache=None):
    from multiprocessing import Pool
    with Pool(prozesse) as pool:
        return pool.map(_job, [(list(map(str, pfade)), s, cache) for s in seqs], chunksize=2)


# --- Ausrichtung ------------------------------------------------------------------
def stichwoerter(werk):
    """Folge aller Absaetze mit erstem fettem Wort (bzw. erstem Wort)."""
    out = []
    for a, h, p in A.C.iter_absaetze(werk):
        m = re.match(r'\s*<b>(.*?)</b>', p['html'], re.S)
        first = C.strip_tags(m.group(1)) if m else C.strip_tags(p['html'])
        wort = (first.split() or [''])[0]
        out.append({'ref': p['ref'], 'abschnitt': a['key'], 'ot': h['n'],
                    'ot_anfang': p['ref'] == next(q['ref'] for q in h['absaetze']
                                                  if C.strip_tags(q['html']).strip()),
                    'wort': nur_buchstaben(wort)})
    return out


_CACHE = {}


def aehnlich(a, b):
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if abs(len(a) - len(b)) > 2:
        return 0.0
    k = (a, b)
    v = _CACHE.get(k)
    if v is None:
        v = _CACHE[k] = difflib.SequenceMatcher(None, a, b).ratio()
    return v


def ausrichten(soll, ist, min_sim=0.75, luecke_soll=-0.15):
    """Globale Ausrichtung (ohne Kreuzungen). soll: JSON-Stichwoerter,
    ist: OCR-Woerter. Ueberspringen von OCR-Woertern kostet nichts (Rauschen),
    nicht gefundene JSON-Absaetze kosten wenig. -> {soll_index: ist_index}"""
    n, m = len(soll), len(ist)
    NEG = -1e9
    # Zeilenweise DP mit Rueckverfolgung ueber kompakte Arrays
    prev = [0.0] * (m + 1)
    zug = []                                      # je i: bytearray der Zuege
    for i in range(1, n + 1):
        cur = [0.0] * (m + 1)
        zz = bytearray(m + 1)
        cur[0] = prev[0] + luecke_soll
        zz[0] = 1
        a = soll[i - 1]
        for j in range(1, m + 1):
            best, z = cur[j - 1], 2               # OCR-Wort ueberspringen
            v = prev[j] + luecke_soll             # JSON-Absatz nicht gefunden
            if v > best:
                best, z = v, 1
            s = aehnlich(a, ist[j - 1])
            if s >= min_sim:
                v = prev[j - 1] + 1.0 + s
                if v > best:
                    best, z = v, 3
            cur[j] = best
            zz[j] = z
        zug.append(zz)
        prev = cur
    paare, i, j = {}, n, m
    while i > 0 and j >= 0:
        z = zug[i - 1][j] if j <= m else 1
        if z == 3:
            paare[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif z == 2:
            j -= 1
        else:
            i -= 1
    return paare


def zuordnen(werk, seiten):
    soll = stichwoerter(werk)
    ist, herkunft = [], []
    for s in seiten:
        for w in s['woerter']:
            ist.append(w[0])
            herkunft.append(s['seq'])
    paare = ausrichten([x['wort'] for x in soll], ist)
    for i, x in enumerate(soll):
        j = paare.get(i)
        x['seite'] = herkunft[j] if j is not None else None
        x['ocr'] = ist[j] if j is not None else ''
    return soll


def seiten_bereiche(soll, seiten):
    """Je Seite: Abschnitte (Druckreihenfolge) und Ot von/bis.
    Beginnt die Seite mitten in einer Halacha (erster Treffer ist kein
    Halacha-Anfang) oder steht die erste Ueberschrift nicht ganz oben, laeuft
    die vorige Halacha auf der Seite weiter."""
    seqs = [s['seq'] for s in seiten]
    oben = {s['seq']: (min((u['y'] for u in s['ueberschriften']), default=None)) for s in seiten}
    je = collections.OrderedDict((q, []) for q in seqs)
    for x in soll:
        if x['seite'] in je:
            je[x['seite']].append(x)
    out, letzter = {}, None
    for q in seqs:
        xs = je[q]
        if not xs:
            out[q] = {'abschnitte': [letzter['abschnitt']] if letzter else [],
                      'ot_von': letzter['ot'] if letzter else None,
                      'ot_bis': letzter['ot'] if letzter else None, 'treffer': 0}
            continue
        erst = xs[0]
        weiter = letzter is not None and (not erst['ot_anfang'] or
                                          (erst['abschnitt'] != letzter['abschnitt'] and
                                           oben[q] is not None and oben[q] > 150))
        ab, von = [], erst['ot']
        if weiter:
            ab.append(letzter['abschnitt'])
            von = letzter['ot']
        for x in xs:
            if x['abschnitt'] not in ab:
                ab.append(x['abschnitt'])
        out[q] = {'abschnitte': ab, 'ot_von': von, 'ot_bis': xs[-1]['ot'], 'treffer': len(xs)}
        letzter = xs[-1]
    return out


def ergaenze_vorschlag(vorschlag_path, bereiche, seiten):
    rows = C.read_tsv(vorschlag_path)
    ueber = {s['seq']: s['ueberschriften'] for s in seiten}
    for r in rows:
        seq = int(r['seq'])
        if seq not in bereiche or r['art'] not in A.HALACHA_ARTEN:
            continue
        b = bereiche[seq]
        kopf = A.abschn(r)
        if b['abschnitte']:
            neu = '+'.join(b['abschnitte'])
            if neu != r['abschnitt']:
                r['bemerkung'] += ' · Abschnitt nach Stichwortabgleich (Kolumnentitel: {})'.format(r['abschnitt'] or '–')
                r['abschnitt'] = neu
            if b['ot_von'] is not None and r['art'] == 'Halakhot':
                r['ot_von'], r['ot_bis'] = b['ot_von'], b['ot_bis']
        r['bemerkung'] += ' · Stichworttreffer {}'.format(b['treffer'])
        if ueber.get(seq):
            r['bemerkung'] += ' · Ueberschrift: ' + '; '.join('פרשה ' + u['name'] for u in ueber[seq])
        if kopf and b['abschnitte'] and not set(kopf) & set(b['abschnitte']):
            r['bemerkung'] += ' · KOLUMNENTITEL WIDERSPRICHT TEXT'
    C.write_tsv(vorschlag_path, A.KONK_HEADER, [[r.get(k, '') for k in A.KONK_HEADER] for r in rows])


def run(scan_pfade, seiten_spec, vorschlag, out, json_path=None, cache=None):
    werk = C.load_werk_korrigiert(json_path)
    seqs = C.parse_range(seiten_spec)
    seiten = lese_seiten(scan_pfade, seqs, cache=cache)
    soll = zuordnen(werk, seiten)
    bereiche = seiten_bereiche(soll, seiten)
    out = Path(out)
    C.write_tsv(out / 'scan' / (C.WERK_TAG + '_Ot_Abgleich.tsv'),
                ['ref', 'abschnitt', 'ot', 'ot_anfang', 'stichwort_json', 'ocr_wort', 'scanseite'],
                [[x['ref'], x['abschnitt'], x['ot'], 'ja' if x['ot_anfang'] else '', x['wort'], x['ocr'],
                  x['seite'] or ''] for x in soll])
    gefunden = sum(1 for x in soll if x['seite'])
    ot_start = [x for x in soll if x['ot_anfang']]
    ot_gef = sum(1 for x in ot_start if x['seite'])
    je_ab = collections.OrderedDict()
    for x in soll:
        d = je_ab.setdefault(x['abschnitt'], {'absaetze': 0, 'gefunden': 0, 'ot': 0, 'ot_gefunden': 0, 'seiten': set()})
        d['absaetze'] += 1
        d['ot'] += 1 if x['ot_anfang'] else 0
        if x['seite']:
            d['gefunden'] += 1
            d['ot_gefunden'] += 1 if x['ot_anfang'] else 0
            d['seiten'].add(x['seite'])
    L = ['OD YOSEF CHAI · HALAKHOT · OT-ABGLEICH (STICHWORT-OCR)', '',
         'Scanseiten {} · OCR-Woerter (Quadratschrift, Konfidenz >= {}): {}'.format(
             seiten_spec, MIN_KONF, sum(len(s['woerter']) for s in seiten)),
         'Absaetze im Scan wiedergefunden: {} von {} ({:.0f} %)'.format(gefunden, len(soll), 100.0 * gefunden / len(soll)),
         'Halacha-Anfaenge wiedergefunden: {} von {} ({:.0f} %)'.format(ot_gef, len(ot_start), 100.0 * ot_gef / len(ot_start)),
         '', '{:<26} {:>6} {:>9} {:>5} {:>8}  {}'.format('Abschnitt', 'Abs.', 'gefunden', 'Ot', 'Ot gef.', 'Seiten')]
    for k, d in je_ab.items():
        sp = sorted(d['seiten'])
        L.append('{:<26} {:>6} {:>9} {:>5} {:>8}  {}'.format(k, d['absaetze'], d['gefunden'], d['ot'], d['ot_gefunden'],
                                                          '{}–{}'.format(sp[0], sp[-1]) if sp else '–'))
    L += ['', 'Ueberschriften im Scan:']
    for s in seiten:
        for u in s['ueberschriften']:
            L.append('  S. {}  פרשה {}'.format(s['seq'], u['name']))
    txt = '\n'.join(L) + '\n'
    (out / 'scan' / (C.WERK_TAG + '_Ot_Abgleich.txt')).write_text(txt, encoding='utf-8')
    if vorschlag and Path(vorschlag).exists():
        ergaenze_vorschlag(vorschlag, bereiche, seiten)
    return {'soll': soll, 'bereiche': bereiche, 'seiten': seiten, 'bericht': txt}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Halachot des JSON den Scanseiten zuordnen (Stichwort-OCR)')
    ap.add_argument('--json', default=str(C.SOURCE_JSON))
    ap.add_argument('--scan', nargs='+', required=True)
    ap.add_argument('--seiten', required=True, help='Halakhot-Seiten, z. B. 322-412')
    ap.add_argument('--vorschlag', help='scan_konkordanz_vorschlag.tsv, wird um Ot-Bereiche ergaenzt')
    ap.add_argument('--out', default=str(C.HERE / 'out'))
    ap.add_argument('--cache', help='Ordner fuer OCR-Rohdaten je Seite (beschleunigt Wiederholungen)')
    a = ap.parse_args(argv)
    r = run(a.scan, a.seiten, a.vorschlag, a.out, a.json, a.cache)
    print(r['bericht'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
