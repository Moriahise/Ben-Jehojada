# Od Yosef Chai · Halakhot — Prüfbericht

Erzeugt 2026-11-03 mit `produzieren.py` · HE-Quelle der Banddatei: **meine**

## 1 Abschnittsliste und Scanabgleich

- JSON: 29 Abschnitte · 506 Halachot/Segmente · 1024 Absätze · 473952 Zeichen
- Scan: 420 Seiten im Inventar · Konkordanz 420 Seiten · Halakhot-Seiten im erfassten Bereich: 91
- Abgleich vollständig: ja

**FEHLER** (0)
- keine

**PRUEFEN** (0)
- keine

**HINWEIS** (10)
- Umfang laut Buch (Scan S. 8, הקדמה של המחבר נר"ו, Schlussabsatz vor der Unterschrift): nur Halakhot zu Bereshit und Shemot. Im JSON ausserhalb: Vayikra, Tzav, Bamidbar, Shoftim (90 Halachot, 52807 Zeichen) – im Scan dennoch gedruckt (S. 402–412)
- Scan S. 322: Vorwort "אלו הם ההלכות…" (Sefaria Bereshit 1:1) steht vor der Überschrift בראשית und gehört zum ganzen Halakhot-Teil; die Absätze 1:2–1:4 (כתב רבינו הרש"ש / ועל / ועל) stehen ohne Ordnungsbuchstaben vor "א' צריך" (1:5). Sefaria-Ot 1 = Vorwort + Vorbemerkung + Ot א. Entschieden 03.11.2026: im Band drei Segmente (gliederung.json).
- Scan S. 376: Kolumnentitel "וארא" falsch gedruckt; Text gehört zu Shemot.
- Scan S. 404: Kolumnentitel "במדבר" falsch gedruckt; Text gehört zu Tzav.
- Scan S. 406: Kolumnentitel "צו" falsch gedruckt; Text gehört zu Bamidbar.
- Scan S. 394: Im Druck "שייך להלכות פורים בפ' תצוה" innerhalb von Tetzaveh (א' מדינות, ב' הקורא); Sefaria führt Purim als eigenen Abschnitt. Entschieden 03.11.2026: im Band wie im Druck unter Tetzaveh (gliederung.json).
- Scan S. 413: S. 413–415 "לוח הטעיות והשמטות" (Druckfehlerverzeichnis, טעות/תיקון). Sefaria-Fassung nennt "incorporation of corrigenda" – Einarbeitung stichprobenartig gegen diese Liste prüfen; berechtigte Korrekturen nach textkorrekturen.json.
- Scan S. 412: Letzte gedruckte Ot נ"א = 51 = JSON. Ebenso Bereshit (S. 323): letzte Ot יא = 11 = JSON.
- Scan S. 311: Zweiter Buchteil (מראות יחזקאל S. 311–321, Halakhot S. 322–412, Druckfehlerverzeichnis S. 413–415) eigens foliiert: Blatt n auf Scanseite 311+2(n-1).
- Scan S. 378: Der Druck zählt in Vaera ב' (S. 378 "כתב עוד רז"ל") direkt weiter zu ד' (S. 379 "אע"ג דצריך"); ein ג' fehlt im Druck. Sefaria-Ot 3 ist deshalb leer – kein Textverlust; n = gedruckte Zählung beibehalten.

| Nr | Abschnitt | Buch | Ot | Status | Scanseiten | Seiten (erwartet) |
|---:|---|---|---:|---|---|---|
| 1 | Bereshit (פרשת בראשית) | Bereshit | 11 | IM SCAN | 322–323 | 1.5 (1.7) |
| 2 | Noach (פרשת נח) | Bereshit | 19 | IM SCAN | 323–327 | 3.8 (3.4) |
| 3 | Lech Lecha (פרשת לך לך) | Bereshit | 5 | IM SCAN | 327–327 | 0.3 (0.5) |
| 4 | Vayera (פרשת וירא) | Bereshit | 23 | IM SCAN | 327–329 | 1.8 (2.0) |
| 5 | Chayei Sara (פרשת חיי שרה) | Bereshit | 20 | IM SCAN | 329–332 | 3.0 (2.3) |
| 6 | Toldot (פרשת תולדות) | Bereshit | 11 | IM SCAN | 332–333 | 1.0 (1.8) |
| 7 | Vayetzei (פרשת ויצא) | Bereshit | 5 | IM SCAN | 333–335 | 2.0 (1.8) |
| 8 | Vayishlach (פרשת וישלח) | Bereshit | 3 | IM SCAN | 335–342 | 7.0 (7.0) |
| 9 | Vayeshev (פרשת וישב) | Bereshit | 18 | IM SCAN | 342–346 | 4.0 (4.3) |
| 10 | Kuntres Chut HaMeshulash (קונטרס חוט המשולש) | Bereshit | 107 | IM SCAN | 346–358 | 12.0 (11.8) |
| 11 | Miketz (פרשת מקץ) | Bereshit | 16 | IM SCAN | 358–363 | 5.0 (5.5) |
| 12 | Vayigash (פרשת ויגש) | Bereshit | 15 | IM SCAN | 363–368 | 5.0 (5.2) |
| 13 | Vayechi (פרשת ויחי) | Bereshit | 27 | IM SCAN | 368–373 | 5.0 (5.1) |
| 14 | Shemot (פרשת שמות) | Shemot | 11 | IM SCAN | 373–378 | 5.0 (4.5) |
| 15 | Vaera (פרשת וארא) | Shemot | 19 | IM SCAN | 378–384 | 6.0 (6.2) |
| 16 | Bo (פרשת בא) | Shemot | 6 | IM SCAN | 384–385 | 1.0 (1.2) |
| 17 | Beshalach (פרשת בשלח) | Shemot | 19 | IM SCAN | 385–388 | 3.0 (3.1) |
| 18 | Yitro (פרשת יתרו) | Shemot | 9 | IM SCAN | 388–390 | 2.0 (1.6) |
| 19 | Mishpatim (פרשת משפטים) | Shemot | 6 | IM SCAN | 390–391 | 1.0 (1.2) |
| 20 | Terumah (פרשת תרומה) | Shemot | 9 | IM SCAN | 391–393 | 2.0 (1.5) |
| 21 | Tetzaveh (פרשת תצוה) | Shemot | 12 | IM SCAN | 393–394 | 0.8 (1.4) |
| 22 | Purim (פורים) | Shemot | 2 | IM SCAN | 394–394 | 0.3 (0.2) |
| 23 | Ki Tisa (פרשת כי תשא) | Shemot | 27 | IM SCAN | 394–398 | 3.8 (4.0) |
| 24 | Vayakhel (פרשת ויקהל) | Shemot | 8 | IM SCAN | 398–399 | 1.0 (1.2) |
| 25 | Pekudei (פרשת פקודי) | Shemot | 8 | IM SCAN | 399–402 | 3.0 (2.3) |
| 26 | Vayikra (פרשת ויקרא) | Vayikra | 7 | IM SCAN | 402–403 | 1.0 (0.7) |
| 27 | Tzav (פרשת צו) | Vayikra | 15 | IM SCAN | 403–405 | 2.0 (2.1) |
| 28 | Bamidbar (פרשת במדבר) | Bamidbar | 17 | IM SCAN | 405–407 | 2.0 (1.7) |
| 29 | Shoftim (פרשת שופטים) | Devarim | 51 | IM SCAN | 407–412 | 5.5 (5.6) |

## 2 Vokalisierung und Kollation

```
OD YOSEF CHAI · HALAKHOT · KOLLATION DER VOKALISIERUNG

Basis: Od_Yosef_Chai_Halakhot_-_he_-_Jerusalem_1910.json (1024 Absaetze)
Zeuge nakdan : 1024 von 1024 Absaetzen · Konsonanten abweichend in 3 Absaetzen
Zeuge meine  : 1024 von 1024 Absaetzen · Konsonanten abweichend in 0 Absaetzen

Befunde gesamt: TEXT_N 6, UNVOK_M 25, VOK 2825

Abschnitt                    Abs. Woerter     VOK UNVOK_M  TEXT_M  TEXT_N
Bereshit                       22    1641      65       0       0       1
Noach                          38    3427      93       0       0       0
Lech Lecha                      8     444      13       1       0       0
Vayera                         30    1988      74       0       0       0
Chayei Sara                    32    2273      79       0       0       0
Toldot                         19    1880      64       0       0       0
Vayetzei                       14    1738      52       0       0       0
Vayishlach                     75    6786     179       0       0       0
Vayeshev                       41    4314      91       2       0       3
Kuntres Chut HaMeshulash      107   11669     330       0       0       0
Miketz                         52    5410     182       3       0       0
Vayigash                       58    5297     146       2       0       0
Vayechi                        54    5095     147       2       0       2
Shemot                         48    4512     204       1       0       0
Vaera                          68    6190     185       0       0       0
Bo                             16    1218      66       0       0       0
Beshalach                      38    3097      81      12       0       0
Yitro                          18    1561      50       0       0       0
Mishpatim                      14    1206      33       0       0       0
Terumah                        16    1534      75       0       0       0
Tetzaveh                       19    1463      46       0       0       0
Purim                           2     167      11       0       0       0
Ki Tisa                        43    3961     104       1       0       0
Vayakhel                       14    1217      29       0       0       0
Pekudei                        25    2330      93       0       0       0
Vayikra                        11     710      42       0       0       0
Tzav                           28    2098      64       1       0       0
Bamidbar                       25    1732      75       0       0       0
Shoftim                        89    5773     152       0       0       0

NAKDAN
  Nakdan-API https://nakdan-2-0.loadbalancer.dicta.org.il/api genre=rabbinic · unbearbeitet · 2026-11-03
  Einstellungen: genre=rabbinic, keepmetagim=true (sonst schreibt Nakdan defektiv und aendert Konsonanten)
  Dicta-Plene-Marken (Meteg auf ו/י der Plene-Schreibung): 6695 – im Vergleich ignoriert, im Satz und in der
  Vorlage "Meine Fassung" entfernt; der Nakdan-Zeuge bleibt unveraendert.
  Nutzung: Dicta-Bedingungen fuer die kommerzielle Ausgabe pruefen, Namensnennung im Impressum vorsehen.

UNVOKALISIERT (ohne Kuerzel/Zahlen mit Geresch): 25 Woerter, 13 verschieden
  ה              6×  Miketz 14:2, Shemot 4:8, Beshalach 3:4, Beshalach 3:4 …
  י              4×  Miketz 5:4, Beshalach 3:4, Beshalach 3:4, Beshalach 3:4
  ז              3×  Vayeshev 7:1, Vayechi 1:2, Tzav 3:1
  א              3×  Miketz 5:4, Beshalach 3:4, Beshalach 3:4
  עבאיי          1×  Lech Lecha 5:1
  ח              1×  Vayeshev 8:10
  ב              1×  Vayigash 2:2
  פז             1×  Vayigash 5:2
  ל              1×  Vayechi 1:2
  ד              1×  Beshalach 3:4
  ו              1×  Beshalach 3:4
  נ              1×  Beshalach 3:4
  ט              1×  Ki Tisa 23:1

Textabweichungen der Zeugen (TEXT/PLUS/MINUS) sind keine Fehler der Basis,
sondern Pruefstellen: gegen den Scan lesen; eine berechtigte Korrektur kommt
mit Scanseite und Grund nach textkorrekturen.json.
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

Quelle: 508 Segmente · 30 Abschnitte · HE-Quelle: meine
Format: 148 × 210 mm · Keter YG 10/12 pt · Cambria 9/10,8 pt (Ben Ish Chai v1.0.17)
Kalibrierung: HE 1050 Zeichen/Seite · EN 2000 Zeichen/Seite · erwartete EN-Laenge 1.95 × HE
Grenzen: Ziel 540 Seiten (davon 12 Reserve) · Textseiten hoechstens 528 · absolute Sperre 600
HE-Zeichen: 473851 Konsonantentext (Planung) · 762043 wie das JSX zaehlt (mit Vokalzeichen)

Plan: 1 Band/Baende
Band 01: ca. 475 Seiten (davon 12 Reserve) · 508 Segmente · OYH-0000001 bis OYH-0000508
    הלכות שנה ראשונה  →  פרשת שופטים
    HE 473851 Zeichen = 451.3 Seiten · EN geschaetzt 924010 Zeichen = 462.0 Seiten · massgeblich EN
    Reserve bis Ziel 540: 65 Seiten · bis Sperre 600: 125 Seiten

EMPFINDLICHKEIT
  Vokalisierter Satz mit 14 statt 12 pt Zeilenabstand (HE 900 Z./S.): 1 Band/Baende, Band 01 ca. 539 Seiten
  EN-Laenge 2.15 statt 1.95 × HE: ca. 521 Seiten
  EN-Laenge 2.44 statt 1.95 × HE: ca. 590 Seiten

GLIEDERUNG (Lektoratsentscheidungen, gliederung.json)
  Bereshit 1 geteilt (Scan S. 322: Titel 'הלכות שנה ראשונה', Vorwort 'אלו הם ההלכות…' vor der Ueberschrift 'בראשית'; danach drei Absaetze ohne Ordnungsbuchstaben, dann 'א' צריך'.):
    OYH-0000001 [0] Bereshit 1:1 · הלכות שנה ראשונה · Vorwort des Halakhot-Teils
    OYH-0000002 [0] Bereshit 1:2–4 · פרשת בראשית · Vorbemerkung zu Bereshit (ohne Ordnungsbuchstaben)
    OYH-0000003 [1] Bereshit 1:5–6 · פרשת בראשית · Ot א
  Purim unter Tetzaveh: Abschnittstitel "שייך להלכות פורים בפ' תצוה" · OYH-0000374 bis OYH-0000375 (Scan S. 394: im Druck nach Tetzaveh Ot 12 die Zeile 'שייך להלכות פורים בפ' תצוה' mit א' מדינות, ב' הקורא; danach 'פרשת כי תשא'.)
  n = 0: im Druck ungezaehlter Text; der Buchmanager setzt dafuer "[0]".

HINWEISE
  OYH-0000097 (Od Yosef Chai; Halakhot, Vayishlach 1) hat 32475 Zeichen > Batch-Kontingent 30000: wird als Einzelbatch exportiert
  Der Ben-Ish-Chai-Buchmanager v1.0.17 wuerde Vokalzeichen mitzaehlen (762043 statt 473851 Zeichen); der Od-Yosef-Chai-Buchmanager v1.0.0 zaehlt ohne Nikud und plant nicht neu (Reiter 1 gesperrt).
  Vokalisierung: 0 Absaetze ohne Zeugentext, 0 Woerter ohne uebertragene Vokale.
  Der Buchmanager laesst beim Zusammenfuehren die Zeile <planning> weg (reserializeParsedBook); die HE-Quelle steht dann nur noch im Pipeline-Master und im Quellenmanifest.
  InDesign: indesign/Od_Yosef_Chai_Bilingual_Book_Manager_v1_0_0.jsx (Reiter 2/3) und indesign/Od_Yosef_Chai_Running_Header_Manager_v1_0_0.jsx.

Dateien:
  Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt
```

