# -*- coding: utf-8 -*-
"""
Schritt 2a — Vokalisierung mit Dicta Nakdan (Pro).

Zwei Zeugen werden getrennt gefuehrt und nie vermischt:

    vokalisierung/nakdan/   automatische Vokalisierung (Nakdan, unbearbeitet)
    vokalisierung/meine/    "meine Fassung" – eigene, von Hand vokalisierte bzw.
                            korrigierte Fassung (eigener Kollationszeuge)

Beide liegen im selben Markerformat vor, das Nakdan Pro unveraendert
durchreicht (lateinische Zeichen werden nicht vokalisiert):

    @@Bereshit 1:2@@
    <Absatztext>

Unterbefehle
    export       Absaetze ohne Tags in Markerdateien je Abschnitt schreiben
                 (Eingabe fuer https://nakdanpro.dicta.org.il, Teile <= --max-zeichen)
    api          dieselben Teile ueber die Nakdan-API vokalisieren (mit Cache);
                 nur mit Netzzugang, Endpunkt einstellbar
    import       vokalisierte Markerdateien (Nakdan-Pro-Ausgabe) pruefen und
                 als Zeuge ablegen (--zeuge nakdan | meine)
    vorlage      "meine Fassung" einmalig aus dem Nakdan-Zeugen anlegen;
                 ueberschreibt nie vorhandene eigene Dateien
    status       Abdeckung der Zeugen je Abschnitt

Aufrufe
    python3 oyc_nakdan.py export
    python3 oyc_nakdan.py api --genre rabbinic
    python3 oyc_nakdan.py import --zeuge nakdan ~/Downloads/nakdan_*.txt
    python3 oyc_nakdan.py vorlage
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

import oyc_common as C

VOK = C.HERE / 'vokalisierung'
EXPORT_DIR = VOK / 'export'
ZEUGEN = {'nakdan': VOK / 'nakdan', 'meine': VOK / 'meine'}
CACHE = VOK / 'nakdan_cache'
MARKER_RE = re.compile(r'^\s*@@\s*(.+?)\s*@@\s*$')
DEFAULT_ENDPOINT = 'auto'
# Bekannte oeffentliche Nakdan-Endpunkte (Dicta). 'auto' nimmt den ersten, der
# auf eine Probe korrekt antwortet; im Bericht steht, welcher es war.
ENDPOINTS = [
    'https://nakdan-2-0.loadbalancer.dicta.org.il/api',
    'https://nakdan-5-3.loadbalancer.dicta.org.il/addnikud',
    'https://nakdan-5-1.loadbalancer.dicta.org.il/addnikud',
    'https://nakdan-u1-0.loadbalancer.dicta.org.il/addnikud',
]


def klartext(html):
    return re.sub(r'\s+', ' ', C.strip_tags(html)).strip()


def dateiname(a, teil, teile):
    key = re.sub(r'[^A-Za-z0-9]+', '_', a['key']).strip('_')
    suffix = '_Teil{:02d}'.format(teil) if teile > 1 else ''
    return 'OYC_{:02d}_{}{}.txt'.format(a['ord'], key, suffix)


def export_teile(werk, max_zeichen):
    """[(dateiname, [(ref, text)])] – kein Absatz wird geteilt."""
    out = []
    for a in werk['abschnitte']:
        teile, cur, n = [], [], 0
        for h in a['halachot']:
            for p in h['absaetze']:
                t = klartext(p['html'])
                if not t:
                    continue
                if cur and n + len(t) > max_zeichen:
                    teile.append(cur)
                    cur, n = [], 0
                cur.append((p['ref'], t))
                n += len(t)
        if cur:
            teile.append(cur)
        for i, t in enumerate(teile, start=1):
            out.append((dateiname(a, i, len(teile)), t))
    return out


def schreibe_marker(path, eintraege, kopf=None):
    lines = []
    if kopf:
        lines.append('# ' + kopf)
    for ref, text in eintraege:
        lines += ['@@{}@@'.format(ref), text, '']
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text('\n'.join(lines), encoding='utf-8')


def lese_marker(path):
    """Markerdatei -> [(ref, text)]; Text vor dem ersten Marker und
    #-Kommentarzeilen werden ignoriert."""
    out, ref, buf = [], None, []
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        m = MARKER_RE.match(line)
        if m:
            if ref is not None:
                out.append((ref, ' '.join(x.strip() for x in buf if x.strip())))
            ref, buf = m.group(1), []
        elif ref is not None and not line.lstrip().startswith('#'):
            buf.append(line)
    if ref is not None:
        out.append((ref, ' '.join(x.strip() for x in buf if x.strip())))
    return out


