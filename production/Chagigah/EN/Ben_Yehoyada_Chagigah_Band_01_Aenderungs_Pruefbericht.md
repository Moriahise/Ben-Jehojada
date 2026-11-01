# Chagigah Band 01 – Änderungs- und Prüfbericht

Stand: 1. November 2026. Bearbeitet: BYH-0000001–BYH-0000146, Daf 2a–27a, 24 vorhandene Daf-Abschnitte. Es wurden alle 146 leeren Kommentarfelder und alle 146 leeren Kopfbänder englisch ausgefüllt.

**Status: Übersetzung vollständig eingetragen; NICHT ZUM SATZ FREIGEGEBEN.** Fünf Quellkonflikte verhindern die vorgeschriebene wortgleiche Wiedergabe des gesamten englischen Lemmas im zugehörigen Kopfband. Der gewünschte Dateiname EN_FERTIG bezeichnet hier den vollständig ausgefüllten Lieferstand, keine fehlerfreie Abnahme. Es wurde keine InDesign-Datei erstellt.

## Grundlage und Dateierhaltung

- Ben_Yehoyada_VERBINDLICHE_Uebersetzungsanweisung_EN_Fassung1.3_20260924.txt.
- Ben_Yehoyada_Arbeitsanleitung_AKTUELL_Fassung1.5_20261005.txt.
- Beigefügter Chagigah-Master und Chagigah-TSV, jeweils unveränderte Ausgangskopie im Audit-Ordner.
- Vorhandene zentrale Repository-Datei glossary_he.json, Git-Blob 356759024b7ff28ba5cc4efbc03567f491084b7f. Diese ist laut Arbeitsanleitung 1.5 die fortzuschreibende JSON. Keine Glossardatei eines anderen Traktats wurde eingesetzt. Eine separate Chagigah-JSON ist im vollständigen Repository-Baum nicht vorhanden.
- Quellenstand: Repository-Commit f46a74b0a241c16d25d2bfaf0a45664ea00a32f6. Die 34 Senlake-Dateien dieses Standes wurden für Kontext und Homographen konsultiert; Quellenmanifest im Audit-Ordner. Drei Dateien über 1 MB wurden über ihren Git-Blob abgerufen, da der Dateiendpunkt leeren Inhalt zurückgab.
- Original-Pipeline v3.2.1 aus ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip; Validator und Gegenprüfung unverändert verwendet.

Ein Bytevergleich nach ausschließlichem Ausblenden der beiden englischen Zielfeldinhalte ist identisch. Damit sind IDs, alle Attribute, Segmentzahl und -reihenfolge, sämtliche Überschriften, hebräische Texte einschließlich Fußnoten und Tags, BOM, Zeilenenden sowie alle übrigen Bytes unverändert. Es gab keine vorgefüllten englischen Felder. Die Platzhalter [TRAKTAT]/[NR] wurden durch Chagigah/01 in den Lieferdateinamen ersetzt; im geschützten Master gab es solche Platzhalter nicht.

## Prüfergebnisse

| Prüfung | Ergebnis |
|---|---|
| Segmente und Reihenfolge | 146/146 unverändert |
| en vollständig nichtleer | 146/146 |
| band_en vollständig nichtleer | 146/146 |
| Geschützte Bytes gegenüber Original | identisch |
| Englisches Anfangslemma | 146/146, jeweils genau eines |
| Vollständiges englisches Lemma im Kopfband | 141/146; fünf Befunde unten |
| Hebräische Zeichen/fn in band_en | 0/0 |
| Rand-Auslassungszeichen | vollständig erhalten |
| Verbotene Gottesnamen, God, Quellenpräfixe, Platzhalter | 0 |
| Englische Tags, Fußnoten, CDATA | ausgeglichen; keine verschachtelten fn |
| Originalvalidator | 0 FEHLER, 46 PRUEFEN; Exit 0 |
| Gegenprüfung Senlake/Dicta, --uebersetzt | A–F ohne Befund; Exit 0 |
| Hebräischer Text ohne Auszeichnung gegen Senlake | 146/146 wortgleich |
| Kopfbänder gegen Dicta | 145 Ausschnitte, 1 zulässiger Lemma-Rückfall |
| Mehrteiliges Lemma | BYH-0000146 gesichtet: zusammengehöriges Talmudzitat |

Der Originalvalidator untersucht vor allem den hebräischen Kopfbandbezug; sein Exit 0 bestätigt keine englische Lemma-Kongruenz. Deshalb kommt zusätzlich die explizite englische Wortlautprüfung hinzu. `by_validate --against` behandelt auch ursprünglich leere englische Felder pauschal als geschützt und ist deshalb kein geeigneter Übersetzungsvergleich; der strengere Bytevergleich prüft stattdessen exakt die vom Auftrag geschützten Bereiche. Die Originalprogramme wurden dafür nicht verändert.

## Fünf blockierende Quellkonflikte

