# Rav Pe’alim · שו״ת רב פעלים — Satzfreigabe-Master

*Responsen in vier Teilen mit dem Anhang Sod Yesharim* · R. Yosef Chayim von Bagdad (Ben Ish Chai) · Jerusalem 1901–1912

Erzeugt 2026-11-07 mit `produzieren.py` · Basis-Commit `058e57709737`

## Bände

| Band | Reihe | Inhalt | Master | Segmente | Seiten (2,375 / 1,95) | Abnahme | Stand |
|---|---|---|---|---:|---|---|---|
| 01 (Pilot) | SY | Sod Yesharim | `Rav_Pealim_Band_01_BILINGUAL.txt` | 698 | 578 / 477 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 02 | OC | Orach Chayim (1/3) | `Rav_Pealim_Band_02_BILINGUAL.txt` | 638 | 527 / 435 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 03 | OC | Orach Chayim (2/3) | `Rav_Pealim_Band_03_BILINGUAL.txt` | 603 | 507 / 419 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 04 | OC | Orach Chayim (3/3) | `Rav_Pealim_Band_04_BILINGUAL.txt` | 710 | 526 / 434 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 05 | YD | Yoreh Deah (1/3) | `Rav_Pealim_Band_05_BILINGUAL.txt` | 512 | 492 / 406 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 06 | YD | Yoreh Deah (2/3) | `Rav_Pealim_Band_06_BILINGUAL.txt` | 500 | 492 / 406 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 07 | YD | Yoreh Deah (3/3) | `Rav_Pealim_Band_07_BILINGUAL.txt` | 628 | 492 / 406 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 08 | EH | Even HaEzer (1/2) | `Rav_Pealim_Band_08_BILINGUAL.txt` | 545 | 546 / 451 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 09 | EH | Even HaEzer (2/2) | `Rav_Pealim_Band_09_BILINGUAL.txt` | 664 | 540 / 446 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |
| 10 | CM | Choshen Mishpat | `Rav_Pealim_Band_10_BILINGUAL.txt` | 409 | 386 / 319 | 0 Fehler, 0 Prüfen | HE satzfrei · EN offen |

Format wie Ben Ish Chai Halakha (148 × 210 mm). Ziel 600 Seiten inkl. 12 Reserve (Sod Yesharim, ca. 578 Seiten, ist ein Band), Sperre 800 Seiten. Seitenschätzung mit EN = 2.375 × HE (Responsen); mit 1,95 (Ben Ish Chai) in Klammern.

## Prüfliste

- [x] Quelle unverändert (sha256 `9f93272b88795936`), gemeinfrei (Sefaria „Public Domain“, Vorlage Jerusalem 1901–1912; `source/LIZENZ_UND_NACHWEIS.md`)
- [x] Struktur: 526 Abschnitte, 5907 Segmente; Simanim Orach Chayim 185, Yoreh Deah 169, Even HaEzer 72, Sod Yesharim 64, Choshen Mishpat 31 (erwartet laut Projektvorgabe); leere Simanim der Quelle: Volume IV, Orach Chayim 36, Volume IV, Orach Chayim 37, Volume IV, Orach Chayim 38
- [x] Mafteachot des Drucks: 487 Simanim mit Inhaltsangabe, 10 Hinweise (Druckfehler, Sammelangaben) – `out/struktur/Rav_Pealim_Mafteach.tsv`
- [x] Sod Yesharim aus den vier Teilen extrahiert und durchnummeriert (1–64), Konkordanz Teil/Abteilung/Siman ↔ Band: `out/konkordanz/Rav_Pealim_Konkordanz.tsv` (526 Zeilen)
- [x] Querverweise des Autors auf Rav Pe’alim: 42 (ANGENOMMEN 11, AUFGELOEST 13, OHNE_SIMAN 17, OHNE_TEIL 1) – `out/konkordanz/Rav_Pealim_Querverweise.tsv`
- [x] Abnahme aller Master ohne FEHLER (`rp_validate.py`)
- [x] InDesign-Skripte aus Ben Ish Chai v1.0.17 / RH v1.0.3 (Bausteine LC RH v1.0.4) reproduzierbar erzeugt
- [x] Glossar halachisch: 88838 Kürzel-Treffer, 79.1 % aufgelöst (BY-Glossar + `glossar_halacha.json` + LC-Klärungen), 2559 neue Formen (NEU·RP) mit Kontext in `out/glossar/Rav_Pealim_Glossar_NEU.json`
- [x] Glossar kabbalistisch: 62 Begriffe, 4611 Treffer in Sod Yesharim (`glossar_kabbala.json`, `out/glossar/Rav_Pealim_Glossar_Kabbala.tsv`)
- [x] Werkverzeichnis der Zitatketten: 51 Werke, 13186 Treffer; Absätze mit ≥ 4 Werken: SY 40, OC 242, YD 242, EH 147, CM 68 (`out/werke/`)
- [ ] Übersetzung nach `Rav_Pealim_VERBINDLICHE_Uebersetzungsanweisung_EN_Fassung1.0_20261107.txt` (Pilot Band 01): noch nicht begonnen