def lese_zeuge(verzeichnis):
    """Alle Markerdateien eines Zeugen -> {ref: text}. Doppelte Refs sind ein Fehler."""
    texte, herkunft = {}, {}
    d = Path(verzeichnis)
    if not d.exists():
        return {}
    for f in sorted(d.glob('*.txt')):
        for ref, text in lese_marker(f):
            if ref in texte:
                raise SystemExit('Zeuge {}: {} doppelt ({} und {})'.format(d.name, ref, herkunft[ref], f.name))
            texte[ref], herkunft[ref] = text, f.name
    return texte


def pruefe_zeuge(werk, texte):
    """Unbekannte Refs, leere Absaetze und Konsonantenabweichungen je Absatz."""
    idx = C.absatz_index(werk)
    unbekannt = [r for r in texte if r not in idx]
    leer = [r for r, t in texte.items() if r in idx and not t.strip()]
    abw = []
    for r, t in texte.items():
        if r in idx and t.strip():
            b = [C.skeleton(w) for w in C.words(idx[r][2]['html'])]
            z = [C.skeleton(w) for w in C.words(t)]
            if b != z:
                abw.append(r)
    return {'unbekannt': unbekannt, 'leer': leer, 'konsonanten_abweichend': abw,
            'abgedeckt': sum(1 for r in texte if r in idx and texte[r].strip()), 'gesamt': len(idx)}


# --- Nakdan-API ---------------------------------------------------------------
def nakdan_payload(text, genre):
    return {'task': 'nakdan', 'data': text, 'genre': genre, 'addmorph': True,
            'keepqq': False, 'nodageshdefmem': False, 'patachma': False, 'keepmetagim': True}


def nakdan_text(resp):
    """Antwort der Nakdan-API -> vokalisierter Text. Vertraegt die bekannten
    Antwortformen (Liste oder {'data': [...]}; Optionen als Text, Liste oder
    {'w': ...}); '|' (Praefixgrenze) wird entfernt."""
    items = resp.get('data') if isinstance(resp, dict) else resp
    if not isinstance(items, list):
        raise ValueError('unbekannte Nakdan-Antwort')
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(it)
            continue
        w = it.get('word', '')
        if it.get('sep'):
            out.append(w)
            continue
        opts = it.get('options') or (it.get('nakdan') or {}).get('options') or []
        o = opts[0] if opts else w
        if isinstance(o, list):
            o = o[0] if o else w
        if isinstance(o, dict):
            o = o.get('w') or o.get('word') or w
        out.append(str(o).replace('|', ''))
    return ''.join(out)


def teile_text(text, max_len=4000):
    """Lange Absaetze fuer die API an Satzgrenzen teilen (Nakdan-Limit)."""
    if len(text) <= max_len:
        return [text]
    teile, rest = [], text
    while len(rest) > max_len:
        cut = max(rest.rfind(': ', 0, max_len), rest.rfind('. ', 0, max_len), rest.rfind(', ', 0, max_len))
        if cut < max_len // 3:
            cut = rest.rfind(' ', 0, max_len)
        if cut <= 0:
            cut = max_len
        teile.append(rest[:cut + 1])
        rest = rest[cut + 1:]
    teile.append(rest)
    return teile