| Segment-ID | Konkreter Widerspruch | Behandlung |
|---|---|---|
| BYH-0000040 | HE-Lemma: ein Tag in der Unterkunft und ein Tag im Lehrhaus. Kopfband: drei Monate unterwegs und ein Tag im Lehrhaus; Unterkunft fehlt. | Beide Aussagen vollständig übersetzt, keine Ergänzung des Kopfbandes. |
| BYH-0000061 | HE-Lemma: verbarg das Licht für die Gerechten. Kopfband: verbarg es vor den sündigen Generationen; die Gerechten fehlen im Ausschnitt. | Wortlaut beider Felder bewahrt. |
| BYH-0000068 | HE-Lemma: Himmel und Erde seien Namen des Heiligen. Kopfband erwähnt in dieser Aussage nur Himmel. | Plural des Lemmas und Singular des Kopfbandes beibehalten. |
| BYH-0000089 | HE-Lemma ergänzt Verzicht auf Schlaf und Geheimnis des Flusses. Kopfband hat nur Einschränkung beim Torastudium und Offenbarung eines Geheimnisses. | Die Zusätze nicht in das geschützte Kopfband hineingelesen. |
| BYH-0000121 | HE-Lemma vergleicht Worte der Tora mit einer Nuss; Kopfband vergleicht Toragelehrte mit einer Nuss. Außerdem daf=15a gegenüber ref=15b:10 bereits im Original. | Unterschied vollständig übersetzt; daf/ref unverändert. |

Diese Befunde lassen sich nicht durch eine bloße andere englische Formulierung beheben, ohne Inhalt zu streichen oder dem Kopfband hinzuzufügen. Es ist eine gesonderte redaktionelle Entscheidung über die hebräische Ausgangsstruktur erforderlich. Die geschützten Felder wurden nicht repariert.

## Glossaränderungen und offene Kürzel

TSV: 287 vorhandene Zeilen unverändert fortgeführt, drei sichere **ausschließlich kontextuelle** Einträge ergänzt; insgesamt 290 eindeutige Schlüssel. Drei Spalten bleiben abbr/hebrew/english, mit Tabulator und CRLF. Die drei Zeilen sind in `_meta.chagigah_band_01_translation.contextual_tsv_rows` der bestehenden JSON exakt gespiegelt. Alle 287 globalen Hauptlesarten und sämtliche letter_names bleiben unverändert, damit andere Traktate keine Fehlauflösung erhalten.

| Kürzel | Segment | Sichere Bedeutung und Grenze |
|---|---|---|
| ת״ו | BYH-0000090 | תבנה ותכונן, „may it be rebuilt and established“, unmittelbar nach Jerusalem; Senlake löst ausdrücklich auf. Anderswo auch Buchstabenname/Zahl. |
| ר״א | BYH-0000099 | רבי אלעזר, „Rabbi Elazar“; derselbe Absatz nennt ihn ausgeschrieben. Nicht global, da andernorts Rabbi Eliezer. |
| אאנך | BYH-0000085 | אגודת אורות ניצוצות כלים; genau das vom Autor ausgeschriebene viergliedrige Initialwort ohne Gershayim. |

| Offener Prüffall | Segment-ID | Behandlung |
|---|---|---|
| בש״ה | BYH-0000016 | Werk-/Torzuordnung nicht sicher; Kürzel erhalten. |
| הרי״ף | BYH-0000014 | „Rif“ erhalten; kein ausgeschriebener Personenname erfunden. |
| מהרש״ם | BYH-0000119 | „Maharsham“ erhalten; Identität offen. |
| מהר״א הכהן | BYH-0000144 | „Mahar A ha-Kohen“ erhalten; Vorname offen. |
| אנ״ך | BYH-0000085 | Mystische Bezeichnung neben gewöhnlichem Wort für einen Edelstein im selben Absatz; keine globale Auflösung. אאנך wurde gesondert exakt ergänzt. |
| מהר״ם מלבים | BYH-0000146 | Durch den ausgeschriebenen Namen als Malbim übersetzt, keine globale Hauptlesart geändert. |

Die übrigen nicht im TSV stehenden Gershayim-Treffer wurden einzeln klassifiziert (Audit/Abkuerzungskandidaten.json): Blatt-/Kapitel-/Zahlenangaben, Buchstabennamen und ihre Plurale, echte Zitatzeichen nach Präfixen, arabische Wörter oder Buchstabengruppen. Sie wurden nicht als neue lexikalische Kürzel erfunden. Kapitel פ״ו in BYH-0000084 ist Kapitel 6; וא״ו in BYH-0000048 ebenfalls Kapitel 6. ע״ד in BYH-0000071 ist Spalte 4. Die expliziten Expansionen erscheinen im Englischen überwiegend ausgeschrieben im Fließtext; Quellenfußnoten stehen beim Beleg. Es wurden keine zusätzlichen Auslegungen in Fußnoten eingeführt.

## Zahlen und weitere einzelne Quellenhinweise

Die nachgerechneten Zahlen- und Buchstabenoperationen sind im Audit als Gematria_Pruefung.json dokumentiert. Ausdrücklich genannte fehlerhafte Ausgangswerte werden in der Übersetzung nicht still korrigiert.

