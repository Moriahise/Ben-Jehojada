# -*- coding: utf-8 -*-
"""
Erzeugt die InDesign-Skripte fuer Od Yosef Chai · Halakhot aus den
freigegebenen Ben-Ish-Chai-Skripten des Repositorys:

    Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17-Milestone.jsx
        -> Od_Yosef_Chai_Bilingual_Book_Manager_v1_0_0.jsx
    Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx
        -> Od_Yosef_Chai_Running_Header_Manager_v1_0_0.jsx

Jede Aenderung ist eine genaue Ersetzung mit erwarteter Trefferzahl; weicht
das Original ab, bricht der Generator ab, statt still etwas anderes zu
erzeugen. Layout, Kalibrierung (148 x 210 mm, 1050/2000 Zeichen, 540/600
Seiten), Batch-, Merge- und Layoutlogik bleiben unveraendert.

Aufruf:  python3 erzeuge_oyc_jsx.py
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import oyc_common as C  # noqa: E402

BM_SRC = C.REPO / 'Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17-Milestone.jsx'
RH_SRC = C.REPO / 'Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx'
BM_DST = HERE / 'Od_Yosef_Chai_Bilingual_Book_Manager_v1_0_0.jsx'
RH_DST = HERE / 'Od_Yosef_Chai_Running_Header_Manager_v1_0_0.jsx'
ANWEISUNG = 'Od_Yosef_Chai_VERBINDLICHE_Uebersetzungsanweisung_EN_Fassung1.0_20261103.txt'


def ersetze(text, alt, neu, anzahl=1):
    n = text.count(alt)
    if n != anzahl:
        raise SystemExit('Erwartet {}x, gefunden {}x: {!r}'.format(anzahl, n, alt[:90]))
    return text.replace(alt, neu)


BM_KOPF = '''/*
    Od Yosef Chai · Halakhot · Zweisprachiger Buchmanager v1.0.0  (03.11.2026)
    Erzeugt mit production/Od_Yosef_Chai_Halakhot/indesign/erzeuge_oyc_jsx.py aus
    Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17-Milestone.jsx.

    Gleich wie Ben Ish Chai v1.0.17: Seitenformat 148 x 210 mm, Rahmen,
    Schriften (Keter YG / Cambria), Kalibrierung, 540/600 Seiten, Einzel- und
    Bulk-Batches, BatchQueue, Merge, Layout-Abgleich, Snapshots, Farblogik.

    Anpassungen fuer Od Yosef Chai:
      - Kennungen OYH statt BIH (Segment-IDs OYH-0000001, Rahmen-Labels
        OYH_HE_FRAME/OYH_EN_FRAME, Formate "OYH · …"); passend zum
        Od Yosef Chai Kolumnentitel-Manager v1.0.0
      - Banddateien kommen ausschliesslich aus der Pipeline
        (produzieren.py / oyc_bandplan.py: Gliederung, Vokalisierung). Reiter 1
        erzeugt keine Banddateien, sondern verweist darauf.
      - Zeichenzaehlung fuer Batch-Kontingent und Seitenschaetzung ohne
        Nikud/Teamim (wie die Pipeline); sonst zaehlte vokalisierter Text
        rund 60 % zu viel.
      - Segmente mit n="0" (im Druck ungezaehlter Text: Vorwort,
        Vorbemerkung) erhalten die Synchronmarke [0] unsichtbar
        (Zeichenformat "OYH · Nullmarke"); die Zuordnung nach IDs bleibt.
      - project="Od Yosef Chai Halakhot"; Translation_Batches verweisen auf
        ''' + ANWEISUNG + '''
      - Dateinamen Od_Yosef_Chai_Halakhot_Band_XX(.indd)
*/
'''

BM_ERSETZUNGEN = [
    ('#targetengine "BenIshChaiBilingualBookManager_v117"', '#targetengine "OdYosefChaiBilingualBookManager_v100"', 1),
    ('var APP_NAME = "Ben Ish Chai · Zweisprachiger Buchmanager";',
     'var APP_NAME = "Od Yosef Chai · Zweisprachiger Buchmanager";', 1),
    ('var VERSION = "1.0.17";', 'var VERSION = "1.0.0";', 1),
    ('Ben_Ish_Chai_Band_', 'Od_Yosef_Chai_Halakhot_Band_', 4),
    ('/Ben_Ish_Chai_Bandplan.txt', '/Od_Yosef_Chai_Halakhot_Bandplan_JSX.txt', 1),
    ('/Ben_Ish_Chai_Segmentkontrolle.tsv', '/Od_Yosef_Chai_Halakhot_Segmentkontrolle_JSX.tsv', 1),
    ('project=\\"Ben Ish Chai Halakha\\"', 'project=\\"Od Yosef Chai Halakhot\\"', 3),
    ('Ben_Ish_Chai_VERBINDLICHE_Uebersetzungsanweisung_EN.txt · Fassung 1.2',
     ANWEISUNG + ' · Fassung 1.0', 1),
    ('"BEN ISH CHAI · FESTER ARBEITSABLAUF\\r\\r" +',
     '"OD YOSEF CHAI · HALAKHOT · FESTER ARBEITSABLAUF\\r\\r" +\n'
     '            "BANDDATEIEN: Die BILINGUAL-Banddateien entstehen ausschließlich mit der Pipeline '
     '(production/Od_Yosef_Chai_Halakhot: produzieren.py bzw. oyc_bandplan.py --he-quelle meine). '
     'Reiter 1 erzeugt keine Banddateien; Schritte 1–3 unten entfallen. Mit Reiter 2 (Übersetzungsportionen) '
     'oder Reiter 3 (InDesign-Band) beginnen.\\r\\r" +', 1),
    # Reiter 1: keine Banddateien aus einer Roh-TXT (Gliederung und Vokalisierung kaemen nicht mit)
    ('''        analyzeBtn.onClick = function () {
            try {''', '''        analyzeBtn.onClick = function () {
            alert(PIPELINE_HINWEIS, APP_NAME); return;
            try {''', 1),
    ('''        createFilesBtn.onClick = function () {
            try {''', '''        createFilesBtn.onClick = function () {
            alert(PIPELINE_HINWEIS, APP_NAME); return;
            try {''', 1),
    ('    var VERSION = "1.0.0";\n', '''    var VERSION = "1.0.0";
    var PIPELINE_HINWEIS = "Od Yosef Chai: Die Banddateien werden mit der Pipeline erzeugt "+
        "(production/Od_Yosef_Chai_Halakhot, produzieren.py bzw. oyc_bandplan.py --he-quelle meine). "+
        "Dort sind Abschnittsgliederung (gliederung.json), Vokalisierung und Bandplanung festgelegt.\\r\\r"+
        "Bitte die fertige Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt in Reiter 2 oder 3 wählen.";
''', 1),
    # Zeichenzaehlung ohne Nikud
    ('            next = current.heChars + visibleLength(seg.he);', '            next = current.heChars + planLength(seg.he);', 1),
    ('            current.heChars += visibleLength(seg.he);', '            current.heChars += planLength(seg.he);', 1),
    ('"\\t" + visibleLength(seg.he) + "\\toffen"', '"\\t" + planLength(seg.he) + "\\toffen"', 1),
    ('            c=visibleLength(s.he);', '            c=planLength(s.he);', 1),
    ('        var heVisible=visibleLength(heText),enVisible=visibleLength(enText);',
     '        var heVisible=planLength(heText),enVisible=visibleLength(enText);', 1),
    ('    function visibleLength(s){return trim(stripTags(s)).length;}',
     '    function visibleLength(s){return trim(stripTags(s)).length;}\n'
     '    // Od Yosef Chai: Zaehlung ohne Nikud/Teamim (U+0591–U+05C7), wie die Pipeline.\n'
     '    function planLength(s){return visibleLength(String(s||"").replace(/[\\u0591-\\u05C7]/g,""));}', 1),
    # n = 0: unsichtbare Synchronmarke
    ('            he.push("<b>["+s.number+"]</b> "+s.he);', '            he.push(segmentMarke(s.number)+s.he);', 1),
    ('                en.push("<b>["+s.number+"]</b> "+s.en);translated++;',
     '                en.push(segmentMarke(s.number)+s.en);translated++;', 1),
    ('    function composeDisplayTexts(p){', '''    // Od Yosef Chai: n=0 = im Druck ungezaehlter Text. Die Marke [0] bleibt fuer die
    // Zuordnung im Textfluss erhalten, wird aber mit "OYH · Nullmarke" unsichtbar gesetzt.
    function segmentMarke(n){return n===0?"<oyhnull>[0]</oyhnull> ":"<b>["+n+"]</b> ";}

    function composeDisplayTexts(p){''', 1),
    ('    var CHAR_SUP = "BIH · Hochgestellt";', '    var CHAR_SUP = "BIH · Hochgestellt";\n    var CHAR_NULL = "BIH · Nullmarke";', 1),
    ('su=ensureChar(doc,CHAR_SUP);', 'su=ensureChar(doc,CHAR_SUP),nm=ensureChar(doc,CHAR_NULL);', 1),
    ('        return {he:he,en:en,heHead:hh,enHead:eh,bold:b,italic:it,heInEn:hi,small:sm,sup:su};',
     '        try{nm.pointSize=0.1;nm.horizontalScale=1;nm.tracking=-1000;nm.fillColor=doc.swatches.itemByName("None");}catch(_){ }\n'
     '        return {he:he,en:en,heHead:hh,enHead:eh,bold:b,italic:it,heInEn:hi,small:sm,sup:su,nullmark:nm};', 1),
    ('        grepApplyAndStrip(story,"<b>([\\\\s\\\\S]*?)</b>",st.bold,"$1");',
     '        grepApplyAndStrip(story,"<oyhnull>([\\\\s\\\\S]*?)</oyhnull>",st.nullmark,"$1");\n'
     '        grepApplyAndStrip(story,"<b>([\\\\s\\\\S]*?)</b>",st.bold,"$1");', 1),
    # Batch-Hinweise fuer Od Yosef Chai
    ('''        out.push("<!-- Englische Parashah-Ueberschrift: uebliche englische Transliteration in <en_title>; keine Uebersetzung und keine Format-Tags. InDesign setzt 15 pt Bold. -->");''',
     '''        out.push("<!-- Englische Parashah-Ueberschrift: uebliche englische Transliteration in <en_title>; keine Uebersetzung und keine Format-Tags. InDesign setzt 15 pt Bold. -->");
        out.push("<!-- Od Yosef Chai: Sonderabschnitte nach Anweisung (הלכות שנה ראשונה = Halakhot of the First Year; קונטרס חוט המשולש = Kuntres Chut HaMeshulash; שייך להלכות פורים בפ' תצוה = Laws of Purim, belonging to Parashat Tetzaveh). n=\\"0\\" = im Druck ungezaehlter Text, normal uebersetzen. <he> ist vokalisiert; das Englische uebersetzt den Inhalt, nicht die Vokalisierung. -->");''', 1),
]

RH_KOPF = '''/*
    Od Yosef Chai · Halakhot · Kolumnentitel-Manager v1.0.0  (03.11.2026)
    Erzeugt mit production/Od_Yosef_Chai_Halakhot/indesign/erzeuge_oyc_jsx.py aus
    Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx.

    Anpassungen fuer Od Yosef Chai:
      - Kennungen OYH statt BIH (passend zum Od Yosef Chai Buchmanager v1.0.0)
      - Vorlagen "OD YOSEF CHAI · {PARASHAH}" / "עוד יוסף חי · פרשת {PARASHAH_HE}";
        Vorlage mit Jahrgang wie im Druck: "עוד יוסף חי · הלכות {YEAR_HE} · פרשת {PARASHAH_HE}"
      - Sonderabschnitt "קונטרס חוט המשולש" als eigener Kolumnentitel ohne "פרשת"
        ("עוד יוסף חי · קונטרס חוט המשולש" / "OD YOSEF CHAI · KUNTRES CHUT HAMESHULASH")
      - Der Abschnitt "שייך להלכות פורים בפ' תצוה" laeuft unter Parascha Tetzaveh
        (wie im Druck); "הלכות שנה ראשונה" setzt den Jahrgang
*/
'''

RH_ERSETZUNGEN = [
    ('#targetengine "BenIshChaiRunningHeaderManager_v103"', '#targetengine "OdYosefChaiRunningHeaderManager_v100"', 1),
    ('var APP_NAME = "Ben Ish Chai · Kolumnentitel-Manager";', 'var APP_NAME = "Od Yosef Chai · Kolumnentitel-Manager";', 1),
    ('var VERSION = "1.0.3";', 'var VERSION = "1.0.0";', 1),
    ('"BEN ISH CHAI · {PARASHAH}"', '"OD YOSEF CHAI · {PARASHAH}"', 3),
    ('"BEN ISH CHAI · {YEAR} · {PARASHAH}"', '"OD YOSEF CHAI · {YEAR} · {PARASHAH}"', 1),
    ('"בן איש חי · פרשת {PARASHAH_HE}"', '"עוד יוסף חי · פרשת {PARASHAH_HE}"', 3),
    ('"בן איש חי · הלכות {YEAR_HE} · פרשת {PARASHAH_HE}"', '"עוד יוסף חי · הלכות {YEAR_HE} · פרשת {PARASHAH_HE}"', 1),
    ('File.openDialog("Ben-Ish-Chai BILINGUAL.txt wählen"', 'File.openDialog("Od-Yosef-Chai BILINGUAL.txt wählen"', 1),
    # Sonderabschnitt Kuntres im Katalog (nach Vayeshev, vor Miketz)
    ('            ["vezot_haberakhah","וזאת הברכה","Vezot Haberakhah",["vezot haberakhah","vezot habracha","v\'zot haberakhah"]]\n        ];',
     '            ["vezot_haberakhah","וזאת הברכה","Vezot Haberakhah",["vezot haberakhah","vezot habracha","v\'zot haberakhah"]],\n'
     '            // Od Yosef Chai: Sonderabschnitt ohne "פרשת" im Kolumnentitel\n'
     '            ["kuntres_chut_hameshulash","קונטרס חוט המשולש","Kuntres Chut HaMeshulash",["kuntres chut hameshulash","kuntres chut ha-meshulash","chut hameshulash"],null,true]\n'
     '        ];', 1),
    ('            out.push({key:a[i][0],he:a[i][1],en:a[i][2],enAliases:a[i][3],heAliases:aliases});',
     '            out.push({key:a[i][0],he:a[i][1],en:a[i][2],enAliases:a[i][3],heAliases:aliases,sonder:!!a[i][5]});', 1),
    ('''        var text = tpl;
        text = replaceAllLiteral(text,"{PARASHAH}",info.enTitle||"");''',
     '''        var text = tpl;
        // Od Yosef Chai: Sonderabschnitt (Kuntres) ohne "פרשת"/"Parashat"
        var sonder = findParashahByHebrewTitle(info.heTitle||"") || findParashahByEnglishTitle(info.enTitle||"");
        if (sonder && sonder.sonder) {
            text = replaceAllLiteral(text,"פרשת {PARASHAH_HE}","{PARASHAH_HE}");
            text = replaceAllLiteral(text,"Parashat {PARASHAH}","{PARASHAH}");
            text = replaceAllLiteral(text,"PARASHAT {PARASHAH}","{PARASHAH}");
        }
        text = replaceAllLiteral(text,"{PARASHAH}",info.enTitle||"");''', 1),
]


def baue(src, dst, kopf, ersetzungen):
    text = src.read_text(encoding='utf-8')
    quelle_sha = hashlib.sha256(src.read_bytes()).hexdigest()
    for alt, neu, n in ersetzungen:
        text = ersetze(text, alt, neu, n)
    text = text.replace('BIH', 'OYH')
    if 'BIH' in text or 'Ben_Ish_Chai_Band' in text:
        raise SystemExit('Restkennung in ' + dst.name)
    zeilen = text.split('\n')
    # Kopfkommentar hinter die #target-Zeilen
    i = next(k for k, l in enumerate(zeilen) if not l.startswith('#'))
    text = '\n'.join(zeilen[:i]) + '\n\n' + kopf.replace('*/', '    Quelle sha256 {}\n*/'.format(quelle_sha), 1) + '\n'.join(zeilen[i:])
    dst.write_text(text, encoding='utf-8', newline='')
    return dst, hashlib.sha256(dst.read_bytes()).hexdigest()


def main():
    for d, s in (baue(BM_SRC, BM_DST, BM_KOPF, BM_ERSETZUNGEN), baue(RH_SRC, RH_DST, RH_KOPF, RH_ERSETZUNGEN)):
        print('{}  sha256 {}'.format(d.name, s))
    return 0


if __name__ == '__main__':
    sys.exit(main())
