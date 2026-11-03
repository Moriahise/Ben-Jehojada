# Od Yosef Chai · Halakhot — Prüfbericht

Erzeugt 2026-11-03 mit `produzieren.py` · HE-Quelle der Banddatei: **basis**

## 1 Abschnittsliste und Scanabgleich

- JSON: 29 Abschnitte · 506 Halachot/Segmente · 1024 Absätze · 473952 Zeichen
- Scan: 25 Seiten im Inventar · Konkordanz 25 Seiten · Halakhot-Seiten im erfassten Bereich: 0
- Abgleich vollständig: nein

**FEHLER** (0)
- keine

**PRUEFEN** (2)
- Umfang laut Buch (Scan S. 8, הקדמה של המחבר נר"ו, Schlussabsatz vor der Unterschrift): nur Halakhot zu Bereshit und Shemot. Im JSON ausserhalb: Vayikra, Tzav, Bamidbar, Shoftim (90 Halachot, 52807 Zeichen) – Herkunft im Scan pruefen
- Vaera: Ot 3 ist in Sefaria leer – Text im Scan suchen

**HINWEIS** (1)
- Gesamtseitenzahl des Digitalisats nicht angegeben (--scan-gesamt); "fehlt" wird deshalb nicht festgestellt.

| Nr | Abschnitt | Buch | Ot | Status |
|---:|---|---|---:|---|
| 1 | Bereshit (פרשת בראשית) | Bereshit | 11 | NOCH NICHT IM SCANBEREICH |
| 2 | Noach (פרשת נח) | Bereshit | 19 | NOCH NICHT IM SCANBEREICH |
| 3 | Lech Lecha (פרשת לך לך) | Bereshit | 5 | NOCH NICHT IM SCANBEREICH |
| 4 | Vayera (פרשת וירא) | Bereshit | 23 | NOCH NICHT IM SCANBEREICH |
| 5 | Chayei Sara (פרשת חיי שרה) | Bereshit | 20 | NOCH NICHT IM SCANBEREICH |
| 6 | Toldot (פרשת תולדות) | Bereshit | 11 | NOCH NICHT IM SCANBEREICH |
| 7 | Vayetzei (פרשת ויצא) | Bereshit | 5 | NOCH NICHT IM SCANBEREICH |
| 8 | Vayishlach (פרשת וישלח) | Bereshit | 3 | NOCH NICHT IM SCANBEREICH |
| 9 | Vayeshev (פרשת וישב) | Bereshit | 18 | NOCH NICHT IM SCANBEREICH |
| 10 | Kuntres Chut HaMeshulash (קונטרס חוט המשולש) | Bereshit | 107 | NOCH NICHT IM SCANBEREICH |
| 11 | Miketz (פרשת מקץ) | Bereshit | 16 | NOCH NICHT IM SCANBEREICH |
| 12 | Vayigash (פרשת ויגש) | Bereshit | 15 | NOCH NICHT IM SCANBEREICH |
| 13 | Vayechi (פרשת ויחי) | Bereshit | 27 | NOCH NICHT IM SCANBEREICH |
| 14 | Shemot (פרשת שמות) | Shemot | 11 | NOCH NICHT IM SCANBEREICH |
| 15 | Vaera (פרשת וארא) | Shemot | 19 | NOCH NICHT IM SCANBEREICH |
| 16 | Bo (פרשת בא) | Shemot | 6 | NOCH NICHT IM SCANBEREICH |
| 17 | Beshalach (פרשת בשלח) | Shemot | 19 | NOCH NICHT IM SCANBEREICH |
| 18 | Yitro (פרשת יתרו) | Shemot | 9 | NOCH NICHT IM SCANBEREICH |
| 19 | Mishpatim (פרשת משפטים) | Shemot | 6 | NOCH NICHT IM SCANBEREICH |
| 20 | Terumah (פרשת תרומה) | Shemot | 9 | NOCH NICHT IM SCANBEREICH |
| 21 | Tetzaveh (פרשת תצוה) | Shemot | 12 | NOCH NICHT IM SCANBEREICH |
| 22 | Purim (פורים) | Shemot | 2 | NOCH NICHT IM SCANBEREICH |
| 23 | Ki Tisa (פרשת כי תשא) | Shemot | 27 | NOCH NICHT IM SCANBEREICH |
| 24 | Vayakhel (פרשת ויקהל) | Shemot | 8 | NOCH NICHT IM SCANBEREICH |
| 25 | Pekudei (פרשת פקודי) | Shemot | 8 | NOCH NICHT IM SCANBEREICH |
| 26 | Vayikra (פרשת ויקרא) | Vayikra | 7 | AUSSERHALB DES ANGEGEBENEN UMFANGS |
| 27 | Tzav (פרשת צו) | Vayikra | 15 | AUSSERHALB DES ANGEGEBENEN UMFANGS |
| 28 | Bamidbar (פרשת במדבר) | Bamidbar | 17 | AUSSERHALB DES ANGEGEBENEN UMFANGS |
| 29 | Shoftim (פרשת שופטים) | Devarim | 51 | AUSSERHALB DES ANGEGEBENEN UMFANGS |

## 2 Vokalisierung und Kollation

```
OD YOSEF CHAI · HALAKHOT · KOLLATION DER VOKALISIERUNG

Basis: Od_Yosef_Chai_Halakhot_-_he_-_Jerusalem_1910.json (1024 Absaetze)
Zeuge nakdan : 0 von 1024 Absaetzen · Konsonanten abweichend in 0 Absaetzen
Zeuge meine  : 0 von 1024 Absaetzen · Konsonanten abweichend in 0 Absaetzen

Noch kein Zeuge vorhanden. Ablauf:
  1. python3 oyc_nakdan.py export   -> vokalisierung/export/*.txt
  2. Dateien in Nakdan Pro vokalisieren (oder: python3 oyc_nakdan.py api)
  3. python3 oyc_nakdan.py import --zeuge nakdan <Dateien>
  4. python3 oyc_nakdan.py vorlage  -> vokalisierung/meine/ bearbeiten
  5. python3 oyc_kollation.py
```

## 3 Glossar (Basis Ben Jehojada)

```
OD YOSEF CHAI · HALAKHOT · GLOSSAR (BASIS: BEN JEHOJADA)

Glossar: glossary_he.json · 289 Eintraege · sha256 d2284d4b84f4722419e35ee1b7e35360cb16c2a7668630621c22b7f1fbc5694a
Pipeline: ben-yehoyada-pipeline v3.2.1 (by_parse.find_abbrs, by_glossary.Glossary)

Kuerzel (Gershajim) gesamt: 8011 Treffer · 1198 verschiedene
aufgeloest mit BY-Glossar: 5295 Treffer = 66.1 %
Zahlen hinter Stellenangaben (STELLENZAHL, OYC-Erweiterung, keine Fussnote): 408
nach Mechanismus: UEBERNOMMEN 3724, NEU 2308, ABGELEITET 1468, STELLENZAHL 408, ZAHLWERT 79
BY-Eintraege im Werk benutzt: 179 von 289
Status (verschiedene Kuerzel): NEU 585, ABGELEITET 276, UEBERNOMMEN 165, STELLENZAHL 96, STELLENZAHL+NEU 31, UEBERNOMMEN+ZAHLWERT 13, ZAHLWERT+STELLENZAHL+NEU 13, ZAHLWERT+NEU 7, ZAHLWERT 6, ZAHLWERT+STELLENZAHL 3, UEBERNOMMEN+ZAHLWERT+NEU 1, ABGELEITET+ZAHLWERT 1, ABGELEITET+NEU 1

NEUE TERMINI nach Stamm (im BY-Glossar nicht aufloesbar; Praefixformen zusammengefasst), haeufigste 40:
    92  או"א       Bereshit 1:6           לאו"א דאו"א ואו"א ומאו"א מאו"א שאו"א
    89  ג"כ        Bereshit 5:1           דג"כ ובג"כ וג"כ
    85  יו"ט       Vayeshev 17:2          ביו"ט ויו"ט ליו"ט וביו"ט כיו"ט
    72  אע"ג       Lech Lecha 1:2         ואע"ג דאע"ג
    67  ע"ד        Bereshit 6:1           וע"ד
    54  ש"ץ        Lech Lecha 2:1         בש"ץ הש"ץ שהש"ץ להש"ץ לש"ץ
    47  עכ"ז       Bereshit 4:1           ועכ"ז שעכ"ז
    46  ע"ג        Bereshit 1:5           בע"ג וע"ג שע"ג
    45  י"ג        Chayei Sara 1:1        הי"ג וי"ג בי"ג די"ג לי"ג והי"ג ולי"ג
    44  ע"פ        Noach 10:1             בע"פ שבע"פ דע"פ וע"פ שע"פ
    35  ב"פ        Bereshit 1:6           
    34  זוה"ק      Vayetzei 5:1           בזוה"ק ובזוה"ק
    32  י"ח        Bereshit 1:5           הי"ח שבי"ח
    31  ג"פ        Toldot 6:2             
    28  י"א        Noach 19:3             וי"א די"א הי"א
    28  תש"ר       Bereshit 6:1           לתש"ר בתש"ר התש"ר ותש"ר שהתש"ר
    26  תש"י       Bereshit 6:1           התש"י בתש"י לתש"י
    23  ז"ס        Kuntres Chut HaMeshulash 11 וז"ס
    23  כנז"ל      Kuntres Chut HaMeshulash 86 וכנז"ל
    22  מג"א       Chayei Sara 3:7        המג"א והמג"א למג"א
    22  ארז"ל      Lech Lecha 1:1         וארז"ל דארז"ל שארז"ל
    20  ר"ז        Noach 8:1              לר"ז
    19  כ"ע        Chayei Sara 3:7        לכ"ע דכ"ע
    19  ע"ק        Kuntres Chut HaMeshulash 13 לע"ק מע"ק בע"ק
    19  יוה"כ      Vayeshev 11:2          ביוה"כ ויוה"כ
    18  כנה"ג      Toldot 2:1             בכנה"ג
    18  א"ק        Kuntres Chut HaMeshulash 4 דא"ק
    18  י"ב        Noach 9:1              לי"ב בי"ב וי"ב
    18  מ"ע        Bereshit 1:2           שמ"ע
    17  יהר"מ      Kuntres Chut HaMeshulash 4 ויהר"מ
    15  זא"ז       Chayei Sara 6:1        בזא"ז
    14  כה"ג       Noach 19:6             בכה"ג מכה"ג
    14  ב"ש        Vayeshev 17:2          בב"ש וב"ש
    14  ט"ז        Vayetzei 3:2           והט"ז הט"ז
    13  בפ"ע       Vayera 9:1             
    13  חת"ך       Vayigash 8:1           
    13  ברכ"י      Lech Lecha 2:1         בברכ"י וברכ"י
    13  קי"ל       Bereshit 1:5           דקי"ל וקי"ל
    12  יה"ר       Kuntres Chut HaMeshulash 32 ויה"ר
    12  חס"ל       Noach 5:1              בחס"ל וחס"ל
  … insgesamt 638 neue Formen / 428 Staemme, vollstaendig in Od_Yosef_Chai_Halakhot_Glossar_NEU.json

KONTEXT PRUEFEN (BY-Lesart im halachischen Zitierkontext fraglich):
  יו"ד       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (12x); vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (10x)
  בש"ע       vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (17x)
  רז"ל       vor lurianischem Werktitel meist 'רבינו ז"ל' (der Ari), nicht 'unsere Rabbinen' (16x)
  וא"ו       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (10x); vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (3x)
  ביו"ד      vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (6x)
  כ"ד        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (5x)
  ע"ב        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (3x); vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (2x)
  פ"ה        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (4x)
  ומ"ד       vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (3x)
  בשה"ט      vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (3x)
  מ"ד        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (2x)
  עכ"ל       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (2x)
  ב"ן        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ע"ש        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ע"א        vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  מ"מ        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ש"ס        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  עכ"ד       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  הש"ע       vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  כמ"ש       vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  תי"ו       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  א"ס        vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  ע"ה        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  קי"ט       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ק"ך        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ס"ד        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ע"ז        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  אבי"ע      vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  דע"ז       vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  נו"ן       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  בהגה"ה     vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  נ"ו        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  בב"ק       vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  וביו"ד     vor Stellenangabe: evtl. Werktitel statt Allgemeinbegriff (1x)
  רע"ו       hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)
  ס"ט        hinter Stellenangabe: wahrscheinlich Zahl, BY-Lesart fraglich (1x)

GERESCH-KUERZEL (vom BY-Mechanismus nicht erfasst), haeufigste 15:
   384  וכו'     im BY-Glossar: ja
   174  הנז'     im BY-Glossar: nein
   133  סי'      im BY-Glossar: nein
    71  וכנז'    im BY-Glossar: nein
    44  כנז'     im BY-Glossar: nein
    29  בסי'     im BY-Glossar: nein
    25  לה'      im BY-Glossar: nein
    19  בגי'     im BY-Glossar: nein
    18  בה'      im BY-Glossar: nein
    17  בפ'      im BY-Glossar: nein
    13  בחי'     im BY-Glossar: nein
    12  הא'      im BY-Glossar: nein
     9  הד'      im BY-Glossar: nein
     9  הב'      im BY-Glossar: nein
     9  והב'     im BY-Glossar: nein
```

## 4 Bandplan (Bandgröße Ben Ish Chai Halakha)

```
OD YOSEF CHAI · HALAKHOT · BANDPLAN (BANDGROESSE BEN ISH CHAI HALAKHA)

Quelle: 506 Segmente · 29 Abschnitte · HE-Quelle: basis
Format: 148 × 210 mm · Keter YG 10/12 pt · Cambria 9/10,8 pt (Ben Ish Chai v1.0.17)
Kalibrierung: HE 1050 Zeichen/Seite · EN 2000 Zeichen/Seite · erwartete EN-Laenge 1.95 × HE
Grenzen: Ziel 540 Seiten (davon 12 Reserve) · Textseiten hoechstens 528 · absolute Sperre 600
HE-Zeichen: 473853 Konsonantentext (Planung) · 473952 wie das JSX zaehlt (mit Vokalzeichen)

Plan: 1 Band/Baende
Band 01: ca. 475 Seiten (davon 12 Reserve) · 506 Segmente · OYH-0000001 bis OYH-0000506
    פרשת בראשית  →  פרשת שופטים
    HE 473853 Zeichen = 451.3 Seiten · EN geschaetzt 924014 Zeichen = 462.0 Seiten · massgeblich EN
    Reserve bis Ziel 540: 65 Seiten · bis Sperre 600: 125 Seiten

EMPFINDLICHKEIT
  Vokalisierter Satz mit 14 statt 12 pt Zeilenabstand (HE 900 Z./S.): 1 Band/Baende, Band 01 ca. 539 Seiten
  Ohne die Abschnitte ausserhalb des im Vorwort genannten Umfangs (Vayikra, Tzav, Bamidbar, Shoftim): ca. 423 Seiten
  EN-Laenge 2.15 statt 1.95 × HE: ca. 521 Seiten
  EN-Laenge 2.44 statt 1.95 × HE: ca. 590 Seiten

HINWEISE
  OYH-0000095 (Od Yosef Chai; Halakhot, Vayishlach 1) hat 32475 Zeichen > Batch-Kontingent 30000: wird als Einzelbatch exportiert
  Der Buchmanager zaehlt Vokalzeichen mit (473952 statt 473853 Zeichen). Banddateien deshalb aus dieser Planung verwenden, nicht im Reiter 1 des JSX neu planen.
  HE-Quelle "basis": Planungsstand. Der Produktionsmaster entsteht nach abgeschlossener Kollation mit --he-quelle meine; <he> ist danach geschuetzt.
  Der Buchmanager schreibt beim Zusammenfuehren project="Ben Ish Chai Halakha" und laesst <planning> weg (reserializeParsedBook); fuer IDs und Text ohne Belang.

Dateien:
  Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt
```