def nakdan_api(text, endpoint, genre, timeout=120, pause=0.3, versuche=4):
    """Ein Text -> vokalisierter Text. Antworten werden je (Endpunkt, Genre,
    Text) im Cache abgelegt; ein abgebrochener Lauf setzt dort wieder an."""
    key = hashlib.sha1('\x00'.join([endpoint, genre, text]).encode('utf-8')).hexdigest()
    cf = CACHE / (key + '.json')
    if cf.exists():
        return nakdan_text(json.loads(cf.read_text(encoding='utf-8')))
    letzter = None
    for i in range(versuche):
        try:
            raw = C.http_get(endpoint, timeout=timeout,
                             data=json.dumps(nakdan_payload(text, genre)).encode('utf-8'),
                             headers={'Content-Type': 'application/json;charset=UTF-8',
                                      'User-Agent': 'od-yosef-chai-pipeline/1.0'})
            resp = json.loads(raw.decode('utf-8'))
            out = nakdan_text(resp)
            CACHE.mkdir(parents=True, exist_ok=True)
            cf.write_text(json.dumps(resp, ensure_ascii=False), encoding='utf-8')
            time.sleep(pause)
            return out
        except Exception as e:                      # Netz, Zeitlimit, Ueberlast
            letzter = e
            time.sleep(2 ** (i + 1))
    raise RuntimeError('Nakdan nicht erreichbar ({}): {}'.format(endpoint, letzter))


PROBE = 'כתב רבינו ז"ל בשער הכונות'


def waehle_endpoint(endpoint, genre):
    """'auto' -> erster Endpunkt, dessen Antwort dieselben Konsonanten traegt
    wie die Probe und Vokalzeichen enthaelt."""
    kandidaten = ENDPOINTS if endpoint == 'auto' else [endpoint]
    fehler = []
    for ep in kandidaten:
        try:
            out = nakdan_api(PROBE, ep, genre, timeout=30, versuche=1)
        except Exception as e:
            fehler.append('{}: {}'.format(ep, e))
            continue
        ok_konsonanten = [C.skeleton(w) for w in C.words(out)] == [C.skeleton(w) for w in C.words(PROBE)]
        if ok_konsonanten and C.NIKUD_RE.search(out):
            return ep
        fehler.append('{}: unerwartete Antwort "{}"'.format(ep, out[:60]))
    raise SystemExit('Kein Nakdan-Endpunkt nutzbar:\n  ' + '\n  '.join(fehler))


# --- Befehle -------------------------------------------------------------------
def cmd_export(werk, max_zeichen):
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    teile = export_teile(werk, max_zeichen)
    for name, eintraege in teile:
        schreibe_marker(EXPORT_DIR / name, eintraege,
                        'OYC Nakdan-Export {} · @@-Zeilen unveraendert lassen'.format(name))
    n = sum(len(e) for _, e in teile)
    z = sum(len(t) for _, e in teile for _, t in e)
    return '{} Dateien · {} Absaetze · {} Zeichen -> {}'.format(len(teile), n, z, EXPORT_DIR)


def cmd_api(werk, max_zeichen, endpoint, genre, nur=None, parallel=3):
    """Alle Exportteile ueber die Nakdan-API vokalisieren -> vokalisierung/nakdan/.
    Lange Absaetze werden an Satzgrenzen geteilt und wieder zusammengesetzt."""
    from concurrent.futures import ThreadPoolExecutor
    ep = waehle_endpoint(endpoint, genre)
    ziel = ZEUGEN['nakdan']
    ziel.mkdir(parents=True, exist_ok=True)
    teile = [(n, e) for n, e in export_teile(werk, max_zeichen) if not nur or any(x in n for x in nur)]
    auftraege = [(ref, t) for _, e in teile for ref, text in e for t in teile_text(text)]
    gesamt, fertig, start = len(auftraege), [0], time.time()

    def eins(a):
        r = nakdan_api(a[1], ep, genre)
        fertig[0] += 1
        if fertig[0] % 50 == 0 or fertig[0] == gesamt:
            print('  Nakdan {}/{} Teile · {:.0f} s'.format(fertig[0], gesamt, time.time() - start), flush=True)
        return r

    with ThreadPoolExecutor(max_workers=parallel) as pool:
        ergebnisse = list(pool.map(eins, auftraege))
    it = iter(ergebnisse)
    n = abw = 0
    for name, eintraege in teile:
        out = []
        for ref, text in eintraege:
            voc = ''.join(next(it) for _ in teile_text(text))
            if [C.skeleton(w) for w in C.words(voc)] != [C.skeleton(w) for w in C.words(text)]:
                abw += 1
            out.append((ref, voc))
            n += 1
        schreibe_marker(ziel / name, out, 'Nakdan-API {} genre={} · unbearbeitet · {}'.format(
            ep, genre, time.strftime('%Y-%m-%d')))
    return '{} Absaetze vokalisiert ({} API-Teile, Endpunkt {}) -> {} · Konsonanten abweichend: {}'.format(
        n, gesamt, ep, ziel, abw)