| Segment-ID | Befund |
|---|---|
| BYH-0000085 | גערה ergibt 278, nicht die im Master stehenden 279. שור 506 minus 279 ergibt 227, nicht כרוב 228; mit 278 ginge die Rechnung auf. רחמים ist 298, אך גערה hingegen 299. Alle Ausgangsbehauptungen unverändert übersetzt. |
| BYH-0000089 | Die zusätzlichen Buchstaben aus נון הה ריש sind ון ה יש = 371; sie ergeben יש הון, aber nicht vollständig שינה = 365 (ein ו bleibt übrig). Die erste Behauptung wird bewahrt, der Rechenbefund hier offengelegt. |
| BYH-0000146 | זהב ergibt 14, nicht die zweimal ausdrücklich genannten 17. Daher עץ זהב=174 gegenüber סימן טוב=177. Die [17]-Angaben bleiben als Ausgangsbehauptung im englischen Text. |
| BYH-0000006 | Die Vorlage verweist für die Kompromissregel zur öffentlichen Lehre auf Berakhot 25a; Verweis unverändert übertragen, genaue Stelle redaktionell prüfen. |
| BYH-0000075 | Die spätere Passage nennt auch die erste Nachthälfte לילה, während vorher ליל gegenüber לילה unterschieden wird. Inhaltliche Halbzeit-Zuordnung erhalten; Schreibweise im Ausgangstext unverändert. |
| BYH-0000145 | Exodus 25:11 ist der in der Vorlage angegebene Vers über Goldüberzug; seine Verwendung in der Erörterung des Altars wird nicht durch einen anderen Vers ersetzt. |

## Die 46 Originalhinweise einzeln

Die folgenden Meldungen betreffen den hebräischen Wortlaut; sie sind keine 46 zusätzlichen englischen Fehler. Die Stellen wurden bei der Übersetzung einzeln betrachtet. Bei nichtblockierenden Varianten wird die im Kopfband tatsächlich vorhandene Wendung englisch zitiert; zusätzliche Belegangaben, „etc.“ oder darüber hinausgehende Wörter des HE-Zitats stehen außerhalb der englischen Lemma-Markierung. Vollständigkeit des Kommentars und geschützte Quellfelder haben Vorrang. Die fünf inhaltlich nicht vereinbaren Fälle bleiben oben offen.

- **BYH-0000004**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000006**: Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000012**: Wortlaut weicht ab (Deckung 0.545) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000013**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000015**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000016**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000017**: Wortlaut weicht ab (Deckung 0.6) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000019**: Wortlaut weicht ab (Deckung 0.714) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000026**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000027**: Wortlaut weicht ab (Deckung 0.571) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000028**: Wortlaut weicht ab (Deckung 0.7) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000032**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000037**: Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000040**: Wortlaut weicht ab (Deckung 0.556) — Stelle einzeln ansehen. Blockierender englischer Quellkonflikt, siehe oben.
- **BYH-0000042**: Wortlaut weicht ab (Deckung 0.6) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000047**: Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000048**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000050**: Wortlaut weicht ab (Deckung 0.7) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000052**: Wortlaut weicht ab (Deckung 0.714) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000058**: Wortlaut weicht ab (Deckung 0.6) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000060**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000061**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Blockierender englischer Quellkonflikt, siehe oben.
- **BYH-0000065**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000068**: Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen. Blockierender englischer Quellkonflikt, siehe oben.
- **BYH-0000071**: Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000072**: Wortlaut weicht ab (Deckung 0.765) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000074**: Wortlaut weicht ab (Deckung 0.824) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000079**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000080**: Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000094**: Wortlaut weicht ab (Deckung 0.6) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000100**: Wortlaut weicht ab (Deckung 0.5) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000108**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000109**: Wortlaut weicht ab (Deckung 0.636) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000110**: Wortlaut weicht ab (Deckung 0.556) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000112**: Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000113**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000122**: Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000123**: Wortlaut weicht ab (Deckung 0.714) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000125**: Wortlaut weicht ab (Deckung 0.625) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000126**: Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000129**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000132**: Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000133**: Wortlaut weicht ab (Deckung 0.577) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000142**: Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000144**: Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.
- **BYH-0000145**: Wortlaut weicht ab (Deckung 0.636) — Stelle einzeln ansehen. Gesichtet; englischer Zitatkern wortgleich im Kopfband, Quellenform unverändert.

## Prüfsummen und Reproduktion

- Ausgangsmaster SHA-256: `38ccab7eccb357901510da8846b1f51e8799d4dc6db36dbf40bf9785a640a06c`.
- Übersetzte Datei SHA-256: `99cf2b29d726a2cb3217df0d376affe42456dca63971c22ae9a48f9ca23e691c`.

Audit enthält Originalmaster, Ausgangsglossare, Korpusmanifest, Originalvalidator und Gegenprüfung samt Protokollen. `english_audit.py` prüft den bytegenauen Schutz, die Zielfelder und die englischen Lemmas erneut. Es muss wegen der fünf offengelegten Lemma-Konflikte mit Exit 1 enden. Originalvalidator und Gegenprüfung enden mit Exit 0. Eine vollständige unabhängige Zweitlektoratsprüfung wird damit nicht behauptet.
