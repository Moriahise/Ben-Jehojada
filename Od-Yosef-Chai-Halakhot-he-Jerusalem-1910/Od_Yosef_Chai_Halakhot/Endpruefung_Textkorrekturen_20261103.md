> Historischer Zwischenstand. Aktueller Fortsetzungsstand: [Gesamtlektorat_Status_20261103.md](Gesamtlektorat_Status_20261103.md).

# Endprüfung nach Freigabe der sechs Textkorrekturen · 03.11.2026

**Die sechs freigegebenen Berichtigungen sind aktiv. Eine vollständige sprachliche Satzfreigabe ist weiterhin nicht erteilt.**

Die ausdrückliche Zustimmung des Nutzers ist in `textkorrekturen.json` dokumentiert. Die Pipeline wendet genau diese sechs Änderungen auf die Arbeitsbasis an. Die Original-JSON-Datei und sämtliche 46 Nakdan-Dateien bleiben bytegleich. In `vokalisierung/meine` sind die sechs betroffenen Wörter mit passender Vokalisierung berichtigt; weitere Buchstabenänderungen wurden nicht vorgenommen.

| Stelle | Vorher | Jetzt | Scanseite |
|---|---|---|---:|
| Bereshit 11:1 | עָרַף | עֵרֶךְ | 323 |
| Vayeshev 8:5 | הֶחָסֵר | הַחֶסֶד | 344 |
| Vayeshev 8:5 | שְׁמָעֵנִי | שָׁמַעְנוּ | 344 |
| Vayeshev 8:5 | יִכְיּוֹן | יְכַוֵּין | 344 |
| Vayechi 16:2 | הַפָּלָה | תְּפִלָּה | 372 |
| Vayechi 16:2 | יִכְמַסְתֵּפֵק | וּכְמִסְתַּפֵּק | 372 |

Die Begründungen und NLI-Bildkennungen stehen in `textkorrekturen.json`. `vokalisierung/Textkorrekturen_Aktivierung_20261103.json` protokolliert den Zwischenstand unmittelbar nach Aktivierung. Die anschließenden 19 reinen Nikud-Korrekturen samt Prüfsummen stehen gesondert in `vokalisierung/Endpruefung_Nikud_20261103.json`. Ältere Korrekturprotokolle beschreiben ihre jeweiligen historischen Prüfstände, nicht die heutigen Dateiprüfsummen.

## Fortgesetzte sprachliche Durchsicht

Zusammenhängend gelesen wurden 59 Absätze mit 4.180 Wörtern aus Bereshit, Lech Lecha, Purim, Bo und Vayikra. Dabei wurden 19 eindeutige Vokalisierungen in fünf Dateien berichtigt, unter anderem Objektsuffixe („ihm/ihn“ statt „uns“), Substantiv עִטּוּף, Absichtsverb יְכַוֵּן, בְּאֵינוֹ, שֶׁבּוֹרוֹת sowie כְּנוֹס und וַיַּגֶּד in den Esther-Zitaten. Die beiden Bibelformen wurden am [vokalisierten Esthertext, Kapitel 4](https://www.mechon-mamre.org/i/t/t3304.htm) überprüft.

Das Leseprotokoll `vokalisierung/Endpruefung_Leseprotokoll_20261103.json` nennt jeden dieser 59 Absätze mit Textprüfsumme. „Gelesen“ ist keine Abschnittsfreigabe: In diesen Absätzen bleiben die folgenden Kontextverdachte offen. Sie wurden weder als Druckbefund bestätigt noch geändert.

| Stelle | Vorhandene Buchstaben | Kontextverdacht, noch am Druck zu prüfen |
|---|---|---|
| Bereshit 1:3 | כהם | שהם |
| Bereshit 10:1 | מוכרת | מוכרח |
| Bo 1:5 | אפינו | אפילו |
| Bo 1:6 | נהחדש | נתחדש |
| Bo 3:2 | אכל | אבל |
| Bo 6:1 | אתרוג | עירוב |
| Vayikra 2:1 | לציבור | לאיבוד / לצִבּוּר? |
| Vayikra 6:1 | ולח | ולא |
| Lech Lecha 5:1 | עבאיי | Historische Vokalisierung offen; Druckschreibung belegt. |

Die übrigen 965 Absätze sind von dieser dokumentierten zusammenhängenden Durchsicht noch nicht erfasst. Frühere gezielte Fehlergruppenprüfungen ersetzen diese Gesamtlektüre nicht. Auch Druckfehlerverzeichnis, fremdsprachige Wörter und verdächtige Ausgangslesungen müssen für eine vollständige sprachliche Freigabe berücksichtigt werden. Zusätzliche Buchstabenänderungen über die ausdrücklich freigegebenen sechs hinaus sind nicht aktiviert.

## Erzeugung und technische Prüfung

```bash
python3 produzieren.py --scan .. --scan-gesamt 420 --he-quelle meine
python3 oyc_validate.py --in out/band/Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt --json out/band/Od_Yosef_Chai_Halakhot_Masterpruefung.json
python3 -m unittest test_oyc -v
```

Der Produktionslauf führt `oyc_kollation.py` und den Bandplan mit HE-Quelle `meine` aus und aktualisiert Quellenmanifest und Prüfbericht.

- 1.024 Absätze vorhanden, alle 1.024 `@@`-Markerzeilen bytegleich zum vorherigen Repository-Stand.
- Außer den sechs genehmigten Textkorrekturen und Nikud bleiben sämtliche Zeichen in `meine` unverändert.
- `TEXT_M`, `PLUS_M`, `MINUS_M`: jeweils **0** gegenüber der korrigierten Arbeitsbasis.
- `TEXT_N`: **6**, genau die genehmigten Stellen gegenüber dem unveränderten Nakdan-Zeugen. Entscheidungen mit Belegen: `vokalisierung/TEXT_N_Entscheidungen_20261103.json`. Diese Befunde werden nicht durch Veränderung des Nakdan-Zeugen beseitigt.
- `VOK`: **2.825** Abweichungen gegenüber Nakdan. Dies ist ein Unterschiedszähler, kein Zähler verbliebener Fehler und kein Nachweis vollständiger sprachlicher Richtigkeit.
- `UNVOK_M`: **25**; darunter das weiterhin offene Kleidungswort `עבאיי`, sonst einzelne Zahlen-/Gottesnamen-Buchstaben.
- Master: **508 Segmente**, 30 Satzabschnitte, `he_quelle="meine"`, **0 FEHLER, 0 PRÜFEN** in der Strukturprüfung. Die EN-Felder sind für den späteren Übersetzungsschritt leer.
- Alle Segmentkennungen, Ordnungszahlen, Tags, Satzzeichen und Konsonanten des Masters stimmen mit der korrigierten Arbeitsbasis überein. Keine fehlenden Zeugentexte oder Wörter ohne übertragenen Vokaltext laut Bandplan.
- **42 vorhandene Tests bestanden**. Vollständiges Testprotokoll: `out/Endpruefung_Tests_20261103.txt`.

Die Schutzprüfung ist in `out/Endpruefung_Schutzpruefung_20261103.json` festgehalten. Die technische Prüfung ersetzt keine vollständige sprachliche Einzelprüfung.

Der neu erzeugte Produktionsmaster ist als **Arbeitsstand ohne vollständige sprachliche Satzfreigabe** verwendbar. Seine Kopie im übergeordneten Werkverzeichnis wurde synchronisiert.

SHA-256 des Masters:
`aeba288ca9ae23ad5132f07ac0e27e93fa43535818315bf59922684df37ed41b`.
