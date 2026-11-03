# -*- coding: utf-8 -*-
"""
Regressionstests Od Yosef Chai · Halakhot (offline).

    python3 -m unittest test_oyc -v

Die JSX-Tests fuehren Funktionen aus Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17
unveraendert in Node aus (parseBilingualFile, composeDisplayTexts, planVolumes);
ohne Node werden sie uebersprungen.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import oyc_common as C
import oyc_abschnitte as A
import oyc_bandplan as B
import oyc_glossar as G
import oyc_kollation as K
import oyc_nakdan as N

NODE = shutil.which('node')
JSX_FUNCS = ['trim', 'normalizeNewlines', 'stripBom', 'stripTags', 'visibleLength', 'xmlUnescape',
             'restoreCdata', 'parseBilingualFile', 'composeDisplayTexts', 'planVolumes',
             'splitOversizeSection', 'newVolume', 'addGroupToVolume', 'finalizeVolume',
             'estimatedBodyPages', 'pad2']


def jsx_function(src, name):
    lines = src.splitlines()
    for i, l in enumerate(lines):
        if re.match(r'^ {4}function ' + re.escape(name) + r'\(', l):
            if l.rstrip().endswith('}') and l.count('{') == l.count('}'):
                return l
            for j in range(i + 1, len(lines)):
                if lines[j] == '    }':
                    return '\n'.join(lines[i:j + 1])
    raise KeyError(name)


def run_jsx(js_body, payload):
    src = C.BIC_JSX.read_text(encoding='utf-8')
    consts = '\n'.join(l for l in src.splitlines() if re.match(
        r'^ {4}var (MAX_PAGES|TARGET_PAGES|RESERVED_PAGES|BODY_TARGET|HE_CHARS_PER_PAGE|'
        r'EN_CHARS_PER_PAGE|EN_EXPANSION) =', l))
    funcs = '\n'.join(jsx_function(src, n) for n in JSX_FUNCS)
    prog = consts + '\n' + funcs + '\nvar INPUT = JSON.parse(require("fs").readFileSync(0, "utf8"));\n' + js_body
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as fh:
        fh.write(prog)
    r = subprocess.run([NODE, fh.name], input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    Path(fh.name).unlink()
    if r.returncode:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Werk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.werk = C.load_werk()
        cls.segs = C.build_segments(cls.werk)

    def test_quelle_unveraendert(self):
        self.assertEqual(C.sha256_file(C.SOURCE_JSON), C.SOURCE_JSON_SHA256)

    def test_struktur(self):
        keys = [a['key'] for a in self.werk['abschnitte']]
        self.assertEqual(len(keys), 29)
        self.assertEqual(keys[9], 'Kuntres Chut HaMeshulash')
        self.assertEqual(self.werk['abschnitte'][9]['tiefe'], 1)
        self.assertEqual(len(self.segs), 508)
        self.assertEqual(len(C.build_segments(self.werk, gliederung={})), 506)
        vaera = next(a for a in self.werk['abschnitte'] if a['key'] == 'Vaera')
        self.assertTrue(vaera['halachot'][2]['leer'])

    def test_ids_und_n(self):
        self.assertEqual([s['id'] for s in self.segs], ['OYH-{:07d}'.format(i) for i in range(1, 509)])
        vaera = [s['n'] for s in self.segs if s['abschnitt'] == 'Vaera']
        self.assertEqual(vaera[:3], [1, 2, 4])          # gedruckte Zaehlung (ב' -> ד')
        self.assertEqual(self.segs[0]['ref'], 'Od Yosef Chai; Halakhot, Bereshit 1:1')

    def test_gliederung_bereshit_und_purim(self):
        s = self.segs
        self.assertEqual([(x['n'], x['section_he']) for x in s[:4]],
                         [(0, 'הלכות שנה ראשונה'), (0, 'פרשת בראשית'), (1, 'פרשת בראשית'), (2, 'פרשת בראשית')])
        self.assertEqual([x['ref'].split(', ')[1] for x in s[:3]], ['Bereshit 1:1', 'Bereshit 1:2–4', 'Bereshit 1:5–6'])
        self.assertTrue(C.strip_tags(s[0]['he']).startswith('אלו הם ההלכות'))
        self.assertTrue(C.strip_tags(s[2]['he']).startswith('צריך לכוין'))
        i = next(k for k, x in enumerate(s) if x['abschnitt'] == 'Purim')
        self.assertEqual(s[i - 1]['abschnitt'], 'Tetzaveh')
        self.assertEqual(s[i - 1]['n'], 12)
        self.assertEqual([(x['n'], x['section_he']) for x in s[i:i + 2]],
                         [(1, "שייך להלכות פורים בפ' תצוה"), (2, "שייך להלכות פורים בפ' תצוה")])
        self.assertEqual(s[i + 2]['section_he'], 'פרשת כי תשא')

    def test_gliederung_wird_geprueft(self):
        gl = C.lade_gliederung()
        kaputt = json.loads(json.dumps(gl))
        kaputt['teilen'][0]['teile'][1]['absaetze'] = [2, 3]     # Absatz 4 fehlt
        with self.assertRaises(SystemExit):
            C.build_segments(self.werk, gliederung=kaputt)
        kaputt = json.loads(json.dumps(gl))
        kaputt['unterabschnitte'][0]['unter'] = 'Nirgendwo'
        with self.assertRaises(SystemExit):
            C.build_segments(self.werk, gliederung=kaputt)

    def test_text_vollstaendig(self):
        joined = ''.join(C.strip_tags(s['he']).replace('\n', '') for s in self.segs)
        quelle = ''.join(C.strip_tags(p['html']).strip() for _, _, p in C.iter_absaetze(self.werk))
        self.assertEqual(joined, quelle)


class Kalibrierung(unittest.TestCase):
    def test_werte_wie_jsx(self):
        src = C.BIC_JSX.read_text(encoding='utf-8')
        def v(name):
            return float(re.search(r'var ' + name + r' = ([0-9.]+);', src).group(1))
        self.assertEqual(v('MAX_PAGES'), C.MAX_PAGES)
        self.assertEqual(v('TARGET_PAGES'), C.TARGET_PAGES)
        self.assertEqual(v('RESERVED_PAGES'), C.RESERVED_PAGES)
        self.assertEqual(v('HE_CHARS_PER_PAGE'), C.HE_CHARS_PER_PAGE)
        self.assertEqual(v('EN_CHARS_PER_PAGE'), C.EN_CHARS_PER_PAGE)
        self.assertEqual(v('EN_EXPANSION'), C.EN_EXPANSION)
        self.assertEqual(v('PAGE_W_MM'), C.PAGE_W_MM)
        self.assertEqual(v('PAGE_H_MM'), C.PAGE_H_MM)
        self.assertEqual(v('HE_LEADING'), C.HE_LEADING_PT)

    def test_ein_band_mit_reserve(self):
        with tempfile.TemporaryDirectory() as d:
            r = B.run(out=d, quiet=True)
        self.assertEqual(r['baende'], 1)
        self.assertLessEqual(r['band_seiten'][0], C.TARGET_PAGES)
        self.assertGreater(C.TARGET_PAGES - r['band_seiten'][0], 30)


@unittest.skipUnless(NODE, 'node fehlt')
class JSX(unittest.TestCase):
    def test_banddatei_vom_buchmanager_lesbar(self):
        with tempfile.TemporaryDirectory() as d:
            r = B.run(out=d, quiet=True)
            raw = Path(r['dateien'][0]).read_text(encoding='utf-8-sig')
            res = run_jsx('''
var p = parseBilingualFile(INPUT.raw);
var t = composeDisplayTexts(p);
process.stdout.write(JSON.stringify({volume:p.volume, n:p.segments.length, sections:p.sections.length,
  ids:p.segments.map(function(s){return s.id;}), nums:p.segments.map(function(s){return s.number;}),
  he:p.segments.map(function(s){return s.he;}), heVisible:t.heVisible}));''', {'raw': raw})
        segs = r['segs']
        self.assertEqual(res['volume'], 1)
        self.assertEqual(res['n'], len(segs))
        self.assertEqual(res['sections'], 30)
        self.assertEqual(res['ids'], [s['id'] for s in segs])
        self.assertEqual(res['nums'], [s['n'] for s in segs])
        self.assertEqual(res['he'], [s['he'] for s in segs])

    def test_kolumnentitel_manager_erkennt_abschnitte(self):
        hdr = C.REPO / 'Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx'
        src = hdr.read_text(encoding='utf-8')
        namen = ['trim', 'readUTF8', 'xmlUnescape', 'restoreCdata', 'cleanHeadingText', 'stripHebrewMarks',
                 'normalizeHebrewWords', 'normalizeEnglishWords', 'detectYearMarker', 'buildParashahCatalogue',
                 'findParashahByHebrewTitle', 'findParashahByEnglishTitle', 'extractProjectEnglishTitle',
                 'parseSourceParashot']
        funcs = '\n'.join(jsx_function(src, n) for n in namen if n != 'readUTF8')
        prog = (funcs + '\nfunction readUTF8(f){return f;}\nvar PARASHOT = buildParashahCatalogue();\n'
                'var raw = require("fs").readFileSync(0, "utf8");\n'
                'var p = parseSourceParashot(raw);\n'
                'var jahr = detectYearMarker("הלכות שנה ראשונה");\n'
                'process.stdout.write(JSON.stringify({jahr: jahr, p: p.map(function(x){return [x.heRaw, x.key, x.year];})}));')
        with tempfile.TemporaryDirectory() as d:
            r = B.run(out=d, quiet=True)
            raw = Path(r['dateien'][0]).read_text(encoding='utf-8-sig')
            js = Path(d) / 'hdr.js'
            js.write_text(prog, encoding='utf-8')
            out = subprocess.run([NODE, str(js)], input=raw, capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        res = json.loads(out.stdout)
        self.assertEqual(res['jahr'], 1)
        keys = [k for _, k, _ in res['p']]
        purim = [k for he, k, _ in res['p'] if 'פורים' in he]
        self.assertEqual(purim, ['tetzaveh'])                 # Purim steht unter Tezawe
        self.assertEqual(keys[:2], ['bereshit', 'noach'])
        self.assertEqual(len(keys), 28)        # 27 Paraschot + Purim; Vorwort und Kuntres ohne Parascha
        self.assertEqual({y for _, _, y in res['p']}, {1})   # 'הלכות שנה ראשונה' setzt den Jahrgang

    def test_planer_wie_jsx(self):
        werk = C.load_werk()
        segs = C.build_segments(werk)
        for s in segs:
            s['plan_chars'] = C.visible_length(s['he'])
        # kuenstlich vergroessert, damit der Planer mehrere Baende schneiden muss
        for faktor in (1, 3):
            sections = []
            for s in segs:
                if not sections or sections[-1]['title'] != s['section_he']:
                    sections.append({'title': s['section_he'], 'segments': []})
                sections[-1]['segments'].append({'id': s['id'], 'he': s['he'] * faktor})
            res = run_jsx('''
var v = planVolumes({sections: INPUT.sections});
process.stdout.write(JSON.stringify(v.map(function(x){return [x.segments[0].id, x.segments[x.segments.length-1].id, x.estimatedPages];})));''',
                          {'sections': sections})
            big = [dict(s, he=s['he'] * faktor, plan_chars=C.visible_length(s['he'] * faktor)) for s in segs]
            py = [[v['segments'][0]['id'], v['segments'][-1]['id'], v['estimated_pages']]
                  for v in B.plan_volumes(big)]
            self.assertEqual(py, res, 'Faktor {}'.format(faktor))


def run_js(src_path, namen, extra, body, payload):
    src = Path(src_path).read_text(encoding='utf-8')
    consts = '\n'.join(l for l in src.splitlines() if re.match(
        r'^ {4}var (MAX_PAGES|TARGET_PAGES|RESERVED_PAGES|BODY_TARGET|HE_CHARS_PER_PAGE|'
        r'EN_CHARS_PER_PAGE|EN_EXPANSION) =', l))
    prog = (consts + '\n' + '\n'.join(jsx_function(src, n) for n in namen) + '\n' + extra +
            '\nvar INPUT = JSON.parse(require("fs").readFileSync(0, "utf8"));\n' + body)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as fh:
        fh.write(prog)
    r = subprocess.run([NODE, fh.name], input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    Path(fh.name).unlink()
    if r.returncode:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


INDESIGN = C.HERE / 'indesign'
OYC_BM = INDESIGN / 'Od_Yosef_Chai_Bilingual_Book_Manager_v1_0_0.jsx'
OYC_RH = INDESIGN / 'Od_Yosef_Chai_Running_Header_Manager_v1_0_0.jsx'

JS_BAND = """
var p = parseBilingualFile(INPUT.raw);
var t = composeDisplayTexts(p);
var secs = [], cur = null;
for (var i = 0; i < p.segments.length; i++) {
  var s = p.segments[i];
  if (!cur || cur.title !== s.sectionHe) { cur = {title: s.sectionHe, segments: []}; secs.push(cur); }
  cur.segments.push({id: s.id, he: s.he});
}
var v = planVolumes({sections: secs});
process.stdout.write(JSON.stringify({n: p.segments.length, ids: [p.segments[0].id, p.segments[p.segments.length-1].id],
  kopf: t.he.substring(0, 200), heVisible: t.heVisible, baende: v.length, seiten: v[0].estimatedPages}));
