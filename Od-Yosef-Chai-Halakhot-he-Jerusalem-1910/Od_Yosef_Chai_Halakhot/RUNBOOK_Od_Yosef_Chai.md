# Od Yosef Chai · Halakhot — Runbook

Zweisprachige Ausgabe (Hebräisch → Englisch) der Halachot aus *Od Yosef Chai*
(R. Yosef Chaim, Jerusalem 1910), gesetzt im **Format und in der Bandgröße
von Ben Ish Chai Halakha**. Grundlage sind die bestehenden Werkzeuge des
Projekts:

| Baustein | verwendet für |
|---|---|
| `ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip` | `by_parse.find_abbrs`, `by_glossary.Glossary` (unverändert, direkt aus dem ZIP importiert) |
| `glossary_he.json` (Repository) | Glossarbasis; wird **nicht** automatisch verändert |
| `Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17-Milestone.jsx` | Bandgröße, Kalibrierung, Planer, Dateiform der Banddatei |
| `Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx` | Kolumnentitel (erkennt `פרשת …` in `<he_title>`) |
| Arbeitsanleitung 1.5 | Regeln 45 (Quelle unverändert), 48 (600 Seiten), Glossarpflege Schritt 5 |

## Gesamtlauf

```bash
python3 produzieren.py --scan ../../Od-Yosef-Chai-Halakhot-he-Jerusalem-1910 --scan-gesamt 420
```

Der Scan liegt im Repository als geteiltes ZIP (`…1910.zip.001` bis `.021`,
420 Seiten); das Skript liest die Teile direkt, ohne sie zusammenzusetzen.

Ergebnisse unter `out/`, Prüfbericht `out/Od_Yosef_Chai_Halakhot_Pruefbericht.md`,
Quellenmanifest mit Prüfsummen `out/Quellenmanifest.json`. Selbsttest:

```bash
python3 -m unittest test_oyc -v
```

(42 Tests; die JSX-Tests führen `parseBilingualFile`, `composeDisplayTexts` und
`planVolumes` aus dem Ben-Ish-Chai-Buchmanager sowie `parseSourceParashot` aus dem
Kolumnentitel-Manager in Node aus.)

## Schritt 1 — Abschnittsliste mit dem Scan abgleichen (`oyc_abschnitte.py`)

**Quellen.** Sefaria-JSON *Od Yosef Chai; Halakhot – he – Jerusalem, 1910*
(`source/`, sha256 `c5c83996…`), `versionSource` = NLI
`NNL_ALEPH990019337340205171`. Scan: NLI-Seitenbilder `NNNN_FLxxxxxxxxx.jpg`.

**Abschnittsliste.** `out/Od_Yosef_Chai_Halakhot_Abschnittsliste.tsv`: eine
Zeile je Halacha (Ot) mit Sefaria-Ref, Absätzen, Zeichen, fettem Stichwort und
Incipit. Struktur des JSON: 29 Abschnitte (27 Paraschot, *Purim*,
*Kuntres Chut HaMeshulash*), 507 Halachot, davon Vaera 3 leer (Zählung des Drucks, siehe unten).
Der Kuntres hat keine Ot-Gliederung (107 Absätze, je Absatz ein Segment).

**Scan-Konkordanz** (`scan_konkordanz.tsv`, Lektoratsdatei): eine Zeile je
Scanseite – Art, Abschnitt(e), Ot von/bis, Kolumnentitel, Bemerkung. Stand
03.11.2026: **alle 420 Seiten erfasst**.

