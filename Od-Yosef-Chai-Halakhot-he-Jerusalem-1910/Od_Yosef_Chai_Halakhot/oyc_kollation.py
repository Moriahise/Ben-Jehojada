# -*- coding: utf-8 -*-
"""
Schritt 2b — Kollation: Basis (Sefaria/NLI 1910) · Nakdan · Meine Fassung.

Jeder Zeuge wird wortweise an der Basis ausgerichtet (Konsonantenskelett,
difflib). Gemeldet werden nur Unterschiede:

    TEXT_N / TEXT_M        Konsonanten des Zeugen weichen von der Basis ab
                           (Wort ersetzt) – Textvariante, gegen den Scan pruefen
    PLUS_N / PLUS_M        Wort nur im Zeugen
    MINUS_N / MINUS_M      Basiswort fehlt im Zeugen
    VOK                    gleiche Konsonanten, Meine Fassung vokalisiert anders
                           als Nakdan (die eigentliche Kollation der Vokalisierung)
    UNVOK_M                Wort in Meiner Fassung (noch) ohne Vokalzeichen
    FEHLT_M / FEHLT_N      Absatz fehlt im Zeugen

Meine Fassung bleibt ein eigener Zeuge: Die Kollation veraendert keine
Zeugendatei. Fuer die Banddatei uebernimmt vokalisiere_html() aus einem Zeugen
nur Vokalzeichen auf die Basiskonsonanten; Tags (<b>) und Satzzeichen der
Basis bleiben. Konsonantische Verbesserungen gehen nur ueber
textkorrekturen.json (mit Scanseite und Grund) in den Text.

Aufruf
    python3 oyc_kollation.py --out out
"""
import argparse
import collections
import difflib
import html
import re
import sys
import unicodedata
from pathlib import Path

import oyc_common as C
import oyc_nakdan as N

LETTER_RE = re.compile('[' + C.HEB_LETTER + ']')
MARK_SET = set(chr(c) for c in range(0x0591, 0x05C8)) - {'־', '׀', '׃', '׆'}
HTML_WORD_RE = re.compile(r'(<[^>]+>)')


def ist_kuerzel(w):
    """Kuerzel oder Zahl: Gershajim im Wort (ז"ל) oder Geresch nach einem
    Buchstaben (ה', ב', כנז'). Ein bloss vorangestelltes Anfuehrungszeichen zaehlt nicht."""
    return bool(re.search('[\u05D0-\u05EA]["\'׳״“”’]', w or ''))


def letter_groups(word):
    groups = []
    for ch in word:
        if LETTER_RE.match(ch):
            groups.append([ch, ''])
        elif ch in MARK_SET:
            if groups:
                groups[-1][1] += ch
    return groups


KM_RE = C.PLENE_RE
ohne_plene_marke = C.ohne_plene_marke


def plene_marken(text):
    return len(KM_RE.findall(text or ''))


def vok_signatur(word):
    """Vokalisierung unabhaengig von der Reihenfolge der Zeichen je Buchstabe;
    die Dicta-Plene-Marke zaehlt nicht."""
    return tuple((l, ''.join(sorted(m))) for l, m in letter_groups(ohne_plene_marke(word)))


def hat_nikud(word):
    return any(m for _, m in letter_groups(word))


def transfer(base_word, voc_word):
    """Vokalzeichen aus voc_word auf die Buchstaben von base_word legen.
    Eigene Zeichen der Basis (Anfuehrungszeichen, Satzzeichen) bleiben; deren
    vereinzelte Nikud werden durch die des Zeugen ersetzt. None bei
    abweichenden Konsonanten."""
    vg = letter_groups(ohne_plene_marke(voc_word))
    out, i = [], 0
    for ch in base_word:
        if LETTER_RE.match(ch):
            if i >= len(vg) or vg[i][0] != ch:
                return None
            out.append(ch + vg[i][1])
            i += 1
        elif ch in MARK_SET:
            continue
        else:
            out.append(ch)
    return ''.join(out) if i == len(vg) else None


def ausrichten(base_words, wit_words):
    a = [C.skeleton(w) for w in base_words]
    b = [C.skeleton(w) for w in wit_words]
    return difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()


