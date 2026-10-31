# Megillah · Band 01 · Änderungs- und Prüfbericht

Stand: 31.10.2026. Verbindlich: EN-Anweisung 1.3 vom 24.09.2026 und Arbeitsanleitung 1.5 vom 05.10.2026 einschließlich 53c/53d. Prüfprogramme unverändert aus Pipeline v3.2.1.

Die Banddatei enthält 247 ausgefüllte englische Kommentare und 247 ausgefüllte englische Kopfbänder. Alle 247 englischen Lemmas stehen wortgleich im jeweiligen Kopfband. Der vollständige Bytevergleich außerhalb dieser zuvor leeren Zielfelder ist identisch. Es gibt weiterhin Quellen-, Wortlaut- und Lesefälle; sie sind unten mit Segment-ID einzeln offengelegt. **Eine technische Prüfung ist keine philologische Freigabe dieser Vorlagenstellen. Es wurde keine InDesign-Datei erstellt.**

## Eingänge und Abgrenzung

Keine benötigte Datei fehlt. Ausgangsmaster und Megillah-TSV sind die übergebenen Dateien. Die dazugehörige vorhandene Repository-JSON ist `glossary_he.json`: Sämtliche 279 TSV-Hauptlesarten entsprachen vor der Bearbeitung genau ihren he/en-Werten. Es wurde kein Glossar eines anderen Traktats verwendet. Zur vorgeschriebenen Prüfung neuer Kürzel wurden alle 34 aktuell im Repository enthaltenen Senlake-Dateien gelesen und gegen ihre Git-Blob-SHAs verifiziert. Die 34-Dateien-Prüfung erweitert die in der Arbeitsanleitung erwähnte historische 32-Dateien-Menge; sie ist kein Import anderer Traktatübersetzungen.

Repository-Eingangsstand: `ea5ed0ee1c28dbbac35ccbe8191a6fcda01e06c6`. Vorhandene JSON: Git-Blob `0cafeef12f9507c63e651da814d17ccb43651c9d`. Megillah-Senlake: `19048e384e698b11c8469ed43cd8545780a5b416`; Dicta-haser: `af4c4f20da06d34ab785abd7f59d6d30a88fec16`. Das Korpusmanifest und die Belegkontexte liegen unter `Audit/`.

Ausgangsmaster SHA-256: `5ccb71ff61769c7442f1e1ae5bf709d6618ec4af8b1c6acb964cbbd68ca720d1`. Ergebnis SHA-256: `4ef974ae16c18a527473d029278c601b37bdf599ad23721cf9f59161a9e9a97e`.

## Änderungen und technische Ergebnisse

| Prüfung | Ergebnis |
|---|---:|
| Segmente, Reihenfolge, IDs und sämtliche Attribute | 247 unverändert |
| `<he>` und `<band_he>` | je 247 bytegleich |
| Sämtliche übrigen geschützten Bytes einschließlich CDATA und vorhandener Fußnoten | identisch |
| HE-/EN-Dafüberschriften | je 39 unverändert |
| Neu gefüllte `<en>` / `<band_en>` | 247 / 247 |
| Wortgleiche englische Lemmas | 247 / 247 |
| Leere erwartete englische Zielfelder | 0 |
| Hebräische Zeichen / `<fn>` in `<band_en>` | 0 / 0 |
| Führende und abschließende Kopfbandellipsen | erhalten |
| Unzulässige Gottesnamen, Platzhalter, verschachtelte Fußnoten oder beschädigte englische Tags | 0 |
| Zusätzlicher Strukturprüfer | 0 Fehler |
| Pipeline-Validator | 0 FEHLER, 53 PRUEFEN |
| Gegenprüfung mit `--uebersetzt` | A–F jeweils OK |
| HE-Quellenabgleich | 247 / 247 wortgleich |
| Kopfband aus Dicta / bestehender Lemma-Rückfall | 246 / 1 |
| Bestehende HE-Fußnoten | 877 unverändert |

