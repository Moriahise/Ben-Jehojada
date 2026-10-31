#!/usr/bin/env python3
"""Moed Katan: unveraenderte Pipeline v3.2.1, dokumentierte Nachkorrektur, Abnahme."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SENLAKE = REPO / 'Ben Yehoyada on Moed Katan - he - Senlake edition 2019 based on Ben Yehoyada, Jerusalem, 1897.txt'
DICTA = REPO / 'מועד_קטן.combinedfullhaser.txt'
ARCHIVE = REPO / 'ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip'
GLOSSARY = REPO / 'glossary_he.json'
GUIDE = REPO / 'Ben_Yehoyada_Arbeitsanleitung_AKTUELL_Fassung1.5_20261005.txt'
TAG = 'Ben_Yehoyada_Moed_Katan'
EXPECTED = {
    SENLAKE: '2dc3908d4b5372a0aa28cd1b142357f7d1cd7c88',
    DICTA: 'ca5d48d19cfbd48206b001cba68eb7c88655c82a',
    ARCHIVE: '2eab4448a8e1e0beec0c9cc2304e6154f06d95f5',
    GUIDE: 'e9f9b020e15c4b9d065bec795a58a686bb17ed08',
}


def blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def exact_replace(text, old, new):
    assert text.count(old) == 1, ('Erwarteter Einzelbeleg fehlt/mehrfach', old)
    return text.replace(old, new, 1)


def main():
    for path, expected in EXPECTED.items():
        assert blob_sha(path) == expected, ('Quelle/Version veraendert', path)
    audit = HERE / 'Audit'
    audit.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='moed_katan_') as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(tmp)
        pipeline = tmp / 'ben-yehoyada-pipeline'
        overrides_path = pipeline / 'band_overrides.json'
        overrides = json.loads(overrides_path.read_text(encoding='utf-8'))
        supplement = json.loads((HERE / 'band_overrides_Moed_Katan.json').read_text(encoding='utf-8'))
        overrides['overrides'].update(supplement['overrides'])
        overrides_path.write_text(json.dumps(overrides, ensure_ascii=False, indent=1), encoding='utf-8')
        rawout = tmp / 'rohlauf'
        result = subprocess.run([
            sys.executable, str(pipeline / 'run_pipeline.py'),
            '--in', str(SENLAKE), '--tractate', 'Moed Katan',
            '--talmud-he', str(DICTA), '--band-words', '42',
            '--band-en', 'empty', '--sample-daf', '9a',
            '--glossary', str(GLOSSARY), '--outdir', str(rawout),
        ], capture_output=True, text=True, check=True)
        (audit / 'Pipeline_Rohbericht.txt').write_text(result.stdout, encoding='utf-8')
        shutil.copyfile(rawout / 'indesign' / (TAG + '_Band_01_BILINGUAL.txt'), audit / 'Pipeline_Rohmaster.txt')
        sys.path.insert(0, str(pipeline))
        import by_indesign
        import by_render
        import by_validate
        import by_gegenpruefung

        doc = json.loads((rawout / 'moed katan.glossed.json').read_text(encoding='utf-8'))
        segs = by_indesign.build_segments(doc, 'Moed Katan', band_en_mode='empty')
        assert len(segs) == 69
        by_id = {s['id']: s for s in segs}
        changes = []

        # Ausschliesslich die im Pruefbericht einzeln belegten Entscheidungen.
        # Kein Eingriff in Pipeline-Code, Lemma, Kommentar, Daf oder Segmentfolge.
        s = by_id['BYH-0000010']
        old_ref = s['ref']
        assert old_ref == 'Moed Katan 9b:8'
        lemma = re.search(r'<lemma>(.*?)</lemma>', s['he'], re.S).group(1)
        old_band = s['band_he']
        s['band_he'], s['ref'] = lemma, ''
        changes.append({'id': s['id'], 'art': 'Kopfband-Rueckfall', 'alt_ref': old_ref,
                        'neu_ref': '', 'alt_band_he': old_band, 'neu_band_he': lemma,
                        'dicta_kontextbeleg': 'Moed Katan 9a:23',
                        'grund': '9b:8 betrifft R. Shimon ben Halafta und Rav, der Kommentar R. Shimon ben Yohai und seinen Sohn. 9a:23 ist der passende Kontext, wird vom unveraenderten Wortlautpruefer wegen Praefixvarianten aber nur mit 0.333 gedeckt. Konservativ bleibt das unveraenderte Senlake-Lemma ohne vorgetaeuschten Dicta-ref.'})
        doc['entries'][9]['talmud'] = {'he': lemma, 'en': None}
        doc['entries'][9]['sefaria_ref'] = None

        patches = [
            ('BYH-0000004', 'למ"ד = הָאוֹת ל', 'למ"ד = מִסְפָּר 30',
             'Senlake: בגמרא דשבת דף למ"ד ע"א; Blattangabe, kein Buchstabenname.'),
            ('BYH-0000046', 'הרי"ף = רַבֵּנוּ יִצְחָק אַלְפָסִי', None,
             'Die beiden Quellen bestimmen den Traeger von הרי"ף hier nicht. Personenaufloesung entfernt, Kuerzel unveraendert.'),
            ('BYH-0000069', 'מהר"ם = מוֹרֵנוּ הָרַב רַבִּי מֵאִיר', 'מהר"ם = מוֹרֵנוּ הָרַב רַבִּי מֹשֶׁה',
             'Senlake: רבינו מהר"ם אלשיך; vorhandene alternative Glossarlesart fuer Alshich statt Meir.'),
        ]
        for sid, old, new, reason in patches:
            s = by_id[sid]
            old_tag = '<fn>' + old + '</fn>'
            new_tag = '<fn>' + new + '</fn>' if new else ''
            s['he'] = exact_replace(s['he'], old_tag, new_tag)
            changes.append({'id': sid, 'art': 'Fussnote', 'alt': old_tag, 'neu': new_tag, 'grund': reason})

        s = by_id['BYH-0000020']
        note = '<fn>תי"ו = מִסְפָּר 416</fn>'
        s['he'] = exact_replace(s['he'], note, '')
        s['he'] = exact_replace(s['he'], 'עולה מספר תי"ו במילואה.', 'עולה מספר תי"ו' + note + ' במילואה.')
        changes.append({'id': s['id'], 'art': 'Fussnotenposition', 'fussnote': note,
                        'alt_nach': 'תי"ו vor תחיה', 'neu_nach': 'עולה מספר תי"ו',
                        'grund': 'Senlake setzt [416] erst an den dritten Beleg nach עולה מספר; keine Zahlaufloesung bei תיו תחיה.'})
        for a in doc['entries'][3]['abbreviations']:
            if a['abbr'] == 'למ"ד':
                a['expansion'], a['expansion_en'] = 'מִסְפָּר 30', '30'

        # Dieselbe Zeichenkalibrierung wie in build_segments(), nach den Korrekturen.
        for s in segs:
            s['he_chars'] = len(re.sub(r'<[^>]+>', '', s['he'])) + len(re.sub(r'<[^>]+>', '', s['band_he']))
            s['footnotes'] = s['he'].count('<fn>')
        volumes, total, n_vol = by_indesign.plan_volumes(segs)
        assert n_vol == len(volumes) == 1
        pgs = sum(s['pages'] for s in volumes[0]) + by_indesign.FRONT_MATTER
        assert pgs <= 588 and pgs + 12 <= 600
        band = HERE / (TAG + '_Band_01_BILINGUAL.txt')
        by_indesign.write_volume(str(band), 1, volumes[0], 'Moed Katan')
        by_indesign.write_glossary(str(HERE / (TAG + '_GLOSSAR.tsv')), doc)
        plan = [
            'BEN YEHOYADA · MOED KATAN · BANDPLAN',
            'Pipeline v3.2.1 (2026-10-05); Arbeitsanleitung 1.5 (20261005).',
            'Ein Band; vollstaendiger Bestand der angegebenen Senlake-Datei.',
            'Band 01: Daf 5a–29a; 16 vorhandene Daf-Abschnitte; 69 Segmente.',
            'BYH-0000001–BYH-0000069; 257 hebraeische Fussnoten.',
            f'Textkoerper geschaetzt: {pgs - 16:.6f} Seiten.',
            f'Pipeline-Schaetzung einschliesslich 16 Seiten FRONT_MATTER: {pgs:.6f} Seiten (aufgerundet {__import__("math").ceil(pgs)}).',
            f'Zusaetzlich 12 Seiten Reserve: {pgs + 12:.6f} Seiten (auf ganze Seiten aufgerundet {__import__("math").ceil(pgs) + 12}).',
            'Grenzen: 588 geschaetzte Seiten vor Reserve; 600 physische Seiten absolut.',
            'Richtwert ca. 540 Seiten ist kein Mindestumfang: keine Auffuellung und kein fremder Traktat.',
            'Kalibrierung: HE 1280 Zeichen/Seite; EN 2420; Expansion 1.95.',
            'Schnitt nur zwischen Daf-Gruppen; hier ist kein Schnitt erforderlich.',
            'Keine Kommentarsegmente fuer nicht vorhandene Dafim ergaenzt.',
            '<en> und <band_en> in allen 69 Segmenten leer; englische Daf-Titel vorhanden.',
            'Tatsaechliche physische Seitenzahl erst nach Uebersetzung und InDesign-Satz feststellbar.',
        ]
        (HERE / (TAG + '_Bandplan.txt')).write_bytes(('\r\n'.join(plan) + '\r\n').encode('utf-8-sig'))
        (HERE / (TAG + '_Muster_9a.html')).write_text(by_render.render(doc, ['9a'], title='Ben Yehoyada · Moed Katan'), encoding='utf-8')
        (audit / 'Lektoratsentscheidungen.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        findings, stats, count = by_validate.validate(str(band), expect=69)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = by_validate.report(findings, stats, count, str(band))
        (HERE / (TAG + '_Band_01_Validator.txt')).write_text(buf.getvalue(), encoding='utf-8')
        (HERE / (TAG + '_Band_01_Validator.json')).write_text(json.dumps({'findings': findings, 'stats': stats, 'segments': count}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        assert rc == 0, 'Validator blockiert'
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = by_gegenpruefung.main(str(band), str(SENLAKE), str(DICTA), str(HERE / (TAG + '_Band_01_Gegenpruefung.json')))
        (HERE / (TAG + '_Band_01_Gegenpruefung.txt')).write_text(buf.getvalue(), encoding='utf-8')
        assert rc == 0, 'Gegenpruefung blockiert'

        # Geschuetzte Quelldaten: nur die im Audit aufgefuehrten Unterschiede.
        _, rawsegs = by_validate.read(str(audit / 'Pipeline_Rohmaster.txt'))
        _, finalsegs = by_validate.read(str(band))
        actual = []
        for before, after in zip(rawsegs, finalsegs):
            assert before['attrs']['id'] == after['attrs']['id']
            for field in ['n', 'daf']:
                assert before['attrs'][field] == after['attrs'][field]
            for field in ['he', 'band_he', 'en', 'band_en']:
                if before[field] != after[field]:
                    actual.append([after['attrs']['id'], field])
            if before['attrs'].get('ref') != after['attrs'].get('ref'):
                actual.append([after['attrs']['id'], 'ref'])
        assert sorted(actual) == sorted([
            ['BYH-0000010', 'band_he'], ['BYH-0000010', 'ref'],
            ['BYH-0000004', 'he'], ['BYH-0000020', 'he'],
            ['BYH-0000046', 'he'], ['BYH-0000069', 'he'],
        ])
        assert band.read_bytes().startswith(b'\xef\xbb\xbf')
        assert b'\n' not in band.read_bytes().replace(b'\r\n', b'')
        assert all(s['en'] == s['band_en'] == '' for s in finalsegs)
        (audit / 'Feldvergleich.json').write_text(json.dumps(actual, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        tests = subprocess.run([sys.executable, '-W', 'ignore::ResourceWarning', '-m', 'unittest', 'test_pipeline_regressions'], cwd=pipeline, capture_output=True, text=True)
        (audit / 'Regressionstests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
        assert tests.returncode == 0
        test = subprocess.run([sys.executable, str(pipeline / 'by_sefaria.py'), '--selftest'], capture_output=True, text=True, check=True)
        (audit / 'Matching_Selbsttest.txt').write_text(test.stdout, encoding='utf-8')
        manifest = {'repository': 'Moriahise/Ben-Jehojada', 'basis_commit': 'ad42c473351f191013cfe39c827db2960c2660d2',
                    'pipeline': 'v3.2.1 (2026-10-05)', 'anleitung': '1.5_20261005',
                    'eingaben': [{'datei': p.name, 'git_blob_sha': blob_sha(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in [SENLAKE, DICTA, ARCHIVE, GUIDE, GLOSSARY]],
                    'geschaetzte_seiten_inkl_frontmatter': pgs,
                    'segmente': 69, 'dafim': list(dict.fromkeys(s['daf'] for s in segs)),
                    'fussnoten': sum(s['footnotes'] for s in segs),
                    'kopfband_dicta': sum(bool(s['ref']) for s in segs),
                    'kopfband_lemma_rueckfall': sum(not bool(s['ref']) for s in segs),
                    'master_sha256': hashlib.sha256(band.read_bytes()).hexdigest()}
        (HERE / 'Quellenmanifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: manifest[k] for k in ['geschaetzte_seiten_inkl_frontmatter', 'segmente', 'fussnoten', 'kopfband_dicta', 'kopfband_lemma_rueckfall', 'master_sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