def kollationiere_absatz(ref, base_html, zeugen):
    """zeugen: {'nakdan': text|None, 'meine': text|None} -> Liste von Befundzeilen."""
    bw = C.words(base_html)
    rows = []
    aligned = {}
    for name, text in zeugen.items():
        tag = 'N' if name == 'nakdan' else 'M'
        if text is None:
            rows.append([ref, '', 'FEHLT_' + tag, '', '', '', ''])
            continue
        ww = C.words(text)
        m = {}
        for op, i1, i2, j1, j2 in ausrichten(bw, ww):
            if op == 'equal':
                for k in range(i2 - i1):
                    m[i1 + k] = ww[j1 + k]
            elif op == 'replace':
                rows.append([ref, i1 + 1, 'TEXT_' + tag, ' '.join(bw[i1:i2]),
                             ' '.join(ww[j1:j2]) if tag == 'N' else '',
                             ' '.join(ww[j1:j2]) if tag == 'M' else '', ''])
            elif op == 'insert':
                rows.append([ref, i1 + 1, 'PLUS_' + tag, '',
                             ' '.join(ww[j1:j2]) if tag == 'N' else '',
                             ' '.join(ww[j1:j2]) if tag == 'M' else '', ''])
            elif op == 'delete':
                rows.append([ref, i1 + 1, 'MINUS_' + tag, ' '.join(bw[i1:i2]), '', '', ''])
        aligned[tag] = m
    n_map, m_map = aligned.get('N'), aligned.get('M')
    if m_map is not None:
        for i, w in sorted(m_map.items()):
            if not hat_nikud(w) and not ist_kuerzel(bw[i]):
                rows.append([ref, i + 1, 'UNVOK_M', bw[i], (n_map or {}).get(i, ''), w, ''])
            elif n_map is not None and i in n_map and vok_signatur(n_map[i]) != vok_signatur(w):
                rows.append([ref, i + 1, 'VOK', bw[i], n_map[i], w, ''])
    return rows, len(bw)


def kollation(werk, zeugen_texte):
    """zeugen_texte: {'nakdan': {ref: text}, 'meine': {ref: text}}"""
    rows, summen = [], collections.OrderedDict()
    for a, h, p in C.iter_absaetze(werk):
        z = {name: texte.get(p['ref']) for name, texte in zeugen_texte.items() if texte}
        if not z:
            continue
        r, nw = kollationiere_absatz(p['ref'], p['html'], z)
        s = summen.setdefault(a['key'], collections.Counter())
        s['absaetze'] += 1
        s['woerter'] += nw
        for row in r:
            s[row[2]] += 1
        rows.extend(r)
    return rows, summen


def vokalisiere_html(base_html, voc_text):
    """Basis-HTML mit den Vokalzeichen eines Zeugen. -> (html, uebertragen, offen)"""
    bw = C.words(base_html)
    ww = C.words(voc_text)
    ersatz = {}
    for op, i1, i2, j1, j2 in ausrichten(bw, ww):
        if op == 'equal':
            for k in range(i2 - i1):
                t = transfer(bw[i1 + k], ww[j1 + k])
                if t is not None:
                    ersatz[i1 + k] = t
    out, idx = [], 0
    for teil in HTML_WORD_RE.split(base_html):
        if not teil:
            continue
        if teil.startswith('<') and teil.endswith('>'):
            out.append(teil)
            continue
        stuecke, pos = [], 0
        for m in C.WORD_RE.finditer(teil.replace(C.MAQAF, ' ')):
            if not re.search('[' + C.HEB_LETTER + ']', C.skeleton(m.group(0))):
                continue
            stuecke.append(teil[pos:m.start()])
            stuecke.append(ersatz.get(idx, m.group(0)))
            pos = m.end()
            idx += 1
        stuecke.append(teil[pos:])
        out.append(''.join(stuecke))
    if idx != len(bw):
        raise RuntimeError('Wortzaehlung inkonsistent ({} / {})'.format(idx, len(bw)))
    return ''.join(out), len(ersatz), len(bw) - len(ersatz)


