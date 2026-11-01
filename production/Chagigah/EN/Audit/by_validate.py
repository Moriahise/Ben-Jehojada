# -*- coding: utf-8 -*-
"""
Abnahmeprüfung einer Banddatei — das Tor vor jedem neuen Uebersetzungsbatch.

Geprueft wird, was bisher niemand geprueft hat: ob das Kopfband die Stelle
wirklich traegt, auf die sich der Kommentar beruft. Genau diese Luecke hat
die Fehlzuordnungen erst beim Uebersetzen sichtbar werden lassen.

  1  STRUKTUR    Segmentzahl, eindeutige IDs, aufsteigende Reihenfolge,
                 alle fuenf Felder vorhanden, CDATA sauber geschlossen
  2  SCHUTZ      <he>, <en>, <band_en>, IDs, n, daf und die Ueberschriften
                 sind gegenueber einer Vergleichsfassung unveraendert
  3  KOPFBAND    das Lemma steckt im Kopfband (Deckungsmass aus by_band)
  4  UEBERSETZUNG  zu jedem geaenderten Kopfband: ist band_en noch stimmig?

Rueckgabe-Code: 0 = frei, 1 = Befunde vorhanden.

    python3 by_validate.py --in datei.txt [--against alte_fassung.txt]
                           [--expect 338] [--json bericht.json]
"""
import argparse, json, os, re, sys

import by_band as BB

SEG_RE = re.compile(r'<segment\s+(?P<attrs>[^>]*)>\s*\n(?P<body>.*?)\n</segment>', re.S)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
FIELDS = ('band_he', 'band_en', 'he', 'en')
ID_RE = re.compile(r'^BYH-\d{7}$')
SECTION_RE = re.compile(r'<he_title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</he_title>', re.S)

# Ab dieser Deckung gilt das Lemma als im Kopfband enthalten.
BAND_OK = 0.85
# Darunter ist es ein Befund, der die Freigabe blockiert.
BAND_BAD = 0.34


def field_re(k):
    # Frische Pipeline-Dateien nutzen CDATA; aeltere/extern bearbeitete
    # Banddateien koennen denselben Feldinhalt auch nackt enthalten.
    return re.compile(r'<%s>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</%s>' % (k, k), re.S)


FIELD_RE = {k: field_re(k) for k in FIELDS}
LEMMA_RE = re.compile(r'<lemma>(.*?)</lemma>', re.S)
FN_RE = re.compile(r'<fn>(.*?)</fn>', re.S)
NEVER_GEMATRIA = {'תנ"ך','ר"מ','ר"פ','נ"ל','הו"א','ס"ל','רמ"א','רמ"ז','צל"ח','כנ"ז','לפ"ז','בד"א','רשב"ם','רמב"ם','רא"ש'}


def read(path):
    with open(path, encoding='utf-8-sig') as fh:
        raw = fh.read()
    out = []
    for m in SEG_RE.finditer(raw):
        rec = {'attrs': dict(ATTR_RE.findall(m.group('attrs'))), 'raw': m.group(0)}
        for k in FIELDS:
            fm = FIELD_RE[k].search(m.group('body'))
            rec[k] = ((fm.group(1) if fm.group(1) is not None else fm.group(2))
                      if fm else None)
        out.append(rec)
    return raw, out