Die 53 Validatorhinweise bestanden bereits im Ausgangsmaster. Sie betreffen die Deckung des hebräischen Lemmas mit dem hebräischen Kopfband, nicht fehlende englische Felder. Englische Lemmas wurden exakt an den vorhandenen englischen Kopfbandwortlaut gebunden; wo der abweichende Autorenwortlaut benötigt wird, folgt eine druckfertige Klammer gemäß 53d. Senlake-Zitatbeigaben, die nicht im geschützten `<he>` stehen, wurden nicht als Kommentartext ergänzt. Nicht ausgeschriebene Gelehrtennamen wurden nicht aus bloßen Vermutungen expandiert.

Die Quellengegenprüfung verwendet eine getrennte, beigefügte Tagkorrekturdatei: Bei BYH-0000077, BYH-0000090 und BYH-0000119 werden lediglich auf mehrere `<small>`-Elemente verteilte Senlake-Zusatzklammern als ein Element gelesen. Kein Textzeichen der Rohquelle und kein geschütztes Masterfeld wurde geändert. Der Gegenprüfungsbericht nennt diese drei angewandten Tagkorrekturen ausdrücklich.

Sieben bereits vorhandene Nachbarblatt-Refs bleiben unverändert: BYH-0000002 (2b → 3a), BYH-0000045 (9a → 9b), BYH-0000105 (13b → 13a), BYH-0000127 (14a → 14b), BYH-0000147 (15a → 15b), BYH-0000167 (16a → 15b), BYH-0000246 (31b → 32a). Das sind Prüfhinweise der Quelldaten, keine neu erfundenen Blattzuweisungen.

## Glossarfortschreibung

Die bestehende JSON wurde fortgeschrieben und zusätzlich neben dem Band als identische Kopie ausgegeben. Alle 279 alten Schlüssel bleiben erhalten. Acht sichere globale Einträge wurden ergänzt; die TSV enthält nun 287 globale Zeilen und zwei ausdrücklich auf Megillah-Segmente beschränkte Kontextzeilen, insgesamt 289. Jeder TSV-Wert stimmt exakt entweder mit `abbreviations` oder mit der gekennzeichneten Kontextangabe in `_meta.megillah_band_01_translation` überein. Die zwei Kontextzeilen werden bewusst nicht global vom Pipeline-Resolver aktiviert.

| Neuer globaler Schlüssel | Auflösung | Beleg |
|---|---|---|
| חח״ן | Hokhmah, Hesed, Netzah | BYH-0000094, ausdrücklich im Kommentar |
| שה״י | Today is Shabbat | BYH-0000113, ausdrücklich im Kommentar |
| פה״י | Today is Pesah | BYH-0000113, ausdrücklich im Kommentar |
| מהרלב״ח | Rabbi Levi ben Haviv | BYH-0000129, Senlake-Erklärung |
| נהי״ם | Netzah, Hod, Yesod, Malkhut | BYH-0000149; einheitliche Korpusbelege |
| כה״ת | Name aus den Initialen kol ha-neshamah tehallel | BYH-0000177; ebenso Berakhot/Chagigah |
| הש״ית | HaShem, blessed be He | BYH-0000246, Schreibvariante von השי״ת |
| מהר״ן | our teacher Rabbi Natan | BYH-0000123; voller Name mit Shapira kontextuell durch Sotah/Bava Kamma belegt |

Nur kontextuell ergänzt: מא״א = Meorei Or (BYH-0000034) und הט״ז = Taz (BYH-0000247). Der Korpus belegt für beide andere Bedeutungen; deshalb keine gefährliche globale Hauptlesart. Zahlen, Buchstabengruppen, Buchstabenpluralformen und mit Gershayim markierte Fremdwörter wurden nicht zu erfundenen Abkürzungen gemacht.

Sechs vorhandene englische Glossarformen wurden ausschließlich nach der zwingenden Gottesnamenregel angepasst: אדנ״י → the Name HaShem; בעה״ו → with the help of G-d and His salvation; בעזה״י → with the help of HaShem, blessed be He; ה״י → may HaShem protect him; השי״ת → HaShem, blessed be He; ח״ו → Heaven forbid. Die hebräischen Glossarwerte bleiben dabei unverändert. Alte `alt`-Angaben und alle früheren Traktatmetadaten bleiben erhalten. Detailänderungen: `Audit/Glossaraenderungen.json`.

## Einzelne Quellen- und Lesefälle

