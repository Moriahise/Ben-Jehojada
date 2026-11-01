# Moed Katan · Band 01 · Änderungs- und Prüfbericht

Stand: 1. November 2026. Ausgangsstand des Repository: `2e6b6ed7d4a314171e330c70bcaf48f2027ffec6`.

Der vollständige Band ist ins Englische übersetzt: BYH-0000001 bis BYH-0000069, 69 Kommentare und 69 Kopfbänder. Die technische Prüfung besteht. Die unten einzeln aufgeführten Quellen- und Lesefragen bleiben zur redaktionellen Freigabe offen. `_EN_FERTIG` bezeichnet die vollständig gefüllte Übersetzungsdatei, keine bereits erteilte Druckfreigabe.

## Verwendete Dateien und Regeln

- Bereitgestellter Ausgangsmaster: `Ben_Yehoyada_Moed_Katan_Band_01_BILINGUAL.txt`, SHA-256 `78d5ca3ae42dad9fac5630bed008e88243686cf1d01e1b49d303bea8372daf86`. Master und Moed-Katan-TSV lagen als bereitgestellte Dateien vor; im zu Beginn gelesenen Repository-Baum waren sie nicht enthalten. Es fehlt keine für diesen Lauf benötigte Datei.
- Bereitgestellte `Ben_Yehoyada_Moed_Katan_GLOSSAR.tsv`: 279 Ausgangseinträge. Keine TSV eines anderen Traktats verwendet.
- Bestehende Repository-Datei `glossary_he.json`, Git-Blob `b342274224fcf48e87ff69fc6c7cf8357a6c1c6d`: 287 globale Einträge; vorhandene Einträge und Metadaten anderer Läufe erhalten.
- `Ben_Yehoyada_VERBINDLICHE_Uebersetzungsanweisung_EN_Fassung1.3_20260924.txt`, Git-Blob `dee7ed31b94042495080ced1500673b7881d06eb`.
- `Ben_Yehoyada_Arbeitsanleitung_AKTUELL_Fassung1.5_20261005.txt`, Git-Blob `e9f9b020e15c4b9d065bec795a58a686bb17ed08`; insbesondere 53c und 53d.
- Repository-Senlake-Datei `Ben Yehoyada on Moed Katan - he - Senlake edition 2019 based on Ben Yehoyada, Jerusalem, 1897.txt`, Blob `2dc3908d4b5372a0aa28cd1b142357f7d1cd7c88`.
- Repository-Dicta-Datei `מועד_קטן.combinedfullhaser.txt`, Blob `ca5d48d19cfbd48206b001cba68eb7c88655c82a`.
- Validator, Gegenprüfung, Parser und Glossarmodul aus `ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip`, Archiv-Blob `2eab4448a8e1e0beec0c9cc2304e6154f06d95f5`. Die tatsächlich verwendeten Skripte wurden bytegleich gegen das Archiv geprüft; siehe `Audit/Pipeline_Identitaet.json`.

Die englische Übersetzung wurde aus den geschützten Feldern des gelieferten Masters erstellt. Entfernte längere Senlake-Zusätze wurden nicht wieder eingeführt. Zur Abkürzungsprüfung wurden ausschließlich die 34 Senlake-Rohdateien des Repository abgeglichen, keine anderen Traktatglossare.

## Änderungen und Erhaltungsprüfung

| Prüfung | Ergebnis |
|---|---|
| Ursprünglich leere `<en>` | 69 von 69 vollständig gefüllt |
| Ursprünglich leere `<band_en>` | 69 von 69 vollständig gefüllt |
| Englische Lemmas | 69, jeweils genau eines am Anfang und wortgleich im eigenen Kopfband |
| IDs, Attribute, Reihenfolge und Zahl | Unverändert, 69 Segmente |
| `<he>`, `<band_he>` einschließlich innerer Tags und Fußnoten | Bytegleich außerhalb der erlaubten englischen Felder |
| Hebräische / englische Dafüberschriften | Je 16, unverändert |
| Bereits gefüllte englische Zielfelder | Keine im Ausgangsmaster; vorhandene englische Überschriften unverändert |
| Rand- und Gesamtzahl der Kopfband-Ellipsen | Je Segment erhalten |
| Hebräisch / `<fn>` in `<band_en>` | Je 0 |
| Verbotene lateinische Gottesnamen / „God“ | 0 in den neuen englischen Feldern |
| Unausgeglichene Tags / verschachtelte Fußnoten / Platzhalter | Je 0 |
| Quellengegenprüfung mit `--uebersetzt` | A bis F ohne Befund |
| Validator mit `--expect 69` | 0 FEHLER, 17 PRUEFEN, 0 HINWEIS |

