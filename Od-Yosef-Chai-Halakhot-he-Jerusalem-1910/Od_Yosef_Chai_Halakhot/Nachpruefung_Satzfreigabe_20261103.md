# Sprachliche Satzfreigabe – Nachprüfung vom 03.11.2026

**Entscheidung: vollständige sprachliche Satzfreigabe nicht erteilt.**

Die Nachprüfung des Stands `d18e2dfd40f12160b2809f70f5cd29a30dfc3f30`
hat weitere Nikud-Fehler und sechs am Druck belegte Textfehler ergeben.
Die bisherige Vorgabe lautet ausdrücklich „nur die Vokale“ und verbietet damit
die für diese sechs Stellen nötigen Buchstabenänderungen.
Ein technisch fehlerfrei erzeugter Master ist unter diesen Umständen noch
kein sprachlich freigegebener Drucktext.

## Bereits ausgeführte Nikud-Korrekturen

27 weitere Wortvorkommen in 15 Dateien wurden korrigiert:

- `האמן`, `ובאמן`, `לאמן` in den besprochenen Gebetsantworten als Amen,
  nicht als Handwerker oder als Verb „trainieren“.
- Nomen `נוסח` an 21 Stellen mit fälschlichem Dagesch im Samech bzw.
  passivischer Vokalisierung; vorhandene gültige Cholam-Nomen bleiben erhalten.
- `וחיותינו` in Vayeshev 8:5 als Lebensunterhalt/Lebenskraft, nicht als „unsere Tiere“.

Die Änderungen stehen einzeln in `vokalisierung/Nachpruefung_20261103.json`.
Das kumulative Protokoll `vokalisierung/Vokalkorrekturen_20261103.json`
enthält jetzt den aktuellen Stand und die aktualisierten Dateiprüfsummen.

## Am Originaldruck belegte Textkorrekturen

Die folgende Tabelle gibt **Konsonanten** wieder. Diese Änderungen wurden
vorbereitet, aber nicht in Quelle, Zeugen oder Produktionsmaster angewendet.

| Stelle | Scanseite | Im Digitaltext | Im Druck | Befund |
|---|---:|---|---|---|
| Bereshit 11:1 | 323 | `ערף` | `ערך` | Wörterbucheintrag: בערוך ערך עטף. |
| Vayeshev 8:5 | 344 | `החסר הזה` | `החסד הזה` | Gemeint ist der Chessed, nicht ein Mangel. |
| Vayeshev 8:5 | 344 | `שמעני` | `שמענו` | „Wir haben von unserem Meister gehört.“ |
| Vayeshev 8:5 | 344 | `יכיון` | `יכוין` | „Er richte seine Absicht darauf.“ |
| Vayechi 16:2 | 372 | `הפלה ובקשה` | `תפלה ובקשה` | Gebet und Bitte. |
| Vayechi 16:2 | 372 | `יכמסתפק` | `וכמסתפק` | Anschluss: ככופר בעיקר וכמסתפק. |

Beleg: Seitenbilder des im Repository liegenden geteilten ZIP-Scans,
Jerusalem 1910, NLI `NNL_ALEPH990019337340205171`.
Die Seiten wurden unmittelbar am Bild gelesen; OCR ist nicht der Beleg.

| Scanseite | NLI-Bildkennung | Gedrucktes Blatt |
|---:|---|---|
| 323 | FL244210678 | 7a |
| 344 | FL244210264 | 17b |
| 372 | FL244210400 | 31b |

Der ausführbare Vorschlag mit `ref`, `alt`, `neu`, `scan_seq` und `grund`
liegt in `textkorrekturen_VORSCHLAG_20261103.json`.
Der abweichende Dateiname ist beabsichtigt: Die Pipeline liest diese Datei
nicht automatisch als aktive `textkorrekturen.json`.
Die sechs Ausgangslesungen kommen jeweils genau einmal im betreffenden
Quellabsatz vor; die Vorschläge wurden darauf geprüft.

## Weitere offene Freigabebedingungen

`עבאיי` in Lech Lecha 5:1 steht auch im Druck (Scan 327, Blatt 9a).
Der Kontext bezeichnet eine arabische Oberbekleidung. Der Wörterbucheintrag
[עבאיה im Avnion-Wörterbuch](https://www.milononline.net/עבאיה) bestätigt das
Kleidungswort, entscheidet aber nicht die genaue historische Lesung dieser
abweichenden Schreibform `עבאיי`. Eine sichere vollständige Punktierung
wurde deshalb nicht erfunden.

Die Durchsicht war eine gezielte Nachprüfung konkreter Fehlergruppen und
Verdachtsstellen. Sie ist keine abgeschlossene sprachliche Einzelprüfung
aller 1.024 Absätze. Auch nach Übernahme der sechs belegten Textkorrekturen
muss diese Gesamtprüfung abgeschlossen werden, bevor eine vollständige
sprachliche Satzfreigabe erteilt werden kann.

## Technischer Prüfstand nach den zusätzlichen Nikud-Korrekturen

Erneut ausgeführt:

```bash
python3 oyc_kollation.py
python3 oyc_bandplan.py --he-quelle meine
python3 oyc_validate.py --in out/band/Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt --json out/band/Od_Yosef_Chai_Halakhot_Masterpruefung.json
```

- 508 Segmente, `he_quelle="meine"`.
- VOK: 2.808 Wortvorkommen insgesamt gegenüber Nakdan.
- TEXT_M, PLUS_M, MINUS_M: jeweils 0 gegenüber der unveränderten Basis.
- Alle 1.024 Markerzeilen bytegleich zur Ausgangsvorlage.
- Alle übrigen Zeichen nach Entfernung der Nikud unverändert.
- 25 UNVOK_M-Stellen: 24 bewusst unpunktierte Zahlen/Gottesnamen-Buchstaben
  und das ausdrücklich offene Kleidungswort.
- Die Master-Strukturprüfung meldet 0 FEHLER und 0 PRÜFEN. Sie prüft nicht,
  ob ein Wort der Textbasis im Vergleich zum Druck falsch abgeschrieben ist.

Der neu erzeugte Master bleibt ein **Arbeitsmaster ohne sprachliche Satzfreigabe**.
Die Original-JSON-Quelle und der unbearbeitete Nakdan-Zeuge bleiben unverändert.

SHA-256 des aktuellen Arbeitsmasters:
`a3da60627bac19c8bbdee7df5e2a674368bb5171aebe17982166b304847f2fe8`.