## Offene Entscheidungen

1. Bandzahl: Der Plan ergibt 10 Bände (Reihen nach Abteilungen, Ziel 600 Seiten). Neun Bände wären nur mit Bänden von ca. 566 Seiten oder mit Bänden über Abteilungsgrenzen möglich.
2. Hakdamot und Petichah (Teil I–III) stehen am Anfang von Orach Chayim (Band 02), der Kuntres Beit Tefillah (Teil III) am Ende von Orach Chayim (`gliederung.json` → reihen). Alternative: Hakdamot vor Sod Yesharim im Pilotband (+ ca. 27 Seiten, dann über dem Ziel 600).
3. Seitenplanung mit EN = 2.375 × HE (Projektvorgabe ≈ 842 HE-Zeichen je Seite). Nach den ersten übersetzten Simanim des Pilotbands messen und `rp_common.EN_EXPANSION` anpassen.
4. Glossar: `glossar_halacha.json` (79 Kürzel) und `glossar_kabbala.json` sind Vorschläge der Pipeline; die Übernahme in `glossary_he.json` entscheidet die Projektleitung (Arbeitsanleitung 1.5, Schritt 5).
5. Lizenz der englischen Übersetzung festlegen (Quelle gemeinfrei).

## InDesign

- `indesign/Rav_Pealim_Bilingual_Book_Manager_v1_0_0.jsx` · sha256 `5964166d4ebf4866` · aus `Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17-Milestone.jsx`
- `indesign/Rav_Pealim_Running_Header_Manager_v1_0_0.jsx` · sha256 `9ab24579c9dec96f` · aus `Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx`
- `indesign/Rav_Pealim_Inhaltsverzeichnis_v1_0_0.jsx` · sha256 `2f24b8fcf64faf9b` · aus `vorlage_Inhaltsverzeichnis.jsx`

Ablauf: Pilot Band 01 (Sod Yesharim) – Reiter 2 (Übersetzungsportionen) oder Speicher `uebersetzung/sy/` mit `rp_uebersetzung.py`; danach Reiter 3 (InDesign-Band) mit `…_Band_01_BILINGUAL_EN_FERTIG.txt`, Kolumnentitel-Manager v1.0.0 (Kolumnentitel = Siman), zuletzt das Inhaltsverzeichnis-Skript (neues Dokument <Band>_Inhalt.indd, mit den Inhaltsangaben der Mafteachot).

## Bandplan

