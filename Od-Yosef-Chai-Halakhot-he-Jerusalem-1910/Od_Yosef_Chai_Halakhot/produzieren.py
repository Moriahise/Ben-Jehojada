#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Od Yosef Chai · Halakhot — Gesamtlauf.

    1  Abschnittsliste + Scanabgleich      oyc_abschnitte.py
    2  Nakdan-Export (+ optional API)      oyc_nakdan.py
    3  Kollation Basis/Nakdan/Meine        oyc_kollation.py
    4  Glossar aus Ben Jehojada            oyc_glossar.py
    5  Bandplan + Banddatei (BIC-Format)   oyc_bandplan.py
    6  Pruefbericht + Quellenmanifest

Beispiele
    python3 produzieren.py --scan ~/Downloads/Od_Yosef_Chai_1-25.zip
    python3 produzieren.py --scan scan_1-25.zip scan_26-412.zip --scan-gesamt 412 --ocr
    python3 produzieren.py --nakdan-api                 # nur mit Netzzugang zu Dicta
    python3 produzieren.py --he-quelle meine            # Produktionsmaster nach Kollation

Ohne Netz laeuft alles ausser --laden-sefaria und --nakdan-api.
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

import oyc_common as C
import oyc_abschnitte as A
import oyc_bandplan as B
import oyc_glossar as G
import oyc_kollation as K
import oyc_nakdan as N