| Scanseiten | Inhalt | Erfassung |
|---|---|---|
| 1–8 | Einband, Vorsatz, Titelblatt (ירושלים ע"ר), מודעה רבא, הקדמה | visuell |
| 9–310 | Derashot (Petichot, dann פרשת בראשית … וזאת הברכה) | OCR der Kolumnentitel übernommen |
| 311–321 | Anhang „מראות יחזקאל“, Bildnis des Autors | visuell |
| 322–412 | **Halakhot** (Kuntres S. 346–358) | OCR + visuell geprüft, jede Paraschagrenze am Seitenbild |
| 413–415 | „לוח הטעיות והשמטות“ (Druckfehlerverzeichnis) | visuell |
| 416–420 | leer, Etikett, Einband hinten | visuell |

Beginnt eine Parascha mitten auf der Seite, trägt die Zeile beide Abschnitte
(`Vayeshev+Kuntres Chut HaMeshulash`). Der zweite Buchteil ist eigens foliiert
(Blatt n auf Scanseite 311+2(n−1)); die Blattzahl steht in der Bemerkung.

So entstand die Konkordanz (für eine Wiederholung oder ein anderes Exemplar):

1. Kolumnentitel per OCR (Tesseract `heb`, Kopfstreifen binarisiert; Paraschot
   nur in Druckreihenfolge zugeordnet, weite Sprünge brauchen eindeutige Lesung):
   ```bash
   python3 oyc_abschnitte.py --scan <Scan> --scan-gesamt 420 --ocr
   ```
   → `out/scan/scan_konkordanz_vorschlag.tsv` (der übernommene Rohvorschlag
   liegt als `out/scan/scan_konkordanz_vorschlag_OCR.tsv` bei).
2. Vorschlag übernehmen – Zeilen ohne „OCR …“ in der Bemerkung (Lektorat)
   bleiben unberührt:
   ```bash
   python3 oyc_abschnitte.py --vorschlag-uebernehmen out/scan/scan_konkordanz_vorschlag.tsv
   ```
3. Paraschagrenzen am Seitenbild prüfen: jede Parascha beginnt mit der
   Überschrift „פרשה/פרשת …“ und Halacha „א'“. Kolumnentitel sind **nicht**
   verlässlich (Druckfehler S. 376, 404, 406).
4. Hilfsmittel `oyc_scan_ot.py`: liest die fetten Stichwörter (Quadratschrift)
   der Halakhot-Seiten und richtet sie an den Stichwörtern der 1.024
   Sefaria-Absätze aus. Ergebnis 03.11.2026: 27 % der Absätze wiedergefunden –
   genug, um Seitenbereiche je Parascha zu bestätigen, **nicht** genug für
   `ot_von`/`ot_bis`. Diese Spalten bleiben Lektorat (Ordnungsbuchstaben am
   Seitenbild ablesen).
   ```bash
   python3 oyc_scan_ot.py --scan <Scan> --seiten 322-412 --cache /tmp/ocr
   ```

Prüfbogen: `out/scan/Od_Yosef_Chai_Halakhot_Scan_Pruefbogen.html`
(Abschnitte mit Status und Seitenbereich, Kopfzeilen-Ausschnitt jeder Seite).
Ein anderes Exemplar oder fehlende Seiten lassen sich per IIIF laden
(`--iiif-manifest <URL> --seiten … --laden-nach …`; Manifest-URL im NLI-Viewer).

**Status je Abschnitt:** `IM SCAN` · `ANZAHL ABWEICHEND` (höchste Ot im Scan ≠
JSON) · `REIHENFOLGE ABWEICHEND` · `NOCH NICHT IM SCANBEREICH` · `FEHLT IM SCAN`
(nur bei vollständigem Scan) · `AUSSERHALB DES ANGEGEBENEN UMFANGS`. Dazu ein
Umfangstest: Seiten im Scan gegen die Textmenge im JSON (Ausreißer = fehlender
oder zusätzlicher Text).

**Ergebnis 03.11.2026:** alle 29 Abschnitte im Scan, Reihenfolge wie im JSON,
Seitenumfang je Abschnitt passend; 0 FEHLER, 0 PRÜFEN. Belege und Befunde
(`scan_belege.json`, im Bericht als HINWEIS):

- Die Vorrede (S. 8) nennt nur Halakhot zu Bereschit und Schemot – **gedruckt
  sind trotzdem Vayikra, Tzav, Bamidbar, Shoftim** (S. 402–412). Sie gehören
  damit zum Werk von 1910.
- S. 322: „אלו הם ההלכות …“ (Sefaria Bereshit 1:1) ist das Vorwort des ganzen
  Halakhot-Teils, 1:2–1:4 sind eine unnummerierte Vorbemerkung, „א' צריך“ (1:5)
  ist die erste gezählte Halacha. Sefaria fasst alles als Ot 1 – im Band geteilt
  (siehe Gliederung).
- Vaera: der Druck zählt ב' → ד' (kein ג'); Sefarias leere Ot 3 folgt dem
  Druck, es fehlt kein Text. `n` bleibt die gedruckte Zählung.
- Purim steht im Druck als „שייך להלכות פורים בפ' תצוה“ innerhalb Tetzaveh –
  im Band ebenso (siehe Gliederung).
- Gezählte Ot stimmen an den geprüften Enden: Bereshit יא = 11, Shoftim נ"א = 51.
- Kolumnentitel falsch gedruckt: S. 376 (וארא statt שמות), 404 (במדבר statt
  צו), 406 (צו statt במדבר).
- S. 413–415 Druckfehlerverzeichnis: Sefaria nennt „incorporation of
  corrigenda“ – stichprobenartig prüfen, Abweichungen nach `textkorrekturen.json`.

**Aktuelle Sefaria-Fassung vergleichen** (Netz nötig):
```bash
python3 oyc_abschnitte.py --laden-sefaria --vergleiche-sefaria
```

**Textkorrekturen nach Scan** (`textkorrekturen.json`, optional):
`{"korrekturen": [{"ref": "Vaera 2:4", "alt": "…", "neu": "…", "scan_seq": 312, "grund": "…"}]}`.
Pflicht sind Scanseite und Grund; `alt` muss im Absatz genau einmal vorkommen.
Die JSON-Quelle bleibt unverändert (Regel 45); alle Schritte lesen den
korrigierten Stand, das Quellenmanifest führt die Korrekturen.

## Gliederung des Bandes (`gliederung.json`)

Lektoratsentscheidungen vom 03.11.2026, angewandt in `oyc_common.build_segments`
(die Sefaria-Quelle bleibt unverändert; `build_segments(werk, gliederung={})`
liefert die reine Sefaria-Gliederung):

| Entscheidung | Segmente | Abschnittstitel |
|---|---|---|
| Bereshit Ot 1 geteilt: Vorwort des Halakhot-Teils (Sefaria 1:1) | OYH-0000001, n = 0 | הלכות שנה ראשונה |
| Vorbemerkung ohne Ordnungsbuchstaben (1:2–4) | OYH-0000002, n = 0 | פרשת בראשית |
| Ot א „צריך“ (1:5–6) | OYH-0000003, n = 1 | פרשת בראשית |
| Purim wie im Druck unter Tetzaveh | OYH-0000374–0375, n = 1, 2 | שייך להלכות פורים בפ' תצוה |

`n = 0` steht für im Druck ungezählten Text; der Buchmanager setzt dafür „[0]“.
Der Kolumnentitel-Manager erkennt „הלכות שנה ראשונה“ als Jahrgang (שנה ראשונה)
und den Purim-Abschnitt als Parascha Tetzaveh (Test). Die Datei wird geprüft:
Teile müssen alle Absätze einer Halacha genau einmal und in Reihenfolge abdecken.
Band 01 hat damit 508 Segmente (Sefaria-Gliederung: 506).

## Schritt 2 — Vokalisierung und Kollation (`oyc_nakdan.py`, `oyc_kollation.py`)

**Stand 03.11.2026:** Nakdan über alle 1.024 Absätze gelaufen
(`nakdan-2-0.loadbalancer.dicta.org.il/api`, `genre=rabbinic`, gut 5 Minuten),
**0 Absätze mit Konsonantenabweichung**. Vorlage „Meine Fassung“ angelegt
(`vokalisierung/meine/`, noch identisch mit Nakdan). Kollation: 32 Wörter ohne
Vokale (einzelne Buchstaben ohne Geresch, Fremdwörter wie „טיליגראף“), Liste im
Bericht. Vokalisierte Probe-Banddatei: `out/probe_nakdan/band/`.

Wichtig zur Nakdan-Einstellung: Mit `keepmetagim=false` schreibt Nakdan
defektiv („קודם“ → „קֹדֶם“) und ändert Konsonanten. Deshalb `keepmetagim=true`;
Dicta markiert dann Lesemütter der Plene-Schreibung mit Meteg auf ו/י
(„קֹוֽדֶם“, 6.695 Stellen). Der Nakdan-Zeuge bleibt so gespeichert; im Vergleich
zählt die Marke nicht, im Satz und in der Vorlage wird sie entfernt
(`oyc_common.ohne_plene_marke`). Das Sicherheitskennzeichen von Nakdan
(`fconfident`) ist als Prüfliste unbrauchbar (79 % der Wörter „unsicher“).
API-Antworten liegen in `vokalisierung/nakdan_cache/` (nicht im Repository);
ein erneuter Lauf setzt dort an.

**Weiter:** `vokalisierung/meine/*.txt` durchsehen und korrigieren (nur Vokale;
`@@`-Zeilen nicht ändern), dann `python3 oyc_kollation.py` – `VOK` zeigt jede
Abweichung von Nakdan, `TEXT_M` jede versehentliche Konsonantenänderung. Danach
den Produktionsmaster mit `python3 oyc_bandplan.py --he-quelle meine`.
Dicta-Nutzungsbedingungen für die kommerzielle Ausgabe prüfen und die
Namensnennung im Impressum vorsehen.

Zwei getrennte Zeugen, nie vermischt:

| Zeuge | Ordner | Inhalt |
|---|---|---|
| Nakdan | `vokalisierung/nakdan/` | automatische Vokalisierung, unbearbeitet |
| Meine Fassung | `vokalisierung/meine/` | eigene, von Hand vokalisierte/korrigierte Fassung |

Format beider: Markerdateien `@@Ref@@` + Absatztext (Nakdan lässt lateinische
Zeichen unverändert).

```bash
python3 oyc_nakdan.py export                 # vokalisierung/export/*.txt (≤ 15.000 Zeichen je Datei)
#   → in https://nakdanpro.dicta.org.il vokalisieren, Ergebnis als TXT sichern
python3 oyc_nakdan.py import --zeuge nakdan ~/Downloads/OYC_*.txt
#   oder automatisch (Netz zu Dicta nötig):  python3 oyc_nakdan.py api --genre rabbinic
python3 oyc_nakdan.py vorlage                # legt meine/ einmalig aus nakdan/ an, überschreibt nie
#   → vokalisierung/meine/*.txt bearbeiten
python3 oyc_kollation.py                     # out/kollation/…
```

Die Kollation richtet jeden Zeugen wortweise am Konsonantenskelett der Basis
aus und meldet: `VOK` (Meine ≠ Nakdan bei gleichen Konsonanten – die
eigentliche Kollation), `UNVOK_M` (noch ohne Vokale), `TEXT_/PLUS_/MINUS_`
(Konsonanten weichen ab → gegen Scan prüfen), `FEHLT_`. Spalte `entscheidung`
in der TSV ist für das Lektorat.

In die Banddatei übernimmt `--he-quelle meine` **nur Vokalzeichen** auf die
Konsonanten der Basis; `<b>`, Satzzeichen und Gershajim der Basis bleiben.
Konsonantische Verbesserungen kommen ausschließlich über `textkorrekturen.json`.

## Schritt 3 — Glossar aus Ben Jehojada (`oyc_glossar.py`)

Kürzelerkennung und -auflösung exakt wie in der BY-Pipeline v3.2.1, mit der
neuesten `glossary_he.json` des Repositorys. Ergebnis `out/glossar/`:

- `…_GLOSSAR.tsv` — Übersetzerhilfe; Spalte `status`:
  `UEBERNOMMEN` (kuratierter BY-Eintrag) · `ABGELEITET` (Präfix/Buchstabe) ·
  `ZAHLWERT` · `STELLENZAHL` (Zahl hinter סי'/דף/ס"ק …, OYC-Erweiterung, keine Fußnote) ·
  **`NEU`** (neuer Terminus); Spalte `neu_stamm` fasst Präfixformen zusammen
  (בש"ץ → ש"ץ); Spalte `hinweis` aus `kontextregeln.json`
  (z. B. רז"ל vor שער הכוונות = רבינו ז"ל, der Ari).
- `…_Glossar_NEU.json` — alle neuen Termini mit Stellen und Kontexten, `he`/`en` leer.
- `…_Geresch_Kuerzel.tsv` — Kürzel mit einfachem Geresch (סי', הנז'), die der
  BY-Mechanismus nicht erfasst.

Neue Termini werden nach Prüfung **mit Beleg** in die `glossary_he.json` des
Repositorys übernommen (Arbeitsanleitung 1.5, Schritt 5; `_meta.stand`:
„Od Yosef Chai Halakhot“). Halachische Werktitel (ש"ץ = שלמי צבור, כנה"ג,
ברכ"י, מג"א …) und Zahlen sind hier häufiger als im Ben Jehojada.

## Schritt 4 — Bandplan mit der Bandgröße von Ben Ish Chai Halakha (`oyc_bandplan.py`)

Kalibrierung und Planer 1:1 aus dem Ben-Ish-Chai-Buchmanager v1.0.17
(Test vergleicht mit dem JSX): 148 × 210 mm, HE 1050 Z./S., EN 2000 Z./S.,
Expansion 1,95, Ziel 540 Seiten inkl. 12 Reserve, Sperre 600.

```bash
python3 oyc_bandplan.py                       # Planungsstand (unvokalisiert)
python3 oyc_bandplan.py --he-quelle meine     # Produktionsmaster nach abgeschlossener Kollation
```

Banddatei `out/band/Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt` in der
Dateiform des BIC-Buchmanagers (`<section><he_title>פרשת …</he_title><en_title></en_title>`,
`<segment id="OYH-0000001" n="1"><he>…</he><en></en>`); Segment = eine Halacha,
Absätze durch Zeilenwechsel getrennt wie die Chapter-Blöcke des Ben Ish Chai,
`n` = Sefaria-Ot. Dazu `…_Bandplan.txt` und `…_Segmentkontrolle.tsv`.

Die Banddatei wird mit dem Od-Yosef-Chai-Buchmanager geladen (Schritt 5),
**nicht** im Reiter 1 neu geplant. Die Zeile `<planning … he_quelle="…">` nennt die
HE-Quelle (basis / nakdan / meine); übersetzt wird nur ein Master mit `meine`.

Ein bereits übersetzter Master wird nie überschrieben (Abbruch).

## Schritt 5 — InDesign (`indesign/`)

| Skript | Zweck |
|---|---|
| `Od_Yosef_Chai_Bilingual_Book_Manager_v1_0_0.jsx` | Band aufbauen, Übersetzungsbatches, Merge, Layout-Abgleich |
| `Od_Yosef_Chai_Running_Header_Manager_v1_0_0.jsx` | Kolumnentitel und Seitenzahlen |
| `erzeuge_oyc_jsx.py` | erzeugt beide aus den Ben-Ish-Chai-Skripten (v1.0.17 / v1.0.3) |

Beide sind aus den Ben-Ish-Chai-Skripten erzeugt; Layout, Kalibrierung,
Batch-, Merge- und Layoutlogik sind unverändert. Anpassungen: Kennungen `OYH`
statt `BIH` (eigene InDesign-Labels und Formate, keine Kollision mit
Ben-Ish-Chai-Dokumenten), Reiter 1 erzeugt keine Banddateien (Pipeline),
Zählung ohne Nikud, `n="0"` ohne sichtbare Nummer, Translation_Batches verweisen
auf die Od-Yosef-Chai-Übersetzungsanweisung; Kolumnentitel „עוד יוסף חי · פרשת …“
bzw. „OD YOSEF CHAI · …“, Kuntres mit eigenem Kopf ohne „פרשת“, Purim unter
Tetzaveh. Getestet in Node mit dem echten Skriptcode (Banddatei lesen, Marke [0],
Bandplan, Kolumnentitel).

Ablauf in InDesign (Schriften Keter YG Medium, Cambria Regular installiert):

1. Beide `.jsx` in den InDesign-Skripteordner legen; Titelzeile muss
   „Od Yosef Chai · Zweisprachiger Buchmanager v1.0.0“ zeigen.
2. Reiter 2 · Übersetzungsportionen: Banddatei
   `Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt` wählen → Einzel- oder
   Bulk-Batches exportieren (12 Segmente / 30.000 Zeichen).
3. Übersetzen nach `Od_Yosef_Chai_VERBINDLICHE_Uebersetzungsanweisung_EN_Fassung1.0_20261103.txt`
   (Prompt: `PROMPT_Uebersetzung_Od_Yosef_Chai.txt`), prüfen mit `oyc_validate.py`.
4. Reiter 2: `_EN_FERTIG`-Dateien nach IDs zusammenführen (Einzel/Bulk).
5. Reiter 3 · InDesign-Band: dieselbe Banddatei wählen → „Neuen InDesign-Band
   erstellen“ → `Od_Yosef_Chai_Halakhot_Band_01.indd` (148 × 210 mm).
6. Nach dem Layout: Kolumnentitel-Manager, Vorlage „עוד יוסף חי · פרשת {PARASHAH_HE}“
   oder wie im Druck „עוד יוסף חי · הלכות {YEAR_HE} · פרשת {PARASHAH_HE}“.

Schritt 5 erst mit freigegebenem Master (`he_quelle="meine"`, Kollation
abgeschlossen); für Satzproben kann die Datei aus `out/probe_nakdan/band/` dienen.

## Übersetzung

- Anweisung: `Od_Yosef_Chai_VERBINDLICHE_Uebersetzungsanweisung_EN_Fassung1.0_20261103.txt`
  (aus Ben Yehoyada 1.3 abgeleitet; ohne Kopfband, Lemma und Fußnoten; Tabelle
  der englischen Abschnittstitel; Kürzel im Fließtext nach Glossar-Status).
- Prompt: `PROMPT_Uebersetzung_Od_Yosef_Chai.txt` (ganzer Band oder ein Batch).
- Abnahme: `python3 oyc_validate.py --in <…_EN_FERTIG.txt> --gegen <Master> --json pruefung.json`
  – 0 FEHLER ist Bedingung (IDs, n, Reihenfolge, `<he>`, Überschriften,
  gefüllte Felder, Tags, Gottesnamen, Quellenpräfixe); PRÜFEN-Zeilen ansehen.

## Offene Punkte für das Lektorat

1. `ot_von`/`ot_bis` je Halakhot-Seite am Seitenbild ablesen (Ordnungsbuchstaben); dann prüft der Abgleich die Ot-Zahl jeder Parascha.
2. Druckfehlerverzeichnis S. 413–415 gegen den Sefaria-Text prüfen.
3. Meine Fassung (`vokalisierung/meine/`) durchsehen und korrigieren; Kollation abschließen; dann Master mit `--he-quelle meine`.
4. Dicta-Nutzungsbedingungen (kommerzielle Ausgabe) klären, Namensnennung im Impressum.
5. Neue Glossar-Termini kuratieren.
6. Vayishlach 1 (32.475 Zeichen) liegt über dem Batch-Kontingent von 30.000 – wird als Einzelbatch exportiert.