```
RAV PE’ALIM · BANDPLAN (REIHEN NACH ABTEILUNGEN, FORMAT BEN ISH CHAI HALAKHA)

Quelle: Responsa Rav Pealim · Rav Pealim, Jerusalem 1901-1912 · sha256 9f93272b88795936ee47b15e449725d2968cdf70b44133a256f8c30a9ae32bbf
        5907 Segmente · 526 Abschnitte · 5 Reihen
Format: 148 × 210 mm · Keter YG 10/12 pt · Cambria 9/10,8 pt (Ben Ish Chai v1.0.17)
Kalibrierung: HE 1050 Zeichen/Seite · EN 2000 Zeichen/Seite · erwartete EN-Laenge 2.375 × HE (Responsen; Ben Ish Chai misst 1.95)
Grenzen: Ziel 600 Seiten (davon 12 Reserve) · Textseiten hoechstens 588 · absolute Sperre 800
HE-Zeichen: 4179080 ohne Nikud/Teamim (Planung) · 4179701 mit Vokalzeichen
Teilung: jede Reihe beginnt einen Band; innerhalb der Reihe gleichmaessig zwischen Simanim

Plan: 10 Baende · ca. 5086 Seiten gesamt
Band 01 · Sod Yesharim · PILOT: ca. 578 Seiten (davon 12 Reserve) · 698 Segmente · RPL-0000001 bis RPL-0000698
    סוד ישרים סימן א׳ (ח״א סי׳ א׳)  →  סוד ישרים סימן ס״ד (ח״ד סי׳ כ׳)
    Sod Yesharim, Siman 1 (Part I, Siman 1)  →  Sod Yesharim, Siman 64 (Part IV, Siman 20)
    HE 476469 Zeichen = 453.8 Seiten · EN geschaetzt 1131614 Zeichen = 565.8 Seiten · Reserve bis Ziel 600: 22 · bis Sperre 800: 222
Band 02 · Orach Chayim (1/3): ca. 527 Seiten (davon 12 Reserve) · 638 Segmente · RPL-0000699 bis RPL-0001336
    הקדמת המחבר · חלק א׳  →  אורח חיים ח״ב סימן י״ב
    Author’s Introduction · Part I  →  Orach Chayim, Part II, Siman 12
    HE 433285 Zeichen = 412.7 Seiten · EN geschaetzt 1029052 Zeichen = 514.5 Seiten · Reserve bis Ziel 600: 73 · bis Sperre 800: 273
Band 03 · Orach Chayim (2/3): ca. 507 Seiten (davon 12 Reserve) · 603 Segmente · RPL-0001337 bis RPL-0001939
    אורח חיים ח״ב סימן י״ג  →  אורח חיים ח״ג סימן י׳
    Orach Chayim, Part II, Siman 13  →  Orach Chayim, Part III, Siman 10
    HE 416537 Zeichen = 396.7 Seiten · EN geschaetzt 989276 Zeichen = 494.6 Seiten · Reserve bis Ziel 600: 93 · bis Sperre 800: 293
Band 04 · Orach Chayim (3/3): ca. 526 Seiten (davon 12 Reserve) · 710 Segmente · RPL-0001940 bis RPL-0002649
    אורח חיים ח״ג סימן י״א  →  קונטרס בית תפלה
    Orach Chayim, Part III, Siman 11  →  Kuntres Beit Tefillah
    HE 432794 Zeichen = 412.2 Seiten · EN geschaetzt 1027886 Zeichen = 513.9 Seiten · Reserve bis Ziel 600: 74 · bis Sperre 800: 274
Band 05 · Yoreh Deah (1/3): ca. 492 Seiten (davon 12 Reserve) · 512 Segmente · RPL-0002650 bis RPL-0003161
    יורה דעה ח״א סימן א׳  →  יורה דעה ח״א סימן מ״ב
    Yoreh Deah, Part I, Siman 1  →  Yoreh Deah, Part I, Siman 42
    HE 403452 Zeichen = 384.2 Seiten · EN geschaetzt 958199 Zeichen = 479.1 Seiten · Reserve bis Ziel 600: 108 · bis Sperre 800: 308
Band 06 · Yoreh Deah (2/3): ca. 492 Seiten (davon 12 Reserve) · 500 Segmente · RPL-0003162 bis RPL-0003661
    יורה דעה ח״א סימן מ״ג  →  יורה דעה ח״ג סימן ז׳
    Yoreh Deah, Part I, Siman 43  →  Yoreh Deah, Part III, Siman 7
    HE 403958 Zeichen = 384.7 Seiten · EN geschaetzt 959401 Zeichen = 479.7 Seiten · Reserve bis Ziel 600: 108 · bis Sperre 800: 308
Band 07 · Yoreh Deah (3/3): ca. 492 Seiten (davon 12 Reserve) · 628 Segmente · RPL-0003662 bis RPL-0004289
    יורה דעה ח״ג סימן ח׳  →  יורה דעה ח״ד סימן ל״ט
    Yoreh Deah, Part III, Siman 8  →  Yoreh Deah, Part IV, Siman 39
    HE 404091 Zeichen = 384.8 Seiten · EN geschaetzt 959717 Zeichen = 479.9 Seiten · Reserve bis Ziel 600: 108 · bis Sperre 800: 308
Band 08 · Even HaEzer (1/2): ca. 546 Seiten (davon 12 Reserve) · 545 Segmente · RPL-0004290 bis RPL-0004834
    אבן העזר ח״א סימן א׳  →  אבן העזר ח״ב סימן כ״א
    Even HaEzer, Part I, Siman 1  →  Even HaEzer, Part II, Siman 21
    HE 449543 Zeichen = 428.1 Seiten · EN geschaetzt 1067665 Zeichen = 533.8 Seiten · Reserve bis Ziel 600: 54 · bis Sperre 800: 254
Band 09 · Even HaEzer (2/2): ca. 540 Seiten (davon 12 Reserve) · 664 Segmente · RPL-0004835 bis RPL-0005498
    אבן העזר ח״ב סימן כ״ב  →  אבן העזר ח״ד סימן י״ג
    Even HaEzer, Part II, Siman 22  →  Even HaEzer, Part IV, Siman 13
    HE 444543 Zeichen = 423.4 Seiten · EN geschaetzt 1055790 Zeichen = 527.9 Seiten · Reserve bis Ziel 600: 60 · bis Sperre 800: 260
Band 10 · Choshen Mishpat: ca. 386 Seiten (davon 12 Reserve) · 409 Segmente · RPL-0005499 bis RPL-0005907
    חושן משפט ח״ב סימן א׳  →  חושן משפט ח״ד סימן ח׳
    Choshen Mishpat, Part II, Siman 1  →  Choshen Mishpat, Part IV, Siman 8
    HE 314408 Zeichen = 299.4 Seiten · EN geschaetzt 746719 Zeichen = 373.4 Seiten · Reserve bis Ziel 600: 214 · bis Sperre 800: 414

REIHEN
  SY  Sod Yesharim      1 Band/Baende ·    476469 HE-Zeichen · ca.   578 Seiten · Pilotband: die 64 kabbalistischen Responsen aus den Anhaengen der vier Teile, durchnummeriert 1–64 (Konkordanz zur Zaehlung des Drucks).
  OC  Orach Chayim      3 Band/Baende ·   1282616 HE-Zeichen · ca.  1560 Seiten · Orach Chayim aus den vier Teilen (185 Simanim); vorn die Hakdamot und die Petichah, am Ende der Kuntres Beit Tefillah (Teil III).
  YD  Yoreh Deah        3 Band/Baende ·   1211501 HE-Zeichen · ca.  1476 Seiten · Yoreh Deah aus den vier Teilen (169 Simanim).
  EH  Even HaEzer       2 Band/Baende ·    894086 HE-Zeichen · ca.  1086 Seiten · Even HaEzer aus den vier Teilen (72 Simanim).
  CM  Choshen Mishpat   1 Band/Baende ·    314408 HE-Zeichen · ca.   386 Seiten · Choshen Mishpat aus Teil II–IV (31 Simanim).

EMPFINDLICHKEIT
  EN-Laenge 1.95 × HE (gemessen bei Ben Ish Chai): 10 Baende · ca. 4199 Seiten · 01 477 · 02 435 · 03 419 · 04 434 · 05 406 · 06 406 · 07 406 · 08 451 · 09 446 · 10 319
  Ziel 540 statt 600 Seiten: 12 Baende (SY 2, OC 3, YD 3, EH 3, CM 1) – Sod Yesharim passt dann nicht in einen Band.
  Gesamtumfang (4179080 HE-Zeichen × 2.375 / 2000 + Reserve): ca. 5086 Seiten; eine Aufteilung in 9 Baende braeuchte Baende von ca. 566 Seiten oder Baende ueber Abteilungsgrenzen hinweg.

HINWEISE
  Master: <en_title> = Titel der Ausgabe (Siman-Zaehlung, Konkordanz zum Druck in out/konkordanz/), <en> leer; die Uebersetzung steht in uebersetzung/ und wird mit rp_uebersetzung.py zu *_EN_FERTIG.txt bzw. *_EN_STAND.txt zusammengefuehrt.
  Sod Yesharim: Simanim des Drucks Teil I 1–17, II 1–14, III 1–13, IV 1–20 → Ausgabe 1–64.
  Nicht gesetzt: Mafteachot des Drucks (gliederung.json → auslassen); leere Simanim der Quelle (Teil IV Orach Chayim 36–38).
  InDesign: indesign/Rav_Pealim_Bilingual_Book_Manager_v1_0_0.jsx (Reiter 2/3), indesign/Rav_Pealim_Running_Header_Manager_v1_0_0.jsx (Kolumnentitel = Siman) und indesign/Rav_Pealim_Inhaltsverzeichnis_v1_0_0.jsx.

Dateien:
  Rav_Pealim_Band_01_BILINGUAL.txt
  Rav_Pealim_Band_02_BILINGUAL.txt
  Rav_Pealim_Band_03_BILINGUAL.txt
  Rav_Pealim_Band_04_BILINGUAL.txt
  Rav_Pealim_Band_05_BILINGUAL.txt
  Rav_Pealim_Band_06_BILINGUAL.txt
  Rav_Pealim_Band_07_BILINGUAL.txt
  Rav_Pealim_Band_08_BILINGUAL.txt
  Rav_Pealim_Band_09_BILINGUAL.txt
  Rav_Pealim_Band_10_BILINGUAL.txt
```