def git_commit():
    try:
        return subprocess.run(['git', '-C', str(C.REPO), 'rev-parse', 'HEAD'], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return ''


def manifest(out, scan_pfade, glossar_res, band_res):
    eing = []
    for p in [C.SOURCE_JSON, C.PIPELINE_ZIP, C.GLOSSARY, C.BIC_JSX,
              C.REPO / 'Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx',
              C.REPO / 'Ben_Yehoyada_Arbeitsanleitung_AKTUELL_Fassung1.5_20261005.txt',
              C.HERE / 'scan_konkordanz.tsv', C.HERE / 'scan_belege.json', C.HERE / 'kontextregeln.json',
              C.HERE / 'gliederung.json']:
        if Path(p).exists():
            eing.append({'datei': str(Path(p).relative_to(C.REPO)), 'git_blob_sha': C.git_blob_sha(p),
                         'sha256': C.sha256_file(p)})
    for p in scan_pfade or []:
        p = Path(p)
        dateien = [p] if p.is_file() else sorted(f for f in p.glob('*.zip.[0-9][0-9][0-9]') if f.is_file()) if p.is_dir() else []
        for f in dateien:
            try:
                rel = str(f.resolve().relative_to(C.REPO))
                art = 'Scan (Repository)'
            except ValueError:
                rel, art = f.name, 'Scan (nicht im Repository)'
            eing.append({'datei': rel, 'art': art, 'sha256': C.sha256_file(f)})
    tk = C.TEXTKORREKTUREN
    m = {'repository': 'Moriahise/Ben-Jehojada', 'basis_commit': git_commit(),
         'erzeugt': datetime.date.today().isoformat(), 'werk': C.WERK_EN,
         'sefaria_url': C.SEFARIA_URL, 'nli': C.NLI_RECORD,
         'pipeline': 'ben-yehoyada-pipeline v3.2.1 (nur by_parse/by_glossary)',
         'buchmanager': 'Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17 (Bandgroesse, Dateiform)',
         'eingaben': eing,
         'textkorrekturen': json.loads(tk.read_text(encoding='utf-8')) if tk.exists() else None,
         'glossar': {k: glossar_res[k] for k in ('treffer', 'aufgeloest', 'verschieden', 'neu', 'neu_staemme',
                                                 'glossar_eintraege', 'glossar_sha256')},
         'band': {'baende': band_res['baende'], 'seiten': band_res['band_seiten'],
                  'segmente': band_res['segmente'], 'he_zeichen': band_res['he_zeichen'],
                  'master_sha256': [C.sha256_file(f) for f in band_res['dateien']]}}
    C.write_json(Path(out) / 'Quellenmanifest.json', m)
    return m


def pruefbericht(out, abs_res, kol_res, glos_res, band_res, he_quelle):
    abgl = abs_res['abgleich']
    summ = abs_res['summary']
    L = ['# Od Yosef Chai · Halakhot — Prüfbericht', '',
         'Erzeugt {} mit `produzieren.py` · HE-Quelle der Banddatei: **{}**'.format(
             datetime.date.today().isoformat(), he_quelle), '',
         '## 1 Abschnittsliste und Scanabgleich', '',
         '- JSON: {} Abschnitte · {} Halachot/Segmente · {} Absätze · {} Zeichen'.format(
             len(summ), sum(s['halachot'] for s in summ), sum(s['absaetze'] for s in summ),
             sum(s['zeichen'] for s in summ)),
         '- Scan: {} Seiten im Inventar · Konkordanz {} Seiten · Halakhot-Seiten im erfassten Bereich: {}'.format(
             abgl['scanseiten_vorhanden'], abgl['konkordanz_seiten'], abgl['halakhot_seiten']),
         '- Abgleich vollständig: {}'.format('ja' if abgl['vollstaendig'] else 'nein'), '']
    for k, v in abgl['befunde'].items():
        L.append('**{}** ({})'.format(k, len(v)))
        L += ['- ' + x for x in v] or ['- keine']
        L.append('')
    L += ['| Nr | Abschnitt | Buch | Ot | Status | Scanseiten | Seiten (erwartet) |',
          '|---:|---|---|---:|---|---|---|']
    for a, s in zip(abgl['abschnitte'], summ):
        sp = a['scanseiten']
        L.append('| {} | {} ({}) | {} | {} | {} | {} | {} |'.format(
            s['ord'], s['key'], s['he_title'], a['buch'], s['halachot'], a['status'],
            '{}–{}'.format(sp[0], sp[-1]) if sp else '–',
            '{} ({})'.format(a.get('seiten_scan', ''), a.get('seiten_erwartet', '')) if sp else '–'))
    L += ['', '## 2 Vokalisierung und Kollation', '', '```', kol_res['bericht'].rstrip(), '```', '',
          '## 3 Glossar (Basis Ben Jehojada)', '', '```', glos_res['bericht'].rstrip(), '```', '',
          '## 4 Bandplan (Bandgröße Ben Ish Chai Halakha)', '', '```', band_res['bericht'].rstrip(), '```', '']
    (Path(out) / (C.WERK_TAG + '_Pruefbericht.md')).write_text('\n'.join(L) + '\n', encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(description='Od Yosef Chai Halakhot – Gesamtlauf')
    ap.add_argument('--json', default=str(C.SOURCE_JSON))
    ap.add_argument('--scan', nargs='*', default=[], help='Scan-ZIP(s)/-Ordner (NNNN_FLxxxx.jpg)')
    ap.add_argument('--scan-gesamt', type=int)
    ap.add_argument('--ocr', action='store_true')
    ap.add_argument('--he-quelle', choices=['basis', 'meine', 'nakdan'], default='basis')
    ap.add_argument('--nakdan-api', action='store_true')
    ap.add_argument('--laden-sefaria', action='store_true')
    ap.add_argument('--out', default=str(C.HERE / 'out'))
    a = ap.parse_args(argv)

    if Path(a.json).resolve() == C.SOURCE_JSON.resolve() and C.sha256_file(a.json) != C.SOURCE_JSON_SHA256:
        raise SystemExit('Quell-JSON veraendert (sha256). Neue Fassung bewusst in oyc_common eintragen.')
    out = Path(a.out)
    vergleich = None
    if a.laden_sefaria:
        vergleich = out / 'sefaria_aktuell.json'
        C.download_sefaria(C.SEFARIA_URL, vergleich)
    print('[1/5] Abschnittsliste und Scanabgleich')
    abs_res = A.run(a.json, a.scan, None, out, a.scan_gesamt, a.ocr, True, vergleich, quiet=True)
    print('[2/5] Nakdan-Export')
    werk = C.load_werk_korrigiert(a.json)
    print('      ' + N.cmd_export(werk, 15000))
    if a.nakdan_api:
        print('      ' + N.cmd_api(werk, 15000, N.DEFAULT_ENDPOINT, 'rabbinic'))
    print('[3/5] Kollation')
    kol_res = K.run(a.json, out, quiet=True)
    print('[4/5] Glossar')
    glos_res = G.run(a.json, None, out, None, None, quiet=True)
    print('[5/5] Bandplan')
    band_res = B.run(a.json, out, a.he_quelle, quiet=True)
    nk = N.lese_zeuge(N.ZEUGEN['nakdan'])
    if a.he_quelle == 'basis' and len(nk) == len(C.absatz_index(werk)):
        probe = B.run(a.json, out / 'probe_nakdan', 'nakdan', quiet=True)
        print('      Probe vokalisiert (Nakdan): {} · {} Zeichen wie das JSX zaehlt'.format(
            probe['dateien'][0], probe['he_zeichen_bic']))
    manifest(out, a.scan, glos_res, band_res)
    pruefbericht(out, abs_res, kol_res, glos_res, band_res, a.he_quelle)
    print(band_res['bericht'])
    print('Pruefbericht: ' + str(out / (C.WERK_TAG + '_Pruefbericht.md')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