Die stärkste Erhaltungsprüfung maskiert ausschließlich die Inhalte von `<en>` und `<band_en>` und vergleicht anschließend die gesamten Dateibytes. Ergebnis: identisch. Der ergänzende XML-Vergleich prüft sämtliche Elemente und Attribute. Einzelresultate aller 69 IDs: `Audit/Feldvergleich_EN.json`.

Eingabe: 182,352 Bytes. Ausgabe: 323,218 Bytes. Die Zunahme um 140,866 Bytes entsteht ausschließlich durch die 138 neu gefüllten englischen Felder. Ausgabe-SHA-256: `6d9df5e2b4a3cf8c6b3ea7ac71294159bce0c8001ef909c5dd8fe2012ad716b9`.

## Glossar

Die Moed-Katan-TSV hat jetzt 281 Einträge: 279 bestehende plus 2 ausdrücklich auf die jeweilige Segment-ID begrenzte Kontextzeilen. Die globale JSON behält ihre 287 automatischen Hauptauflösungen unverändert; die beiden neuen Kontextauflösungen sind konsistent in `_meta.moed_katan_band_01_translation.contextual_abbreviations` dokumentiert. Dadurch wird keine für andere Traktate falsche Personenautomatik eingeführt.

| Kürzel | Segment | Sicher belegte Bedeutung in diesem Band | Beleg und Begrenzung |
|---|---|---|---|
| מהרנ״ש | BYH-0000005 | R. Natan Shapira ben Reuven David von Jerusalem | Unmittelbare Senlake-Erklärung, Werk Tuv HaAretz. 2 Korpusbelege in 2 Traktaten; der Bava-Batra-Beleg bezeichnet R. Natan Neta Shapira. |
| מהרש״ל | BYH-0000028 | R. Shemuel Laniado | Unmittelbare Senlake-Erklärung, Werk Keli Yakar. 3 Korpusbelege in 3 Traktaten; keine gleiche Auflösung aller Belege belegbar. |

Sechs englische Ersatzformen der bereitgestellten TSV wurden an die vorhandene Repository-JSON und die Gottesnamenregeln angeglichen:

| Kürzel | Bisher in TSV | Jetzt |
|---|---|---|
| אדנ"י | the Name Adonai | the Name HaShem |
| בעה"ו | with the help of God and His salvation | with the help of G-d and His salvation |
| בעזה"י | with the help of God, blessed be He | with the help of HaShem, blessed be He |
| ה"י | may God protect him | may HaShem protect him |
| השי"ת | God, blessed be He | HaShem, blessed be He |
| ח"ו | God forbid | Heaven forbid |

Der offene Personenbezug הרי״ף in BYH-0000046 bleibt „the Rif“. Buchstabenplurale, Zahlenangaben, die Wochentagsgruppe אב״ג und die arabischen Wörter זרנטא״ח, כ״ס, שי״ץ erhalten keine erfundenen Akronymauflösungen. Einzelzuordnungen stehen in `Audit/glossary_changes.json`.