def vokalisierte_texte(werk, texte, unvollstaendig_erlaubt=False):
    """{ref: vokalisiertes HTML} fuer die Banddatei."""
    out, fehlend, offen = {}, [], 0
    for a, h, p in C.iter_absaetze(werk):
        t = texte.get(p['ref'])
        if t is None:
            fehlend.append(p['ref'])
            continue
        out[p['ref']], _, o = vokalisiere_html(p['html'], t)
        offen += o
    if fehlend and not unvollstaendig_erlaubt:
        raise SystemExit('Zeuge unvollstaendig: {} Absaetze fehlen (z. B. {})'.format(
            len(fehlend), ', '.join(fehlend[:5])))
    return out, fehlend, offen


ART_TEXT = {'TEXT_N': 'Konsonanten Nakdan ≠ Basis', 'TEXT_M': 'Konsonanten Meine ≠ Basis',
            'PLUS_N': 'nur Nakdan', 'PLUS_M': 'nur Meine', 'MINUS_N': 'fehlt Nakdan',
            'MINUS_M': 'fehlt Meine', 'VOK': 'Vokalisierung Meine ≠ Nakdan',
            'UNVOK_M': 'Meine unvokalisiert', 'FEHLT_M': 'Absatz fehlt Meine',
            'FEHLT_N': 'Absatz fehlt Nakdan'}


def bericht(werk, zeugen_texte, rows, summen):
    idx = C.absatz_index(werk)
    L = ['OD YOSEF CHAI · HALAKHOT · KOLLATION DER VOKALISIERUNG', '',
         'Basis: {} ({} Absaetze)'.format(Path(werk['meta']['datei']).name, len(idx))]
    for name, texte in zeugen_texte.items():
        b = N.pruefe_zeuge(werk, texte or {})
        L.append('Zeuge {:<7}: {} von {} Absaetzen · Konsonanten abweichend in {} Absaetzen'.format(
            name, b['abgedeckt'], len(idx), len(b['konsonanten_abweichend'])))
    if not any(zeugen_texte.values()):
        L += ['', 'Noch kein Zeuge vorhanden. Ablauf:',
              '  1. python3 oyc_nakdan.py export   -> vokalisierung/export/*.txt',
              '  2. Dateien in Nakdan Pro vokalisieren (oder: python3 oyc_nakdan.py api)',
              '  3. python3 oyc_nakdan.py import --zeuge nakdan <Dateien>',
              '  4. python3 oyc_nakdan.py vorlage  -> vokalisierung/meine/ bearbeiten',
              '  5. python3 oyc_kollation.py']
        return '\n'.join(L) + '\n'
    gesamt = collections.Counter(r[2] for r in rows)
    L += ['', 'Befunde gesamt: ' + (', '.join('{} {}'.format(k, v) for k, v in sorted(gesamt.items())) or 'keine'), '',
          '{:<26} {:>6} {:>7} {:>7} {:>7} {:>7} {:>7}'.format('Abschnitt', 'Abs.', 'Woerter', 'VOK', 'UNVOK_M', 'TEXT_M', 'TEXT_N')]
    for k, s in summen.items():
        L.append('{:<26} {:>6} {:>7} {:>7} {:>7} {:>7} {:>7}'.format(
            k, s['absaetze'], s['woerter'], s['VOK'], s['UNVOK_M'], s['TEXT_M'] + s['PLUS_M'] + s['MINUS_M'],
            s['TEXT_N'] + s['PLUS_N'] + s['MINUS_N']))
    nk = zeugen_texte.get('nakdan') or {}
    if nk:
        kopf = ''
        for f in sorted(N.ZEUGEN['nakdan'].glob('*.txt'))[:1]:
            kopf = f.read_text(encoding='utf-8').split('\n', 1)[0].lstrip('# ')
        L += ['', 'NAKDAN', '  ' + (kopf or 'Herkunft nicht vermerkt'),
              '  Einstellungen: genre=rabbinic, keepmetagim=true (sonst schreibt Nakdan defektiv und aendert Konsonanten)',
              '  Dicta-Plene-Marken (Meteg auf ו/י der Plene-Schreibung): {} – im Vergleich ignoriert, im Satz und in der'.format(
                  sum(plene_marken(t) for t in nk.values())),
              '  Vorlage "Meine Fassung" entfernt; der Nakdan-Zeuge bleibt unveraendert.',
              '  Nutzung: Dicta-Bedingungen fuer die kommerzielle Ausgabe pruefen, Namensnennung im Impressum vorsehen.']
    unvok = collections.OrderedDict()
    for r in rows:
        if r[2] == 'UNVOK_M':
            unvok.setdefault(r[3], []).append(r[0])
    if unvok:
        L += ['', 'UNVOKALISIERT (ohne Kuerzel/Zahlen mit Geresch): {} Woerter, {} verschieden'.format(
            sum(len(v) for v in unvok.values()), len(unvok))]
        for w, refs in sorted(unvok.items(), key=lambda kv: -len(kv[1])):
            L.append('  {:<12} {:>3}×  {}'.format(w, len(refs), ', '.join(refs[:4]) + (' …' if len(refs) > 4 else '')))
    L += ['', 'Textabweichungen der Zeugen (TEXT/PLUS/MINUS) sind keine Fehler der Basis,',
          'sondern Pruefstellen: gegen den Scan lesen; eine berechtigte Korrektur kommt',
          'mit Scanseite und Grund nach textkorrekturen.json.']
    return '\n'.join(L) + '\n'