def validate(path, against=None, expect=None):
    raw, segs = read(path)
    findings = []

    def bad(level, sid, code, msg):
        findings.append({'level': level, 'id': sid, 'code': code, 'text': msg})

    # ---- 1 Struktur -------------------------------------------------------
    if expect and len(segs) != expect:
        bad('FEHLER', '-', 'anzahl',
            'Segmentzahl {} statt erwarteter {}'.format(len(segs), expect))
    seen, prev = {}, None
    for s in segs:
        sid = s['attrs'].get('id', '?')
        if not ID_RE.match(sid):
            bad('FEHLER', sid, 'id_form', 'ID entspricht nicht BYH-0000000')
        if sid in seen:
            bad('FEHLER', sid, 'id_doppelt', 'ID kommt mehrfach vor')
        seen[sid] = True
        if prev and sid <= prev:
            bad('FEHLER', sid, 'reihenfolge', 'ID nicht groesser als ' + prev)
        prev = sid
        for k in FIELDS:
            if s[k] is None:
                bad('FEHLER', sid, 'feld_fehlt', 'Feld <{}> fehlt oder ist unsauber'.format(k))
        for k in ('n', 'daf'):
            if k not in s['attrs']:
                bad('FEHLER', sid, 'attribut', 'Attribut {} fehlt'.format(k))
        if ']]>' in (s['band_he'] or '') or ']]>' in (s['he'] or ''):
            bad('FEHLER', sid, 'cdata', 'CDATA-Ende im Feldinhalt')

    # ---- 2 Geschuetzte Felder --------------------------------------------
    if against and os.path.exists(against):
        raw0, old = read(against)
        old_by = {s['attrs'].get('id'): s for s in old}
        sec = lambda txt: [(a if a is not None else b) for a, b in SECTION_RE.findall(txt)]
        if sec(raw) != sec(raw0):
            bad('FEHLER', '-', 'ueberschriften', 'Abschnittsueberschriften weichen ab')
        if [s['attrs'].get('id') for s in segs] != [s['attrs'].get('id') for s in old]:
            bad('FEHLER', '-', 'id_liste', 'ID-Folge weicht von der Vergleichsfassung ab')
        for s in segs:
            sid = s['attrs'].get('id')
            o = old_by.get(sid)
            if not o:
                bad('FEHLER', sid, 'neu', 'Segment gibt es in der Vergleichsfassung nicht')
                continue
            for k in ('he', 'en', 'band_en'):
                if (s[k] or '') != (o[k] or ''):
                    bad('FEHLER', sid, 'geschuetzt_' + k,
                        'geschuetztes Feld <{}> wurde veraendert'.format(k))
            for k in ('n', 'daf'):
                if s['attrs'].get(k) != o['attrs'].get(k):
                    bad('FEHLER', sid, 'attribut_' + k,
                        'Attribut {} wurde veraendert'.format(k))

    # ---- 3 Kopfband traegt das Lemma -------------------------------------
    stats = {'geprueft': 0, 'ok': 0, 'schwach': 0, 'fehlend': 0, 'ohne_lemma': 0}
    for s in segs:
        sid = s['attrs'].get('id', '?')
        lm = LEMMA_RE.search(s['he'] or '')
        if not lm:
            stats['ohne_lemma'] += 1
            if (s['band_he'] or '').strip():
                bad('FEHLER', sid, 'band_ohne_lemma',
                    'Kopfband vorhanden, aber kein <lemma> im Kommentar — Dibbur-ha-Matchil verloren')
            continue
        lemma = lm.group(1)
        stats['geprueft'] += 1
        if not (s['band_he'] or '').strip():
            stats['fehlend'] += 1
            bad('HINWEIS', sid, 'band_leer', 'kein Kopfband zugeordnet')
            continue
        ok, cov = BB.band_contains_lemma(s['band_he'], lemma, need=BAND_OK)
        if ok:
            stats['ok'] += 1
        elif cov < BAND_BAD:
            stats['schwach'] += 1
            bad('FEHLER', sid, 'band_ohne_stelle',
                'Lemma steckt nicht im Kopfband (Deckung {})'.format(cov))
        else:
            stats['schwach'] += 1
            bad('PRUEFEN', sid, 'band_wortlaut',
                'Wortlaut weicht ab (Deckung {}) — Stelle einzeln ansehen'.format(cov))

    # ---- 3b Fussnoten-Plausibilitaet --------------------------------------
    # Einige Kuerzel sind eindeutig lexikalisch und duerfen niemals durch den
    # Gematria-Fallback als Zahlwert erklaert werden. Dieser Check haette die
    # in Band 02 gefundenen Fehler (תנ"ך, ר"מ, ר"פ, ...) sofort blockiert.
    for s in segs:
        sid = s['attrs'].get('id', '?')
        for note in FN_RE.findall(s['he'] or ''):
            if ' = ' not in note or 'מִסְפָּר' not in note:
                continue
            token = note.split(' = ', 1)[0].strip()
            core = token
            # einfache morphologische Praefixe fuer den Vergleich abziehen
            for pfx in ('וה','שה','לה','בה','וכ','ול','וב','וש','ו','ש','ל','ב','כ','מ','ה','ד'):
                if core.startswith(pfx) and core[len(pfx):] in NEVER_GEMATRIA:
                    core = core[len(pfx):]
                    break
            if core in NEVER_GEMATRIA:
                bad('FEHLER', sid, 'fn_falsche_gematria',
                    'lexikalisches Kuerzel als Gematria erklaert: {}'.format(note))

    # ---- 4 Uebersetzungsfolgen -------------------------------------------
    if against and os.path.exists(against):
        for s in segs:
            sid = s['attrs'].get('id')
            o = old_by.get(sid)
            if not o:
                continue
            if (s['band_he'] or '') != (o['band_he'] or '') and (s['band_en'] or '').strip():
                bad('PRUEFEN', sid, 'band_en_nachziehen',
                    'band_he geaendert, band_en ist bereits uebersetzt — inhaltlich nachziehen')

    return findings, stats, len(segs)


def report(findings, stats, n, path):
    order = {'FEHLER': 0, 'PRUEFEN': 1, 'HINWEIS': 2}
    findings = sorted(findings, key=lambda f: (order.get(f['level'], 9), f['id']))
    print('== ABNAHMEPRUEFUNG ==', path)
    print('Segmente          :', n)
    print('mit Lemma geprueft:', stats['geprueft'])
    print('  Kopfband traegt die Stelle :', stats['ok'])
    print('  Wortlaut weicht ab         :', stats['schwach'])
    print('  ohne Kopfband              :', stats['fehlend'])
    print('ohne Lemma (Freitext):', stats['ohne_lemma'])
    from collections import Counter
    c = Counter(f['level'] for f in findings)
    print('Befunde: FEHLER {} · PRUEFEN {} · HINWEIS {}'
          .format(c.get('FEHLER', 0), c.get('PRUEFEN', 0), c.get('HINWEIS', 0)))
    if findings:
        print()
        for f in findings:
            print('  [{}] {:<14} {:<22} {}'.format(f['level'], f['id'], f['code'], f['text']))
    return 1 if c.get('FEHLER') else 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', required=True)
    ap.add_argument('--against', help='Vergleichsfassung fuer die geschuetzten Felder')
    ap.add_argument('--expect', type=int, help='erwartete Segmentzahl')
    ap.add_argument('--json', help='Befunde zusaetzlich als JSON ablegen')
    a = ap.parse_args()
    f, st, n = validate(a.src, a.against, a.expect)
    if a.json:
        json.dump({'findings': f, 'stats': st, 'segments': n},
                  open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(report(f, st, n, a.src))