Vor den Ergänzungen wurden alle 34 Senlake-Dateien auf Gleichheit mit ihren aktuellen Repository-Blob-SHAs geprüft und die Kandidaten über den gesamten Korpus gesucht. Belege und Trefferzahlen: `Audit/corpus_abbreviations.json`. Der erneute Lauf des unveränderten Pipeline-Parsers und Glossarmoduls mit der fortgeschriebenen JSON ergibt 181 von 191 Treffern, 94,8 %. Die 10 algorithmisch offenen Formen sind oben genannte Buchstaben-, Zahl- oder Fremdwortformen. Dieser Neulauf erzeugt keinen neuen Master und keine Layoutdateien. Die bereits vorhandenen hebräischen Fußnoten bleiben geschützt.

## Die 17 geerbten Wortlaut-Prüfhinweise

Diese Hinweise waren bereits vor der Übersetzung vorhanden und betreffen den hebräischen Lemma-/Kopfbandvergleich. Keiner wurde durch Veränderung geschützter Daten entfernt. Das englische Lemma passt in allen Fällen wortgleich zum eigenen englischen Kopfband.

| Segment-ID | Sichtprüfung und Behandlung |
|---|---|
| BYH-0000003 | Zusatz „in this world“ im Ben-Yehoyada-Lemma; nach dem englischen Lemma gemaess 53d erhalten. |
| BYH-0000005 | זה בזה / זה לזה: gleiche Bedeutung „clung to one another“; keine Aenderung des hebraeischen Wortlauts. |
| BYH-0000007 | Ausgeschriebenes Psalmzitat gegen abgekuerztes Kopfbandzitat; Fortsetzung nach dem englischen Lemma gemaess 53d. |
| BYH-0000009 | דכתיב / שנאמר und abgekuerztes Zitat; gemeinsamer englischer Zitatanfang, „etc.“ ausserhalb des Lemmas. |
| BYH-0000011 | Orthographische/arameische Varianten הדור / הדר und מיבעיא / מבעי; gleicher englischer Sinn. |
| BYH-0000013 | Arameische Flexions-/Formulierungsvarianten; Doppelung der Verbalformen im Kommentar erlaeutert, ohne HE-Reparatur. |
| BYH-0000015 | קבורתה / קברה; englisches gemeinsames Lemma „even one standing at her grave“, Wortspiel mit keburah im Kommentar erklaert. |
| BYH-0000017 | מנא ליה / מנלן sowie שלוחא / שליחא und weitere Flexionsformen; gemeinsames englisches Lemma, kein Quellenfeld veraendert. |
| BYH-0000022 | Das Kopfband endet nach „Just as a thigh is concealed“. Nur diese gemeinsame Wendung im EN-Lemma; Fortsetzung gemaess 53d. Abgeschnittenes Kopfband nicht vervollstaendigt. |
| BYH-0000023 | ראה und מבַחוץ im Autorenlemma gegen kuerzeren Kopfbandwortlaut; benoetigte Autorenfassung unmittelbar nach dem EN-Lemma gemaess 53d. |
| BYH-0000039 | עלייהו / עליהן sowie Orthographie/Vokalisierung; im Englischen gleiche Aussage. |
| BYH-0000043 | פלונית / פלוני ist fuer die Auslegung wesentlich. Gemeinsame englische Form „a certain field for so-and-so“; die feminine Autorenlesart wird anschliessend erklaert. |
| BYH-0000048 | Orthographische Varianten und Klammerlesart (ענש) im unveraenderten HE-Kopfband; EN gibt die gemeinsame Bedeutung einmal wieder. Gemeinsamer englischer Lemmaanfang; vollstaendige Autorenfassung folgt gemaess 53d. |
| BYH-0000049 | Arameische Flexionsvarianten und לי/ליה; im Englischen sinnentsprechend, wortgleich zum eigenen Kopfband. |
| BYH-0000055 | Rava/Tigris-Formulierung mit/ohne Praeposition; der Kommentar behandelt das Anschwellen des Flusses und Ravas Gang dorthin. Der vom Autor ausgelegte Schlussruf ist laenger als im Kopfband und wird nur im Kommentar wiedergegeben. |
| BYH-0000065 | Zweite Person דחקת gegen Kopfband דחקא; Autorenfassung nach dem gemeinsamen EN-Lemma gemaess 53d erhalten. |
| BYH-0000067 | די לא / דלא: gleicher Satzsinn; die Autoreninterpretation als Selbsterniedrigung im Kommentar vollstaendig uebersetzt. |