def kollation_html(path, rows, limit=4000):
    e = html.escape
    out = ['<!doctype html><html lang="de"><head><meta charset="utf-8"><title>OYC Kollation</title>',
           '<style>body{font-family:system-ui,sans-serif;margin:16px;background:#fff;color:#222}',
           'table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:3px 6px;font-size:13px}',
           '.he{direction:rtl;font-family:"Frank Ruhl Libre","Times New Roman",serif;font-size:17px}',
           '.TEXT_M,.PLUS_M,.MINUS_M{background:#ffebee}.TEXT_N,.PLUS_N,.MINUS_N{background:#fff8e1}.VOK{background:#e3f2fd}',
           '</style></head><body><h1>Kollation · Basis / Nakdan / Meine Fassung</h1>',
           '<p>{} Befunde{}</p>'.format(len(rows), ' (erste {} gezeigt)'.format(limit) if len(rows) > limit else ''),
           '<table><tr><th>Ref</th><th>Wort</th><th>Art</th><th>Basis</th><th>Nakdan</th><th>Meine Fassung</th></tr>']
    for r in rows[:limit]:
        out.append('<tr class="{}"><td>{}</td><td>{}</td><td>{}</td><td class="he">{}</td><td class="he">{}</td><td class="he">{}</td></tr>'.format(
            e(r[2]), e(str(r[0])), r[1], e(ART_TEXT.get(r[2], r[2])), e(r[3]), e(r[4]), e(r[5])))
    out.append('</table></body></html>')
    Path(path).write_text('\n'.join(out), encoding='utf-8')


def run(json_path=None, out='out', quiet=False):
    out = Path(out) / 'kollation'
    out.mkdir(parents=True, exist_ok=True)
    werk = C.load_werk_korrigiert(json_path)
    zeugen = {name: N.lese_zeuge(d) for name, d in N.ZEUGEN.items()}
    rows, summen = kollation(werk, {k: v for k, v in zeugen.items() if v})
    C.write_tsv(out / (C.WERK_TAG + '_Kollation.tsv'),
                ['ref', 'wort_nr', 'art', 'basis', 'nakdan', 'meine', 'entscheidung'], rows)
    txt = bericht(werk, zeugen, rows, summen)
    (out / (C.WERK_TAG + '_Kollation_Bericht.txt')).write_text(txt, encoding='utf-8')
    kollation_html(out / (C.WERK_TAG + '_Kollation.html'), rows)
    if not quiet:
        print(txt)
    return {'zeugen': {k: len(v) for k, v in zeugen.items()}, 'befunde': collections.Counter(r[2] for r in rows),
            'bericht': txt}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Kollation Basis/Nakdan/Meine Fassung')
    ap.add_argument('--json', default=str(C.SOURCE_JSON))
    ap.add_argument('--out', default=str(C.HERE / 'out'))
    a = ap.parse_args(argv)
    run(a.json, a.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