"""

JS_KOPF = """
var p = parseSourceParashot(INPUT.raw);
var cfg = {enTemplate: "OD YOSEF CHAI · {PARASHAH}", heTemplate: "עוד יוסף חי · פרשת {PARASHAH_HE}",
           shortEnTemplate: "OD YOSEF CHAI · {PARASHAH}", shortHeTemplate: "עוד יוסף חי · פרשת {PARASHAH_HE}", yearMode: 0};
var cfgJahr = {enTemplate: "OD YOSEF CHAI · {YEAR} · {PARASHAH}", heTemplate: "עוד יוסף חי · הלכות {YEAR_HE} · פרשת {PARASHAH_HE}",
           shortEnTemplate: cfg.shortEnTemplate, shortHeTemplate: cfg.shortHeTemplate, yearMode: 0};
var k = {heTitle: "קונטרס חוט המשולש", enTitle: "Kuntres Chut HaMeshulash", year: 1};
var n = {heTitle: "נח", enTitle: "Noach", year: 1};
process.stdout.write(JSON.stringify({keys: p.map(function(x){return x.key;}),
  purim: p.filter(function(x){return x.heRaw.indexOf("פורים")>=0;}).map(function(x){return x.key;}),
  kHe: renderHeaderText(k, cfg, "he", false).text, kEn: renderHeaderText(k, cfg, "en", false).text,
  nHe: renderHeaderText(n, cfgJahr, "he", false).text, nEn: renderHeaderText(n, cfgJahr, "en", false).text}));