## Verbleibende Quellenfragen und Unsicherheiten, einzeln

Die technischen Prüfungen erkennen keine verbleibenden Fehler in Struktur oder Füllung. Die folgenden Sach- und Lesefragen werden ausdrücklich offengelegt; Quellenbehauptungen wurden weder erfunden noch stillschweigend berichtigt.

| Segment-ID | Art | Befund |
|---|---|---|
| BYH-0000002 | Quellenzuordnung | daf=5a bei ref=Moed Katan 5b:1; bereits im Ausgangsmaster. Gegenpruefung meldet Nachbarblatt, A–F bleiben ohne Befund. Attribute nicht geaendert. |
| BYH-0000003 | Rechnung | 86 + 295 = 381; ישע hat 380. Die Gleichsetzung des Autors ist erhalten, nicht berichtigt. |
| BYH-0000006 | Bezugsumfang | Der erste Satz spricht von 24 Versen im Psalm „Remember, HaShem, for David“. Erst anschliessend nennt der Autor Psalmen 132, 133 und 134 gemeinsam: 18 + 3 + 3 = 24. Diese Abfolge und ihre anfaengliche Verkuerzung bleiben erhalten. |
| BYH-0000007 | Buchstabenzahl | Die ausgeschriebene Formel שאו שערים ראשיכם והנשאו פתחי עולם ויבוא מלך הכבוד hat 41 Buchstaben. Der Autor nennt 39; כוזו hat tatsaechlich den Zahlwert 39. Keine stille Angleichung. |
| BYH-0000008 | Vokalrechnung | לב = 32, בן = 52. Unter der ueblichen Punktwertung Segol = 30 ergibt sich 62; mit Zere = 20 waeren es 52. Der Autor schreibt ausdruecklich Segol und spricht danach ueber Zere. Konvention/Lesart bleibt Prueffall. |
| BYH-0000012 | Quellenwortlaut | Der boese Trieb wird im erhaltenen HE-Text als Hausherr „בעולם הבא בגוף האדם“ bezeichnet. EN erhaelt „in the World to Come within the human body“; ein moeglicher Schreibfehler הבא/הזה wird nicht repariert. |
| BYH-0000016 | Namensvariante | Kopfband: Adda der Fischer; im Autorenkommentar spaeter Abba der Fischer. Beide Namen bleiben entsprechend der jeweiligen Quelle erhalten. |
| BYH-0000022 | Rechnung | בול = 38; der Autor schreibt 48 und verbindet dies mit den 48 Erwerbsweisen der Torah. EN erhaelt 48. Keine Korrektur von HE oder Autorenbehauptung. |
| BYH-0000028 | Namensvariante | Kopfband: Zutra bar Toviyya; der Kommentar spricht von Mar Zutra. Beide Formen bleiben erhalten. מהרש"ל wird hier ausschliesslich als der ausdruecklich belegte R. Shemuel Laniado gelesen. |
| BYH-0000032 | Arabische Woerter | זרנטא"ח und כ"ס sind im Kontext keine Abkuerzungen. Der Autor erklaert Wurm bzw. Salat. Die lateinischen Formen zarnatah/khass sind Umschriften; die genaue Vokalisierung von זרנטא"ח ist in den beiden Quellen nicht gesichert. |
| BYH-0000034 | Namensverweis | Der Autorenkommentar nennt in der wiederaufgenommenen Frauengeschichte Rabbi Natan, waehrend BYH-0000027 Rav Nahman nennt. EN erhaelt Rabbi Natan an dieser Stelle; keine Harmonisierung. |
| BYH-0000046 | Offenes Kuerzel | הרי"ף wird nur als „the Rif“ wiedergegeben. Die Quellen legen hier weder R. Yitzhak Alfasi noch R. Yoshiyahu Pinto sicher fest; keine erfundene Personenfussnote. |
| BYH-0000048 | Vom Autor beanstandete Zuordnung | Der Autor selbst unterscheidet Rav Huna, den Exilarchen zur Zeit Rabbis, von Rav Huna, Ravs Schueler und Rav Hisdas Lehrer, und vermutet einen Kopistenfehler. Diese Kritik wird uebersetzt; die Zuordnung wird nicht eigenmaechtig repariert. |
| BYH-0000056 | Klammerlesart und Umschrift | Kopfband enthaelt die Varianten (למחלציא) [למחצליא]; EN bietet (smooth) [like mats]. Die genaue Nuance der ersten Klammerlesart bleibt sprachlicher Prueffall. שי"ץ ist das vom Autor erklaerte arabische Wort fuer harte, unbrauchbare Datteln, kein Akronym; Umschrift shitz ohne gesicherte Vokalisierung. |
| BYH-0000064 | Pronomen der Quelle | Im Autorenkommentar steht beim Gespraech mit dem Todesengel אמר לה, „told her“. EN erhaelt dieses Pronomen; keine Angleichung an andere Fassungen der erwaehnten Geschichte. |
| BYH-0000069 | Mehrteiliges Lemma / Buchstabenspiel | G-Sichtliste: Das vorhandene aus mehreren fetten Stuecken gewonnene HE-Lemma enthaelt nur die Talmudstelle; der abschliessende Schraegstrich bleibt im geschuetzten HE erhalten. EN enthaelt genau ein wortgleiches Lemma. Erste Fuellung mit הא: 207; zweite mit הה: 211 = פני הודנו. Der Wechsel ist in Quelle und EN erhalten. Der Autor nennt die Buchstaben von תל כוס „vor“ שכינה; alphabetische Nachfolger ergeben תלכסו, dessen Buchstaben sich zu תלכוס umstellen lassen. Die Richtungs-/Umstellungsformulierung des Autors bleibt ungeaendert. |

