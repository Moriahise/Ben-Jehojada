# Ben Yehoyada · Yevamot · Band 01 · Änderungs- und Prüfbericht

Stand: 01.11.2026. Übersetzt: BYH-0000001–BYH-0000120; 40 Daf-Abschnitte, 6a–121b.

Die vollständige Banddatei ist ausgefüllt und technisch geprüft. Alle 120 englischen Lemmas kommen exakt im jeweiligen englischen Kopfband vor. Die unten genannten Quellenfragen bleiben zur redaktionellen Entscheidung offen. Eine Satzfreigabe ist damit nicht erteilt; es wurde keine InDesign-Datei erstellt.

## Verwendete Grundlagen

Repository: https://github.com/Moriahise/Ben-Jehojada, Ausgangscommit `1e55c1a92e7af302339e444af024700c13c51c29`. Maßgeblich sind die Übersetzungsanweisung EN Fassung 1.3 vom 24.09.2026 und die Arbeitsanleitung Fassung 1.5 vom 05.10.2026, einschließlich 53c und 53d.

Die Dateien `Ben_Yehoyada_Yevamot_Band_01_BILINGUAL.txt` und `Ben_Yehoyada_Yevamot_GLOSSAR.tsv` waren im abgerufenen Repository-Baum nicht vorhanden, lagen jedoch als Anlagen dieser Anfrage vollständig vor und wurden verwendet. Die bestehende zugehörige JSON im Repository heißt `glossary_he.json` (kein traktatspezifisch benannter JSON-Neubau), Quellblob `08b73cad5ae9f2af48ad029e3a2490f61571d852`. Keine für die Bearbeitung benötigte Datei war unerreichbar.

Als Referenz dienen die vorhandene Senlake-Datei zu Yevamot und `יבמות..combinedfullhaser.txt` aus Dicta. 34 Senlake-Quelldateien des genannten Commits wurden für Kontextbelege konsultiert; Manifest im Audit. Es wurde ausschließlich das Yevamot-TSV verwendet. Keine Glossardatei eines anderen Traktats wurde herangezogen. Bereits vorhandene Metadaten anderer Arbeiten in der gemeinsamen JSON bleiben erhalten.

## Änderungen und Schutzvergleich

| Prüfung | Ergebnis |
| --- | --- |
| Neu gefüllte <en> | 120 von 120 |
| Neu gefüllte <band_en> | 120 von 120 |
| Englische Lemmas | 120 von 120 wortgleiche Teilzeichenfolgen im eigenen <band_en> |
| IDs, Reihenfolge, Zahl, sämtliche Segmentattribute | Unverändert |
| <he>, <band_he> | Vollständig bytegleich |
| <he_title>, <en_title> | Je 40, unverändert |
| Alle Bytes außerhalb der Zielinhalte | Identisch mit Ausgangsmaster; einschließlich BOM, Tags, Überschriften und Zeilenenden |
| Bereits gefüllte englische Zielfelder | Keine vorhanden; alle Zielinhalte waren leer |
| Hebräische Zeichen / <fn> im englischen Kopfband | Je 0 |
| Führende/abschließende Auslassungspunkte | Erhalten |
| XML, CDATA, unterstützte Tags, Fußnotenverschachtelung | Ohne Befund |
| Verbotene Gottesnamenschreibungen / Platzhalter | 0 |

Der Bytevergleich maskiert ausschließlich die CDATA-Inhalte von <en> und <band_en>; das verbleibende vollständige Dokument ist identisch. Zusätzlich wurden Attribute und geschützte Felder einzeln verglichen. `protected_fields.json` und `EN_Abnahme.json` enthalten maschinenlesbare Ergebnisse.

## Abweichende Lemmas nach Arbeitsanleitung 53d

In elf Fällen reicht der Wortlaut im Kopfband nicht für das vollständige Kommentarlemma oder bietet eine andere Lesart. Das englische <lemma> ist deshalb am tatsächlich vorhandenen Kopfband ausgerichtet. Unmittelbar anschließend folgt die vorgeschriebene Klammer mit der abweichenden Ben-Yehoyada-Lesart. Der hebräische Text wurde nicht geändert. Damit bleibt kein englischer Lemmafehler offen.

Die folgenden Angaben stehen vollständig auch in `lemma_variants_53d.json`:

| Segment-ID | Englisches Lemma | Erhaltene Abweichung |
| --- | --- | --- |
| BYH-0000001 | You do not fear Shabbat itself, but Him who commanded concerning Shabbat; likewise, the reverence stated concerning the Temple means that you do not fear the Temple itself, but Him who commanded concerning the Temple. | [Ben Yehoyada's text opens: Just as the observance stated concerning Shabbat means that you do not fear Shabbat itself, but Him who commanded concerning Shabbat. It then makes the comparison with reverence for the Temple.] |
| BYH-0000005 | He applied this verse to him: ‘I was young and have grown old, yet I have not seen a righteous man forsaken, nor his offspring seeking bread.’ | [Ben Yehoyada's text opens: Does our colleague Azaryah have a son?] |
| BYH-0000018 | If his name was Yosef, they call him Yosef; if Yohanan, they call him Yohanan. | [Ben Yehoyada's text reads: If his name was Yosef, they call him Yosef; if Yaakov, they call him Yaakov.] |
| BYH-0000034 | These are the years of generations. | [Ben Yehoyada's text opens: ‘I shall fulfill the number of your days.’] |
| BYH-0000041 | The son of David will not come until all the souls in Guf are exhausted, as it is stated: ‘For the spirit before Me would be delayed,’ etc. | [Ben Yehoyada's text continues: ‘and the souls I have made.’] |
| BYH-0000046 | Any man without a wife lives without joy, without blessing, without goodness. | [Ben Yehoyada's text reads: Any Jew without a wife lives without joy, without blessing, without goodness.] |
| BYH-0000051 | Any man without a wife is not adam | [Ben Yehoyada's text reads: Any Jew without a wife is not adam.] |
| BYH-0000070 | ‘HaShem delivered me into hands from which I cannot rise.’ Rav Hisda said in Mar Ukva bar Hiyya's name: This is a bad wife with a large ketubah. | [Ben Yehoyada's text reads: Mar Ukva, without bar Hiyya.] |
| BYH-0000079 | Whoever does not engage in procreation is as though he sheds blood, as it is stated: ‘One who sheds man's blood, by man shall his blood be shed,’ | [Ben Yehoyada's text opens: Every [Jew] who does not engage in procreation.] |
| BYH-0000082 | This teaches that the Shekhinah rests upon no fewer than two thousand and two myriads of Israel. | [Ben Yehoyada's text opens: ‘When it rested, he said: Return, HaShem, to the myriads of thousands of Israel.’] |
| BYH-0000094 | ‘Shaul clothed David in his garments’—to his measure. | [Ben Yehoyada's text reads: What does ‘his garments’ mean? To his measure.] |

## Glossar und JSON

Das Yevamot-TSV enthält jetzt 288 statt 287 Einträge. Alle vorhandenen Zeilen bleiben inhaltlich unverändert. Neu ist `ר״ח → רַבִּי חִיָּיא → Rabbi Hiyya`, ausschließlich für `בי ר״ח` in BYH-0000077, im Kontext der Aussprache von Alef als Ayin. Die Auflösung wird als kontextuelle Ergänzung in `_meta.yevamot_band_01_translation.contextual_tsv_rows` der vorhandenen JSON gespiegelt. Keine globale Automatikregel wurde ergänzt, weil ר״ח andernorts Rosh Hodesh oder eine Zahl bezeichnen kann.

Die 287 vorhandenen globalen Abkürzungsschlüssel, sämtliche 22 Buchstabennamen und fremde Metadaten der JSON bleiben unverändert. Unsichere Personenkürzel stehen als Prüffälle in der JSON und unten einzeln. Zahlenangaben, alphabetische Formen und fremdsprachige Wörter mit Anführungszeichen wurden nicht als neue Abkürzungen erfunden. Beispiele: ל״א = 31; תתס״א = 861; פ״ו = 86; שורב״א = shorba; שמנדפי״ר = Eisenbahnbezeichnung; זא״ר = Würfel; לאהנ״א = örtliche Benennung des Kohls. Die durch fehlenden Wortabstand entstandene Suchform ז״לומה (BYH-0000090) ist kein eigenes Kürzel.

## Validatoren und Nachprüfung

Die unveränderten Originalskripte aus Pipeline v3.2.1 sind beigefügt.

| Lauf | Ergebnis |
| --- | --- |
| by_validate.py, Ausgangsmaster | 0 FEHLER, 22 PRUEFEN |
| by_validate.py, übersetzte Datei (normaler Lauf) | 0 FEHLER, 22 PRUEFEN; identische Quellhinweise |
| by_gegenpruefung.py --uebersetzt | A–F ohne Befund; 120/120 hebräische Absätze wortgleich mit Senlake |
| Dicta-Kopfbänder | 119 zusammenhängende Quellausschnitte; 1 erlaubter Lemma-Rückfall |
| G, mehrteilige Lemmas | 0 |
| Ergänzende englische Abnahme | Exit 0; keine Befunde |
| Geschützte Felder/Bytes | Alle Vergleiche bestanden |
| Gematria | 40 nachgerechnete Beziehungen; 39 stimmen, 1 Quellenfrage BYH-0000025 |

Wichtig zur Reproduzierbarkeit: Der zusätzliche Versuch mit `by_validate.py --against AUSGANGSMASTER` meldet 240 „geschuetzt_en/geschuetzt_band_en“-Befunde, da diese Skriptoption auch ursprünglich leere englische Felder unterschiedslos als unveränderlich vergleicht. Dies sind genau die 240 beauftragten Füllungen. Der Lauf wurde mit seinen Rohbefunden separat als `validation_against_full_fields.*` erhalten. Er ist kein Nachweis von 240 Übersetzungsfehlern. Der reguläre Validatorlauf und die ergänzende Prüfung, die leere Zielfelder korrekt behandelt und ALLE übrigen Bytes schützt, sind die maßgeblichen Prüfungen. Das Originalskript wurde dafür nicht verändert.

Reproduzierbare Befehle, aus dem entpackten Paketverzeichnis:

```bash
python3 Audit/by_validate.py --in Ben_Yehoyada_Yevamot_Band_01_BILINGUAL_EN_FERTIG.txt --expect 120
python3 Audit/by_gegenpruefung.py Ben_Yehoyada_Yevamot_Band_01_BILINGUAL_EN_FERTIG.txt Audit/Yevamot_Senlake.txt Audit/Yevamot_Dicta_haser.txt --uebersetzt
python3 Audit/english_audit.py Audit/Ben_Yehoyada_Yevamot_Band_01_AUSGANGSMASTER.txt Ben_Yehoyada_Yevamot_Band_01_BILINGUAL_EN_FERTIG.txt
```

Alle 22 PRUEFEN-Hinweise sind wortlautbezogene Hinweise des Ausgangsmasters; sie wurden gesichtet. Im Einzelnen:

| Segment-ID | Deckung laut Validator | Prüfvermerk |
| --- | --- | --- |
| BYH-0000001 | 0.808 | Kopfband beginnt später als das Kommentarlemma; Ergänzung nach 53d. |
| BYH-0000005 | 0.75 | Einleitende Frage fehlt im Kopfbandfenster; Ergänzung nach 53d. |
| BYH-0000009 | 0.8 | Schreibung/Zeichensetzung; englische Entsprechung deckungsgleich. |
| BYH-0000013 | 0.833 | Singular/Plural bei „Hirte“; englisches Lemma am Kopfband ausgerichtet. |
| BYH-0000016 | 0.833 | Schreibung von „ha-el“ und Versnachweis im Lemma; Quellenfußnote außerhalb des englischen Lemmas. |
| BYH-0000018 | 0.75 | Yaakov im Kommentar, Yohanan im Kopfband; beide Lesarten nach 53d sichtbar. |
| BYH-0000020 | 0.8 | Schreib-/Flexionsvariante bei der Beeinträchtigung der Schönheit; gleicher englischer Sinn. |
| BYH-0000025 | 0.667 | Ziffernabkürzung gegenüber ausgeschriebener Zahl 613; zusätzlich Zahlenprüffall unten. |
| BYH-0000026 | 0.667 | Versangabe und Trennzeichen; Fundstelle außerhalb des englischen Lemmas. |
| BYH-0000027 | 0.833 | Versangabe und Trennzeichen; zusätzlich Namensprüffall unten. |
| BYH-0000032 | 0.667 | Versangabe und Schreibweise der Festnamen; Entsprechung vollständig. |
| BYH-0000034 | 0.429 | Vorangehendes Schriftzitat fehlt im Kopfband; Ergänzung nach 53d. |
| BYH-0000038 | 0.75 | עכו״ם gegenüber הגוים; Sammelbezeichnung im Kontext; Buchstabenargument bleibt erhalten. |
| BYH-0000041 | 0.688 | Kopfband kürzt den Vers mit „etc.“; Fortsetzung nach 53d. |
| BYH-0000044 | 0.8 | נפטרו gegenüber מתו; beides hier „died“. |
| BYH-0000060 | 0.8 | Einleitendes „und sein Ausspruch“ sowie Schreib-/Flexionsvariante; englischer Zitierkern deckungsgleich. |
| BYH-0000077 | 0.75 | סודך gegenüber סוד; Wortargument סוד erhalten; ר״ח kontextuell glossiert. |
| BYH-0000082 | 0.611 | Schriftzitat vor dem Lehrsatz fehlt im Kopfband; Ergänzung nach 53d. |
| BYH-0000092 | 0.75 | Aramäische Schreib-/Flexionsvarianten; gleicher englischer Ausspruch. |
| BYH-0000100 | 0.778 | Bestimmte Artikel/Schreibweisen bei den drei Eigenschaften; gleiche englische Aufzählung. |
| BYH-0000116 | 0.833 | Aramäische Flexionsvariante; gleicher englischer Ausspruch. |
| BYH-0000119 | 0.833 | Verkürzung mit וכו׳ gegenüber längerer Erzählung; zitierter Ausspruch passt. |

Drei unveränderte Nachbarblatt-Verweise: BYH-0000001 (daf=6a, ref=Yevamot 6b:1); BYH-0000040 (daf=61b, ref=Yevamot 62a:6); BYH-0000100 (daf=78b, ref=Yevamot 79a:3). Die Gegenprüfung akzeptiert diese Zuordnungen; keine Attribute wurden geändert.

## Offene Quellen- und Identitätsfragen

Diese Hinweise betreffen den überlieferten Inhalt. Keine Auflösung oder Quellreparatur wurde erfunden. Jeder einzelne Fall ist mit Segment-ID angegeben:

| Segment-ID | Prüffall | Befund / Behandlung |
| --- | --- | --- |
| BYH-0000001 | מהר״י | Personenidentität des in Yoreh Deah zitierten Gaon nicht sicher belegt. Abgekürzt als Mahar Y belassen. |
| BYH-0000002 | Aharon „der König“ | Die Vorlage sagt אהרן המלך. Als „Aharon the king“ übersetzt; möglicher Quellfehler, keine stillschweigende Änderung zu „priest“. |
| BYH-0000005 | Exodus 20:11 | Die überlieferte Fundstelle zum Elterngebot bleibt erhalten. Die verbreitete andere Verszählung 20:12 wurde nicht still eingesetzt. |
| BYH-0000025 | Gematria 613 | ישראל = 541; die übliche Alef-Füllung יו״ד ה״א וא״ו ה״א = 45, zusammen 586 statt 613. Eine Yod-Füllung mit 72 ergäbe 613, ist aber nicht der überlieferte Wortlaut. Originalbehauptung übersetzt; siehe gematria_checks.json. |
| BYH-0000027 | Naomi/Ruth | Im Schlusssatz wird die erste Antwort Naomi zugeschrieben, obwohl Ruth im vorangehenden Gespräch antwortet. Quellzuordnung beibehalten. |
| BYH-0000047 | Doppelte Erklärung „ohne Gutes“ | Die Vorlage beginnt auch die Erklärung des Segens mit בלא טובה und wiederholt die Wendung anschließend. Beide Vorkommen erhalten. |
| BYH-0000048 | ר״א | Personenauflösung im Rückverweis nicht sicher. Keine erfundene Wahl zwischen Elazar/Eliezer. |
| BYH-0000070 | Buchstabenform היה | Die Vorlage enthält in der Wortzerlegung ausdrücklich היה; nicht eigenmächtig zu ה oder הי normalisiert. |
| BYH-0000079 | המשך מאן דאמר | Die Wendung steht bereits in der Senlake-Quelle in der kabbalistischen Erklärung der oberen Yod-Form. Bedeutung hier nicht sicher; vorsichtig als „a drawing down termed here man de-amar“ wiedergegeben. Nicht zu mayin dukhrin repariert. |
| BYH-0000083 | טובה und 22.000 | טובה = 22; die Auslegung bezieht den Wert auf 22 Einheiten von je tausend. Keine unmittelbare Gematria-Gleichheit 22 = 22.000 behauptet. |
| BYH-0000086 | הש״ך | Hier zur Torah, Vayetze, zitiert. Keine ungesicherte Identifikation mit dem gleichnamigen Yoreh-Deah-Kommentator. |
| BYH-0000086 | מהר״ם רקאנטי | Recanati steht ausdrücklich in der Vorlage; der Vorname ist aus dem unmittelbaren Kontext nicht gesichert. „Maharam Recanati“ beibehalten. |
| BYH-0000098 | מואבי ולא מואבי | Eine Stelle wiederholt in der Vorlage dieselbe Form; die anschließende Argumentation unterscheidet מואבי und מואב. Keine Konjektur in den geschützten Text eingesetzt; englischer Zusammenhang ohne erfundene neue Quelllesart. |
| BYH-0000103 | הרי״ף | „The Rif“ beibehalten; aus dem Kontext keine sichere persönliche Identifikation abgeleitet. |
| BYH-0000103 | Widersprüchliche Haftungszuordnung | Das Referat aus Ir Binyamin nennt zunächst den Auftraggeber haftbar und den Boten frei, während die folgende Auslegung die Gegenposition voraussetzt. Überlieferte Abfolge übersetzt, nicht durch die übliche Talmudformel ersetzt. |
| BYH-0000117 | מור״ם | „Moram“ beibehalten; keine sichere Zuordnung zu Isserles aus dem vorliegenden Nachweis. |
| BYH-0000117 | מהר״ם סוזין | „Maharam Suzin“ beibehalten; der Vorname wurde nicht erfunden. |
| BYH-0000117 | פסלקא דעתך | Diese auffällige Form steht bereits im Senlake-Original. Als pesalka daatakh sichtbar belassen; wahrscheinliche Text-/Abkürzungskorruption, ohne gesicherte Rekonstruktion. |
| BYH-0000118 | Begrenzte/unbegrenzte Gewässer, erste Stelle | Die Frage im zweiten Absatz sagt ausdrücklich: Erlaubnis nur in unbegrenzten Gewässern. Dies widerspricht dem zuvor formulierten Grundsatz und dem Kopfband. Als „unbounded waters“ übersetzt, Quelle nicht umgekehrt. |
| BYH-0000118 | Begrenzte/unbegrenzte Gewässer, zweite Stelle | Der Schlusssatz wiederholt die Erlaubnis nur bei unbegrenzten Gewässern. Gleicher Quellenwiderspruch; ebenfalls wörtlich beibehalten. |
| BYH-0000120 | Hanina/Nehunya | Der Kommentar nennt zuletzt Hanina als Brunnengräber; das Kopfband der Erzählung nennt Nehunya. Überlieferter Kommentarname erhalten. |

## Dateien und Freigabestand

Die Lieferung enthält den vollständigen englisch gefüllten Master, das aktualisierte Yevamot-TSV, die fortgeschriebene bestehende JSON, diesen Bericht und ein Audit-Verzeichnis mit Ausgangsdateien, Anleitungen, Quellenmanifest, Prüfskripten und Rohprotokollen. SHA256SUMS.txt hält die Dateistände fest.

Repository-Arbeitszweig für die Prüfung: https://github.com/Moriahise/Ben-Jehojada/tree/work/yevamot-band-01-en-20261101 . Keine Übernahme in main. Das vollständige Audit ist im mitgelieferten ZIP-Paket enthalten.

Technischer Abschluss: 0 offene englische Lemmafehler, 0 leere Zielfelder, 0 Änderungen an geschützten Inhalten. Die aufgeführten Quellenfragen bleiben offen; eine wissenschaftliche Satz-/Publikationsfreigabe obliegt der Projektleitung. Keine InDesign-Datei wurde erzeugt.

Master SHA-256: `b5d29fb89cb5e20b6f4a5e0d823e163e273dca4c234a3c2d32796a77691f41b7`. Ausgangsmaster SHA-256: `631f1fc252e11a638e5370a5789bcd82618493d96bf05215584306726426d3ea`.