## Struktur

```
RAV PE’ALIM · STRUKTUR (TEIL › ABTEILUNG › SIMAN › ABSATZ)

Quelle: Responsa Rav Pealim · Rav Pealim, Jerusalem 1901-1912 · Public Domain
        sha256 9f93272b88795936ee47b15e449725d2968cdf70b44133a256f8c30a9ae32bbf

Teil        Bereich                 Simanim  leer Absaetze HE-Zeichen
Volume I    Orach Chayim                 35     0      455     304366
Volume I    Yoreh Deah                   57     0      609     480501
Volume I    Even HaEzer                  13     0      217     177312
Volume I    Sod Yesharim                 17     0      215     149904
Volume I    Introduction                  -     -        9       2099
Volume I    Preface                       -     -       19      16641
Volume II   Orach Chayim                 65     0      665     464701
Volume II   Yoreh Deah                   41     0      351     292441
Volume II   Even HaEzer                  34     0      418     339965
Volume II   Choshen Mishpat              15     0      223     171931
Volume II   Sod Yesharim                 14     0      199     147770
Volume II   Introduction                  -     -        8       2107
Volume III  Orach Chayim                 45     0      374     283420
Volume III  Yoreh Deah                   32     0      231     167560
Volume III  Even HaEzer                  12     0      211     163941
Volume III  Choshen Mishpat               8     0       81      72118
Volume III  Sod Yesharim                 13     0      161     113719
Volume III  Introduction                  -     -        8       1841
Volume III  Kuntres Beit Tefillah         -     -       50      19034
Volume IV   Orach Chayim                 43     3      363     188407
Volume IV   Yoreh Deah                   39     0      449     270999
Volume IV   Even HaEzer                  13     0      363     212868
Volume IV   Choshen Mishpat               8     0      105      70359
Volume IV   Sod Yesharim                 20     0      123      65076

Simanim (nicht leer) je Abteilung: Orach Chayim 185 · Yoreh Deah 169 · Even HaEzer 72 · Sod Yesharim 64 · Choshen Mishpat 31
Leere Simanim der Quelle (nicht gesetzt): Volume IV, Orach Chayim 36, Volume IV, Orach Chayim 37, Volume IV, Orach Chayim 38
HE-Zeichen gesamt (ohne Nikud): 4179080
Ausgabe: 526 Abschnitte · 5907 Segmente (Absaetze) · Reihen SY 64, OC 190, YD 169, EH 72, CM 31
Nicht gesetzt: Mafteachot (493 Eintraege, Inhaltsangaben in Rav_Pealim_Mafteach.tsv / Konkordanz)
Absaetze ueber 30000 Zeichen: keine

MAFTEACH-ABGLEICH: 487 Simanim mit Inhaltsangabe, 10 Hinweise
  Volume III Orach Chayim: Eintrag "שאלה ה'," nach der Folge als Siman 8 gezaehlt
  Volume III Choshen Mishpat: Eintrag "שאלה ה'," nach der Folge als Siman 8 gezaehlt
  Volume III Sod Yesharim: Mafteach nur Sammelangabe ("י"ג תשובות על שאלות שונות בחכמת האמת:")
  Volume IV Orach Chayim: Eintrag "שאלה ה'" nach der Folge als Siman 8 gezaehlt
  Volume IV Orach Chayim: Eintrag "שאלה כ"ה" nach der Folge als Siman 28 gezaehlt
  Volume IV Orach Chayim: 40 Mafteach-Eintraege fuer 43 Simanim
  Volume IV Yoreh Deah: Mafteach-Liste ohne eigene Ueberschrift (Zaehlung beginnt neu in der vorigen Liste)
  Volume IV Yoreh Deah: 1 Simanim ohne Mafteach-Eintrag (38)
  Volume IV Yoreh Deah: 38 Mafteach-Eintraege fuer 39 Simanim
  Volume IV Sod Yesharim: Mafteach nur Sammelangabe ("כמה שאלות ע"ד הסוד:")

FEHLER: 0
```

