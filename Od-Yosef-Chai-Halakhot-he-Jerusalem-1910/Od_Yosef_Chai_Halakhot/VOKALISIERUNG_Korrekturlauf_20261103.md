# Od Yosef Chai Halakhot – Nikud-Korrekturlauf, 03.11.2026

Grundlage: `Od_Yosef_Chai_Halakhot_2026-11-03_v6.zip`, Blob
`cb61bed7ef28be360e85961659b69df63d0f11d0`, aus Repository-Stand
`7938402a71a98845606b039914eca2e1bd981194`.
Die Arbeitsdateien und unveränderten Programme sind jetzt unter diesem
entpackten Projektordner versioniert. Die ursprüngliche ZIP-Datei bleibt erhalten.

## Ergebnis

- 46 Dateien in `vokalisierung/meine/`, 1.024 Absätze vollständig vorhanden.
- 2.802 Wörter gegenüber Nakdan geändert: 2.710 reine Plene-Normalisierungen
  und 92 kontextuelle Einzelkorrekturen; alle unter `VOK` protokolliert.
- 0 `TEXT_M`, `PLUS_M`, `MINUS_M` oder fehlende Absätze.
- Alle 1.024 `@@`-Zeilen einschließlich ihrer Zeilenenden bytegleich zur Vorlage.
- In den Arbeitsdateien ist nach Entfernung der Nikud jedes andere Zeichen
  identisch zur Vorlage: Buchstaben, Satzzeichen, Leerzeichen und Kommentare.
- Nakdan-Zeuge und Sefaria-JSON unverändert; SHA-256 der JSON-Quelle:
  `c5c83996dffd446ad3f8711361a438271e0e1e3304c4665fe4ca5b6801d70b62`.

Der Korrekturlauf umfasst die durchgängige Bereinigung der Plene-Vokalplatzierung
(z. B. `קֹודֶם` → `קוֹדֶם`, `מֻותָּר` → `מוּתָּר`) und kontextuell geprüfte
Einzelstellen, darunter `באמן` als Antwort Amen, `כללו של דבר`, `שקרן אחת מן הבגד`,
defektiv geschriebene Formen von ניצוץ sowie fehlende Vokale in gewöhnlichen Wörtern.
Alle Einzeländerungen mit Absatz, Wortnummer, vorheriger und neuer Lesung und
Begründung stehen in `vokalisierung/Vokalkorrekturen_20261103.json`.
Die 46 Vorher-/Nachher-Prüfsummen stehen dort ebenfalls.

Die technische Prüfung ist keine vollständige philologische Druckfreigabe aller
hebräischen, aramäischen und fremdsprachlichen Lesungen des Werkes. Der Bestand
bleibt für ein abschließendes sprachliches Lektorat offen; das unveränderte
Nakdan-Ergebnis ist Vergleichszeuge, keine automatische Richtigkeitsgarantie.

## Verbleibende UNVOK_M-Stellen

25 Vorkommen sind in der Kollations-TSV einzeln kommentiert:

- 24 sind Stellen-/Ordnungszahlen oder einzelne Buchstaben von Gottesnamen.
  Sie wurden bewusst nicht als gewöhnliche Wörter vokalisiert.
- `עבאיי` in Lech Lecha 5:1 ist ein historisches arabisches Kleidungswort.
  Seine genaue Lesung ist nicht sicher belegt und wurde nicht erfunden.
  Diese Stelle bleibt ausdrücklich offen.

Offensichtliche oder mögliche Schreibfehler der Basis wurden ebenfalls nicht
konsonantisch verbessert. Beispiele für spätere Prüfung gegen den Scan:
`ערף` in Bereshit 11:1, `יכיון` in Vayeshev 8:5 und `יכמסתפק` in Vayechi 16:2.
Sie gehören gegebenenfalls in `textkorrekturen.json`, außerhalb dieses Auftrags.

## Produktionsmaster und Prüfungen

Ausgeführt im entpackten Projektordner:

```bash
python3 oyc_kollation.py
python3 oyc_bandplan.py --he-quelle meine
python3 oyc_validate.py --in out/band/Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt --json out/band/Od_Yosef_Chai_Halakhot_Masterpruefung.json
```

Masterprüfung: **0 FEHLER, 0 PRÜFEN** (Modus Master, Englisch noch leer).
Zusätzlich wurden IDs, `n`, Segment- und Abschnittsfolge, Titel, Tags,
Satzzeichen und Konsonanten aller 508 Segmente gegen den bisher im Repository
liegenden Band geprüft. Nur die Nikud und die Auswahl `he_quelle="meine"`
ändern sich. 22 einschlägige vorhandene Regressionstests wurden bestanden;
ein zunächst wegen einer lokal fehlenden JSX-Abhängigkeit gescheiterter Test
bestand nach Laden dieser unveränderten Repository-Datei.

Der Master enthält 508 Segmente und 30 Satzabschnitte. Bandplanung:
ca. 475 Seiten einschließlich 12 Reserveseiten; dies ist eine Schätzung,
keine in InDesign gemessene Seitenzahl.

SHA-256 des Produktionsmasters:
`7bab635a52d732c6645a0a277c1bc42ed98bbcbb29271d30eb5758e33d5910ef`.

Ausgaben:

- `out/band/Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt`
- `out/band/Od_Yosef_Chai_Halakhot_Bandplan.txt`
- `out/band/Od_Yosef_Chai_Halakhot_Segmentkontrolle.tsv`
- `out/band/Od_Yosef_Chai_Halakhot_Masterpruefung.json`
- `out/kollation/Od_Yosef_Chai_Halakhot_Kollation_Bericht.txt`
- `out/kollation/Od_Yosef_Chai_Halakhot_Kollation.tsv` (mit Entscheidungen)
- `out/kollation/Od_Yosef_Chai_Halakhot_Kollation.html`

Master und Kollationsbericht werden auch am bisherigen Ort im übergeordneten
Repository-Ordner aktualisiert. Ein neuer Kollationslauf erzeugt die TSV neu;
die dauerhaften Korrekturbegründungen stehen zusätzlich in der JSON-Datei.

Zum Nachschlagen einzelner Lexeme wurden auch die Einträge der Akademie für
die hebräische Sprache zu
[ניצוץ](https://terms.hebrew-academy.org.il/munnah/2330_1/נִיצוֹץ) und
[נוסח](https://terms.hebrew-academy.org.il/munnah/33663_1/נֹסַח) herangezogen.
Gültige alternative Nomen-Lesungen mit Cholam wurden nicht pauschal in Schuruk geändert.