Die 32 protokollierten Zahlen-/Buchstabenprüfungen stehen in `Audit/numerical_audit.json`; 4 sind als PRUEFEN markiert. Das ist keine Korrekturfreigabe. Quellennummerierungen und vom Autor wiedergegebene Aussagen anderer Werke wurden nach der Vorlage übersetzt, ohne fremde Textfassungen einzusetzen.

## Prüfdateien und Wiederholung

`Audit/Validator_EN_FERTIG.txt/.json` und `Audit/Gegenpruefung_EN_FERTIG.txt/.json` enthalten die unveränderten Skriptausgaben; die entsprechenden Ausgangsläufe liegen daneben. `Audit/Einzelprueffaelle.json` enthält die Quellenfragen maschinenlesbar. Ausgangsmaster, ursprüngliche Moed-Katan-TSV und ursprüngliche JSON sind separat im Audit-Verzeichnis gesichert.

Nach dem Entpacken des vorgeschriebenen Pipeline-Archivs lassen sich die Prüfungen wiederholen:

```sh
python3 by_validate.py --in Ben_Yehoyada_Moed_Katan_Band_01_BILINGUAL_EN_FERTIG.txt --expect 69 --json Validator_EN_FERTIG.json
python3 by_gegenpruefung.py Ben_Yehoyada_Moed_Katan_Band_01_BILINGUAL_EN_FERTIG.txt "Ben Yehoyada on Moed Katan - he - Senlake edition 2019 based on Ben Yehoyada, Jerusalem, 1897.txt" "מועד_קטן.combinedfullhaser.txt" --uebersetzt --json Gegenpruefung_EN_FERTIG.json
python3 Audit/verify_master.py Audit/Ausgangsmaster_Moed_Katan_Band_01.txt Ben_Yehoyada_Moed_Katan_Band_01_BILINGUAL_EN_FERTIG.txt Feldvergleich_EN.json
```

Es wurde keine InDesign-Datei erstellt. Satz und Druck bleiben bis zur Freigabe des geprüften Masters ausgesetzt. Eine physische Seitenzahl wird aus dieser Textdatei nicht behauptet.