Die folgenden Fälle sind getrennt von der technischen Fehlerzahl zu beurteilen. Insbesondere BYH-0000105 erfordert eine Entscheidung zur Quellenzuordnung. Keine der genannten geschützten Stellen wurde repariert.

| Segment-ID | Gegenstand | Befund / Behandlung |
|---|---|---|
| BYH-0000007 | Quellenwortlaut / Kürzel | Der geschützte Kommentar nennt „Elisha, den König“. EN gibt „King Elisha“ wieder. Die ungewöhnliche Titulatur bleibt ein Quellenprüffall. ש״ר bleibt Sh.R.; keine sicher belegte Auflösung. |
| BYH-0000009 | Unbestimmter Werktitel | כ״מ bleibt K.M.; eine ausgeschriebene Werkzuordnung ist nicht belegt. Keine erfundene Quellenfußnote. |
| BYH-0000022 | Milui-Rechnung | ירושלים soll ausgeschrieben תפארת entsprechen. Die Füllungen stehen nicht vollständig im Kommentar. Die offengelegte Vergleichsfüllung יוד ריש ואו שין למד יוד מם ergibt 1077; תפארת ergibt 1081. Andere beabsichtigte Schreibweisen sind nicht ausgeschlossen; im Englischen bleibt die Aussage des Autors stehen. |
| BYH-0000034 | Bestehende HE-Fußnote | מא״א ist hier Meorei Or, unmittelbar zuvor ausgeschrieben; die HE-Fußnote „מ + אריך אנפין“ passt nicht. Nur die englische Lesart und der getrennte Kontextglossareintrag wurden entsprechend gesetzt. |
| BYH-0000047 | Bestehende HE-Personenauflösung | מהר״ם אלשיך ist Rabbi Moshe Alshich, nicht Rabbi Meir. EN verwendet Moshe Alshich; die geschützte HE-Fußnote bleibt stehen. |
| BYH-0000051 | Bestehende HE-Personenauflösung | מהר״ם אלשיך ist Rabbi Moshe Alshich, nicht Rabbi Meir. EN verwendet Moshe Alshich; die geschützte HE-Fußnote bleibt stehen. |
| BYH-0000051 | Bestehende HE-Zahlenfußnote | ע״ב und ק״ל sind hier 72 und 130; zusammen רב = 202. Die an ק״ל angehängte Fußnote „=רב 202“ ist nur als Summenhinweis nachvollziehbar, nicht als Wert von ק״ל allein. |
| BYH-0000061 | Geographischer Ausdruck | אלקי״ם / אלקמי״ם bezeichnet hier ein geographisches Klima bzw. einen Erdteil. Die automatische Gottesnamen-Fußnote bei באלקי״ם ist im Kontext falsch; EN übersetzt „clime“. Die Fremdwortschreibung wird nicht als neue lexikalische Abkürzung erfunden. |
| BYH-0000064 | Schreibungsabhängige Gematria | Der Kommentar wechselt zwischen בלשצר (622) und בלשצאר (623). Die genannte 623 passt zur Form mit Alef; der genannte Unterschied 821 − 623 = 198 passt zu צחק. חיצים hat dagegen den Wert 158, nicht 198. EN bewahrt die Quellenbehauptungen; beide Lesefragen bleiben offen dokumentiert. |
| BYH-0000075 | Gematria-Abweichung | צרעת זנב ergibt bereits 819, mit der genannten Gesamteinheit 820. Die im Kommentar ausgeschriebene Namensfüllung ויו שין תיו יוד ergibt 818. EN bewahrt die Angabe 819 und korrigiert den geschützten Text nicht. |
| BYH-0000081 | Kontextauflösung / Person offen | בי״ד wird nach der vorhandenen JSON-Kontextangabe als „in Ya’arot Devash“ gelesen, nicht als „court of law“. Der Personenname מהר״י bleibt Mahari; die automatische Festlegung auf Yaakov wird nicht übernommen. |
| BYH-0000089 | Buchstabenwortlaut | Der Quelltext druckt in der Zusammensetzung des Gottesnamens die Folge ה׳ים. Sie bleibt im englischen Buchstabenargument sichtbar; die auffällige Schreibweise wird nicht stillschweigend durch eine passendere ersetzt. |
| BYH-0000097 | Bestehende HE-Fußnote | בי״ד wird entsprechend der vorhandenen JSON-Kontextangabe als „in Ya’arot Devash“ gelesen. HE „בית דין“ bleibt unverändert. |
| BYH-0000105 | Wesentliche Kopfband-Zuordnung | daf=13b, ref=Megillah 13a:11: Das Kopfband behandelt Esther/Hadassah und ihre Namen; der Kommentar setzt bei Esthers Verschwiegenheit an. Nur ein kurzer Wortlaut ist gemeinsam. Englisches Lemma ist exakt im unveränderten Kopfband enthalten; der abweichende Autorenwortlaut steht nach Regel 53d in einer Klammer. Die sachlich schwache Zuordnung bleibt zur Quellenentscheidung offen; keine Layoutfreigabe daraus ableiten. |
| BYH-0000108 | Bestehende HE-Personenauflösung | מהר״ם אלשיך ist Rabbi Moshe Alshich, nicht Rabbi Meir. EN verwendet Moshe Alshich; die geschützte HE-Fußnote bleibt stehen. |
| BYH-0000113 | Bestehende HE-Kürzelauflösung | שה״י = שבת היום und פה״י = פסח היום sind im Kommentar selbst erklärt. HE „ש + השם ישמרהו“ ist falsch. Die beiden sicheren fehlenden Einträge wurden in TSV und JSON ergänzt. |
| BYH-0000119 | Personenauflösung offen | ר״י bleibt R.Y. Die automatische HE-Auflösung „Rabbi Yehudah“ ist durch die vorliegenden Belege nicht sicher. Der entfernte längere Senlake-Zusatz wird nicht als Kommentarübersetzung eingefügt. |
| BYH-0000123 | Bestehende HE-Kürzelauflösung | מהר״ן שפירא wird durch die Parallelstelle in Sotah und die ausgeschriebene Senlake-Erklärung in Bava Kamma als Rabbi Natan Neta Shapira belegt. HE „מ + רבנו נסים“ bleibt unverändert; EN verwendet den belegten Namen. |
| BYH-0000124 | Personenauflösung offen | מהר״א נחום bleibt Mahar.A. Nahum. Der Korpus verwendet מהר״א für mehrere verschiedene Vornamen; ein nicht belegter Vorname wird nicht eingesetzt. |
| BYH-0000127 | Bestehende HE-Zahlenfußnote | דף מ״ד ist Daf 44, nicht „the one who says“. EN liest die Stellenangabe als 44; HE bleibt unverändert. |
| BYH-0000129 | Quellendivergenz / Person offen | Das Kopfband und das hebräische Lemma nennen 3 Parasangen; die nachfolgende Auslegung nennt 4. EN erhält beide Zahlen an ihrer jeweiligen Stelle. הרי״ף bleibt „the Rif“; Alfasi/Pinto ist nicht sicher unterschieden. |
| BYH-0000130 | Personenauflösung offen | מהר״י bleibt Mahari. Die feste automatische Auflösung auf Rabbi Yaakov ist für die konkrete Referenz nicht sicher belegt. |
| BYH-0000140 | Abweichende Sprecherangabe | Kopfband: Rabbi Yirmeyah; Autorenlemma und Kommentar: Shemuel. Beide Angaben werden an ihrem Ort übersetzt; die Abweichung wird im englischen Anschluss nach 53d sichtbar. |
| BYH-0000158 | Quellenzahl | כת = 420; der Kommentar nennt jedoch ת״ק = 500 Jahre. EN bewahrt 500. Keine stillschweigende Änderung auf 420. |
| BYH-0000161 | Abweichender Titel | Kopfband nennt an der zweiten Stelle Rabbi Gamliel; Autorenlemma nennt Rabban Gamliel. EN bewahrt den jeweiligen Wortlaut und weist die Lesart nach 53d aus. |
| BYH-0000165 | Bestehende HE-Zahlenfußnoten | בי״ד אמות = 14 Cubits, nicht court of law; כ״ד = 24, nicht „thus are the words of“. EN folgt den Zahlenkontexten. Alle sechs Differenzrechnungen der Stablänge wurden nachgerechnet. |
| BYH-0000167 | Bestehende HE-Personenauflösung | מהר״ם אלשיך ist Rabbi Moshe Alshich, nicht Rabbi Meir. EN verwendet Moshe Alshich; die geschützte HE-Fußnote bleibt stehen. |
| BYH-0000169 | Personenauflösung offen | מהר״י bleibt Mahari. Die feste automatische Auflösung auf Rabbi Yaakov ist für die konkrete Referenz nicht sicher belegt. |
| BYH-0000173 | Abweichende Lesung | Das Kopfband hat זוזא (als zuz wiedergegeben), das Autorenlemma זוגא (pair of scissors). EN bewahrt die Kopfbandlesung und druckt die Autorenlesung in der 53d-Klammer. Quellenentscheidung offen. |
| BYH-0000176 | Offengelegte Rechenkonvention | Die Differenz כוכבים − עפר = שח ist mit erweitertem Schluss-Mem 600 nachvollziehbar: 658 − 350 = 308. Mit Standardwerten ergibt sie −252. Die erweiterte Schlussbuchstabenrechnung wird im Audit offengelegt und nicht als neuer Erklärungssatz in den Kommentar eingefügt. |
| BYH-0000189 | Präzisierung der Milui-Fußnote | Voller Milui שין דלת יוד = 814, Zusatzbuchstaben allein = 500. EN versteht miluo hier als Zusatzwert, passend zur anschließenden Rechnung 6 × 500 = 12 × 250. Die verkürzte HE-Fußnote bleibt unangetastet. |
| BYH-0000194 | Personenauflösung offen | הרי״ף bleibt „the Rif“. Die feste HE-Zuordnung zu Alfasi ist im aggadischen Kontext nicht gesichert; mögliche Zuordnung zu Pinto wird nicht als Tatsache eingesetzt. |
| BYH-0000204 | Personenauflösung offen | מהר״י bleibt Mahari. Die feste automatische Auflösung auf Rabbi Yaakov ist für die konkrete Referenz nicht sicher belegt. |
| BYH-0000206 | Lesewendung | Der Kommentar schreibt דוק בבכי. Die Bedeutung wird nach dem eindeutigen Mahlzeitkontext und der im selben Autorenkorpus ausdrücklich erklärten Wendung דוק בככי („grind with the teeth“, Shabbat) gelesen. EN erhält zusätzlich die überlieferte Form duk bivkhi. Die Abweichung Bet/Kaf bleibt ein offener Schreibungsprüffall; Beleg in Audit/Lesefall_BYH-0000206.txt. |
| BYH-0000217 | Zwei Gematria-Abweichungen | שין תיו ergibt 776 statt der genannten 766; משיסה ergibt 415 statt 766. EN bewahrt 766 und die Buchstabenargumente. Keine erfundene Harmonisierung. |
| BYH-0000234 | Auslegungswortlaut | Das Kopfband spricht von einer Trauerrede, bei der Rav Sheshet / Rav Hisda anwesend ist; die Autorenlesung בי wird im Kommentar als „im Haus von“ ausgelegt. EN hält beide Ebenen durch die 53d-Klammer auseinander. Der gedrängte Satz zur Zukunftsform in Rashi bleibt lektoratsbedürftig. |
| BYH-0000239 | Erweitertes Autorenlemma | Das Autorenlemma nennt zusätzlich „able / unable“, während das Kopfband die Frage nach dem Zurücktreten nennt. Der Zusatz wird ausschließlich in der 53d-Klammer des Kommentars übersetzt. |
| BYH-0000241 | Abweichender Geltungsbereich | Kopfband: in Babylonia; Autorenlemma: outside the Land. Beide Wortlaute bleiben in ihren englischen Feldern erhalten; kein eigenmächtiges Vereinheitlichen. |
| BYH-0000245 | Bestehende HE-Personenauflösung | מהר״ם אלשיך ist Rabbi Moshe Alshich, nicht Rabbi Meir. EN verwendet Moshe Alshich; die geschützte HE-Fußnote bleibt stehen. |
| BYH-0000246 | Bestehende HE-Zahlenfußnote | ש״ס שעות meint 360 Stunden, nicht die sechs Ordnungen des Talmuds. EN verwendet 360. 15 × 24 = 6 × 60 = 360 ist geprüft. |
| BYH-0000247 | Lemma-Sichtliste G / Kontextglossar | Das vorhandene mehrteilige hebräische Lemma bleibt als ein vollständiges englisches Lemma erhalten; der Wortlaut steht exakt im englischen Kopfband. הט״ז ist im Kontext der Taz, aber global auch eine Zahl; nur eine ausdrücklich segmentgebundene TSV-/JSON-Kontextangabe wurde hinzugefügt. |