def cmd_import(werk, zeuge, dateien, ersetzen=False):
    ziel = ZEUGEN[zeuge]
    ziel.mkdir(parents=True, exist_ok=True)
    texte = {}
    for f in dateien:
        for ref, t in lese_marker(f):
            if ref in texte:
                raise SystemExit('{} doppelt in den Importdateien'.format(ref))
            texte[ref] = t
    befund = pruefe_zeuge(werk, texte)
    if befund['unbekannt']:
        raise SystemExit('Unbekannte Refs: ' + ', '.join(befund['unbekannt'][:10]))
    for f in dateien:
        z = ziel / Path(f).name
        if z.exists() and not ersetzen:
            raise SystemExit('Abbruch ohne Ueberschreiben: {} existiert (--ersetzen)'.format(z))
        shutil.copyfile(f, z)
    return ('{} Absaetze importiert nach {} · Konsonanten abweichend: {} (siehe Kollation)'.format(
        len(texte), ziel, len(befund['konsonanten_abweichend'])))


def cmd_vorlage():
    quelle, ziel = ZEUGEN['nakdan'], ZEUGEN['meine']
    if not quelle.exists() or not any(quelle.glob('*.txt')):
        raise SystemExit('Kein Nakdan-Zeuge vorhanden – zuerst api oder import --zeuge nakdan.')
    ziel.mkdir(parents=True, exist_ok=True)
    neu = 0
    for f in sorted(quelle.glob('*.txt')):
        z = ziel / f.name
        if z.exists():
            continue
        text = f.read_text(encoding='utf-8')
        text = re.sub(r'^#.*$', '# Meine Fassung · Vorlage aus Nakdan (ohne Dicta-Plene-Marken) · hier korrigieren',
                      text, count=1, flags=re.M)
        text = '\n'.join(l if l.startswith(('#', '@@')) else C.ohne_plene_marke(l) for l in text.split('\n'))
        z.write_text(text, encoding='utf-8')
        neu += 1
    return '{} Vorlagedateien angelegt in {} (vorhandene unberuehrt)'.format(neu, ziel)


def status(werk):
    idx = C.absatz_index(werk)
    zeilen = []
    for name, d in ZEUGEN.items():
        texte = lese_zeuge(d)
        b = pruefe_zeuge(werk, texte)
        zeilen.append('{:<7} {:>5}/{} Absaetze · Konsonanten abweichend {} · unbekannt {}'.format(
            name, b['abgedeckt'], len(idx), len(b['konsonanten_abweichend']), len(b['unbekannt'])))
    return '\n'.join(zeilen)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Vokalisierung mit Dicta Nakdan (Pro)')
    ap.add_argument('--json', default=str(C.SOURCE_JSON))
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('export')
    e.add_argument('--max-zeichen', type=int, default=15000)
    p = sub.add_parser('api')
    p.add_argument('--max-zeichen', type=int, default=15000)
    p.add_argument('--endpoint', default=DEFAULT_ENDPOINT, help="'auto' oder URL")
    p.add_argument('--parallel', type=int, default=3)
    p.add_argument('--genre', default='rabbinic', choices=['rabbinic', 'modern', 'poetry'])
    p.add_argument('--nur', nargs='*', help='nur Dateien, deren Name dies enthaelt (z. B. Bereshit)')
    i = sub.add_parser('import')
    i.add_argument('--zeuge', choices=sorted(ZEUGEN), required=True)
    i.add_argument('--ersetzen', action='store_true')
    i.add_argument('dateien', nargs='+')
    sub.add_parser('vorlage')
    sub.add_parser('status')
    a = ap.parse_args(argv)
    werk = C.load_werk_korrigiert(a.json)
    if a.cmd == 'export':
        print(cmd_export(werk, a.max_zeichen))
    elif a.cmd == 'api':
        print(cmd_api(werk, a.max_zeichen, a.endpoint, a.genre, a.nur, a.parallel))
    elif a.cmd == 'import':
        print(cmd_import(werk, a.zeuge, a.dateien, a.ersetzen))
    elif a.cmd == 'vorlage':
        print(cmd_vorlage())
    print(status(werk))
    return 0


if __name__ == '__main__':
    sys.exit(main())