"""


@unittest.skipUnless(NODE, 'node fehlt')
class InDesignOYC(unittest.TestCase):
    """Die Od-Yosef-Chai-Skripte (aus den Ben-Ish-Chai-Skripten erzeugt), echter Code in Node."""

    def test_generator_reproduzierbar(self):
        sys.path.insert(0, str(INDESIGN))
        import erzeuge_oyc_jsx as E
        with tempfile.TemporaryDirectory() as d:
            for src, dst, kopf, ers in ((E.BM_SRC, OYC_BM, E.BM_KOPF, E.BM_ERSETZUNGEN),
                                        (E.RH_SRC, OYC_RH, E.RH_KOPF, E.RH_ERSETZUNGEN)):
                neu, _ = E.baue(src, Path(d) / dst.name, kopf, ers)
                self.assertEqual(neu.read_bytes(), dst.read_bytes(), dst.name)
        for f in (OYC_BM, OYC_RH):
            t = f.read_text(encoding='utf-8')
            self.assertNotIn('Ben_Ish_Chai_Band', t)
            self.assertNotIn('"BIH', t)

    def test_buchmanager_liest_vokalisierten_band(self):
        quelle = 'nakdan' if len(N.lese_zeuge(N.ZEUGEN['nakdan'])) == 1024 else 'basis'
        with tempfile.TemporaryDirectory() as d:
            r = B.run(out=d, he_quelle=quelle, quiet=True)
            raw = Path(r['dateien'][0]).read_text(encoding='utf-8-sig')
        namen = ['trim', 'normalizeNewlines', 'stripBom', 'stripTags', 'visibleLength', 'planLength', 'xmlUnescape',
                 'restoreCdata', 'parseBilingualFile', 'segmentMarke', 'composeDisplayTexts', 'planVolumes',
                 'splitOversizeSection', 'newVolume', 'addGroupToVolume', 'finalizeVolume', 'estimatedBodyPages', 'pad2']
        res = run_js(OYC_BM, namen, '', JS_BAND, {'raw': raw})
        self.assertEqual(res['n'], 508)
        self.assertEqual(res['ids'], ['OYH-0000001', 'OYH-0000508'])
        self.assertIn('<oyhnull>[0]</oyhnull> ', res['kopf'])          # Vorwort ohne sichtbare Nummer
        self.assertNotIn('<b>[0]</b>', res['kopf'])
        self.assertLess(res['heVisible'], r['he_zeichen'] * 1.05)      # Zaehlung ohne Nikud
        self.assertEqual((res['baende'], res['seiten']), (1, r['band_seiten'][0]))

    def test_kolumnentitel_kuntres_und_purim(self):
        with tempfile.TemporaryDirectory() as d:
            r = B.run(out=d, quiet=True)
            raw = Path(r['dateien'][0]).read_text(encoding='utf-8-sig')
        namen = ['trim', 'xmlUnescape', 'restoreCdata', 'cleanHeadingText', 'stripHebrewMarks', 'normalizeHebrewWords',
                 'normalizeEnglishWords', 'detectYearMarker', 'buildParashahCatalogue', 'findParashahByHebrewTitle',
                 'findParashahByEnglishTitle', 'extractProjectEnglishTitle', 'parseSourceParashot',
                 'replaceAllLiteral', 'cleanTemplateSeparators', 'renderHeaderText']
        extra = 'function readUTF8(f){return f;}\nvar PARASHOT = buildParashahCatalogue();'
        res = run_js(OYC_RH, namen, extra, JS_KOPF, {'raw': raw})
        keys = res['keys']
        self.assertEqual(len(keys), 29)                      # 27 Paraschot + Purim + Kuntres
        self.assertEqual(keys[keys.index('vayeshev') + 1], 'kuntres_chut_hameshulash')
        self.assertEqual(res['purim'], ['tetzaveh'])
        self.assertEqual(res['kHe'], 'עוד יוסף חי · קונטרס חוט המשולש')
        self.assertEqual(res['kEn'], 'OD YOSEF CHAI · Kuntres Chut HaMeshulash')
        self.assertEqual(res['nHe'], 'עוד יוסף חי · הלכות שנה ראשונה · פרשת נח')
        self.assertEqual(res['nEn'], 'OD YOSEF CHAI · FIRST YEAR · Noach')


class Abnahme(unittest.TestCase):
    """oyc_validate.py gegen einen Master und eine (Test-)EN_FERTIG-Fassung."""

    @classmethod
    def setUpClass(cls):
        import oyc_validate as V
        cls.V = V
        cls.tmp = tempfile.mkdtemp()
        cls.master = Path(B.run(out=cls.tmp, quiet=True)['dateien'][0])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def fertig(self, aendern=None):
        raw = self.master.read_text(encoding='utf-8-sig')
        raw = re.sub(r'<en></en>', '<en><![CDATA[English text of this halakhah.]]></en>', raw)
        raw = re.sub(r'<en_title></en_title>', '<en_title>Section</en_title>', raw)
        raw = raw.replace('<en_title>Section</en_title>', '<en_title>Parashat Noach</en_title>', 0)
        if aendern:
            raw = aendern(raw)
        f = Path(self.tmp) / 'Band_01_BILINGUAL_EN_FERTIG.txt'
        C.write_bic_text(f, raw)
        return self.V.pruefe(f, self.master, None, None)

    def test_frischer_master(self):
        r = self.V.pruefe(self.master, None, False, None)
        self.assertEqual(r['fehler'], [])
        self.assertEqual(r['segmente'], 508)
        self.assertEqual(r['he_quelle'], 'basis')

    def test_fertige_fassung_ohne_fehler(self):
        r = self.fertig()
        self.assertTrue(r['fertig_modus'])
        self.assertEqual(r['fehler'], [])
        self.assertEqual(r['en_gefuellt'], 508)

    def test_fehler_werden_erkannt(self):
        r = self.fertig(lambda t: t.replace('צריך לכוין', 'צריך לכון', 1))
        self.assertTrue(any('<he> veraendert' in x for x in r['fehler']))
        r = self.fertig(lambda t: t.replace('English text of this halakhah.', 'Text<fn>x</fn> of YHWH', 1))
        self.assertTrue(any('<fn>' in x for x in r['fehler']))
        self.assertTrue(any('YHWH' in x for x in r['fehler']))
        r = self.fertig(lambda t: t.replace('<en_title>Section</en_title>', '<en_title>פרשת</en_title>', 1))
        self.assertTrue(any('hebraeischen Zeichen' in x for x in r['fehler']))
        r = self.fertig(lambda t: t.replace('id="OYH-0000005"', 'id="OYH-0000004"', 1))
        self.assertTrue(any('Doppelte IDs' in x for x in r['fehler']))

    def test_batch_gegen_master(self):
        raw = self.master.read_text(encoding='utf-8-sig')
        segs = re.findall(r'<segment id="OYH-000001[0-1]".*?</segment>', raw, re.S)
        batch = ('<translation_batch project="Od Yosef Chai Halakhot" volume="01">\n<section>\n'
                 '<he_title>פרשת בראשית</he_title>\n<en_title>Parashat Bereshit</en_title>\n</section>\n' +
                 '\n'.join(s.replace('<en></en>', '<en><![CDATA[English.]]></en>') for s in segs) +
                 '\n</translation_batch>')
        f = Path(self.tmp) / 'Translation_Batch_01_EN_FERTIG.txt'
        C.write_bic_text(f, batch)
        r = self.V.pruefe(f, self.master, None, None)
        self.assertEqual(r['fehler'], [])
        self.assertEqual(r['segmente'], 2)


class Vokalisierung(unittest.TestCase):
    BASIS = '<b>כתב</b> רבינו הרש"ש ז"ל בנהר שלום דף ב"ן, בענין'
    VOK = 'כָּתַב רַבֵּינוּ הָרַשַׁ"שׁ זַ"ל בִּנְהַר שָׁלוֹם דַּף ב"ן בְּעִנְיַן'

    def test_kuerzel(self):
        for w in ('ה\'', 'ב\'', 'כנז\'', 'ז"ל', 'בסה"ק'):
            self.assertTrue(K.ist_kuerzel(w), w)
        for w in ('"כי', 'משה', 'טיליגראף'):
            self.assertFalse(K.ist_kuerzel(w), w)

    def test_plene_marke(self):
        self.assertEqual(K.ohne_plene_marke('קֹוֽדֶם'), 'קֹודֶם')
        self.assertEqual(K.ohne_plene_marke('הַמְּגִיֽלָּה'), 'הַמְּגִילָּה')
        self.assertEqual(K.ohne_plene_marke('הָֽאָרֶץ'), 'הָֽאָרֶץ')        # echtes Meteg bleibt
        self.assertEqual(K.transfer('קודם', 'קֹוֽדֶם'), 'קֹודֶם')
        self.assertEqual(K.vok_signatur('קֹוֽדֶם'), K.vok_signatur('קֹודֶם'))

    def test_transfer(self):
        self.assertEqual(K.transfer('בסה"ק', 'בְּסֵהַ״ק'), 'בְּסֵהַ"ק')
        self.assertIsNone(K.transfer('רבינו', 'רַבֵּנוּ'))

    def test_vokalisiere_html_behaelt_tags_und_konsonanten(self):
        out, ok, offen = K.vokalisiere_html(self.BASIS, self.VOK)
        self.assertTrue(out.startswith('<b>כָּתַב</b> '))
        self.assertEqual(C.strip_nikud(out), self.BASIS)
        self.assertEqual(offen, 0)
        out2, _, offen2 = K.vokalisiere_html(self.BASIS, self.VOK.replace('רַבֵּינוּ', 'רַבֵּנוּ'))
        self.assertIn(' רבינו ', out2)                 # Abweichung: Basiswort bleibt
        self.assertEqual(offen2, 1)

    def test_kollation_arten(self):
        meine = self.VOK.replace('שָׁלוֹם', 'שלום').replace('דַּף', 'דָּף')
        rows, _ = K.kollationiere_absatz('X 1:1', self.BASIS, {'nakdan': self.VOK.replace('רַבֵּינוּ', 'רַבֵּנוּ'),
                                                               'meine': meine})
        arten = {(r[2], r[3]) for r in rows}
        self.assertIn(('TEXT_N', 'רבינו'), arten)
        self.assertIn(('UNVOK_M', 'שלום'), arten)
        self.assertIn(('VOK', 'דף'), arten)
        self.assertFalse(any(r[2].endswith('_M') and r[2] != 'UNVOK_M' for r in rows))

    def test_marker_rundlauf(self):
        werk = C.load_werk()
        teile = N.export_teile(werk, 15000)
        with tempfile.TemporaryDirectory() as d:
            for name, e in teile:
                N.schreibe_marker(Path(d) / name, e, 'Test')
            texte = N.lese_zeuge(d)
        self.assertEqual(len(texte), 1024)
        b = N.pruefe_zeuge(werk, texte)
        self.assertEqual(b['konsonanten_abweichend'], [])
        self.assertTrue(all(sum(len(t) for _, t in e) <= 15000 or len(e) == 1 for _, e in teile))

    def test_nakdan_antwortformen(self):
        a = [{'word': 'שלום', 'sep': False, 'options': [['שָׁ|לוֹם', []]]}, {'word': ' ', 'sep': True}]
        b = {'data': [{'word': 'שלום', 'sep': False, 'nakdan': {'options': [{'w': 'שָׁלוֹם'}]}}]}
        c = [{'word': 'שלום', 'sep': False, 'options': ['שָׁלוֹם']}]
        self.assertEqual(N.nakdan_text(a), 'שָׁלוֹם ')
        self.assertEqual(N.nakdan_text(b), 'שָׁלוֹם')
        self.assertEqual(N.nakdan_text(c), 'שָׁלוֹם')

    def test_api_lauf_mit_simuliertem_server(self):
        """Nur der Ablauf: Endpunktwahl, Teilung, Zusammensetzen, Markerdateien.
        Der 'Server' setzt Patach unter jeden Buchstaben – kein Ergebnis."""
        import json as _json
        import re as _re

        def fake_http(url, timeout=60, data=None, headers=None):
            if 'nakdan-2-0' in url:
                raise OSError('403 Forbidden')
            text = _json.loads(data.decode('utf-8'))['data']
            out = []
            for tok in _re.split(r'(\s+)', text):
                if not tok:
                    continue
                if tok.isspace():
                    out.append({'word': tok, 'sep': True})
                else:
                    voc = _re.sub('([\u05D0-\u05EA])', '\\1\u05B7', tok)
                    out.append({'word': tok, 'sep': False, 'options': [[voc, []]]})
            return _json.dumps(out, ensure_ascii=False).encode('utf-8')

        werk = C.load_werk()
        alt = (C.http_get, N.ZEUGEN['nakdan'], N.CACHE, N.time.sleep)
        with tempfile.TemporaryDirectory() as d:
            try:
                C.http_get = fake_http
                N.ZEUGEN['nakdan'] = Path(d) / 'nakdan'
                N.CACHE = Path(d) / 'cache'
                N.time.sleep = lambda *_: None
                msg = N.cmd_api(werk, 15000, 'auto', 'rabbinic', nur=['Purim', 'Lech_Lecha'], parallel=2)
                texte = N.lese_zeuge(N.ZEUGEN['nakdan'])
            finally:
                C.http_get, N.ZEUGEN['nakdan'], N.CACHE, N.time.sleep = alt
        self.assertIn('nakdan-5-3', msg)                     # erster Endpunkt 'gesperrt' -> naechster
        self.assertIn('Konsonanten abweichend: 0', msg)
        self.assertEqual(len(texte), 8 + 2)                  # Lech Lecha 8 Absaetze, Purim 2
        self.assertEqual(N.pruefe_zeuge(werk, texte)['konsonanten_abweichend'], [])

    def test_teile_text(self):
        t = ('אבג דהו, ' * 900).strip()
        teile = N.teile_text(t, 4000)
        self.assertEqual(''.join(teile), t)
        self.assertTrue(all(len(x) <= 4000 for x in teile))


class Glossar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.res = G.run(out=cls.tmp, quiet=True)
        cls.neu = json.loads((Path(cls.tmp) / 'glossar' / (C.WERK_TAG + '_Glossar_NEU.json')).read_text(encoding='utf-8'))
        cls.rows = C.read_tsv(Path(cls.tmp) / 'glossar' / (C.WERK_TAG + '_GLOSSAR.tsv'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_by_glossar_uebernommen(self):
        st = {r['abbr']: r['status'] for r in self.rows}
        self.assertTrue(st['ק"ש'].startswith('UEBERNOMMEN'))
        self.assertTrue(st['הרש"ש'].startswith('UEBERNOMMEN'))
        self.assertIn('NEU', st['ש"ץ'])

    def test_neue_termini_markiert(self):
        self.assertIn('ש"ץ', self.neu['neu'])
        self.assertTrue(all(v['neu'] and v['he'] == '' for v in self.neu['neu'].values()))
        self.assertEqual(self.neu['neu']['בש"ץ']['stamm'], 'ש"ץ')
        self.assertEqual(self.neu['_meta']['basis_eintraege'],
                         len(json.loads(C.GLOSSARY.read_text(encoding='utf-8'))['abbreviations']))

    def test_glossar_unveraendert(self):
        self.assertEqual(self.res['glossar_sha256'], C.sha256_file(C.GLOSSARY))

    def test_stellenzahl(self):
        C.import_pipeline()
        import by_glossary
        g = by_glossary.Glossary(str(C.GLOSSARY))
        self.assertEqual(G.stellenzahl(g, 'י"ג', "כתב מרן ז\"ל סי' "), 13)
        self.assertIsNone(G.stellenzahl(g, 'י"ג', 'כתב מרן ז"ל '))


class Scan(unittest.TestCase):
    def test_konkordanz_und_belege(self):
        werk = C.load_werk()
        _, summary = A.abschnittsliste(werk)
        konk = A.lade_konkordanz(C.HERE / 'scan_konkordanz.tsv')
        ab = A.scanabgleich(werk, summary, None, konk, None, A.lade_belege(C.HERE / 'scan_belege.json'))
        self.assertEqual(ab['befunde']['FEHLER'], [])
        st = {a['key']: a for a in ab['abschnitte']}
        self.assertTrue(all(a['status'] == 'IM SCAN' for a in st.values()), [a['status'] for a in st.values()])
        self.assertEqual(st['Bereshit']['scanseiten'], [322, 323])
        self.assertEqual(st['Purim']['scanseiten'], [394])
        self.assertEqual(st['Shoftim']['scanseiten'][-1], 412)
        self.assertEqual(st['Kuntres Chut HaMeshulash']['scanseiten'][0], 346)
        # Vaera 3: Druck zaehlt ב' -> ד', belegt; Umfangsbefund nur noch Hinweis
        self.assertEqual(ab['befunde']['PRUEFEN'], [])
        self.assertTrue(any('Umfang laut Buch' in b for b in ab['befunde']['HINWEIS']))
        self.assertEqual(len(konk), 420)
        self.assertFalse([r['seq'] for r in konk if r['art'] in ('', 'Unklar')])

    def test_ot_zahl_und_reihenfolge(self):
        werk = C.load_werk()
        _, summary = A.abschnittsliste(werk)
        konk = [{'seq': 100, 'fl_id': '', 'art': 'Halakhot', 'abschnitt': 'Noach', 'ot_von': 1, 'ot_bis': 19},
                {'seq': 90, 'fl_id': '', 'art': 'Halakhot', 'abschnitt': 'Bereshit', 'ot_von': 1, 'ot_bis': 10},
                {'seq': 95, 'fl_id': '', 'art': 'Halakhot', 'abschnitt': 'Lech Lecha', 'ot_von': 1, 'ot_bis': 5},
                {'seq': 96, 'fl_id': '', 'art': 'Halakhot', 'abschnitt': 'Bechukotai', 'ot_von': 1, 'ot_bis': 2}]
        ab = A.scanabgleich(werk, summary, None, konk, 400, [])
        st = {a['key']: a['status'] for a in ab['abschnitte']}
        self.assertEqual(st['Bereshit'], 'ANZAHL ABWEICHEND')
        self.assertEqual(st['Lech Lecha'], 'REIHENFOLGE ABWEICHEND')
        self.assertTrue(any('NUR IM SCAN' in b for b in ab['befunde']['PRUEFEN']))

    def test_kopfzeile_deuten(self):
        werk = C.load_werk()
        self.assertEqual(A.deute_kopfzeile('חיי שרה  עוד יוסף חי  הלכות ש"ר', werk), ('Halakhot', 'Chayei Sara'))
        self.assertEqual(A.deute_kopfzeile('הלכות  עוד יוסף חי  חיי שרה', werk), ('Halakhot', 'Chayei Sara'))
        self.assertEqual(A.deute_kolumnentitel({'rechts': 'קנטריס', 'links': 'חוט המשולש'}, werk)[1],
                         'Kuntres Chut HaMeshulash')
        self.assertEqual(A.deute_kolumnentitel({'rechts': 'פרשת', 'links': 'בראשית'}, werk)[0], 'Derashot')
        self.assertEqual(A.deute_kopfzeile('פתיחה עוד יוסף חי ראשנה', werk), ('Derashot', ''))

    def test_kolumnentitel_aus_woertern(self):
        def w(t, x, conf=90, zeile=('1', '1', '1')):
            return {'t': t, 'x': x, 'y': 10, 'w': 60, 'h': 30, 'conf': conf, 'zeile': zeile}
        k = A.kolumnentitel([w('נח', 1100), w('עוד', 800), w('יוסף', 700), w('חי', 640), w('הלכות', 300),
                             w('ש"ר', 220), w('|', 1500, 20)])
        self.assertEqual((k['rechts'], k['links']), ('נח', 'הלכות ש"ר'))
        # Mitteltitel unleserlich: Teilung an der Seitenmitte
        k = A.kolumnentitel([w('תרומה', 1200), w('עזר', 800, 20), w('הלכות', 300), w('ש"ר', 220)], 1600)
        self.assertEqual((k['rechts'], k['links']), ('תרומה', 'הלכות ש"ר'))
        self.assertIsNone(A.kolumnentitel([w('כתב', 500)], 1600))

    def test_parascha_reihenfolge(self):
        werk = C.load_werk()
        self.assertEqual(A.deute_kolumnentitel({'rechts': 'נח לך לך זירא', 'links': "חלכות ש'ר"}, werk, 1)[1],
                         'Noach+Lech Lecha+Vayera')
        # 'וינש' liegt gleich nah an ויגש und וישב: hinter Miketz gewinnt ויגש
        pos = [k for k, _ in A.KANDIDATEN].index('Miketz')
        self.assertEqual(A.deute_kolumnentitel({'rechts': 'וינש', 'links': 'הלכות ש"ר'}, werk, pos)[1], 'Vayigash')
        # Derashot mit 'שרה' im Titel ist keine Halakhot-Seite
        self.assertEqual(A.deute_kolumnentitel({'rechts': 'פרשת', 'links': 'חיי שרה'}, werk)[0], 'Derashot')

    def test_teilzip(self):
        import io, zipfile
        with tempfile.TemporaryDirectory() as d:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w') as z:
                for i in range(1, 4):
                    z.writestr('{:04d}_FL{}.jpg'.format(i, 100 + i), bytes([i]) * 5000)
            data = buf.getvalue()
            teile = [data[i:i + 4000] for i in range(0, len(data), 4000)]
            for n, t in enumerate(teile, start=1):
                (Path(d) / 'scan.zip.{:03d}'.format(n)).write_bytes(t)
            q = A.ScanQuelle([d])
            self.assertEqual(sorted(q.seiten), [1, 2, 3])
            self.assertEqual(q.bytes_of(2), bytes([2]) * 5000)

    def test_stichwort_ausrichtung(self):
        import oyc_scan_ot as S
        soll = ['כתב', 'ועל', 'צריך', 'מוכרי', 'אם', 'מי']
        ist = ['רעש', 'כתב', 'ועל', 'סנס', 'צריד', 'מוכרי', 'כתב', 'מי']
        p = S.ausrichten(soll, ist)
        self.assertEqual(p, {0: 1, 1: 2, 2: 4, 3: 5, 5: 7})

    def test_iiif(self):
        v2 = {'sequences': [{'canvases': [{'images': [{'resource': {
            '@id': 'x', 'service': {'@id': 'https://iiif.example/IIIFv21/FL244210892'}}}]}]}]}
        v3 = {'items': [{'items': [{'items': [{'body': {
            'id': 'y', 'service': [{'id': 'https://iiif.example/iiif/3/FL1'}]}}]}]}]}
        self.assertEqual(A.iiif_seiten(v2), [(1, 'FL244210892', 'https://iiif.example/IIIFv21/FL244210892/full/full/0/default.jpg')])
        self.assertEqual(A.iiif_seiten(v3)[0][1], 'FL1')

    def test_kurzliste(self):
        self.assertEqual(A.kurzliste([1, 2, 3, 5, 7, 8]), '1-3,5,7-8')


class Schutz(unittest.TestCase):
    def test_kein_ueberschreiben_mit_englisch(self):
        with tempfile.TemporaryDirectory() as d:
            r = B.run(out=d, quiet=True)
            f = Path(r['dateien'][0])
            raw = f.read_text(encoding='utf-8-sig').replace('<en></en>', '<en><![CDATA[Translated.]]></en>', 1)
            C.write_bic_text(f, raw)
            with self.assertRaises(SystemExit):
                B.run(out=d, quiet=True)

    def test_textkorrektur_nur_mit_beleg(self):
        werk = C.load_werk()
        with self.assertRaises(SystemExit):
            C.wende_textkorrekturen(werk, [{'ref': 'Nicht 1:1', 'alt': 'x', 'neu': 'y', 'scan_seq': 1, 'grund': 'g'}])
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'tk.json'
            f.write_text(json.dumps({'korrekturen': [{'ref': 'Bereshit 2:1', 'alt': 'a', 'neu': 'b'}]}), encoding='utf-8')
            with self.assertRaises(SystemExit):
                C.lade_textkorrekturen(f)
        log = C.wende_textkorrekturen(werk, [{'ref': 'Bereshit 2:1', 'alt': 'שעדיין', 'neu': 'שעדין',
                                              'scan_seq': 99, 'grund': 'Test'}])
        self.assertEqual(len(log), 1)


if __name__ == '__main__':
    unittest.main()