## Numerische Nachrechnung

`Audit/Gematria_Nachrechnung.json` enthält 83 explizite Vergleichsrechnungen: 75 stimmen unter der jeweils offengelegten Konvention, acht Vergleiche bleiben in den fünf Segmenten BYH-0000022, BYH-0000064, BYH-0000075, BYH-0000158 und BYH-0000217 offen. Die Wortlautwerte sind im EN nicht durch eigene Zahlen ersetzt worden. Sonderkonventionen wie Schluss-Nun 700 (BYH-0000125), Schluss-Mem 600 (BYH-0000176) und Zusatzwert statt vollem Milui (BYH-0000189) sind getrennt dokumentiert. Die Rechnung ist mit dem beigefügten Skript reproduzierbar; sie ersetzt kein Quellenlektorat.

## Alle 53 unveränderten Validator-Prüfhinweise

| Segment-ID | Code | Meldung |
|---|---|---|
| BYH-0000001 | band_wortlaut | Wortlaut weicht ab (Deckung 0.5) — Stelle einzeln ansehen |
| BYH-0000002 | band_wortlaut | Wortlaut weicht ab (Deckung 0.375) — Stelle einzeln ansehen |
| BYH-0000005 | band_wortlaut | Wortlaut weicht ab (Deckung 0.615) — Stelle einzeln ansehen |
| BYH-0000026 | band_wortlaut | Wortlaut weicht ab (Deckung 0.818) — Stelle einzeln ansehen |
| BYH-0000032 | band_wortlaut | Wortlaut weicht ab (Deckung 0.714) — Stelle einzeln ansehen |
| BYH-0000043 | band_wortlaut | Wortlaut weicht ab (Deckung 0.429) — Stelle einzeln ansehen |
| BYH-0000044 | band_wortlaut | Wortlaut weicht ab (Deckung 0.524) — Stelle einzeln ansehen |
| BYH-0000046 | band_wortlaut | Wortlaut weicht ab (Deckung 0.533) — Stelle einzeln ansehen |
| BYH-0000050 | band_wortlaut | Wortlaut weicht ab (Deckung 0.842) — Stelle einzeln ansehen |
| BYH-0000051 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000052 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000053 | band_wortlaut | Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen |
| BYH-0000079 | band_wortlaut | Wortlaut weicht ab (Deckung 0.625) — Stelle einzeln ansehen |
| BYH-0000082 | band_wortlaut | Wortlaut weicht ab (Deckung 0.846) — Stelle einzeln ansehen |
| BYH-0000083 | band_wortlaut | Wortlaut weicht ab (Deckung 0.5) — Stelle einzeln ansehen |
| BYH-0000095 | band_wortlaut | Wortlaut weicht ab (Deckung 0.533) — Stelle einzeln ansehen |
| BYH-0000100 | band_wortlaut | Wortlaut weicht ab (Deckung 0.826) — Stelle einzeln ansehen |
| BYH-0000104 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000105 | band_wortlaut | Wortlaut weicht ab (Deckung 0.429) — Stelle einzeln ansehen |
| BYH-0000109 | band_wortlaut | Wortlaut weicht ab (Deckung 0.625) — Stelle einzeln ansehen |
| BYH-0000114 | band_wortlaut | Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen |
| BYH-0000116 | band_wortlaut | Wortlaut weicht ab (Deckung 0.577) — Stelle einzeln ansehen |
| BYH-0000120 | band_wortlaut | Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen |
| BYH-0000121 | band_wortlaut | Wortlaut weicht ab (Deckung 0.615) — Stelle einzeln ansehen |
| BYH-0000124 | band_wortlaut | Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen |
| BYH-0000130 | band_wortlaut | Wortlaut weicht ab (Deckung 0.812) — Stelle einzeln ansehen |
| BYH-0000137 | band_wortlaut | Wortlaut weicht ab (Deckung 0.778) — Stelle einzeln ansehen |
| BYH-0000139 | band_wortlaut | Wortlaut weicht ab (Deckung 0.364) — Stelle einzeln ansehen |
| BYH-0000140 | band_wortlaut | Wortlaut weicht ab (Deckung 0.5) — Stelle einzeln ansehen |
| BYH-0000146 | band_wortlaut | Wortlaut weicht ab (Deckung 0.714) — Stelle einzeln ansehen |
| BYH-0000148 | band_wortlaut | Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen |
| BYH-0000156 | band_wortlaut | Wortlaut weicht ab (Deckung 0.647) — Stelle einzeln ansehen |
| BYH-0000158 | band_wortlaut | Wortlaut weicht ab (Deckung 0.643) — Stelle einzeln ansehen |
| BYH-0000159 | band_wortlaut | Wortlaut weicht ab (Deckung 0.5) — Stelle einzeln ansehen |
| BYH-0000161 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000163 | band_wortlaut | Wortlaut weicht ab (Deckung 0.692) — Stelle einzeln ansehen |
| BYH-0000164 | band_wortlaut | Wortlaut weicht ab (Deckung 0.556) — Stelle einzeln ansehen |
| BYH-0000167 | band_wortlaut | Wortlaut weicht ab (Deckung 0.6) — Stelle einzeln ansehen |
| BYH-0000173 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000177 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000184 | band_wortlaut | Wortlaut weicht ab (Deckung 0.375) — Stelle einzeln ansehen |
| BYH-0000191 | band_wortlaut | Wortlaut weicht ab (Deckung 0.714) — Stelle einzeln ansehen |
| BYH-0000192 | band_wortlaut | Wortlaut weicht ab (Deckung 0.52) — Stelle einzeln ansehen |
| BYH-0000193 | band_wortlaut | Wortlaut weicht ab (Deckung 0.778) — Stelle einzeln ansehen |
| BYH-0000207 | band_wortlaut | Wortlaut weicht ab (Deckung 0.818) — Stelle einzeln ansehen |
| BYH-0000217 | band_wortlaut | Wortlaut weicht ab (Deckung 0.846) — Stelle einzeln ansehen |
| BYH-0000218 | band_wortlaut | Wortlaut weicht ab (Deckung 0.636) — Stelle einzeln ansehen |
| BYH-0000220 | band_wortlaut | Wortlaut weicht ab (Deckung 0.833) — Stelle einzeln ansehen |
| BYH-0000221 | band_wortlaut | Wortlaut weicht ab (Deckung 0.625) — Stelle einzeln ansehen |
| BYH-0000224 | band_wortlaut | Wortlaut weicht ab (Deckung 0.75) — Stelle einzeln ansehen |
| BYH-0000226 | band_wortlaut | Wortlaut weicht ab (Deckung 0.818) — Stelle einzeln ansehen |
| BYH-0000239 | band_wortlaut | Wortlaut weicht ab (Deckung 0.667) — Stelle einzeln ansehen |
| BYH-0000241 | band_wortlaut | Wortlaut weicht ab (Deckung 0.8) — Stelle einzeln ansehen |

## Reproduktion und Freigabegrenze

`python3 pruefen_megillah.py` prüft den mitgelieferten Ausgangsmaster gegen das Ergebnis, sämtliche Zielfelder und die TSV-/JSON-Konsistenz. Die Ausgabe liegt als `Ben_Yehoyada_Megillah_Band_01_Strukturvergleich.json` einschließlich Einzelstatus aller 247 IDs vor. Die unveränderten Pipelineprogramme wurden mit `--expect 247` beziehungsweise `--uebersetzt --quellkorrektur Megillah_Quellkorrekturen_Pruefung.json` ausgeführt; ihre Text- und JSON-Berichte liegen bei.

Der Name `_BILINGUAL_EN_FERTIG` bezeichnet die vollständig befüllte Banddatei, keine automatische Lektorats- oder Satzfreigabe. Die offenen Quellenentscheidungen sind vor einer solchen Freigabe zu behandeln. Es wurde kein InDesign-Dokument und keine physische Seitenzahl behauptet.
