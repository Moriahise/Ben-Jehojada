# Gesamtlektorat · Prüfstand vom 03.11.2026

**Auftrag noch nicht abgeschlossen. Keine vollständige sprachliche Satzfreigabe.**

Basis dieses Fortsetzungslaufs: Commit `5812c106ad1825baf0e53461fff045cdc2fffb4d`.
Die vorhandene Endprüfung wurde fortgesetzt. Der Auftrag, alles für die vollständige Freigabe zu erledigen, wurde als Erlaubnis verstanden, weitere eindeutig am Druck belegte Übertragungsfehler über `textkorrekturen.json` zu berichtigen. Für ungesicherte Lesungen wurden keine Buchstaben erfunden.

## Sprachliche Einzelprüfung und vollständige Prüfliste

- 169 von 1.024 Absätzen zusammenhängend gelesen, davon 110 in diesem Fortsetzungslauf zusätzlich zum bisherigen Stand.
- Vollständig durchgelesene Textgruppen: Bereshit, Noach, Lech Lecha, Vayetzei, Bo, Purim, Mishpatim, Vayakhel und Bamidbar sowie der zuvor geprüfte Abschnitt Vayikra; außerdem fünf einzeln protokollierte Absätze. „Gelesen“ ist keine Abschnittsfreigabe.
- 855 Absätze sind noch nicht zusammenhängend sprachlich durchgesehen. Frühere automatische und gezielte Fehlergruppensuchen gelten nicht als abgeschlossene Einzelprüfung.
- `vokalisierung/Satzfreigabe_Status_20261103.json` nennt **alle 1.024 Absätze**, ihren Status, die aktuelle Textprüfsumme und die offenen Befunde. Ausstehende Absätze werden nicht als freigegeben gezählt.

Das neue Leseprotokoll steht in `vokalisierung/Gesamtlektorat_Leseprotokoll_20261103.json`; das ältere Protokoll der ersten 59 Absätze bleibt als historischer Stand erhalten.

## Ausgeführte Korrekturen seit dem letzten Commit

60 weitere reine Nikud-Korrekturen, darunter:

- Bamidbar 3:1: פָּרוֹת für die Milch gebenden Kühe statt פֵּרוֹת für Früchte; alle vier Wortvorkommen im Absatz.
- Defektiv geschriebene Formen von בצים als Eier, nicht mit falscher Schwa-/Qibbuz-Lesung.
- Objektsuffixe, Infinitive, Zeitadverbien und Verknüpfungen wie דְּעַתָּה sowie Substantive wie מִלּוּי.
- Ijob 20,15: וַיְקִיאֶנּוּ und מִבִּטְנוֹ, mit Erhaltung der vorgegebenen Konsonantenschreibung.
- Mishpatim 3:1: גִּבַּרְוָותָא, belegt im [Jastrow-Lexikon](https://www.sefaria.org/Jastrow%2C_%D7%92%D6%B0%D6%BC%D7%91%D6%B7%D7%A8_II.1).
- Der Herkunftsname מִפָּאנוֹ statt der falschen Suffixlesung. Identität des genannten Rema: [NLI-Normdatensatz](https://www.nli.org.il/he/a-topic/987007279134205171).

Zusätzlich 241 Abkürzungsbereinigungen: Die eindeutig abgekürzten Verweisformen `הנז'`, `כנז'`, `וכנז'`, `בגי'`, `בחי'`, `בבחי'`, `כבחי'` bleiben unpunktiert. Damit entfallen irreführende Vollwortlesungen wie הֲנֵז. Buchstaben und Abkürzungszeichen bleiben erhalten. Andere Abkürzungen wurden durch diese Regel nicht verändert.

Alle Änderungen einschließlich einzelner Gründe und Wortpositionen sind in `vokalisierung/Gesamtlektorat_Aenderungen_20261103.json` dokumentiert. Dateiprüfsummen und die abschließende Schutzprüfung stehen in `out/Gesamtlektorat_Schutzpruefung_20261103.json` und in der vollständigen Statusliste.

## Weitere am Druck belegte Übertragungsfehler

14 neue Einträge ergänzen die sechs zuvor ausdrücklich freigegebenen Korrekturen. Insgesamt sind jetzt 20 Einträge aktiv. Die Original-JSON-Datei und die 46 Nakdan-Dateien bleiben unverändert.

| Stelle | Digitaltext vorher | Nach Druck | Scanseite |
|---|---|---|---:|
| Bereshit 1:3 | כהם | שהם | 322 |
| Bereshit 10:1 | מוכרת | מוכרח | 323 |
| Bo 1:5 | אפינו | אפילו | 384 |
| Bo 1:6 | נהחדש | נתחדש | 384 |
| Bo 1:6 | ועשה כמו | ונעשה כמו | 384 |
| Bo 3:2 | אכל אם | אבל אם | 385 |
| Vayikra 6:1 | ולח סמכתי | ולא סמכתי | 403 |
| Kuntres Chut HaMeshulash 6 | אחרות אחד | אחדות אחד | 347 |
| Kuntres Chut HaMeshulash 54 | עונה ז"א | עולה ז"א | 353 |
| Kuntres Chut HaMeshulash 54 | כמו ס"א | כמו א"א | 353 |
| Kuntres Chut HaMeshulash 82 | לדהגא | לדרגא | 355 |
| Shemot 10:3 | וקרבתלו | וקרבתנו | 377 |
| Vayakhel 1:3 | המשבח | המזבח | 399 |
| Vayakhel 7:1 | נשאר תפילות | כשאר תפילות | 399 |

Bildkennungen und Einzelbegründungen stehen in `textkorrekturen.json`. Grundlage sind die Seitenbilder im geteilten Scan-ZIP des Repositorys. Der Textzeuge `meine` und der Produktionsmaster enthalten dieselben Berichtigungen.

## Noch offene Befunde

- **Bo 6:1 – אתרוג וסוכה**: Steht im Druck; Kontext legt עירוב nahe. Keine unbelegte Konsonantenemendation. Status: `DRUCKLESUNG_BESTAETIGT_EDITORISCHE_PRUEFUNG_OFFEN`.
- **Vayikra 2:1 – הולכת לציבור**: Steht im Druck. Kontext legt verlorengehenden Stoff nahe. Keine stillschweigende Emendation. Status: `DRUCKLESUNG_BESTAETIGT_EDITORISCHE_PRUEFUNG_OFFEN`.
- **Lech Lecha 5:1 – עבאיי**: Suche bestätigt Abaya als Kleidungswort, liefert keinen hinreichenden Beleg für genau diese historische Lautung. Status: `FREMDWORT_PUNKTIERUNG_OFFEN`.
- **Druckfehlerverzeichnis – Halakhot-Nachträge auf Scanseiten 414–415**: Bilder 413–415 gesichtet; insbesondere die Verweise Blatt 22a/22b und die langen Zusätze müssen zuverlässig zugeordnet und mit der Digitalbasis abgeglichen werden. Status: `ZUORDNUNG_UND_UEBERNAHME_NICHT_VOLLSTAENDIG_GEPRUEFT`.
- **Noach 15:1 – תחכם**: Kontext: Fäden durch die Ecke ziehen; gegen Druck prüfen. Status: `TEXTVERDACHT_OFFEN`.
- **Noach 19:7 – שבעתה**: Kontext und genaue Drucklesung prüfen. Status: `TEXTVERDACHT_OFFEN`.
- **Vayetzei 1:1 – הנכנם**: Druckbild gelesen, Endbuchstabe nicht hinreichend eindeutig für eine dokumentierte Emendation. Status: `DRUCKBUCHSTABE_UNKLAR`.
- **Vayetzei 3:5 – להכנים**: Kontext: Nahrung einführen. Verlässliche Bestimmung von ס/ם am Original erforderlich. Status: `DRUCKBUCHSTABE_UNKLAR`.
- **Vayetzei 3:7 – עירות**: Zwei Schichten der Harnblase. Lesung und Vokalisierung prüfen. Status: `TEXTVERDACHT_OFFEN`.
- **Vayetzei 3:7 – התיבה**: Auch der Druck bezeichnet das Gefäß hier als תיבה; nicht allein nach heutiger Erwartung zu קיבה ändern. Status: `DRUCKLESUNG_BEIBEHALTEN`.

Die Bilder des Druckfehlerverzeichnisses (413–415) wurden gesichtet. Das ist **kein** Nachweis, dass sämtliche Halakhot-Korrekturen und Nachträge bereits vollständig zugeordnet oder übernommen wurden. Dieser Abgleich bleibt ausdrücklich offen.

## Erzeugung und Schutzprüfung

Ausgeführt:

```bash
python3 produzieren.py --scan .. --scan-gesamt 420 --he-quelle meine
python3 -m unittest test_oyc -v
python3 oyc_validate.py --in out/band/Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt --json out/band/Od_Yosef_Chai_Halakhot_Masterpruefung.json
```

Der Produktionslauf ruft Kollation und Bandplan mit `meine` auf. Ergebnis:

- `TEXT_M`, `PLUS_M`, `MINUS_M`: **0** gegenüber der korrigierten Arbeitsbasis.
- `TEXT_N`: **20**, genau die aktiven, belegten Berichtigungen gegenüber dem unveränderten Nakdan-Zeugen.
- `VOK`: **3.118** Unterschiede zu Nakdan; kein Zähler verbleibender Fehler oder vollständig geprüfter Wörter.
- `UNVOK_M`: **25**, darunter weiterhin das offene Fremdwort `עבאיי`.
- 1.024 `@@`-Marker bytegleich zum Stand vor diesem Lauf.
- Nur die 14 zusätzlichen Textkorrekturen und Nikud unterscheiden den neuen Zeugen vom vorherigen Stand. Keine weiteren Konsonanten-, Satzzeichen- oder Leerraumänderungen.
- Master: **508 Segmente, 30 Satzabschnitte, HE-Quelle `meine`, 0 FEHLER, 0 PRÜFEN** in der Strukturprüfung. IDs, n, Tags und Konsonantentext stimmen mit der korrigierten Basis überein.
- **42 Tests bestanden**. Testprotokoll: `out/Gesamtlektorat_Tests_20261103.txt`.
- Entscheidungen in der Kollations-TSV erhalten bzw. ergänzt. Die 20 erwarteten Textabweichungen sind zusätzlich in `vokalisierung/Gesamtlektorat_TEXT_N_20261103.json` einzeln zugeordnet.

Die Masterkopie im übergeordneten Werkverzeichnis wurde synchronisiert. Die EN-Felder sind weiterhin leer und gehören zum späteren Übersetzungsschritt.

Master SHA-256: `7c675151b0e3bd99041bc48bb05566930bf1753651e4415a2c7a91cdb9a83fb9`.

**Dieser Arbeitsmaster ist technisch geprüft, aber nicht vollständig sprachlich freigegeben.** Eine positive Gesamtfreigabe wäre angesichts der 855 ausstehenden Absätze und der genannten offenen Befunde unbelegt.
