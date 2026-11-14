#target "InDesign"
#targetengine "RavPealimRunningHeaderManager_v100"

/*
    Rav Pe’alim · Kolumnentitel-Manager v1.0.0  (07.11.2026)
    Erzeugt mit Rav_Pealim/indesign/erzeuge_rp_jsx.py aus
    Ben_Ish_Chai_Running_Header_Manager_v1_0_3.jsx und rh_abschnitte_bausteine.js
    (Stand Leshon Chakhamim Kolumnentitel-Manager v1.0.4).

    Kolumnentitel = Siman-Ueberschrift der Seite, genau wie im Dokument: linke
    Seiten die englische Ueberschrift aus dem EN-Textfluss, rechte Seiten die
    hebraeische aus dem HE-Textfluss (Absatzformate "RPL · Section · English" /
    "RPL · Abschnitt · Hebräisch"): "RAV PE’ALIM · {ABSCHNITT}" /
    "רב פעלים · {ABSCHNITT_HE}". Vorlage "Gruppe" ({GRUPPE} = Abteilung · Teil)
    bleibt waehlbar.
      - Seitenregel (Reiter 1): Abschnitt am Seitenanfang (Standard), erste oder
        letzte Ueberschrift der Seite.
      - Platzmangel: Kurztitel je Siman aus der Pipeline ("Sod Yesharim 18",
        "Orach Chayim II:14"), dann kleinere Schrift bis zum Minimum, zuletzt
        wortweise Kuerzung mit "…", zuletzt nur der Werktitel; passt nichts,
        bleibt die Seite ohne Kopfrahmen (nie Uebersatz) und steht im Bericht.
      - Kopfrahmen werden bei jedem Lauf frisch angelegt und neutral gesetzt
        (keine geerbten Absatzformate, ganze Textkette ersetzt).
      - Fettung des Abschnittstitels standardmaessig aus.
      - kein Jahrgang ({YEAR} bleibt leer)
      - ExtendScript (ES3): test_rp.py prueft alle Skripte auf reservierte Woerter.
    Quelle sha256 efd9fb6548406d9d60fcd896bd9a82c375abbc3972f322134e1aa60ac7462651
*/

/*
    Ben Ish Chai · Running Header Manager v1.0.3
    Target: Adobe InDesign 18.1 / ExtendScript (ES3)

    Purpose
    -------
    Adds bilingual running headers retrospectively to finished Ben Ish Chai
    bilingual volumes without touching the Hebrew/English body-text geometry.

    Production convention
    ---------------------
      LEFT-HAND pages  : English running head + outer page number
      RIGHT-HAND pages : Hebrew running head + outer page number
      First page of each newly detected Parashah: running head remains visible
      and the Parashah name is emphasized in bold for orientation
      Front matter / excluded pages: no running head

    Primary title source
    --------------------
      1. The BILINGUAL.txt stored in the document label RPL_BILINGUAL_SOURCE
      2. InDesign paragraph styles RPL · Abschnitt · Hebräisch / English
      3. Built-in Parashah catalogue
      4. Manual page-range overrides

    v1.0.3
    ------
      - based on the clean v1.0.2 branch (which itself is directly based on v1.0.0)
      - Parashah start pages now KEEP their running header by default
      - on a Parashah start page only the Parashah portion is emphasized in bold
        (English: Parashah name; Hebrew: "פרשת + name" when present)
      - the former "hide first Parashah page" option remains available only as an optional legacy exception
      - no changes to page numbering, page-number labels, HE/EN body-frame geometry or Parashah detection
      - the v1.0.2 report listing of pages without a running header remains intact

    Safety
    ------
      - INDD backup before destructive actions (optional, default ON)
      - one-step Undo for each button action where InDesign supports ENTIRE_SCRIPT
      - body text frames RPL_HE_FRAME / RPL_EN_FRAME are never moved or resized
      - only page-number frames, dedicated header frames and optional top rules
        are created/updated/removed
*/

(function () {
    var APP_NAME = "Rav Pe’alim · Kolumnentitel-Manager";
    var VERSION = "1.0.0";

    // ---- Existing labels/styles from the bilingual book manager ----
    var FRAME_HE_LABEL = "RPL_HE_FRAME";
    var FRAME_EN_LABEL = "RPL_EN_FRAME";
    var PAGE_NUMBER_LABEL = "RPL_PAGE_NUMBER";
    var DOC_SOURCE_LABEL = "RPL_BILINGUAL_SOURCE";
    var DOC_VOLUME_LABEL = "RPL_VOLUME_NUMBER";
    var STYLE_HE_HEAD = "RPL · Abschnitt · Hebräisch";
    var STYLE_EN_HEAD = "RPL · Section · English";

    // ---- New labels ----
    var HEADER_FRAME_LABEL = "RPL_RUNNING_HEADER";
    var HEADER_RULE_LABEL = "RPL_RUNNING_HEADER_RULE";
    var HEADER_LAYER_NAME = "RPL · Kolumnentitel";
    var DOC_LAST_BACKUP_LABEL = "RPL_RUNNING_HEADER_LAST_BACKUP";
    var DOC_LAST_REPORT_LABEL = "RPL_RUNNING_HEADER_LAST_REPORT";
    var RULE_ORIGIN_KEY = "RPL_HEADER_RULE_ORIGIN";
    var RULE_OLD_WEIGHT_KEY = "RPL_HEADER_RULE_OLD_WEIGHT";

    // ---- Page geometry calibrated to the existing A5 production layout ----
    var PAGE_W_MM = 148;
    var DEFAULT_TOP_MM = 5.20;
    var DEFAULT_BOTTOM_MM = 11.50;
    var PAGE_NUM_LEFT_MM = 15.90;
    var PAGE_NUM_RIGHT_MM = 28.00;
    var HEADER_LEFT_MM = 31.50;
    var TEXT_RIGHT_MM = 128.57;
    var DEFAULT_RULE_Y_MM = 16.10;

    // ---- UI colours, same logic as the main book manager ----
    var UI_BLUE = [0.18, 0.43, 0.73, 1];
    var UI_GREEN = [0.16, 0.56, 0.31, 1];
    var UI_MAGENTA = [0.82, 0.20, 0.52, 1];
    var UI_ORANGE = [0.86, 0.49, 0.10, 1];
    var UI_TEXT_LIGHT = [1, 1, 1, 1];
    var UI_DISABLED = [0.36, 0.36, 0.36, 1];

    var state = {
        sourceFile: null,
        overrides: [],
        lastAnalysis: null
    };

    var PARASHOT = buildParashahCatalogue();
    var SECTIONS = buildSectionCatalogue();

    showPalette();

    // =====================================================================
    // UI
    // =====================================================================

    function showPalette() {
        try {
            var old = $.global.__RPL_RUNNING_HEADER_MANAGER_V103__;
            if (old && old.visible) { old.active = true; return; }
        } catch (_) {}

        var w = new Window("palette", APP_NAME + " v" + VERSION, undefined, {resizeable:true});
        $.global.__RPL_RUNNING_HEADER_MANAGER_V103__ = w;
        w.orientation = "column";
        w.alignChildren = "fill";
        w.margins = 12;
        w.spacing = 8;
        w.minimumSize = [990, 650];
        w.preferredSize = [1160, 860];

        var tabs = w.add("tabbedpanel");
        tabs.alignChildren = ["fill", "fill"];
        tabs.alignment = ["fill", "fill"];

        // -----------------------------------------------------------------
        // Tab 1: Source / analysis
        // -----------------------------------------------------------------
        var sourceTab = tabs.add("tab", undefined, "1 · Quelle & Analyse");
        sourceTab.orientation = "column";
        sourceTab.alignChildren = "fill";
        sourceTab.margins = 12;
        sourceTab.spacing = 9;

        addWorkflowLegend(sourceTab, [
            {label:"BLAU · Analyse / Quelle", color:UI_BLUE, tip:"Nicht-destruktive Erkennung der Parashah-Bereiche und der gespeicherten Bandquelle."},
            {label:"MAGENTA · Fallback", color:UI_MAGENTA, tip:"Ersatzwege, wenn Quelle oder Absatzformat nicht eindeutig verfügbar sind."}
        ]);

        var docPanel = sourceTab.add("panel", undefined, "Aktiver InDesign-Band");
        docPanel.orientation = "column";
        docPanel.alignChildren = "fill";
        docPanel.margins = 10;
        var docRow = docPanel.add("group");
        docRow.add("statictext", undefined, "Dokument:");
        var docInfo = docRow.add("edittext", undefined, "Kein Dokument erkannt", {readonly:true});
        docInfo.characters = 72;
        var refreshDocBtn = docRow.add("button", undefined, "Aktualisieren");

        var srcPanel = sourceTab.add("panel", undefined, "BILINGUAL-TXT · bevorzugte Titelquelle");
        srcPanel.orientation = "column";
        srcPanel.alignChildren = "fill";
        srcPanel.margins = 10;
        var srcRow = srcPanel.add("group");
        srcRow.add("statictext", undefined, "Banddatei:");
        var sourceEdit = srcRow.add("edittext", undefined, "");
        sourceEdit.characters = 68;
        var sourceFromDocBtn = srcRow.add("button", undefined, "Aus Dokumentlabel");
        var sourceChooseBtn = srcRow.add("button", undefined, "Auswählen …");
        var srcHelp = srcPanel.add("statictext", undefined,
            "Wenn die gespeicherte Datei nicht mehr am ursprünglichen Ort liegt, kann sie hier neu gewählt werden. Ohne TXT gilt der eingebaute Siman-Katalog (Kurztitel aus der Pipeline).",
            {multiline:true});
        srcHelp.preferredSize.width = 930;

        var analyzePanel = sourceTab.add("panel", undefined, "Erkennung");
        analyzePanel.orientation = "row";
        analyzePanel.alignChildren = ["left", "center"];
        analyzePanel.margins = 10;
        var analyzeBtn = analyzePanel.add("button", undefined, "Band analysieren");
        var yearMode = analyzePanel.add("dropdownlist", undefined, [
            "Jahr: Auto (nur wenn sicher)",
            "Jahr: FIRST YEAR / שנה ראשונה",
            "Jahr: SECOND YEAR / שנה שנייה",
            "Jahr im Header nicht verwenden"
        ]);
        yearMode.selection = 0;
        var bodyOnlyCheck = analyzePanel.add("checkbox", undefined, "Nur RPL-Textseiten");
        bodyOnlyCheck.value = true;
        var pageRuleList = analyzePanel.add("dropdownlist", undefined, [
            "Seitenregel: Abschnitt am Seitenanfang",
            "Seitenregel: erste Überschrift der Seite",
            "Seitenregel: letzte Überschrift der Seite"
        ]);
        pageRuleList.selection = 0;
        pageRuleList.helpTip = "Welche Überschrift im Kolumnentitel steht: der Siman, in dem die Seite beginnt (Standard; beginnt oben auf der Seite ein Siman, gilt er), der erste oder der letzte auf der Seite beginnende Siman.";
        bodyOnlyCheck.helpTip = "Header werden nur auf Seiten gesetzt, die RPL_HE_FRAME oder RPL_EN_FRAME enthalten. Das schützt nachträglich eingefügte Titel-/Impressumsseiten.";

        var analysisStatus = sourceTab.add("edittext", undefined,
            "Noch nicht analysiert.", {multiline:true, readonly:true, scrolling:true});
        analysisStatus.preferredSize = [940, 390];

        // -----------------------------------------------------------------
        // Tab 2: Design
        // -----------------------------------------------------------------
        var designTab = tabs.add("tab", undefined, "2 · Gestaltung");
        designTab.orientation = "column";
        designTab.alignChildren = "fill";
        designTab.margins = 12;
        designTab.spacing = 9;

        addWorkflowLegend(designTab, [
            {label:"GRÜN · Kolumnentitel setzen", color:UI_GREEN, tip:"Produktive Gestaltung der neuen Kolumnentitel."},
            {label:"ORANGE · Seitenzahl / Linie", color:UI_ORANGE, tip:"Bestehende Seitenzahlen werden nur im Kopfbereich repariert bzw. formatiert; der Fließtext bleibt unangetastet."}
        ]);

        var templatePanel = designTab.add("panel", undefined, "Textvorlage");
        templatePanel.orientation = "column";
        templatePanel.alignChildren = "fill";
        templatePanel.margins = 10;
        var templateRow = templatePanel.add("group");
        templateRow.add("statictext", undefined, "Vorlage:");
        var templateMode = templateRow.add("dropdownlist", undefined, [
            "Siman-Überschrift · empfohlen",
            "Gruppe (Abteilung · Teil)",
            "Benutzerdefiniert"
        ]);
        templateMode.selection = 0;
        var autoShortCheck = templateRow.add("checkbox", undefined, "Bei Platzmangel automatisch Kurztitel");
        autoShortCheck.value = true;

        var enTplRow = templatePanel.add("group");
        enTplRow.add("statictext", undefined, "Englisch:");
        var enTemplateEdit = enTplRow.add("edittext", undefined, "RAV PE’ALIM · {ABSCHNITT}");
        enTemplateEdit.characters = 82;
        var heTplRow = templatePanel.add("group");
        heTplRow.add("statictext", undefined, "Hebräisch:");
        var heTemplateEdit = heTplRow.add("edittext", undefined, "רב פעלים · {ABSCHNITT_HE}");
        heTemplateEdit.characters = 82;
        var tokenHelp = templatePanel.add("statictext", undefined,
            "Platzhalter: {ABSCHNITT} · {ABSCHNITT_HE} = Siman-Überschrift der Seite (genau wie im Dokument; bei Platzmangel Kurztitel, kleinere Schrift, zuletzt Kürzung mit …) · {GRUPPE} · {GRUPPE_HE} = Abteilung · Teil.",
            {multiline:true});
        tokenHelp.preferredSize.width = 930;

        var typePanel = designTab.add("panel", undefined, "Typografie");
        typePanel.orientation = "column";
        typePanel.alignChildren = "fill";
        typePanel.margins = 10;

        var enTypeRow = typePanel.add("group");
        enTypeRow.add("statictext", undefined, "EN Font:");
        var enFontEdit = enTypeRow.add("edittext", undefined, "Cambria"); enFontEdit.characters = 16;
        enTypeRow.add("statictext", undefined, "Schnitt:");
        var enStyleEdit = enTypeRow.add("edittext", undefined, "Regular"); enStyleEdit.characters = 10;
        enTypeRow.add("statictext", undefined, "Größe:");
        var enSizeEdit = enTypeRow.add("edittext", undefined, "7.5"); enSizeEdit.characters = 5;
        enTypeRow.add("statictext", undefined, "pt · Laufweite:");
        var enTrackingEdit = enTypeRow.add("edittext", undefined, "35"); enTrackingEdit.characters = 5;
        enTypeRow.add("statictext", undefined, "· Minimum:");
        var enMinSizeEdit = enTypeRow.add("edittext", undefined, "6.5"); enMinSizeEdit.characters = 5;

        var heTypeRow = typePanel.add("group");
        heTypeRow.add("statictext", undefined, "HE Font:");
        var heFontEdit = heTypeRow.add("edittext", undefined, "Keter YG"); heFontEdit.characters = 16;
        heTypeRow.add("statictext", undefined, "Schnitt:");
        var heStyleEdit = heTypeRow.add("edittext", undefined, "Medium"); heStyleEdit.characters = 10;
        heTypeRow.add("statictext", undefined, "Größe:");
        var heSizeEdit = heTypeRow.add("edittext", undefined, "8"); heSizeEdit.characters = 5;
        heTypeRow.add("statictext", undefined, "pt · Laufweite:");
        var heTrackingEdit = heTypeRow.add("edittext", undefined, "0"); heTrackingEdit.characters = 5;
        heTypeRow.add("statictext", undefined, "· Minimum:");
        var heMinSizeEdit = heTypeRow.add("edittext", undefined, "7"); heMinSizeEdit.characters = 5;

        var startTypeRow = typePanel.add("group");
        var emphasizeStartCheck = startTypeRow.add("checkbox", undefined, "Siman-Titel auf der Seite seines Beginns fett hervorheben");
        emphasizeStartCheck.value = false;
        emphasizeStartCheck.helpTip = "Der Kolumnentitel bleibt auf der Seite des Siman-Beginns sichtbar; nur der Titel wird stärker gesetzt.";
        startTypeRow.add("statictext", undefined, "EN-Schnitt:");
        var startEnStyleEdit = startTypeRow.add("edittext", undefined, "Bold"); startEnStyleEdit.characters = 10;
        startTypeRow.add("statictext", undefined, "HE-Schnitt:");
        var startHeStyleEdit = startTypeRow.add("edittext", undefined, "Bold"); startHeStyleEdit.characters = 10;
        startTypeRow.add("statictext", undefined, "(Fallback: Grundschnitt; wird im Ergebnis gemeldet)");

        var numTypeRow = typePanel.add("group");
        numTypeRow.add("statictext", undefined, "Seitenzahl:");
        var numFontEdit = numTypeRow.add("edittext", undefined, "Cambria"); numFontEdit.characters = 16;
        var numStyleEdit = numTypeRow.add("edittext", undefined, "Bold"); numStyleEdit.characters = 10;
        var numSizeEdit = numTypeRow.add("edittext", undefined, "8.5"); numSizeEdit.characters = 5;
        numTypeRow.add("statictext", undefined, "pt · Trennzeichen:");
        var separatorEdit = numTypeRow.add("edittext", undefined, "·"); separatorEdit.characters = 3;
        numTypeRow.add("statictext", undefined, "Header-Tonwert:");
        var tintEdit = numTypeRow.add("edittext", undefined, "85"); tintEdit.characters = 4;
        numTypeRow.add("statictext", undefined, "% Schwarz");

        var geoPanel = designTab.add("panel", undefined, "Position · A5");
        geoPanel.orientation = "row";
        geoPanel.alignChildren = ["left", "center"];
        geoPanel.margins = 10;
        geoPanel.add("statictext", undefined, "Rahmen oben:");
        var topEdit = geoPanel.add("edittext", undefined, String(DEFAULT_TOP_MM)); topEdit.characters = 6;
        geoPanel.add("statictext", undefined, "mm · unten:");
        var bottomEdit = geoPanel.add("edittext", undefined, String(DEFAULT_BOTTOM_MM)); bottomEdit.characters = 6;
        geoPanel.add("statictext", undefined, "mm · Abstand Zahl/Header: 3,5 mm · Headerbreite ≈ 97 mm");

        var rulePanel = designTab.add("panel", undefined, "Optionale feine Linie");
        rulePanel.orientation = "row";
        rulePanel.alignChildren = ["left", "center"];
        rulePanel.margins = 10;
        var ruleCheck = rulePanel.add("checkbox", undefined, "Vorhandene obere RPL-Linie als Headerlinie verwenden");
        ruleCheck.value = false;
        rulePanel.add("statictext", undefined, "Stärke:");
        var ruleWeightEdit = rulePanel.add("edittext", undefined, "0.25"); ruleWeightEdit.characters = 5;
        rulePanel.add("statictext", undefined, "pt · Y:");
        var ruleYEdit = rulePanel.add("edittext", undefined, String(DEFAULT_RULE_Y_MM)); ruleYEdit.characters = 6;
        rulePanel.add("statictext", undefined, "mm");

        // -----------------------------------------------------------------
        // Tab 3: fallback / exceptions
        // -----------------------------------------------------------------
        var fallbackTab = tabs.add("tab", undefined, "3 · Fallback & Ausnahmen");
        fallbackTab.orientation = "column";
        fallbackTab.alignChildren = "fill";
        fallbackTab.margins = 12;
        fallbackTab.spacing = 9;

        addWorkflowLegend(fallbackTab, [
            {label:"MAGENTA · Manuelle Fallbacks", color:UI_MAGENTA, tip:"Manuelle Parashah-Zuweisung für Seitenbereiche, wenn automatische Erkennung nicht genügt."},
            {label:"ORANGE · Ausnahmen", color:UI_ORANGE, tip:"Seiten, auf denen bewusst kein Kolumnentitel erscheinen soll."}
        ]);

        var hidePanel = fallbackTab.add("panel", undefined, "Automatische Ausblendung");
        hidePanel.orientation = "column";
        hidePanel.alignChildren = "left";
        hidePanel.margins = 10;
        var hideFirstCheck = hidePanel.add("checkbox", undefined, "Ausnahme: auf der Seite eines Siman-Beginns keinen Kolumnentitel setzen");
        hideFirstCheck.value = false;
        hideFirstCheck.helpTip = "Standard ab v1.0.3: Parashah-Startseiten behalten den Kolumnentitel. Diese Option nur aktivieren, wenn die frühere Ausblendregel ausdrücklich gewünscht ist.";
        var excludedRow = hidePanel.add("group");
        excludedRow.add("statictext", undefined, "Zusätzlich ohne Kolumnentitel · physische Dokumentseiten:");
        var excludedEdit = excludedRow.add("edittext", undefined, "");
        excludedEdit.characters = 38;
        excludedRow.add("statictext", undefined, "z. B. 1-8, 17, 22-24");

        var overridePanel = fallbackTab.add("panel", undefined, "Manueller Bereich (eigener Kolumnentitel)");
        overridePanel.orientation = "column";
        overridePanel.alignChildren = "fill";
        overridePanel.margins = 10;

        var ovRow1 = overridePanel.add("group");
        ovRow1.add("statictext", undefined, "Seiten:");
        var ovPagesEdit = ovRow1.add("edittext", undefined, ""); ovPagesEdit.characters = 15;
        ovRow1.add("statictext", undefined, "English:");
        var ovEnEdit = ovRow1.add("edittext", undefined, ""); ovEnEdit.characters = 24;
        ovRow1.add("statictext", undefined, "עברית:");
        var ovHeEdit = ovRow1.add("edittext", undefined, ""); ovHeEdit.characters = 24;

        var ovRow2 = overridePanel.add("group");
        ovRow2.add("statictext", undefined, "Jahr:");
        var ovYear = ovRow2.add("dropdownlist", undefined, ["Auto", "First Year", "Second Year", "kein Jahr"]);
        ovYear.selection = 0;
        var ovStartCheck = ovRow2.add("checkbox", undefined, "erste Bereichsseite = Siman-Beginn");
        ovStartCheck.value = true;
        var ovAddBtn = ovRow2.add("button", undefined, "Override hinzufügen");
        var ovRemoveBtn = ovRow2.add("button", undefined, "Markierten Override entfernen");
        var ovClearBtn = ovRow2.add("button", undefined, "Alle Overrides löschen");

        var overrideList = overridePanel.add("listbox", undefined, [], {
            multiselect:false,
            numberOfColumns:4,
            showHeaders:true,
            columnTitles:["Seiten", "English", "עברית", "Jahr"],
            columnWidths:[110, 220, 220, 110]
        });
        overrideList.preferredSize = [930, 240];

        var fallbackHelp = fallbackTab.add("statictext", undefined,
            "Ein Override überschreibt die automatische Erkennung nur im angegebenen Seitenbereich. Dadurch kann ein einzelner problematischer Abschnitt repariert werden, ohne den restlichen Band neu aufzubauen.",
            {multiline:true});
        fallbackHelp.preferredSize.width = 930;

        // -----------------------------------------------------------------
        // Tab 4: actions / validation
        // -----------------------------------------------------------------
        var actionTab = tabs.add("tab", undefined, "4 · Ausführen & Prüfen");
        actionTab.orientation = "column";
        actionTab.alignChildren = "fill";
        actionTab.margins = 12;
        actionTab.spacing = 9;

        addWorkflowLegend(actionTab, [
            {label:"GRÜN · Anwenden", color:UI_GREEN, tip:"Kolumnentitel erzeugen oder aktualisieren."},
            {label:"BLAU · Prüfen", color:UI_BLUE, tip:"Nicht-destruktive Kontrolle."},
            {label:"ORANGE · Sicherheit / Reparatur", color:UI_ORANGE, tip:"Backup, Entfernen und reine Seitenzahlreparatur."}
        ]);

        var safetyPanel = actionTab.add("panel", undefined, "Sicherheit");
        safetyPanel.orientation = "row";
        safetyPanel.margins = 10;
        var backupCheck = safetyPanel.add("checkbox", undefined, "Vor Änderungen INDD-Sicherung anlegen");
        backupCheck.value = true;
        var saveAfterCheck = safetyPanel.add("checkbox", undefined, "Dokument nach erfolgreichem Lauf speichern");
        saveAfterCheck.value = false;
        safetyPanel.add("statictext", undefined, "Jeder Lauf ist zusätzlich als ein Undo-Schritt angelegt, soweit InDesign dies unterstützt.");

        var applyPanel = actionTab.add("panel", undefined, "Produktiver Lauf");
        applyPanel.orientation = "row";
        applyPanel.margins = 10;
        var testSpreadBtn = applyPanel.add("button", undefined, "Aktuelle Doppelseite testen");
        var applyAllBtn = applyPanel.add("button", undefined, "Alle Kolumnentitel erstellen / aktualisieren");
        var validateBtn = applyPanel.add("button", undefined, "Kolumnentitel prüfen");

        var repairPanel = actionTab.add("panel", undefined, "Reparatur / Rückbau");
        repairPanel.orientation = "row";
        repairPanel.margins = 10;
        var numbersBtn = repairPanel.add("button", undefined, "Seitenzahlen außen reparieren");
        var removeBtn = repairPanel.add("button", undefined, "Nur Kolumnentitel entfernen");

        var actionStatus = actionTab.add("edittext", undefined,
            "Bereit.", {multiline:true, readonly:true, scrolling:true});
        actionStatus.preferredSize = [940, 390];

        // -----------------------------------------------------------------
        // Workflow colours and tips
        // -----------------------------------------------------------------
        styleWorkflowButton(refreshDocBtn, UI_BLUE, "Aktives Dokument und gespeicherte Bandquelle neu einlesen.");
        styleWorkflowButton(sourceFromDocBtn, UI_BLUE, "Den in RPL_BILINGUAL_SOURCE gespeicherten Pfad aus dem aktiven Band übernehmen.");
        styleWorkflowButton(sourceChooseBtn, UI_BLUE, "BILINGUAL.txt manuell wählen. Nützlich, wenn der Projektordner verschoben wurde.");
        styleWorkflowButton(analyzeBtn, UI_BLUE, "Parashah-Starts, Jahresangaben, Seitenbereiche und Fallbacks ermitteln. Es wird nichts verändert.");

        styleWorkflowButton(ovAddBtn, UI_MAGENTA, "Manuellen Seitenbereich als Parashah-Override hinzufügen.");
        styleWorkflowButton(ovRemoveBtn, UI_MAGENTA, "Nur den markierten manuellen Override entfernen.");
        styleWorkflowButton(ovClearBtn, UI_MAGENTA, "Alle manuellen Overrides aus dieser Sitzung löschen.");

        styleWorkflowButton(testSpreadBtn, UI_GREEN, "Nur die aktuell sichtbare Doppelseite mit den jetzigen Einstellungen setzen. Ideal zur optischen Kontrolle.");
        styleWorkflowButton(applyAllBtn, UI_GREEN, "Alle automatisch und manuell ermittelten Kolumnentitel im aktiven Band setzen bzw. aktualisieren.");
        styleWorkflowButton(validateBtn, UI_BLUE, "Erwartete und vorhandene Kolumnentitel sowie Seitenzahlen vergleichen. Es wird nichts verändert.");
        styleWorkflowButton(numbersBtn, UI_ORANGE, "Nur die äußeren Seitenzahlen auf den RPL-Textseiten reparieren/formatieren; keine Kolumnentitel erzeugen.");
        styleWorkflowButton(removeBtn, UI_ORANGE, "Alle vom Header-Manager erzeugten Kolumnentitel entfernen. Seitenzahlen bleiben bestehen.");

        // -----------------------------------------------------------------
        // UI event helpers
        // -----------------------------------------------------------------
        function activeDocOrThrow() {
            if (!app.documents.length) throw new Error("Kein InDesign-Dokument geöffnet.");
            return app.activeDocument;
        }

        function updateDocDisplay() {
            try {
                if (!app.documents.length) {
                    docInfo.text = "Kein Dokument geöffnet";
                    return;
                }
                var d = app.activeDocument;
                docInfo.text = d.name + " · " + d.pages.length + " Seiten · Band " + (d.extractLabel(DOC_VOLUME_LABEL) || "?");
                var p = d.extractLabel(DOC_SOURCE_LABEL);
                if (p && !sourceEdit.text) sourceEdit.text = p;
            } catch (e) {
                docInfo.text = "Dokument konnte nicht gelesen werden: " + errorText(e);
            }
        }

        function applyTemplatePreset() {
            var idx = templateMode.selection ? templateMode.selection.index : 0;
            if (idx === 0) {
                enTemplateEdit.text = "RAV PE’ALIM · {ABSCHNITT}";
                heTemplateEdit.text = "רב פעלים · {ABSCHNITT_HE}";
            } else if (idx === 1) {
                enTemplateEdit.text = "RAV PE’ALIM · {GRUPPE}";
                heTemplateEdit.text = "רב פעלים · {GRUPPE_HE}";
            }
        }

        function refreshOverrideList() {
            overrideList.removeAll();
            var i, ov, item;
            for (i = 0; i < state.overrides.length; i++) {
                ov = state.overrides[i];
                item = overrideList.add("item", ov.rangeText);
                item.subItems[0].text = ov.enTitle;
                item.subItems[1].text = ov.heTitle;
                item.subItems[2].text = ov.year === 1 ? "First" : (ov.year === 2 ? "Second" : (ov.year === 0 ? "kein" : "Auto"));
            }
        }

        function collectConfig() {
            var cfg = {};
            cfg.yearMode = yearMode.selection ? yearMode.selection.index : 0;
            cfg.bodyOnly = bodyOnlyCheck.value;
            cfg.pageRule = pageRuleList.selection ? pageRuleList.selection.index : 0;
            cfg.templateMode = templateMode.selection ? templateMode.selection.index : 0;
            cfg.enTemplate = String(enTemplateEdit.text || "");
            cfg.heTemplate = String(heTemplateEdit.text || "");
            cfg.shortEnTemplate = "RAV PE’ALIM · {PARASHAH}";
            cfg.shortHeTemplate = "רב פעלים · {PARASHAH_HE}";
            cfg.autoShort = autoShortCheck.value;
            cfg.enFont = String(enFontEdit.text || "Cambria");
            cfg.enStyle = String(enStyleEdit.text || "Regular");
            cfg.enSize = positiveNumber(enSizeEdit.text, 7.5);
            cfg.enTracking = numberValue(enTrackingEdit.text, 35);
            cfg.enMinSize = positiveNumber(enMinSizeEdit.text, 6.5);
            cfg.heFont = String(heFontEdit.text || "Keter YG");
            cfg.heStyle = String(heStyleEdit.text || "Medium");
            cfg.heSize = positiveNumber(heSizeEdit.text, 8);
            cfg.heTracking = numberValue(heTrackingEdit.text, 0);
            cfg.heMinSize = positiveNumber(heMinSizeEdit.text, 7);
            cfg.emphasizeStart = emphasizeStartCheck.value;
            cfg.startEnStyle = String(startEnStyleEdit.text || "Bold");
            cfg.startHeStyle = String(startHeStyleEdit.text || "Bold");
            cfg.numFont = String(numFontEdit.text || "Cambria");
            cfg.numStyle = String(numStyleEdit.text || "Bold");
            cfg.numSize = positiveNumber(numSizeEdit.text, 8.5);
            cfg.separator = String(separatorEdit.text || "·");
            cfg.tint = clamp(numberValue(tintEdit.text, 85), 1, 100);
            cfg.topMm = positiveNumber(topEdit.text, DEFAULT_TOP_MM);
            cfg.bottomMm = positiveNumber(bottomEdit.text, DEFAULT_BOTTOM_MM);
            if (cfg.bottomMm <= cfg.topMm) throw new Error("Der untere Header-Rand muss unterhalb des oberen liegen.");
            cfg.ruleEnabled = ruleCheck.value;
            cfg.ruleWeight = positiveNumber(ruleWeightEdit.text, 0.25);
            cfg.ruleY = positiveNumber(ruleYEdit.text, DEFAULT_RULE_Y_MM);
            cfg.hideFirst = hideFirstCheck.value;
            cfg.excludedText = String(excludedEdit.text || "");
            cfg.backup = backupCheck.value;
            cfg.saveAfter = saveAfterCheck.value;
            cfg.overrides = state.overrides.slice(0);
            cfg.sourceFile = sourceEdit.text ? new File(sourceEdit.text) : null;
            return cfg;
        }

        refreshDocBtn.onClick = function () {
            try {
                updateDocDisplay();
                var d = activeDocOrThrow();
                var p = d.extractLabel(DOC_SOURCE_LABEL);
                if (p) sourceEdit.text = p;
            } catch (e) { alert(errorText(e), APP_NAME); }
        };

        sourceFromDocBtn.onClick = function () {
            try {
                var d = activeDocOrThrow();
                var p = d.extractLabel(DOC_SOURCE_LABEL);
                if (!p) throw new Error("Im aktiven Dokument ist kein " + DOC_SOURCE_LABEL + " gespeichert.");
                sourceEdit.text = p;
            } catch (e) { alert(errorText(e), APP_NAME); }
        };

        sourceChooseBtn.onClick = function () {
            var f = File.openDialog("Rav-Pe’alim BILINGUAL.txt wählen", "Text:*.txt");
            if (f) sourceEdit.text = f.fsName;
        };

        analyzeBtn.onClick = function () {
            try {
                var d = activeDocOrThrow();
                var cfg = collectConfig();
                var a = analyzeDocument(d, cfg);
                state.lastAnalysis = a;
                analysisStatus.text = formatAnalysisReport(d, a, cfg);
            } catch (e) {
                analysisStatus.text = "ANALYSEFEHLER\r\n\r\n" + errorText(e);
                alert("Analyse fehlgeschlagen:\n\n" + errorText(e), APP_NAME);
            }
        };

        templateMode.onChange = function () {
            if (templateMode.selection && templateMode.selection.index < 2) applyTemplatePreset();
        };

        enTemplateEdit.onChanging = function () {
            if (templateMode.selection && templateMode.selection.index !== 2) templateMode.selection = 2;
        };
        heTemplateEdit.onChanging = function () {
            if (templateMode.selection && templateMode.selection.index !== 2) templateMode.selection = 2;
        };

        ovAddBtn.onClick = function () {
            try {
                var d = activeDocOrThrow();
                var rangeText = trim(ovPagesEdit.text);
                if (!rangeText) throw new Error("Bitte einen Seitenbereich angeben.");
                var flags = parsePhysicalPageRange(rangeText, d.pages.length);
                if (!countTrue(flags)) throw new Error("Der Seitenbereich enthält keine gültige physische Dokumentseite.");
                var enT = trim(ovEnEdit.text), heT = trim(ovHeEdit.text);
                if (!enT || !heT) throw new Error("Für einen manuellen Override werden englischer und hebräischer Titel benötigt.");
                var yi = ovYear.selection ? ovYear.selection.index : 0;
                var y = yi === 1 ? 1 : (yi === 2 ? 2 : (yi === 3 ? 0 : null));
                state.overrides.push({
                    rangeText:rangeText,
                    flags:flags,
                    enTitle:enT,
                    heTitle:heT,
                    year:y,
                    newStart:ovStartCheck.value
                });
                refreshOverrideList();
                ovPagesEdit.text = ""; ovEnEdit.text = ""; ovHeEdit.text = "";
            } catch (e) { alert("Override konnte nicht hinzugefügt werden:\n\n" + errorText(e), APP_NAME); }
        };

        ovRemoveBtn.onClick = function () {
            if (!overrideList.selection) return;
            var idx = overrideList.selection.index;
            if (idx === undefined || idx === null || idx < 0) return;
            state.overrides.splice(idx, 1);
            refreshOverrideList();
        };

        ovClearBtn.onClick = function () {
            state.overrides = [];
            refreshOverrideList();
        };

        testSpreadBtn.onClick = function () {
            try {
                var d = activeDocOrThrow(), cfg = collectConfig(), pages = activeSpreadPageIndexes(d);
                var result = runUndoable("RPL Kolumnentitel · Test-Doppelseite", function () {
                    return applyRunningHeaders(d, cfg, pages, "test");
                });
                actionStatus.text = result;
                updateDocDisplay();
            } catch (e) { alert("Testlauf fehlgeschlagen:\n\n" + errorText(e), APP_NAME); }
        };

        applyAllBtn.onClick = function () {
            try {
                var d = activeDocOrThrow(), cfg = collectConfig();
                var result = runUndoable("RPL Kolumnentitel · Alle Seiten", function () {
                    return applyRunningHeaders(d, cfg, null, "all");
                });
                actionStatus.text = result;
                updateDocDisplay();
            } catch (e) { alert("Kolumnentitel konnten nicht erstellt werden:\n\n" + errorText(e), APP_NAME); }
        };

        validateBtn.onClick = function () {
            try {
                var d = activeDocOrThrow(), cfg = collectConfig();
                actionStatus.text = validateRunningHeaders(d, cfg);
            } catch (e) { alert("Prüfung fehlgeschlagen:\n\n" + errorText(e), APP_NAME); }
        };

        numbersBtn.onClick = function () {
            try {
                var d = activeDocOrThrow(), cfg = collectConfig();
                var result = runUndoable("RPL Seitenzahlen reparieren", function () {
                    return repairPageNumbersOnly(d, cfg);
                });
                actionStatus.text = result;
            } catch (e) { alert("Seitenzahlen konnten nicht repariert werden:\n\n" + errorText(e), APP_NAME); }
        };

        removeBtn.onClick = function () {
            try {
                var d = activeDocOrThrow(), cfg = collectConfig();
                var result = runUndoable("RPL Kolumnentitel entfernen", function () {
                    return removeRunningHeaders(d, cfg);
                });
                actionStatus.text = result;
            } catch (e) { alert("Kolumnentitel konnten nicht entfernt werden:\n\n" + errorText(e), APP_NAME); }
        };

        w.onClose = function () {
            try { $.global.__RPL_RUNNING_HEADER_MANAGER_V103__ = null; } catch (_) {}
        };

        updateDocDisplay();
        try {
            if (app.documents.length) {
                var initialPath = app.activeDocument.extractLabel(DOC_SOURCE_LABEL);
                if (initialPath) sourceEdit.text = initialPath;
            }
        } catch (_) {}

        w.center();
        w.show();
    }

    // =====================================================================
    // Analysis
    // =====================================================================

    function analyzeDocument(doc, cfg) {
        // Rav Pe’alim (wie Leshon Chakhamim v1.0.1): Ueberschriften je Sprache aus dem eigenen Textfluss
        var sourceEntries = [], sourceUsed = false, sourceWarning = "", aliases = 0, i;
        for (i = 0; i < SECTIONS.length; i++) SECTIONS[i].enAlias = [];
        if (cfg.sourceFile && cfg.sourceFile.exists) {
            try {
                sourceEntries = parseSourceSections(readUTF8(cfg.sourceFile));
                sourceUsed = sourceEntries.length > 0;
                aliases = registerSourceAliases(sourceEntries);
                state.sourceFile = cfg.sourceFile;
            } catch (e) {
                sourceWarning = "BILINGUAL-TXT konnte nicht ausgewertet werden: " + errorText(e);
            }
        } else if (cfg.sourceFile && cfg.sourceFile.fsName) {
            sourceWarning = "Gespeicherte BILINGUAL-TXT nicht gefunden: " + cfg.sourceFile.fsName;
        }

        var heHeadings = collectHeadingParagraphs(doc, STYLE_HE_HEAD, FRAME_HE_LABEL, true, false);
        var enHeadings = collectHeadingParagraphs(doc, STYLE_EN_HEAD, FRAME_EN_LABEL, false, false);
        var heStarts = buildSectionStarts(heHeadings, true);
        var enStarts = buildSectionStarts(enHeadings, false);
        var fallbackLang = "";
        if (!enStarts.length && heStarts.length) { enStarts = mirrorStarts(heStarts); fallbackLang = "en"; }
        else if (!heStarts.length && enStarts.length) { heStarts = mirrorStarts(enStarts); fallbackLang = "he"; }

        var pageMap = buildPageMap(doc, heStarts, enStarts, cfg);
        applyManualOverrides(pageMap, doc, cfg);
        applyExcludedPages(pageMap, doc, cfg);

        var unmatched = [];
        for (i = 0; i < heStarts.length; i++) if (!heStarts[i].matched) unmatched.push("HE S. " + heStarts[i].pageName + ": " + heStarts[i].title);
        for (i = 0; i < enStarts.length; i++) if (!enStarts[i].matched) unmatched.push("EN S. " + enStarts[i].pageName + ": " + enStarts[i].title);

        return {
            sourceEntries:sourceEntries,
            sourceUsed:sourceUsed,
            sourceWarning:sourceWarning,
            sourceAliases:aliases,
            heHeadings:heHeadings,
            enHeadings:enHeadings,
            heStarts:heStarts,
            enStarts:enStarts,
            starts:heStarts.length ? heStarts : enStarts,
            pageMap:pageMap,
            usedEnglishFallback:fallbackLang === "he",
            fallbackLang:fallbackLang,
            unmatched:unmatched,
            unresolvedYears:0
        };
    }

    function collectHeadingParagraphs(doc, styleName, frameLabel, isHebrew, allowHeuristic) {
        // Rav Pe’alim (wie Leshon Chakhamim v1.0.1): nur Absaetze mit dem Ueberschriften-Format des Buchmanagers;
        // Text genau wie im Dokument, dazu Seite und ob die Ueberschrift oben im Rahmen steht.
        var stories = collectStoriesByFrameLabel(doc, frameLabel);
        var out = [], i, j, story, paras, p, txt, styleOk, pageInfo, sid;
        for (i = 0; i < stories.length; i++) {
            story = stories[i];
            try { sid = String(story.id); } catch (_) { sid = String(i); }
            paras = story.paragraphs;
            for (j = 0; j < paras.length; j++) {
                p = paras[j];
                styleOk = false;
                try { styleOk = p.appliedParagraphStyle && p.appliedParagraphStyle.isValid && p.appliedParagraphStyle.name === styleName; } catch (_) {}
                if (!styleOk) continue;
                txt = cleanHeadingText(p.contents);
                if (!txt) continue;
                pageInfo = paragraphPageInfo(p);
                if (!pageInfo) continue;
                out.push({text:txt, pageIndex:pageInfo.index, pageName:pageInfo.name, textIndex:safeTextIndex(p),
                          storyId:sid, atTop:paragraphAtFrameTop(p), yearMarker:null, source:"style"});
            }
        }
        return dedupeHeadings(out);
    }

    function collectStoriesByFrameLabel(doc, label) {
        var out = [], seen = {}, i, j, page, tf, story, id;
        for (i = 0; i < doc.pages.length; i++) {
            page = doc.pages[i];
            for (j = 0; j < page.textFrames.length; j++) {
                tf = page.textFrames[j];
                if (tf.label !== label) continue;
                try { story = tf.parentStory; } catch (_) { story = null; }
                if (!story || !story.isValid) continue;
                try { id = String(story.id); } catch (__){ id = "story_" + i + "_" + j; }
                if (!seen[id]) { seen[id] = true; out.push(story); }
            }
        }
        return out;
    }

    function paragraphPageInfo(p) {
        try {
            var ip = p.insertionPoints[0];
            var frames = ip.parentTextFrames;
            if (!frames || !frames.length) return null;
            var page = frames[0].parentPage;
            if (!page || !page.isValid) return null;
            return {index:page.documentOffset, name:page.name};
        } catch (_) { return null; }
    }

    function safeTextIndex(p) {
        try { return p.insertionPoints[0].index; } catch (_) { return 0; }
    }

    function looksLikeHeadingParagraph(p) {
        try {
            var ps = Number(p.pointSize);
            if (!isNaN(ps) && ps >= 12) return true;
        } catch (_) {}
        try {
            if (p.justification === Justification.CENTER_ALIGN) return true;
        } catch (_) {}
        return false;
    }

    function dedupeHeadings(a) {
        // gleichlautende Ueberschriften bleiben erhalten; doppelt nur derselbe Absatz
        a.sort(function(x,y){ if (x.pageIndex !== y.pageIndex) return x.pageIndex-y.pageIndex; return x.textIndex-y.textIndex; });
        var out=[], seen={}, i, k;
        for(i=0;i<a.length;i++){
            k=(a[i].storyId||"")+"|"+a[i].textIndex;
            if(!seen[k]){seen[k]=true;out.push(a[i]);}
        }
        return out;
    }

    function parseSourceParashot(file) {
        var raw = readUTF8(file);
        var re = /<section>\s*<he_title>([\s\S]*?)<\/he_title>\s*<en_title>([\s\S]*?)<\/en_title>\s*<\/section>/ig;
        var m, out=[], currentYear=null, he, en, y, par, projectEn, index=0;
        while ((m = re.exec(raw)) !== null) {
            he = cleanHeadingText(restoreCdata(xmlUnescape(m[1])));
            en = cleanHeadingText(restoreCdata(xmlUnescape(m[2])));
            y = detectYearMarker(he + " " + en);
            if (y) currentYear = y;
            par = findParashahByHebrewTitle(he);
            if (!par && en) par = findParashahByEnglishTitle(en);
            if (!par) continue;
            projectEn = extractProjectEnglishTitle(en, par.en);
            out.push({
                index:index++,
                heRaw:he,
                enRaw:en,
                parashaHe:par.he,
                parashaEn:projectEn,
                year:currentYear,
                key:par.key
            });
        }
        return out;
    }

    function buildParashahStartsFromHebrew(headings, sourceEntries) {
        var starts=[], sourceCursor=0, currentYear=null, i, h, par, match;
        for (i = 0; i < headings.length; i++) {
            h = headings[i];
            if (h.yearMarker) currentYear = h.yearMarker;
            par = findParashahByHebrewTitle(h.text);
            if (!par) continue;
            match = findSequentialSourceMatch(sourceEntries, sourceCursor, par.key, h.text, true);
            if (match) {
                sourceCursor = match.index + 1;
                if (match.entry.year) currentYear = match.entry.year;
            }
            starts.push({
                pageIndex:h.pageIndex,
                pageName:h.pageName,
                textIndex:h.textIndex,
                parashaHe:match ? match.entry.parashaHe : par.he,
                parashaEn:match ? match.entry.parashaEn : par.en,
                year:match && match.entry.year ? match.entry.year : currentYear,
                detection:match ? "HE style + BILINGUAL" : (h.source === "heuristic" ? "HE heuristic + catalogue" : "HE style + catalogue")
            });
        }
        return starts;
    }

    function buildParashahStartsFromEnglish(headings, sourceEntries) {
        var starts=[], sourceCursor=0, currentYear=null, i, h, par, match;
        for (i = 0; i < headings.length; i++) {
            h = headings[i];
            if (h.yearMarker) currentYear = h.yearMarker;
            par = findParashahByEnglishTitle(h.text);
            if (!par) continue;
            match = findSequentialSourceMatch(sourceEntries, sourceCursor, par.key, h.text, false);
            if (match) {
                sourceCursor = match.index + 1;
                if (match.entry.year) currentYear = match.entry.year;
            }
            starts.push({
                pageIndex:h.pageIndex,
                pageName:h.pageName,
                textIndex:h.textIndex,
                parashaHe:match ? match.entry.parashaHe : par.he,
                parashaEn:match ? match.entry.parashaEn : par.en,
                year:match && match.entry.year ? match.entry.year : currentYear,
                detection:"EN fallback"
            });
        }
        return starts;
    }

    function findSequentialSourceMatch(entries, cursor, key, rawTitle, isHebrew) {
        if (!entries || !entries.length) return null;
        var i, e, normalizedRaw = normalizeTitle(rawTitle);
        for (i = cursor; i < entries.length; i++) {
            e = entries[i];
            if (e.key !== key) continue;
            if (isHebrew && normalizeTitle(e.heRaw) === normalizedRaw) return {index:i, entry:e};
            if (!isHebrew && normalizeTitle(e.enRaw) === normalizedRaw) return {index:i, entry:e};
        }
        for (i = cursor; i < entries.length; i++) {
            e = entries[i]; if (e.key === key) return {index:i, entry:e};
        }
        for (i = 0; i < cursor && i < entries.length; i++) {
            e = entries[i]; if (e.key === key) return {index:i, entry:e};
        }
        return null;
    }

    function collapseSamePageStarts(starts) {
        if (!starts.length) return starts;
        var out=[], i, last;
        for(i=0;i<starts.length;i++){
            last=out.length?out[out.length-1]:null;
            if(last && last.pageIndex===starts[i].pageIndex){
                // Keep the last heading on the page: if two short sections share
                // one page, the next page belongs to the later Parashah.
                out[out.length-1]=starts[i];
            }else out.push(starts[i]);
        }
        return out;
    }

    function applyGlobalYearFallback(starts, mode) {
        var forced = mode === 1 ? 1 : (mode === 2 ? 2 : null);
        var remove = mode === 3;
        var i;
        for (i = 0; i < starts.length; i++) {
            if (remove) starts[i].year = 0;
            else if (forced) starts[i].year = forced;
        }
    }

    function buildPageMap(doc, heStarts, enStarts, cfg) {
        var map = [], i, he, en, rule = cfg.pageRule || 0;
        for (i = 0; i < doc.pages.length; i++) {
            he = sectionForPage(heStarts, i, rule);
            en = sectionForPage(enStarts, i, rule);
            if (!he && !en) { map.push(null); continue; }
            map.push({
                heTitle:he ? he.s.title : "", heShort:he ? he.s.kurzTitel : "", heGroup:he ? he.s.groupHe : "",
                enTitle:en ? en.s.title : "", enShort:en ? en.s.kurzTitel : "", enGroup:en ? en.s.groupEn : "",
                startPageHe:he ? he.start : false, startPageEn:en ? en.start : false,
                startPage:!!((he && he.start) || (en && en.start)),
                year:null,
                source:(he ? he.s.detection : "") + (en ? (he ? " / " : "") + en.s.detection : ""),
                visible:true
            });
        }
        if (cfg.bodyOnly) {
            for (i = 0; i < doc.pages.length; i++) if (map[i] && !isBihBodyPage(doc.pages[i])) map[i].visible = false;
        }
        if (cfg.hideFirst) {
            for (i = 0; i < doc.pages.length; i++) {
                if (map[i] && (isLeftPage(doc.pages[i]) ? map[i].startPageEn : map[i].startPageHe)) map[i].visible = false;
            }
        }
        return map;
    }

    function applyManualOverrides(map, doc, cfg) {
        var i,j,ov,year,first=-1;
        for(i=0;i<cfg.overrides.length;i++){
            ov=cfg.overrides[i];first=-1;
            // Re-parse against current page count so an override survives page-count changes.
            var flags=parsePhysicalPageRange(ov.rangeText,doc.pages.length);
            for(j=0;j<doc.pages.length;j++){
                if(!flags[j])continue;
                if(first<0)first=j;
                year=ov.year;
                if(year===null || year===undefined){
                    year=(map[j] && map[j].year!==undefined)?map[j].year:null;
                    if((year===null || year===undefined) && cfg.yearMode===1)year=1;
                    if((year===null || year===undefined) && cfg.yearMode===2)year=2;
                    if(cfg.yearMode===3)year=0;
                }
                map[j]={
                    enTitle:ov.enTitle,
                    heTitle:ov.heTitle,
                    year:year,
                    startPage:false,
                    source:"manual override",
                    visible:true
                };
                if(cfg.bodyOnly && !isBihBodyPage(doc.pages[j]))map[j].visible=false;
            }
            if(first>=0 && ov.newStart){
                map[first].startPage=true;
                if(cfg.hideFirst)map[first].visible=false;
            }
        }
    }

    function applyExcludedPages(map, doc, cfg) {
        var flags=parsePhysicalPageRange(cfg.excludedText,doc.pages.length),i;
        for(i=0;i<doc.pages.length;i++)if(flags[i]){
            if(!map[i])map[i]={enTitle:"",heTitle:"",year:null,startPage:false,source:"excluded",visible:false};
            else map[i].visible=false;
        }
    }

    function isBihBodyPage(page) {
        var i, tf;
        try {
            for(i=0;i<page.textFrames.length;i++){
                tf=page.textFrames[i];
                if(tf.label===FRAME_HE_LABEL || tf.label===FRAME_EN_LABEL)return true;
            }
        } catch (_) {}
        return false;
    }

    // =====================================================================
    // Apply / format
    // =====================================================================

    function applyRunningHeaders(doc, cfg, pageIndexes, mode) {
        requireHeaderFonts(cfg);
        var a = analyzeDocument(doc, cfg);
        state.lastAnalysis = a;
        var backup = null;
        if (cfg.backup) backup = createInDesignBackup(doc, mode === "test" ? "header_test" : "headers");
        var layer = ensureHeaderLayer(doc);
        var selected = pageIndexLookup(pageIndexes, doc.pages.length);
        var allPages = pageIndexes === null || pageIndexes === undefined;
        var changed=0,hidden=0,created=0,updated=0,shortFallbacks=0,shrunk=0,truncated=[],rules=0,startEmphasis=0,emphasisFallbacks=0,noHeaderPages=[],notFitted=[],pageErrors=[],i,page,info,headerResult;

        for(i=0;i<doc.pages.length;i++){
            if(!allPages && !selected[i])continue;
            page=doc.pages[i];info=a.pageMap[i];

            if(!info || !info.visible || !headerTitle(info,isLeftPage(page)?"en":"he",false)){
                if(removeHeaderFramesFromPage(page)>0)changed++;
                if(isBihBodyPage(page)) setPageNumberFrame(doc,page,cfg,false,layer);
                hidden++;
                noHeaderPages.push(displayPageNumber(page,i));
                if(cfg.ruleEnabled && isBihBodyPage(page)){normalizeHeaderRule(doc,page,cfg,layer);rules++;}
                continue;
            }

            try{
                setPageNumberFrame(doc,page,cfg,true,layer);
                headerResult=setHeaderForPage(doc,page,info,cfg,layer);
            }catch(ePage){
                // eine Seite mit Problem haelt den Lauf nicht an; sie steht im Bericht
                pageErrors.push("S. "+displayPageNumber(page,i)+": "+errorText(ePage));
                continue;
            }
            if(headerResult.failed){
                notFitted.push("S. "+displayPageNumber(page,i)+" („"+headerTitle(info,isLeftPage(page)?"en":"he",false)+"“): "+headerResult.failed);
                try{setPageNumberFrame(doc,page,cfg,false,layer);}catch(_){}
            }
            if(headerResult.created)created++;else updated++;
            if(headerResult.usedShort)shortFallbacks++;
            if(headerResult.shrunk)shrunk++;
            if(headerResult.truncated)truncated.push(displayPageNumber(page,i));
            if(headerResult.startEmphasis)startEmphasis++;
            if(headerResult.emphasisFallback)emphasisFallbacks++;
            if(cfg.ruleEnabled){normalizeHeaderRule(doc,page,cfg,layer);rules++;}
            changed++;
        }

        if(cfg.saveAfter)doc.save();
        var report = [], probleme = notFitted.length + pageErrors.length, j;
        if(probleme){
            report.push((mode === "test" ? "TESTLAUF" : "KOLUMNENTITEL AKTUALISIERT")+" · "+probleme+" SEITE(N) PRÜFEN (siehe unten)");
        }else{
            report.push(mode === "test" ? "TEST AUF AKTUELLER DOPPELSEITE ERFOLGREICH" : "KOLUMNENTITEL ERFOLGREICH AKTUALISIERT");
        }
        report.push("Dokument: "+doc.name);
        report.push("Abschnittsüberschriften erkannt: HE "+a.heStarts.length+" · EN "+a.enStarts.length+
                    (a.fallbackLang?" · "+(a.fallbackLang==="en"?"EN":"HE")+" aus der anderen Sprache übernommen":"")+
                    " · Seitenregel: "+pageRuleLabel(cfg.pageRule));
        report.push("Header erstellt: "+created+" · aktualisiert: "+updated+" · ausgeblendet/ohne Header: "+hidden);
        report.push("Seiten ohne Kolumnentitel: "+formatPageLabelList(noHeaderPages));
        report.push("Kurztitel verwendet: "+shortFallbacks+" · automatisch verkleinert: "+shrunk+" · mit „…“ gekürzt: "+truncated.length+
                    (truncated.length?" (S. "+formatPageLabelList(truncated)+")":""));
        if(a.unmatched.length)report.push("Überschriften ohne Katalogeintrag (Titel wie im Dokument, kein Kurztitel): "+a.unmatched.length);
        if(cfg.emphasizeStart) report.push("Seiten mit fett gesetztem Abschnittsbeginn: "+startEmphasis+(emphasisFallbacks?" · Schrift-Fallbacks: "+emphasisFallbacks:""));
        if(cfg.ruleEnabled)report.push("Headerlinien geprüft/gesetzt: "+rules+" · "+cfg.ruleWeight+" pt");
        if(a.sourceWarning)report.push("WARNUNG Quelle: "+a.sourceWarning);
        if(notFitted.length){
            report.push("OHNE KOLUMNENTITEL – passt in keiner Fassung in eine Zeile, Kopfrahmen entfernt (kein Übersatz): "+notFitted.length);
            for(j=0;j<notFitted.length&&j<12;j++)report.push("  "+notFitted[j]);
            if(notFitted.length>12)report.push("  … und "+(notFitted.length-12)+" weitere");
        }
        if(pageErrors.length){
            report.push("FEHLER auf einzelnen Seiten (übersprungen): "+pageErrors.length);
            for(j=0;j<pageErrors.length&&j<12;j++)report.push("  "+pageErrors[j]);
            if(pageErrors.length>12)report.push("  … und "+(pageErrors.length-12)+" weitere");
        }
        if(backup)report.push("INDD-Sicherung: "+backup.fsName);
        report.push("Fließtext-Rahmen wurden nicht verändert.");
        var txt=report.join("\r\n");
        try{doc.insertLabel(DOC_LAST_REPORT_LABEL,txt);}catch(_){}
        return txt;
    }

    function setHeaderForPage(doc, page, info, cfg, layer) {
        // v1.0.4 einfach und sicher: alter Kopfrahmen wird geloescht (samt verstecktem Uebersatz,
        // der sonst als doppelte, groessere Woerter wieder auftauchte), ein frischer Rahmen angelegt,
        // dann gilt die erste Fassung, die in EINE Zeile passt:
        //   voller Titel -> Kurztitel -> kleinere Schrift bis Minimum -> wortweise mit "…" ->
        //   nur Werktitel. Passt nichts, bleibt die Seite ohne Kopfrahmen (nie Uebersatz).
        var isLeft = isLeftPage(page);
        var created = labeledFrames(page, HEADER_FRAME_LABEL).length === 0;
        removeHeaderFramesFromPage(page);
        var tf = getOrCreateSingleLabeledTextFrame(page, HEADER_FRAME_LABEL, layer);
        tf.geometricBounds = headerBounds(page, cfg.topMm, cfg.bottomMm);
        setFrameInsets(tf,0);
        try{tf.textFramePreferences.ignoreWrap=true;}catch(_){}
        try{tf.textFramePreferences.verticalJustification=VerticalJustification.CENTER_ALIGN;}catch(_){}
        try{tf.itemLayer=layer;}catch(_){}

        var lang = isLeft ? "en" : "he";
        var full = headerTitle(info, lang, false), kurz = headerTitle(info, lang, true);
        var size = lang === "en" ? cfg.enSize : cfg.heSize;
        var minSize = lang === "en" ? cfg.enMinSize : cfg.heMinSize;
        var langStart = lang === "en" ? info.startPageEn : info.startPageHe;
        if (langStart === undefined) langStart = info.startPage;
        var group = lang === "en" ? (info.enGroup || "") : (info.heGroup || "");
        var showsSection = templateShowsSection(cfg, lang);
        var shown = (cfg.autoShort && showsSection && kurz && kurz !== full) ? kurz : full;
        var emph = null, ok = false, usedShort = false, shrunk = false, truncated = false, failed = "";
        var sz = size, words, keep;

        function versuche(title, pt) {
            var r = renderHeaderText(info, cfg, lang, false, title);
            var needle = showsSection ? title : group;
            emph = formatHeaderTextFrame(doc, tf, r.text, cfg, lang, pt,
                {startPage:!!langStart, enTitle:lang === "en" ? needle : "", heTitle:lang === "he" ? needle : ""});
            return !headerNeedsFallback(tf);
        }

        ok = versuche(full, size);
        if (!ok && shown !== full) { ok = versuche(shown, size); usedShort = ok; }
        while (!ok && sz - 0.25 >= minSize - 0.001) {
            sz -= 0.25;
            ok = versuche(shown, sz);
            if (ok) { shrunk = true; usedShort = shown !== full; }
        }
        if (!ok && showsSection) {
            words = trim(shown).split(/\s+/);
            for (keep = words.length - 1; !ok && keep >= 1; keep--) {
                ok = versuche(shortenWords(shown, keep), minSize);
                if (ok) { truncated = true; shrunk = minSize < size; usedShort = shown !== full; }
            }
            if (!ok) { ok = versuche("", minSize); if (ok) truncated = true; }
        }
        if (!ok) {
            failed = headerDiagnosis(tf) || "Kopfrahmen läuft über";
            try { tf.remove(); } catch (_) {}
        }
        return {created:created,usedShort:usedShort,shrunk:shrunk,truncated:truncated,failed:failed,
                startEmphasis:!!(emph&&emph.applied),emphasisFallback:!!(emph&&emph.fallback)};
    }

    function renderHeaderText(info, cfg, lang, forceShort, title) {
        // {ABSCHNITT}/{PARASHAH} = englische, {ABSCHNITT_HE}/{PARASHAH_HE} = hebraeische Abschnittsueberschrift,
        // {GRUPPE}/{GRUPPE_HE} = Gruppe (Abteilung · Teil); title ersetzt den Titel der Seitensprache (Kurz-/Kuerzungsstufe)
        var tpl = lang === "en" ? cfg.enTemplate : cfg.heTemplate;
        var given = title !== undefined && title !== null;
        var enT = (lang === "en" && given) ? String(title) : headerTitle(info, "en", forceShort);
        var heT = (lang === "he" && given) ? String(title) : headerTitle(info, "he", forceShort);
        var text = tpl;
        text = replaceAllLiteral(text, "{ABSCHNITT}", enT);
        text = replaceAllLiteral(text, "{ABSCHNITT_HE}", heT);
        text = replaceAllLiteral(text, "{PARASHAH}", enT);
        text = replaceAllLiteral(text, "{PARASHAH_HE}", heT);
        text = replaceAllLiteral(text, "{GRUPPE}", info.enGroup || "");
        text = replaceAllLiteral(text, "{GRUPPE_HE}", info.heGroup || "");
        text = replaceAllLiteral(text, "{YEAR}", "");
        text = replaceAllLiteral(text, "{YEAR_HE}", "");
        text = cleanTemplateSeparators(text);
        return {text:text, usedShort:!!forceShort};
    }

    function formatHeaderTextFrame(doc, tf, text, cfg, lang, pointSize, info) {
        // v1.0.4: ganze Textkette ersetzen (tf.contents ersetzt nur den sichtbaren Teil; versteckter
        // Uebersatz blieb stehen) und alle geerbten Absatz-/Zeichenattribute neutralisieren
        var story = tf.parentStory, t, font;
        try { story.contents = text; } catch (_) { tf.contents = text; }
        t = story.texts[0];
        resetHeaderText(doc, tf, t);
        if(lang==="en"){
            font=requireFont(cfg.enFont,cfg.enStyle);
            try{t.appliedFont=font;}catch(_){}
            try{t.fontStyle=cfg.enStyle;}catch(_){}
            t.pointSize=pointSize;
            try{t.leading=pointSize+1.1;}catch(_){}
            try{t.tracking=cfg.enTracking;}catch(_){}
            try{t.justification=Justification.LEFT_ALIGN;}catch(_){}
            try{t.paragraphDirection=ParagraphDirectionOptions.LEFT_TO_RIGHT_DIRECTION;}catch(_){}
            try{t.composer="Adobe Paragraph Composer";}catch(_){}
        }else{
            font=requireFont(cfg.heFont,cfg.heStyle);
            try{t.appliedFont=font;}catch(_){}
            try{t.fontStyle=cfg.heStyle;}catch(_){}
            t.pointSize=pointSize;
            try{t.leading=pointSize+1.2;}catch(_){}
            try{t.tracking=cfg.heTracking;}catch(_){}
            try{t.justification=Justification.RIGHT_ALIGN;}catch(_){}
            try{t.paragraphDirection=ParagraphDirectionOptions.RIGHT_TO_LEFT_DIRECTION;}catch(_){}
            try{t.composer="Adobe World-Ready Paragraph Composer";}catch(_){}
        }
        try{t.hyphenation=false;}catch(_){}
        try{t.fillColor=blackSwatch(doc);t.fillTint=cfg.tint;}catch(_){}
        var emphasisResult = cfg.emphasizeStart ? applyStartPageEmphasis(doc, tf, info, cfg, lang) : {applied:false,fallback:false};
        try{story.recompose();}catch(_){}
        return emphasisResult;
    }

    function applyStartPageEmphasis(doc, tf, info, cfg, lang) {
        var result={applied:false,fallback:false};
        if(!cfg.emphasizeStart || !info || !info.startPage)return result;
        var full="",needle="",start=-1,end=-1,prefix="",preferredStyle="",family="",baseStyle="",font=null,range=null;
        try{full=String(tf.contents||"");}catch(_){return result;}
        if(lang==="en"){
            needle=String(info.enTitle||"");
            family=cfg.enFont; preferredStyle=cfg.startEnStyle; baseStyle=cfg.enStyle;
        }else{
            needle=String(info.heTitle||"");
            family=cfg.heFont; preferredStyle=cfg.startHeStyle; baseStyle=cfg.heStyle;
        }
        if(!needle)return result;
        if(lang==="he"){
            prefix="פרשת ";
            start=full.indexOf(prefix+needle);
            if(start>=0)end=start+prefix.length+needle.length-1;
        }
        if(start<0){
            start=full.indexOf(needle);
            if(start>=0)end=start+needle.length-1;
        }
        if(start<0 || end<start)return result;

        font=exactFontOrNull(family,preferredStyle);
        if(!font){
            font=strongerFontOrNull(family,baseStyle);
            if(!font){font=requireFont(family,baseStyle);result.fallback=true;}
            else if(String(preferredStyle||"").toLowerCase()!==fontStyleNameSafe(font).toLowerCase())result.fallback=true;
        }
        try{
            range=tf.texts[0].characters.itemByRange(start,end);
            range.appliedFont=font;
            try{range.fillTint=100;}catch(_){}
            result.applied=true;
        }catch(_){
            result.fallback=true;
        }
        return result;
    }

    function exactFontOrNull(family,style){
        var f=null;
        try{f=app.fonts.itemByName(family+"\t"+style);if(f&&f.isValid)return f;}catch(_){}
        return null;
    }

    function fontStyleNameSafe(font){
        try{return String(font.fontStyleName||font.styleName||"");}catch(_){return "";}
    }

    function strongerFontOrNull(family,baseStyle){
        var styles=["Bold","SemiBold","Semibold","Demi Bold","Demi","Medium"],i,f;
        for(i=0;i<styles.length;i++){
            if(String(styles[i]).toLowerCase()===String(baseStyle||"").toLowerCase())continue;
            f=exactFontOrNull(family,styles[i]);
            if(f)return f;
        }
        return null;
    }

    function headerNeedsFallback(tf) {
        try{if(tf.overflows)return true;}catch(_){}
        try{if(tf.parentStory.lines.length>1)return true;}catch(_){}
        return false;
    }

    function setPageNumberFrame(doc,page,cfg,withSeparator,layer){
        var tf=getOrCreateSingleLabeledTextFrame(page,PAGE_NUMBER_LABEL,null);
        tf.geometricBounds=pageNumberBounds(page,cfg.topMm,cfg.bottomMm);
        setFrameInsets(tf,0);
        try{tf.textFramePreferences.ignoreWrap=true;}catch(_){}
        try{tf.textFramePreferences.verticalJustification=VerticalJustification.CENTER_ALIGN;}catch(_){}
        tf.contents="";
        var isLeft=isLeftPage(page),sep=trim(cfg.separator);
        if(isLeft){
            try{tf.insertionPoints[0].contents=SpecialCharacters.AUTO_PAGE_NUMBER;}catch(_){tf.contents=page.name;}
            if(withSeparator&&sep)tf.insertionPoints[-1].contents=" "+sep;
        }else{
            if(withSeparator&&sep)tf.insertionPoints[0].contents=sep+" ";
            try{tf.insertionPoints[-1].contents=SpecialCharacters.AUTO_PAGE_NUMBER;}catch(_){tf.insertionPoints[-1].contents=page.name;}
        }
        var t=tf.texts[0], reg=requireFont(cfg.numFont,"Regular"), bold=requireFont(cfg.numFont,cfg.numStyle);
        try{t.appliedFont=bold;}catch(_){}
        try{t.fontStyle=cfg.numStyle;}catch(_){}
        t.pointSize=cfg.numSize;
        try{t.leading=cfg.numSize+0.8;}catch(_){}
        try{t.fillColor=blackSwatch(doc);t.fillTint=100;}catch(_){}
        try{t.justification=isLeft?Justification.LEFT_ALIGN:Justification.RIGHT_ALIGN;}catch(_){}
        try{t.paragraphDirection=ParagraphDirectionOptions.LEFT_TO_RIGHT_DIRECTION;}catch(_){}
        try{t.hyphenation=false;}catch(_){}
        if(withSeparator&&sep){
            try{
                var ci,ch;
                for(ci=0;ci<tf.characters.length;ci++){
                    ch=tf.characters[ci];
                    if(String(ch.contents)===sep){ch.appliedFont=reg;ch.fontStyle="Regular";ch.pointSize=Math.max(6.5,cfg.numSize-1);}
                }
            }catch(_){}
        }
        try{tf.parentStory.recompose();}catch(_){}
        return tf;
    }

    function normalizeHeaderRule(doc,page,cfg,layer){
        var line=findHeaderRule(page),origin,oldWeight;
        if(!line){
            line=page.graphicLines.add();
            line.label=HEADER_RULE_LABEL;
            try{line.insertLabel(RULE_ORIGIN_KEY,"created");}catch(_){}
            try{line.itemLayer=layer;}catch(_){}
            origin="created";
        }else{
            try{origin=line.extractLabel(RULE_ORIGIN_KEY);}catch(_){origin="";}
            if(!origin){
                try{oldWeight=String(line.strokeWeight);line.insertLabel(RULE_OLD_WEIGHT_KEY,oldWeight);line.insertLabel(RULE_ORIGIN_KEY,"existing");}catch(_){}
                try{line.label=HEADER_RULE_LABEL;}catch(_){}
            }
        }
        var b=ruleBounds(page,cfg.ruleY);
        try{line.paths[0].entirePath=[[b[1],b[0]],[b[3],b[2]]];}catch(_){}
        try{line.strokeWeight=cfg.ruleWeight;}catch(_){}
        try{line.strokeColor=blackSwatch(doc);}catch(_){}
        return line;
    }

    function findHeaderRule(page){
        var i,line,path,p1,p2,y1,y2,x1,x2;
        for(i=0;i<page.graphicLines.length;i++){
            line=page.graphicLines[i];
            if(line.label===HEADER_RULE_LABEL)return line;
        }
        // Fallback: locate the original RPL top rule near y=16.10 mm.
        for(i=0;i<page.graphicLines.length;i++){
            line=page.graphicLines[i];
            try{
                path=line.paths[0].entirePath;p1=path[0];p2=path[path.length-1];
                x1=Number(p1[0]);y1=Number(p1[1]);x2=Number(p2[0]);y2=Number(p2[1]);
                if(horizontalNearMm(y1,y2,DEFAULT_RULE_Y_MM,1.1) && spanAtLeastMm(x1,x2,80))return line;
            }catch(_){}
        }
        return null;
    }

    function removeRunningHeaders(doc,cfg){
        var backup=cfg.backup?createInDesignBackup(doc,"headers_remove"):null;
        var removed=0,restoredRules=0,i,page;
        for(i=0;i<doc.pages.length;i++){
            page=doc.pages[i];
            removed+=removeHeaderFramesFromPage(page);
            if(isBihBodyPage(page))setPageNumberFrame(doc,page,cfg,false,null);
            restoredRules+=restoreManagedRule(page);
        }
        if(cfg.saveAfter)doc.save();
        return "KOLUMNENTITEL ENTFERNT\r\nDokument: "+doc.name+"\r\nEntfernte Headerrahmen: "+removed+"\r\nWiederhergestellte/entfernte Headerlinien: "+restoredRules+(backup?"\r\nINDD-Sicherung: "+backup.fsName:"")+"\r\nSeitenzahlen bleiben bestehen.";
    }

    function restoreManagedRule(page){
        var i,line,origin,oldWeight,count=0;
        for(i=page.graphicLines.length-1;i>=0;i--){
            line=page.graphicLines[i];
            if(line.label!==HEADER_RULE_LABEL)continue;
            try{origin=line.extractLabel(RULE_ORIGIN_KEY);}catch(_){origin="";}
            if(origin==="created"){
                try{line.remove();count++;}catch(_){}
            }else{
                try{oldWeight=line.extractLabel(RULE_OLD_WEIGHT_KEY);if(oldWeight!=="")line.strokeWeight=Number(oldWeight);}catch(_){}
                try{line.label="";}catch(_){}
                try{line.insertLabel(RULE_ORIGIN_KEY,"");line.insertLabel(RULE_OLD_WEIGHT_KEY,"");}catch(_){}
                count++;
            }
        }
        return count;
    }

    function repairPageNumbersOnly(doc,cfg){
        requireFont(cfg.numFont,cfg.numStyle);
        var backup=cfg.backup?createInDesignBackup(doc,"page_numbers"):null;
        var count=0,i,page;
        for(i=0;i<doc.pages.length;i++){
            page=doc.pages[i];
            if(cfg.bodyOnly && !isBihBodyPage(page))continue;
            setPageNumberFrame(doc,page,cfg,false,null);count++;
        }
        if(cfg.saveAfter)doc.save();
        return "SEITENZAHLEN REPARIERT\r\nBearbeitete Seiten: "+count+"\r\nAußenposition: links auf linken Seiten, rechts auf rechten Seiten\r\nSchrift: "+cfg.numFont+" "+cfg.numStyle+" "+cfg.numSize+" pt"+(backup?"\r\nINDD-Sicherung: "+backup.fsName:"");
    }

    // =====================================================================
    // Validation / reports
    // =====================================================================

    function validateRunningHeaders(doc,cfg){
        var a=analyzeDocument(doc,cfg),missing=[],extra=[],wrongSide=[],dup=[],numMissing=[],noHeaderExpected=[],wrongTitle=[],overset=[],i,page,info,headers,nums,lang,txt,expected;
        for(i=0;i<doc.pages.length;i++){
            page=doc.pages[i];info=a.pageMap[i];headers=labeledFrames(page,HEADER_FRAME_LABEL);nums=labeledFrames(page,PAGE_NUMBER_LABEL);
            lang=isLeftPage(page)?"en":"he";
            expected=!!(info&&info.visible&&headerTitle(info,lang,false));
            if(!expected)noHeaderExpected.push(displayPageNumber(page,i));
            if(expected&&!headers.length)missing.push(i+1);
            if(!expected&&headers.length)extra.push(i+1);
            if(headers.length>1)dup.push(i+1);
            if(cfg.bodyOnly&&isBihBodyPage(page)&&!nums.length)numMissing.push(i+1);
            if(headers.length){
                txt=cleanHeadingText(headers[0].contents);
                if(isLeftPage(page)&&containsHebrew(txt))wrongSide.push((i+1)+"(HE auf links)");
                if(!isLeftPage(page)&&!containsHebrew(txt))wrongSide.push((i+1)+"(EN auf rechts)");
                if(expected&&templateShowsSection(cfg,lang)&&!headerMatchesTitle(txt,info,lang))wrongTitle.push(displayPageNumber(page,i));
                if(headerNeedsFallback(headers[0]))overset.push(displayPageNumber(page,i));
            }
        }
        var out=[];
        out.push("KOLUMNENTITEL-PRÜFUNG");
        out.push("Dokument: "+doc.name+" · "+doc.pages.length+" Seiten");
        out.push("Abschnittsüberschriften erkannt: HE "+a.heStarts.length+" · EN "+a.enStarts.length+" · Seitenregel: "+pageRuleLabel(cfg.pageRule));
        out.push("Seiten ohne Kolumnentitel (laut aktueller Regel): "+formatPageLabelList(noHeaderExpected));
        out.push("Fehlende erwartete Header: "+formatNumberList(missing));
        out.push("Header auf laut Regel ausgeschlossenen Seiten: "+formatNumberList(extra));
        out.push("Doppelte Headerrahmen: "+formatNumberList(dup));
        out.push("Sprachseite auffällig: "+(wrongSide.length?wrongSide.join(", "):"keine"));
        out.push("Titel passt nicht zur Überschrift der Seite (z. B. nach neuem Umbruch): "+formatPageLabelList(wrongTitle));
        out.push("Kopfrahmen mit Übersatz oder zweizeilig: "+formatPageLabelList(overset));
        out.push("Fehlende RPL-Seitenzahlen: "+formatNumberList(numMissing));
        if(a.unmatched.length)out.push("Überschriften ohne Katalogeintrag: "+a.unmatched.length);
        if(a.sourceWarning)out.push("Quelle: "+a.sourceWarning);
        out.push((!missing.length&&!extra.length&&!dup.length&&!wrongSide.length&&!wrongTitle.length&&!overset.length)?"Ergebnis: keine Headerfehler erkannt.":"Ergebnis: oben genannte Seiten prüfen/reparieren (Kolumnentitel neu erstellen).");
        return out.join("\r\n");
    }

    function displayPageNumber(page,index){
        try{
            if(page && page.isValid && page.name!==undefined && String(page.name)!=="")return String(page.name);
        }catch(_){}
        return String(index+1);
    }

    function formatPageLabelList(a){
        if(!a || !a.length)return "keine";
        var out=[],i,chunk=[];
        for(i=0;i<a.length;i++){
            chunk.push(String(a[i]));
            if(chunk.length===18){out.push(chunk.join(", "));chunk=[];}
        }
        if(chunk.length)out.push(chunk.join(", "));
        return out.join("\r\n  ");
    }

    function formatAnalysisReport(doc,a,cfg){
        var out=[],i,info,key,curKey=null,from=0;
        out.push("RAV PE’ALIM · KOLUMNENTITEL-ANALYSE · Kolumnentitel = Abschnittsüberschrift der Seite");
        out.push("Dokument: "+doc.name+" · "+doc.pages.length+" physische Seiten · Band "+(doc.extractLabel(DOC_VOLUME_LABEL)||"?"));
        out.push("Überschriften im Dokument: HE "+a.heHeadings.length+" · EN "+a.enHeadings.length+" · Seitenregel: "+pageRuleLabel(cfg.pageRule));
        out.push("BILINGUAL-TXT: "+(a.sourceUsed?a.sourceEntries.length+" Abschnitte"+(a.sourceAliases?" · "+a.sourceAliases+" abweichende englische Titel übernommen":""):"nicht verwendet (eingebauter Katalog)"));
        if(a.sourceUsed&&a.sourceEntries.length!==a.heHeadings.length)out.push("HINWEIS: Banddatei "+a.sourceEntries.length+" Abschnitte, Dokument "+a.heHeadings.length+" hebräische Überschriften.");
        if(a.sourceUsed&&a.enHeadings.length&&a.sourceEntries.length!==a.enHeadings.length)out.push("HINWEIS: Banddatei "+a.sourceEntries.length+" Abschnitte, Dokument "+a.enHeadings.length+" englische Überschriften.");
        if(a.fallbackLang)out.push("Fallback: keine "+(a.fallbackLang==="en"?"englischen":"hebräischen")+" Überschriften gefunden; Titel über den Katalog aus der anderen Sprache.");
        if(a.sourceWarning)out.push("WARNUNG: "+a.sourceWarning);
        if(a.unmatched.length){
            out.push("Nicht im Katalog (Titel wie im Dokument, ohne Kurztitel): "+a.unmatched.length);
            for(i=0;i<a.unmatched.length&&i<20;i++)out.push("  "+a.unmatched[i]);
        }
        out.push("");
        if(!a.heStarts.length&&!a.enStarts.length){
            out.push("Keine Abschnittsüberschrift erkannt. Prüfe die Absatzformate \""+STYLE_HE_HEAD+"\" / \""+STYLE_EN_HEAD+"\" oder lege im Fallback-Reiter manuelle Bereiche an.");
            return out.join("\r\n");
        }
        out.push("Kolumnentitel je Seitenbereich (rechte Seiten Hebräisch | linke Seiten Englisch):");
        function bereich(a0,a1){
            var inf=a.pageMap[a0];
            out.push("  S. "+displayPageNumber(doc.pages[a0],a0)+(a1>a0?"–"+displayPageNumber(doc.pages[a1],a1):"")+" · "+
                     (inf.heTitle||"–")+" | "+(inf.enTitle||"–")+(inf.visible?"":" · ohne Kolumnentitel"));
        }
        for(i=0;i<doc.pages.length;i++){
            info=a.pageMap[i];
            key=info?(info.heTitle+"|"+info.enTitle+"|"+info.visible):null;
            if(key!==curKey){
                if(curKey!==null)bereich(from,i-1);
                curKey=key;from=i;
            }
        }
        if(curKey!==null)bereich(from,doc.pages.length-1);
        if(cfg.excludedText)out.push("Zusätzlich ausgeschlossen: "+cfg.excludedText);
        if(cfg.overrides.length)out.push("Manuelle Overrides in dieser Sitzung: "+cfg.overrides.length);
        out.push("");
        out.push("Noch keine Layoutänderung vorgenommen.");
        return out.join("\r\n");
    }

    // =====================================================================
    // Page-item helpers
    // =====================================================================

    function getOrCreateSingleLabeledTextFrame(page,label,layer){
        var arr=labeledFrames(page,label),tf,i;
        if(arr.length){
            tf=arr[0];
            for(i=arr.length-1;i>=1;i--)try{arr[i].remove();}catch(_){}
            return tf;
        }
        tf=page.textFrames.add();tf.label=label;
        if(layer)try{tf.itemLayer=layer;}catch(_){}
        return tf;
    }

    function labeledFrames(page,label){
        var a=[],i,tf;
        for(i=0;i<page.textFrames.length;i++){tf=page.textFrames[i];if(tf.label===label)a.push(tf);}
        return a;
    }

    function removeHeaderFramesFromPage(page){
        var a=labeledFrames(page,HEADER_FRAME_LABEL),i,n=0;
        for(i=a.length-1;i>=0;i--)try{a[i].remove();n++;}catch(_){}
        return n;
    }

    function headerBounds(page,top,bottom){
        // Canonical left-page coordinates: 31.5 .. 128.57 mm.
        // On right-hand pages they are mirrored to 19.43 .. 116.5 mm.
        if(isLeftPage(page))return [mm(top),mm(HEADER_LEFT_MM),mm(bottom),mm(TEXT_RIGHT_MM)];
        return [mm(top),mm(PAGE_W_MM-TEXT_RIGHT_MM),mm(bottom),mm(PAGE_W_MM-HEADER_LEFT_MM)];
    }

    function pageNumberBounds(page,top,bottom){
        if(isLeftPage(page))return [mm(top),mm(PAGE_NUM_LEFT_MM),mm(bottom),mm(PAGE_NUM_RIGHT_MM)];
        return [mm(top),mm(PAGE_W_MM-PAGE_NUM_RIGHT_MM),mm(bottom),mm(PAGE_W_MM-PAGE_NUM_LEFT_MM)];
    }

    function ruleBounds(page,y){
        if(isLeftPage(page))return [mm(y),mm(PAGE_NUM_LEFT_MM),mm(y),mm(TEXT_RIGHT_MM)];
        return [mm(y),mm(PAGE_W_MM-TEXT_RIGHT_MM),mm(y),mm(PAGE_W_MM-PAGE_NUM_LEFT_MM)];
    }

    function isLeftPage(page){
        try{return page.side===PageSideOptions.LEFT_HAND;}catch(_){}
        // Fallback for standard left-to-right facing-page documents.
        return ((page.documentOffset+1)%2===0);
    }

    function ensureHeaderLayer(doc){
        var l=doc.layers.itemByName(HEADER_LAYER_NAME);
        if(!l||!l.isValid)l=doc.layers.add({name:HEADER_LAYER_NAME});
        try{l.visible=true;l.locked=false;}catch(_){}
        return l;
    }

    function activeSpreadPageIndexes(doc){
        var a=[],i,p;
        try{
            var spread=app.activeWindow.activeSpread;
            for(i=0;i<spread.pages.length;i++){p=spread.pages[i];a.push(p.documentOffset);}
        }catch(_){}
        if(!a.length){
            try{a.push(app.activeWindow.activePage.documentOffset);}catch(__){a.push(0);}
        }
        return a;
    }

    function pageIndexLookup(indexes,count){
        var o={},i;
        if(indexes===null||indexes===undefined){for(i=0;i<count;i++)o[i]=true;return o;}
        for(i=0;i<indexes.length;i++)if(indexes[i]>=0&&indexes[i]<count)o[indexes[i]]=true;
        return o;
    }

    // =====================================================================
    // Parashah catalogue and matching
    // =====================================================================

    // =====================================================================
    // Rav Pe’alim (wie Leshon Chakhamim v1.0.1): Kolumnentitel = Abschnittsueberschrift
    // =====================================================================

    function normalizeSectionEn(s){
        // Rav Pe’alim: Siman-Titel unterscheiden sich nur durch Zahlen ("Siman 13") – Ziffern bleiben
        // erhalten (normalizeEnglishWords des Ben-Ish-Chai-Skripts entfernt sie).
        s=cleanHeadingText(s).toLowerCase();
        s=s.replace(/[^a-z0-9]+/g," ").replace(/\s+/g," ");
        return trim(s);
    }

    function buildSectionCatalogue(){
        // [hebraeischer Titel, englischer Titel, HE-Kurztitel, EN-Kurztitel, Gruppe] in Werkfolge;
        // erzeugt aus der Pipeline (rp_common.build_edition: Titel und Kurztitel je Siman)
        var a=[
            ["סוד ישרים סימן א׳ (ח״א סי׳ א׳)", "Sod Yesharim, Siman 1 (Part I, Siman 1)", "סוד ישרים א׳", "Sod Yesharim 1", "SY·I"],
            ["סוד ישרים סימן ב׳ (ח״א סי׳ ב׳)", "Sod Yesharim, Siman 2 (Part I, Siman 2)", "סוד ישרים ב׳", "Sod Yesharim 2", "SY·I"],
            ["סוד ישרים סימן ג׳ (ח״א סי׳ ג׳)", "Sod Yesharim, Siman 3 (Part I, Siman 3)", "סוד ישרים ג׳", "Sod Yesharim 3", "SY·I"],
            ["סוד ישרים סימן ד׳ (ח״א סי׳ ד׳)", "Sod Yesharim, Siman 4 (Part I, Siman 4)", "סוד ישרים ד׳", "Sod Yesharim 4", "SY·I"],
            ["סוד ישרים סימן ה׳ (ח״א סי׳ ה׳)", "Sod Yesharim, Siman 5 (Part I, Siman 5)", "סוד ישרים ה׳", "Sod Yesharim 5", "SY·I"],
            ["סוד ישרים סימן ו׳ (ח״א סי׳ ו׳)", "Sod Yesharim, Siman 6 (Part I, Siman 6)", "סוד ישרים ו׳", "Sod Yesharim 6", "SY·I"],
            ["סוד ישרים סימן ז׳ (ח״א סי׳ ז׳)", "Sod Yesharim, Siman 7 (Part I, Siman 7)", "סוד ישרים ז׳", "Sod Yesharim 7", "SY·I"],
            ["סוד ישרים סימן ח׳ (ח״א סי׳ ח׳)", "Sod Yesharim, Siman 8 (Part I, Siman 8)", "סוד ישרים ח׳", "Sod Yesharim 8", "SY·I"],
            ["סוד ישרים סימן ט׳ (ח״א סי׳ ט׳)", "Sod Yesharim, Siman 9 (Part I, Siman 9)", "סוד ישרים ט׳", "Sod Yesharim 9", "SY·I"],
            ["סוד ישרים סימן י׳ (ח״א סי׳ י׳)", "Sod Yesharim, Siman 10 (Part I, Siman 10)", "סוד ישרים י׳", "Sod Yesharim 10", "SY·I"],
            ["סוד ישרים סימן י״א (ח״א סי׳ י״א)", "Sod Yesharim, Siman 11 (Part I, Siman 11)", "סוד ישרים י״א", "Sod Yesharim 11", "SY·I"],
            ["סוד ישרים סימן י״ב (ח״א סי׳ י״ב)", "Sod Yesharim, Siman 12 (Part I, Siman 12)", "סוד ישרים י״ב", "Sod Yesharim 12", "SY·I"],
            ["סוד ישרים סימן י״ג (ח״א סי׳ י״ג)", "Sod Yesharim, Siman 13 (Part I, Siman 13)", "סוד ישרים י״ג", "Sod Yesharim 13", "SY·I"],
            ["סוד ישרים סימן י״ד (ח״א סי׳ י״ד)", "Sod Yesharim, Siman 14 (Part I, Siman 14)", "סוד ישרים י״ד", "Sod Yesharim 14", "SY·I"],
            ["סוד ישרים סימן ט״ו (ח״א סי׳ ט״ו)", "Sod Yesharim, Siman 15 (Part I, Siman 15)", "סוד ישרים ט״ו", "Sod Yesharim 15", "SY·I"],
            ["סוד ישרים סימן ט״ז (ח״א סי׳ ט״ז)", "Sod Yesharim, Siman 16 (Part I, Siman 16)", "סוד ישרים ט״ז", "Sod Yesharim 16", "SY·I"],
            ["סוד ישרים סימן י״ז (ח״א סי׳ י״ז)", "Sod Yesharim, Siman 17 (Part I, Siman 17)", "סוד ישרים י״ז", "Sod Yesharim 17", "SY·I"],
            ["סוד ישרים סימן י״ח (ח״ב סי׳ א׳)", "Sod Yesharim, Siman 18 (Part II, Siman 1)", "סוד ישרים י״ח", "Sod Yesharim 18", "SY·II"],
            ["סוד ישרים סימן י״ט (ח״ב סי׳ ב׳)", "Sod Yesharim, Siman 19 (Part II, Siman 2)", "סוד ישרים י״ט", "Sod Yesharim 19", "SY·II"],
            ["סוד ישרים סימן כ׳ (ח״ב סי׳ ג׳)", "Sod Yesharim, Siman 20 (Part II, Siman 3)", "סוד ישרים כ׳", "Sod Yesharim 20", "SY·II"],
            ["סוד ישרים סימן כ״א (ח״ב סי׳ ד׳)", "Sod Yesharim, Siman 21 (Part II, Siman 4)", "סוד ישרים כ״א", "Sod Yesharim 21", "SY·II"],
            ["סוד ישרים סימן כ״ב (ח״ב סי׳ ה׳)", "Sod Yesharim, Siman 22 (Part II, Siman 5)", "סוד ישרים כ״ב", "Sod Yesharim 22", "SY·II"],
            ["סוד ישרים סימן כ״ג (ח״ב סי׳ ו׳)", "Sod Yesharim, Siman 23 (Part II, Siman 6)", "סוד ישרים כ״ג", "Sod Yesharim 23", "SY·II"],
            ["סוד ישרים סימן כ״ד (ח״ב סי׳ ז׳)", "Sod Yesharim, Siman 24 (Part II, Siman 7)", "סוד ישרים כ״ד", "Sod Yesharim 24", "SY·II"],
            ["סוד ישרים סימן כ״ה (ח״ב סי׳ ח׳)", "Sod Yesharim, Siman 25 (Part II, Siman 8)", "סוד ישרים כ״ה", "Sod Yesharim 25", "SY·II"],
            ["סוד ישרים סימן כ״ו (ח״ב סי׳ ט׳)", "Sod Yesharim, Siman 26 (Part II, Siman 9)", "סוד ישרים כ״ו", "Sod Yesharim 26", "SY·II"],
            ["סוד ישרים סימן כ״ז (ח״ב סי׳ י׳)", "Sod Yesharim, Siman 27 (Part II, Siman 10)", "סוד ישרים כ״ז", "Sod Yesharim 27", "SY·II"],
            ["סוד ישרים סימן כ״ח (ח״ב סי׳ י״א)", "Sod Yesharim, Siman 28 (Part II, Siman 11)", "סוד ישרים כ״ח", "Sod Yesharim 28", "SY·II"],
            ["סוד ישרים סימן כ״ט (ח״ב סי׳ י״ב)", "Sod Yesharim, Siman 29 (Part II, Siman 12)", "סוד ישרים כ״ט", "Sod Yesharim 29", "SY·II"],
            ["סוד ישרים סימן ל׳ (ח״ב סי׳ י״ג)", "Sod Yesharim, Siman 30 (Part II, Siman 13)", "סוד ישרים ל׳", "Sod Yesharim 30", "SY·II"],
            ["סוד ישרים סימן ל״א (ח״ב סי׳ י״ד)", "Sod Yesharim, Siman 31 (Part II, Siman 14)", "סוד ישרים ל״א", "Sod Yesharim 31", "SY·II"],
            ["סוד ישרים סימן ל״ב (ח״ג סי׳ א׳)", "Sod Yesharim, Siman 32 (Part III, Siman 1)", "סוד ישרים ל״ב", "Sod Yesharim 32", "SY·III"],
            ["סוד ישרים סימן ל״ג (ח״ג סי׳ ב׳)", "Sod Yesharim, Siman 33 (Part III, Siman 2)", "סוד ישרים ל״ג", "Sod Yesharim 33", "SY·III"],
            ["סוד ישרים סימן ל״ד (ח״ג סי׳ ג׳)", "Sod Yesharim, Siman 34 (Part III, Siman 3)", "סוד ישרים ל״ד", "Sod Yesharim 34", "SY·III"],
            ["סוד ישרים סימן ל״ה (ח״ג סי׳ ד׳)", "Sod Yesharim, Siman 35 (Part III, Siman 4)", "סוד ישרים ל״ה", "Sod Yesharim 35", "SY·III"],
            ["סוד ישרים סימן ל״ו (ח״ג סי׳ ה׳)", "Sod Yesharim, Siman 36 (Part III, Siman 5)", "סוד ישרים ל״ו", "Sod Yesharim 36", "SY·III"],
            ["סוד ישרים סימן ל״ז (ח״ג סי׳ ו׳)", "Sod Yesharim, Siman 37 (Part III, Siman 6)", "סוד ישרים ל״ז", "Sod Yesharim 37", "SY·III"],
            ["סוד ישרים סימן ל״ח (ח״ג סי׳ ז׳)", "Sod Yesharim, Siman 38 (Part III, Siman 7)", "סוד ישרים ל״ח", "Sod Yesharim 38", "SY·III"],
            ["סוד ישרים סימן ל״ט (ח״ג סי׳ ח׳)", "Sod Yesharim, Siman 39 (Part III, Siman 8)", "סוד ישרים ל״ט", "Sod Yesharim 39", "SY·III"],
            ["סוד ישרים סימן מ׳ (ח״ג סי׳ ט׳)", "Sod Yesharim, Siman 40 (Part III, Siman 9)", "סוד ישרים מ׳", "Sod Yesharim 40", "SY·III"],
            ["סוד ישרים סימן מ״א (ח״ג סי׳ י׳)", "Sod Yesharim, Siman 41 (Part III, Siman 10)", "סוד ישרים מ״א", "Sod Yesharim 41", "SY·III"],
            ["סוד ישרים סימן מ״ב (ח״ג סי׳ י״א)", "Sod Yesharim, Siman 42 (Part III, Siman 11)", "סוד ישרים מ״ב", "Sod Yesharim 42", "SY·III"],
            ["סוד ישרים סימן מ״ג (ח״ג סי׳ י״ב)", "Sod Yesharim, Siman 43 (Part III, Siman 12)", "סוד ישרים מ״ג", "Sod Yesharim 43", "SY·III"],
            ["סוד ישרים סימן מ״ד (ח״ג סי׳ י״ג)", "Sod Yesharim, Siman 44 (Part III, Siman 13)", "סוד ישרים מ״ד", "Sod Yesharim 44", "SY·III"],
            ["סוד ישרים סימן מ״ה (ח״ד סי׳ א׳)", "Sod Yesharim, Siman 45 (Part IV, Siman 1)", "סוד ישרים מ״ה", "Sod Yesharim 45", "SY·IV"],
            ["סוד ישרים סימן מ״ו (ח״ד סי׳ ב׳)", "Sod Yesharim, Siman 46 (Part IV, Siman 2)", "סוד ישרים מ״ו", "Sod Yesharim 46", "SY·IV"],
            ["סוד ישרים סימן מ״ז (ח״ד סי׳ ג׳)", "Sod Yesharim, Siman 47 (Part IV, Siman 3)", "סוד ישרים מ״ז", "Sod Yesharim 47", "SY·IV"],
            ["סוד ישרים סימן מ״ח (ח״ד סי׳ ד׳)", "Sod Yesharim, Siman 48 (Part IV, Siman 4)", "סוד ישרים מ״ח", "Sod Yesharim 48", "SY·IV"],
            ["סוד ישרים סימן מ״ט (ח״ד סי׳ ה׳)", "Sod Yesharim, Siman 49 (Part IV, Siman 5)", "סוד ישרים מ״ט", "Sod Yesharim 49", "SY·IV"],
            ["סוד ישרים סימן נ׳ (ח״ד סי׳ ו׳)", "Sod Yesharim, Siman 50 (Part IV, Siman 6)", "סוד ישרים נ׳", "Sod Yesharim 50", "SY·IV"],
            ["סוד ישרים סימן נ״א (ח״ד סי׳ ז׳)", "Sod Yesharim, Siman 51 (Part IV, Siman 7)", "סוד ישרים נ״א", "Sod Yesharim 51", "SY·IV"],
            ["סוד ישרים סימן נ״ב (ח״ד סי׳ ח׳)", "Sod Yesharim, Siman 52 (Part IV, Siman 8)", "סוד ישרים נ״ב", "Sod Yesharim 52", "SY·IV"],
            ["סוד ישרים סימן נ״ג (ח״ד סי׳ ט׳)", "Sod Yesharim, Siman 53 (Part IV, Siman 9)", "סוד ישרים נ״ג", "Sod Yesharim 53", "SY·IV"],
            ["סוד ישרים סימן נ״ד (ח״ד סי׳ י׳)", "Sod Yesharim, Siman 54 (Part IV, Siman 10)", "סוד ישרים נ״ד", "Sod Yesharim 54", "SY·IV"],
            ["סוד ישרים סימן נ״ה (ח״ד סי׳ י״א)", "Sod Yesharim, Siman 55 (Part IV, Siman 11)", "סוד ישרים נ״ה", "Sod Yesharim 55", "SY·IV"],
            ["סוד ישרים סימן נ״ו (ח״ד סי׳ י״ב)", "Sod Yesharim, Siman 56 (Part IV, Siman 12)", "סוד ישרים נ״ו", "Sod Yesharim 56", "SY·IV"],
            ["סוד ישרים סימן נ״ז (ח״ד סי׳ י״ג)", "Sod Yesharim, Siman 57 (Part IV, Siman 13)", "סוד ישרים נ״ז", "Sod Yesharim 57", "SY·IV"],
            ["סוד ישרים סימן נ״ח (ח״ד סי׳ י״ד)", "Sod Yesharim, Siman 58 (Part IV, Siman 14)", "סוד ישרים נ״ח", "Sod Yesharim 58", "SY·IV"],
            ["סוד ישרים סימן נ״ט (ח״ד סי׳ ט״ו)", "Sod Yesharim, Siman 59 (Part IV, Siman 15)", "סוד ישרים נ״ט", "Sod Yesharim 59", "SY·IV"],
            ["סוד ישרים סימן ס׳ (ח״ד סי׳ ט״ז)", "Sod Yesharim, Siman 60 (Part IV, Siman 16)", "סוד ישרים ס׳", "Sod Yesharim 60", "SY·IV"],
            ["סוד ישרים סימן ס״א (ח״ד סי׳ י״ז)", "Sod Yesharim, Siman 61 (Part IV, Siman 17)", "סוד ישרים ס״א", "Sod Yesharim 61", "SY·IV"],
            ["סוד ישרים סימן ס״ב (ח״ד סי׳ י״ח)", "Sod Yesharim, Siman 62 (Part IV, Siman 18)", "סוד ישרים ס״ב", "Sod Yesharim 62", "SY·IV"],
            ["סוד ישרים סימן ס״ג (ח״ד סי׳ י״ט)", "Sod Yesharim, Siman 63 (Part IV, Siman 19)", "סוד ישרים ס״ג", "Sod Yesharim 63", "SY·IV"],
            ["סוד ישרים סימן ס״ד (ח״ד סי׳ כ׳)", "Sod Yesharim, Siman 64 (Part IV, Siman 20)", "סוד ישרים ס״ד", "Sod Yesharim 64", "SY·IV"],
            ["הקדמת המחבר · חלק א׳", "Author’s Introduction · Part I", "הקדמת המחבר ח״א", "Introduction, Part I", "VOR"],
            ["פתיחת הספר · חלק א׳", "Opening of the Book · Part I", "פתיחת הספר", "Opening of the Book", "VOR"],
            ["הקדמת המחבר · חלק ב׳", "Author’s Introduction · Part II", "הקדמת המחבר ח״ב", "Introduction, Part II", "VOR"],
            ["הקדמת המחבר · חלק ג׳", "Author’s Introduction · Part III", "הקדמת המחבר ח״ג", "Introduction, Part III", "VOR"],
            ["אורח חיים ח״א סימן א׳", "Orach Chayim, Part I, Siman 1", "או״ח ח״א א׳", "Orach Chayim I:1", "OC·I"],
            ["אורח חיים ח״א סימן ב׳", "Orach Chayim, Part I, Siman 2", "או״ח ח״א ב׳", "Orach Chayim I:2", "OC·I"],
            ["אורח חיים ח״א סימן ג׳", "Orach Chayim, Part I, Siman 3", "או״ח ח״א ג׳", "Orach Chayim I:3", "OC·I"],
            ["אורח חיים ח״א סימן ד׳", "Orach Chayim, Part I, Siman 4", "או״ח ח״א ד׳", "Orach Chayim I:4", "OC·I"],
            ["אורח חיים ח״א סימן ה׳", "Orach Chayim, Part I, Siman 5", "או״ח ח״א ה׳", "Orach Chayim I:5", "OC·I"],
            ["אורח חיים ח״א סימן ו׳", "Orach Chayim, Part I, Siman 6", "או״ח ח״א ו׳", "Orach Chayim I:6", "OC·I"],
            ["אורח חיים ח״א סימן ז׳", "Orach Chayim, Part I, Siman 7", "או״ח ח״א ז׳", "Orach Chayim I:7", "OC·I"],
            ["אורח חיים ח״א סימן ח׳", "Orach Chayim, Part I, Siman 8", "או״ח ח״א ח׳", "Orach Chayim I:8", "OC·I"],
            ["אורח חיים ח״א סימן ט׳", "Orach Chayim, Part I, Siman 9", "או״ח ח״א ט׳", "Orach Chayim I:9", "OC·I"],
            ["אורח חיים ח״א סימן י׳", "Orach Chayim, Part I, Siman 10", "או״ח ח״א י׳", "Orach Chayim I:10", "OC·I"],
            ["אורח חיים ח״א סימן י״א", "Orach Chayim, Part I, Siman 11", "או״ח ח״א י״א", "Orach Chayim I:11", "OC·I"],
            ["אורח חיים ח״א סימן י״ב", "Orach Chayim, Part I, Siman 12", "או״ח ח״א י״ב", "Orach Chayim I:12", "OC·I"],
            ["אורח חיים ח״א סימן י״ג", "Orach Chayim, Part I, Siman 13", "או״ח ח״א י״ג", "Orach Chayim I:13", "OC·I"],
            ["אורח חיים ח״א סימן י״ד", "Orach Chayim, Part I, Siman 14", "או״ח ח״א י״ד", "Orach Chayim I:14", "OC·I"],
            ["אורח חיים ח״א סימן ט״ו", "Orach Chayim, Part I, Siman 15", "או״ח ח״א ט״ו", "Orach Chayim I:15", "OC·I"],
            ["אורח חיים ח״א סימן ט״ז", "Orach Chayim, Part I, Siman 16", "או״ח ח״א ט״ז", "Orach Chayim I:16", "OC·I"],
            ["אורח חיים ח״א סימן י״ז", "Orach Chayim, Part I, Siman 17", "או״ח ח״א י״ז", "Orach Chayim I:17", "OC·I"],
            ["אורח חיים ח״א סימן י״ח", "Orach Chayim, Part I, Siman 18", "או״ח ח״א י״ח", "Orach Chayim I:18", "OC·I"],
            ["אורח חיים ח״א סימן י״ט", "Orach Chayim, Part I, Siman 19", "או״ח ח״א י״ט", "Orach Chayim I:19", "OC·I"],
            ["אורח חיים ח״א סימן כ׳", "Orach Chayim, Part I, Siman 20", "או״ח ח״א כ׳", "Orach Chayim I:20", "OC·I"],
            ["אורח חיים ח״א סימן כ״א", "Orach Chayim, Part I, Siman 21", "או״ח ח״א כ״א", "Orach Chayim I:21", "OC·I"],
            ["אורח חיים ח״א סימן כ״ב", "Orach Chayim, Part I, Siman 22", "או״ח ח״א כ״ב", "Orach Chayim I:22", "OC·I"],
            ["אורח חיים ח״א סימן כ״ג", "Orach Chayim, Part I, Siman 23", "או״ח ח״א כ״ג", "Orach Chayim I:23", "OC·I"],
            ["אורח חיים ח״א סימן כ״ד", "Orach Chayim, Part I, Siman 24", "או״ח ח״א כ״ד", "Orach Chayim I:24", "OC·I"],
            ["אורח חיים ח״א סימן כ״ה", "Orach Chayim, Part I, Siman 25", "או״ח ח״א כ״ה", "Orach Chayim I:25", "OC·I"],
            ["אורח חיים ח״א סימן כ״ו", "Orach Chayim, Part I, Siman 26", "או״ח ח״א כ״ו", "Orach Chayim I:26", "OC·I"],
            ["אורח חיים ח״א סימן כ״ז", "Orach Chayim, Part I, Siman 27", "או״ח ח״א כ״ז", "Orach Chayim I:27", "OC·I"],
            ["אורח חיים ח״א סימן כ״ח", "Orach Chayim, Part I, Siman 28", "או״ח ח״א כ״ח", "Orach Chayim I:28", "OC·I"],
            ["אורח חיים ח״א סימן כ״ט", "Orach Chayim, Part I, Siman 29", "או״ח ח״א כ״ט", "Orach Chayim I:29", "OC·I"],
            ["אורח חיים ח״א סימן ל׳", "Orach Chayim, Part I, Siman 30", "או״ח ח״א ל׳", "Orach Chayim I:30", "OC·I"],
            ["אורח חיים ח״א סימן ל״א", "Orach Chayim, Part I, Siman 31", "או״ח ח״א ל״א", "Orach Chayim I:31", "OC·I"],
            ["אורח חיים ח״א סימן ל״ב", "Orach Chayim, Part I, Siman 32", "או״ח ח״א ל״ב", "Orach Chayim I:32", "OC·I"],
            ["אורח חיים ח״א סימן ל״ג", "Orach Chayim, Part I, Siman 33", "או״ח ח״א ל״ג", "Orach Chayim I:33", "OC·I"],
            ["אורח חיים ח״א סימן ל״ד", "Orach Chayim, Part I, Siman 34", "או״ח ח״א ל״ד", "Orach Chayim I:34", "OC·I"],
            ["אורח חיים ח״א סימן ל״ה", "Orach Chayim, Part I, Siman 35", "או״ח ח״א ל״ה", "Orach Chayim I:35", "OC·I"],
            ["אורח חיים ח״ב סימן א׳", "Orach Chayim, Part II, Siman 1", "או״ח ח״ב א׳", "Orach Chayim II:1", "OC·II"],
            ["אורח חיים ח״ב סימן ב׳", "Orach Chayim, Part II, Siman 2", "או״ח ח״ב ב׳", "Orach Chayim II:2", "OC·II"],
            ["אורח חיים ח״ב סימן ג׳", "Orach Chayim, Part II, Siman 3", "או״ח ח״ב ג׳", "Orach Chayim II:3", "OC·II"],
            ["אורח חיים ח״ב סימן ד׳", "Orach Chayim, Part II, Siman 4", "או״ח ח״ב ד׳", "Orach Chayim II:4", "OC·II"],
            ["אורח חיים ח״ב סימן ה׳", "Orach Chayim, Part II, Siman 5", "או״ח ח״ב ה׳", "Orach Chayim II:5", "OC·II"],
            ["אורח חיים ח״ב סימן ו׳", "Orach Chayim, Part II, Siman 6", "או״ח ח״ב ו׳", "Orach Chayim II:6", "OC·II"],
            ["אורח חיים ח״ב סימן ז׳", "Orach Chayim, Part II, Siman 7", "או״ח ח״ב ז׳", "Orach Chayim II:7", "OC·II"],
            ["אורח חיים ח״ב סימן ח׳", "Orach Chayim, Part II, Siman 8", "או״ח ח״ב ח׳", "Orach Chayim II:8", "OC·II"],
            ["אורח חיים ח״ב סימן ט׳", "Orach Chayim, Part II, Siman 9", "או״ח ח״ב ט׳", "Orach Chayim II:9", "OC·II"],
            ["אורח חיים ח״ב סימן י׳", "Orach Chayim, Part II, Siman 10", "או״ח ח״ב י׳", "Orach Chayim II:10", "OC·II"],
            ["אורח חיים ח״ב סימן י״א", "Orach Chayim, Part II, Siman 11", "או״ח ח״ב י״א", "Orach Chayim II:11", "OC·II"],
            ["אורח חיים ח״ב סימן י״ב", "Orach Chayim, Part II, Siman 12", "או״ח ח״ב י״ב", "Orach Chayim II:12", "OC·II"],
            ["אורח חיים ח״ב סימן י״ג", "Orach Chayim, Part II, Siman 13", "או״ח ח״ב י״ג", "Orach Chayim II:13", "OC·II"],
            ["אורח חיים ח״ב סימן י״ד", "Orach Chayim, Part II, Siman 14", "או״ח ח״ב י״ד", "Orach Chayim II:14", "OC·II"],
            ["אורח חיים ח״ב סימן ט״ו", "Orach Chayim, Part II, Siman 15", "או״ח ח״ב ט״ו", "Orach Chayim II:15", "OC·II"],
            ["אורח חיים ח״ב סימן ט״ז", "Orach Chayim, Part II, Siman 16", "או״ח ח״ב ט״ז", "Orach Chayim II:16", "OC·II"],
            ["אורח חיים ח״ב סימן י״ז", "Orach Chayim, Part II, Siman 17", "או״ח ח״ב י״ז", "Orach Chayim II:17", "OC·II"],
            ["אורח חיים ח״ב סימן י״ח", "Orach Chayim, Part II, Siman 18", "או״ח ח״ב י״ח", "Orach Chayim II:18", "OC·II"],
            ["אורח חיים ח״ב סימן י״ט", "Orach Chayim, Part II, Siman 19", "או״ח ח״ב י״ט", "Orach Chayim II:19", "OC·II"],
            ["אורח חיים ח״ב סימן כ׳", "Orach Chayim, Part II, Siman 20", "או״ח ח״ב כ׳", "Orach Chayim II:20", "OC·II"],
            ["אורח חיים ח״ב סימן כ״א", "Orach Chayim, Part II, Siman 21", "או״ח ח״ב כ״א", "Orach Chayim II:21", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ב", "Orach Chayim, Part II, Siman 22", "או״ח ח״ב כ״ב", "Orach Chayim II:22", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ג", "Orach Chayim, Part II, Siman 23", "או״ח ח״ב כ״ג", "Orach Chayim II:23", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ד", "Orach Chayim, Part II, Siman 24", "או״ח ח״ב כ״ד", "Orach Chayim II:24", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ה", "Orach Chayim, Part II, Siman 25", "או״ח ח״ב כ״ה", "Orach Chayim II:25", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ו", "Orach Chayim, Part II, Siman 26", "או״ח ח״ב כ״ו", "Orach Chayim II:26", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ז", "Orach Chayim, Part II, Siman 27", "או״ח ח״ב כ״ז", "Orach Chayim II:27", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ח", "Orach Chayim, Part II, Siman 28", "או״ח ח״ב כ״ח", "Orach Chayim II:28", "OC·II"],
            ["אורח חיים ח״ב סימן כ״ט", "Orach Chayim, Part II, Siman 29", "או״ח ח״ב כ״ט", "Orach Chayim II:29", "OC·II"],
            ["אורח חיים ח״ב סימן ל׳", "Orach Chayim, Part II, Siman 30", "או״ח ח״ב ל׳", "Orach Chayim II:30", "OC·II"],
            ["אורח חיים ח״ב סימן ל״א", "Orach Chayim, Part II, Siman 31", "או״ח ח״ב ל״א", "Orach Chayim II:31", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ב", "Orach Chayim, Part II, Siman 32", "או״ח ח״ב ל״ב", "Orach Chayim II:32", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ג", "Orach Chayim, Part II, Siman 33", "או״ח ח״ב ל״ג", "Orach Chayim II:33", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ד", "Orach Chayim, Part II, Siman 34", "או״ח ח״ב ל״ד", "Orach Chayim II:34", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ה", "Orach Chayim, Part II, Siman 35", "או״ח ח״ב ל״ה", "Orach Chayim II:35", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ו", "Orach Chayim, Part II, Siman 36", "או״ח ח״ב ל״ו", "Orach Chayim II:36", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ז", "Orach Chayim, Part II, Siman 37", "או״ח ח״ב ל״ז", "Orach Chayim II:37", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ח", "Orach Chayim, Part II, Siman 38", "או״ח ח״ב ל״ח", "Orach Chayim II:38", "OC·II"],
            ["אורח חיים ח״ב סימן ל״ט", "Orach Chayim, Part II, Siman 39", "או״ח ח״ב ל״ט", "Orach Chayim II:39", "OC·II"],
            ["אורח חיים ח״ב סימן מ׳", "Orach Chayim, Part II, Siman 40", "או״ח ח״ב מ׳", "Orach Chayim II:40", "OC·II"],
            ["אורח חיים ח״ב סימן מ״א", "Orach Chayim, Part II, Siman 41", "או״ח ח״ב מ״א", "Orach Chayim II:41", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ב", "Orach Chayim, Part II, Siman 42", "או״ח ח״ב מ״ב", "Orach Chayim II:42", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ג", "Orach Chayim, Part II, Siman 43", "או״ח ח״ב מ״ג", "Orach Chayim II:43", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ד", "Orach Chayim, Part II, Siman 44", "או״ח ח״ב מ״ד", "Orach Chayim II:44", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ה", "Orach Chayim, Part II, Siman 45", "או״ח ח״ב מ״ה", "Orach Chayim II:45", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ו", "Orach Chayim, Part II, Siman 46", "או״ח ח״ב מ״ו", "Orach Chayim II:46", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ז", "Orach Chayim, Part II, Siman 47", "או״ח ח״ב מ״ז", "Orach Chayim II:47", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ח", "Orach Chayim, Part II, Siman 48", "או״ח ח״ב מ״ח", "Orach Chayim II:48", "OC·II"],
            ["אורח חיים ח״ב סימן מ״ט", "Orach Chayim, Part II, Siman 49", "או״ח ח״ב מ״ט", "Orach Chayim II:49", "OC·II"],
            ["אורח חיים ח״ב סימן נ׳", "Orach Chayim, Part II, Siman 50", "או״ח ח״ב נ׳", "Orach Chayim II:50", "OC·II"],
            ["אורח חיים ח״ב סימן נ״א", "Orach Chayim, Part II, Siman 51", "או״ח ח״ב נ״א", "Orach Chayim II:51", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ב", "Orach Chayim, Part II, Siman 52", "או״ח ח״ב נ״ב", "Orach Chayim II:52", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ג", "Orach Chayim, Part II, Siman 53", "או״ח ח״ב נ״ג", "Orach Chayim II:53", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ד", "Orach Chayim, Part II, Siman 54", "או״ח ח״ב נ״ד", "Orach Chayim II:54", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ה", "Orach Chayim, Part II, Siman 55", "או״ח ח״ב נ״ה", "Orach Chayim II:55", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ו", "Orach Chayim, Part II, Siman 56", "או״ח ח״ב נ״ו", "Orach Chayim II:56", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ז", "Orach Chayim, Part II, Siman 57", "או״ח ח״ב נ״ז", "Orach Chayim II:57", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ח", "Orach Chayim, Part II, Siman 58", "או״ח ח״ב נ״ח", "Orach Chayim II:58", "OC·II"],
            ["אורח חיים ח״ב סימן נ״ט", "Orach Chayim, Part II, Siman 59", "או״ח ח״ב נ״ט", "Orach Chayim II:59", "OC·II"],
            ["אורח חיים ח״ב סימן ס׳", "Orach Chayim, Part II, Siman 60", "או״ח ח״ב ס׳", "Orach Chayim II:60", "OC·II"],
            ["אורח חיים ח״ב סימן ס״א", "Orach Chayim, Part II, Siman 61", "או״ח ח״ב ס״א", "Orach Chayim II:61", "OC·II"],
            ["אורח חיים ח״ב סימן ס״ב", "Orach Chayim, Part II, Siman 62", "או״ח ח״ב ס״ב", "Orach Chayim II:62", "OC·II"],
            ["אורח חיים ח״ב סימן ס״ג", "Orach Chayim, Part II, Siman 63", "או״ח ח״ב ס״ג", "Orach Chayim II:63", "OC·II"],
            ["אורח חיים ח״ב סימן ס״ד", "Orach Chayim, Part II, Siman 64", "או״ח ח״ב ס״ד", "Orach Chayim II:64", "OC·II"],
            ["אורח חיים ח״ב סימן ס״ה", "Orach Chayim, Part II, Siman 65", "או״ח ח״ב ס״ה", "Orach Chayim II:65", "OC·II"],
            ["אורח חיים ח״ג סימן א׳", "Orach Chayim, Part III, Siman 1", "או״ח ח״ג א׳", "Orach Chayim III:1", "OC·III"],
            ["אורח חיים ח״ג סימן ב׳", "Orach Chayim, Part III, Siman 2", "או״ח ח״ג ב׳", "Orach Chayim III:2", "OC·III"],
            ["אורח חיים ח״ג סימן ג׳", "Orach Chayim, Part III, Siman 3", "או״ח ח״ג ג׳", "Orach Chayim III:3", "OC·III"],
            ["אורח חיים ח״ג סימן ד׳", "Orach Chayim, Part III, Siman 4", "או״ח ח״ג ד׳", "Orach Chayim III:4", "OC·III"],
            ["אורח חיים ח״ג סימן ה׳", "Orach Chayim, Part III, Siman 5", "או״ח ח״ג ה׳", "Orach Chayim III:5", "OC·III"],
            ["אורח חיים ח״ג סימן ו׳", "Orach Chayim, Part III, Siman 6", "או״ח ח״ג ו׳", "Orach Chayim III:6", "OC·III"],
            ["אורח חיים ח״ג סימן ז׳", "Orach Chayim, Part III, Siman 7", "או״ח ח״ג ז׳", "Orach Chayim III:7", "OC·III"],
            ["אורח חיים ח״ג סימן ח׳", "Orach Chayim, Part III, Siman 8", "או״ח ח״ג ח׳", "Orach Chayim III:8", "OC·III"],
            ["אורח חיים ח״ג סימן ט׳", "Orach Chayim, Part III, Siman 9", "או״ח ח״ג ט׳", "Orach Chayim III:9", "OC·III"],
            ["אורח חיים ח״ג סימן י׳", "Orach Chayim, Part III, Siman 10", "או״ח ח״ג י׳", "Orach Chayim III:10", "OC·III"],
            ["אורח חיים ח״ג סימן י״א", "Orach Chayim, Part III, Siman 11", "או״ח ח״ג י״א", "Orach Chayim III:11", "OC·III"],
            ["אורח חיים ח״ג סימן י״ב", "Orach Chayim, Part III, Siman 12", "או״ח ח״ג י״ב", "Orach Chayim III:12", "OC·III"],
            ["אורח חיים ח״ג סימן י״ג", "Orach Chayim, Part III, Siman 13", "או״ח ח״ג י״ג", "Orach Chayim III:13", "OC·III"],
            ["אורח חיים ח״ג סימן י״ד", "Orach Chayim, Part III, Siman 14", "או״ח ח״ג י״ד", "Orach Chayim III:14", "OC·III"],
            ["אורח חיים ח״ג סימן ט״ו", "Orach Chayim, Part III, Siman 15", "או״ח ח״ג ט״ו", "Orach Chayim III:15", "OC·III"],
            ["אורח חיים ח״ג סימן ט״ז", "Orach Chayim, Part III, Siman 16", "או״ח ח״ג ט״ז", "Orach Chayim III:16", "OC·III"],
            ["אורח חיים ח״ג סימן י״ז", "Orach Chayim, Part III, Siman 17", "או״ח ח״ג י״ז", "Orach Chayim III:17", "OC·III"],
            ["אורח חיים ח״ג סימן י״ח", "Orach Chayim, Part III, Siman 18", "או״ח ח״ג י״ח", "Orach Chayim III:18", "OC·III"],
            ["אורח חיים ח״ג סימן י״ט", "Orach Chayim, Part III, Siman 19", "או״ח ח״ג י״ט", "Orach Chayim III:19", "OC·III"],
            ["אורח חיים ח״ג סימן כ׳", "Orach Chayim, Part III, Siman 20", "או״ח ח״ג כ׳", "Orach Chayim III:20", "OC·III"],
            ["אורח חיים ח״ג סימן כ״א", "Orach Chayim, Part III, Siman 21", "או״ח ח״ג כ״א", "Orach Chayim III:21", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ב", "Orach Chayim, Part III, Siman 22", "או״ח ח״ג כ״ב", "Orach Chayim III:22", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ג", "Orach Chayim, Part III, Siman 23", "או״ח ח״ג כ״ג", "Orach Chayim III:23", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ד", "Orach Chayim, Part III, Siman 24", "או״ח ח״ג כ״ד", "Orach Chayim III:24", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ה", "Orach Chayim, Part III, Siman 25", "או״ח ח״ג כ״ה", "Orach Chayim III:25", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ו", "Orach Chayim, Part III, Siman 26", "או״ח ח״ג כ״ו", "Orach Chayim III:26", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ז", "Orach Chayim, Part III, Siman 27", "או״ח ח״ג כ״ז", "Orach Chayim III:27", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ח", "Orach Chayim, Part III, Siman 28", "או״ח ח״ג כ״ח", "Orach Chayim III:28", "OC·III"],
            ["אורח חיים ח״ג סימן כ״ט", "Orach Chayim, Part III, Siman 29", "או״ח ח״ג כ״ט", "Orach Chayim III:29", "OC·III"],
            ["אורח חיים ח״ג סימן ל׳", "Orach Chayim, Part III, Siman 30", "או״ח ח״ג ל׳", "Orach Chayim III:30", "OC·III"],
            ["אורח חיים ח״ג סימן ל״א", "Orach Chayim, Part III, Siman 31", "או״ח ח״ג ל״א", "Orach Chayim III:31", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ב", "Orach Chayim, Part III, Siman 32", "או״ח ח״ג ל״ב", "Orach Chayim III:32", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ג", "Orach Chayim, Part III, Siman 33", "או״ח ח״ג ל״ג", "Orach Chayim III:33", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ד", "Orach Chayim, Part III, Siman 34", "או״ח ח״ג ל״ד", "Orach Chayim III:34", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ה", "Orach Chayim, Part III, Siman 35", "או״ח ח״ג ל״ה", "Orach Chayim III:35", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ו", "Orach Chayim, Part III, Siman 36", "או״ח ח״ג ל״ו", "Orach Chayim III:36", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ז", "Orach Chayim, Part III, Siman 37", "או״ח ח״ג ל״ז", "Orach Chayim III:37", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ח", "Orach Chayim, Part III, Siman 38", "או״ח ח״ג ל״ח", "Orach Chayim III:38", "OC·III"],
            ["אורח חיים ח״ג סימן ל״ט", "Orach Chayim, Part III, Siman 39", "או״ח ח״ג ל״ט", "Orach Chayim III:39", "OC·III"],
            ["אורח חיים ח״ג סימן מ׳", "Orach Chayim, Part III, Siman 40", "או״ח ח״ג מ׳", "Orach Chayim III:40", "OC·III"],
            ["אורח חיים ח״ג סימן מ״א", "Orach Chayim, Part III, Siman 41", "או״ח ח״ג מ״א", "Orach Chayim III:41", "OC·III"],
            ["אורח חיים ח״ג סימן מ״ב", "Orach Chayim, Part III, Siman 42", "או״ח ח״ג מ״ב", "Orach Chayim III:42", "OC·III"],
            ["אורח חיים ח״ג סימן מ״ג", "Orach Chayim, Part III, Siman 43", "או״ח ח״ג מ״ג", "Orach Chayim III:43", "OC·III"],
            ["אורח חיים ח״ג סימן מ״ד", "Orach Chayim, Part III, Siman 44", "או״ח ח״ג מ״ד", "Orach Chayim III:44", "OC·III"],
            ["אורח חיים ח״ג סימן מ״ה", "Orach Chayim, Part III, Siman 45", "או״ח ח״ג מ״ה", "Orach Chayim III:45", "OC·III"],
            ["אורח חיים ח״ד סימן א׳", "Orach Chayim, Part IV, Siman 1", "או״ח ח״ד א׳", "Orach Chayim IV:1", "OC·IV"],
            ["אורח חיים ח״ד סימן ב׳", "Orach Chayim, Part IV, Siman 2", "או״ח ח״ד ב׳", "Orach Chayim IV:2", "OC·IV"],
            ["אורח חיים ח״ד סימן ג׳", "Orach Chayim, Part IV, Siman 3", "או״ח ח״ד ג׳", "Orach Chayim IV:3", "OC·IV"],
            ["אורח חיים ח״ד סימן ד׳", "Orach Chayim, Part IV, Siman 4", "או״ח ח״ד ד׳", "Orach Chayim IV:4", "OC·IV"],
            ["אורח חיים ח״ד סימן ה׳", "Orach Chayim, Part IV, Siman 5", "או״ח ח״ד ה׳", "Orach Chayim IV:5", "OC·IV"],
            ["אורח חיים ח״ד סימן ו׳", "Orach Chayim, Part IV, Siman 6", "או״ח ח״ד ו׳", "Orach Chayim IV:6", "OC·IV"],
            ["אורח חיים ח״ד סימן ז׳", "Orach Chayim, Part IV, Siman 7", "או״ח ח״ד ז׳", "Orach Chayim IV:7", "OC·IV"],
            ["אורח חיים ח״ד סימן ח׳", "Orach Chayim, Part IV, Siman 8", "או״ח ח״ד ח׳", "Orach Chayim IV:8", "OC·IV"],
            ["אורח חיים ח״ד סימן ט׳", "Orach Chayim, Part IV, Siman 9", "או״ח ח״ד ט׳", "Orach Chayim IV:9", "OC·IV"],
            ["אורח חיים ח״ד סימן י׳", "Orach Chayim, Part IV, Siman 10", "או״ח ח״ד י׳", "Orach Chayim IV:10", "OC·IV"],
            ["אורח חיים ח״ד סימן י״א", "Orach Chayim, Part IV, Siman 11", "או״ח ח״ד י״א", "Orach Chayim IV:11", "OC·IV"],
            ["אורח חיים ח״ד סימן י״ב", "Orach Chayim, Part IV, Siman 12", "או״ח ח״ד י״ב", "Orach Chayim IV:12", "OC·IV"],
            ["אורח חיים ח״ד סימן י״ג", "Orach Chayim, Part IV, Siman 13", "או״ח ח״ד י״ג", "Orach Chayim IV:13", "OC·IV"],
            ["אורח חיים ח״ד סימן י״ד", "Orach Chayim, Part IV, Siman 14", "או״ח ח״ד י״ד", "Orach Chayim IV:14", "OC·IV"],
            ["אורח חיים ח״ד סימן ט״ו", "Orach Chayim, Part IV, Siman 15", "או״ח ח״ד ט״ו", "Orach Chayim IV:15", "OC·IV"],
            ["אורח חיים ח״ד סימן ט״ז", "Orach Chayim, Part IV, Siman 16", "או״ח ח״ד ט״ז", "Orach Chayim IV:16", "OC·IV"],
            ["אורח חיים ח״ד סימן י״ז", "Orach Chayim, Part IV, Siman 17", "או״ח ח״ד י״ז", "Orach Chayim IV:17", "OC·IV"],
            ["אורח חיים ח״ד סימן י״ח", "Orach Chayim, Part IV, Siman 18", "או״ח ח״ד י״ח", "Orach Chayim IV:18", "OC·IV"],
            ["אורח חיים ח״ד סימן י״ט", "Orach Chayim, Part IV, Siman 19", "או״ח ח״ד י״ט", "Orach Chayim IV:19", "OC·IV"],
            ["אורח חיים ח״ד סימן כ׳", "Orach Chayim, Part IV, Siman 20", "או״ח ח״ד כ׳", "Orach Chayim IV:20", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״א", "Orach Chayim, Part IV, Siman 21", "או״ח ח״ד כ״א", "Orach Chayim IV:21", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ב", "Orach Chayim, Part IV, Siman 22", "או״ח ח״ד כ״ב", "Orach Chayim IV:22", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ג", "Orach Chayim, Part IV, Siman 23", "או״ח ח״ד כ״ג", "Orach Chayim IV:23", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ד", "Orach Chayim, Part IV, Siman 24", "או״ח ח״ד כ״ד", "Orach Chayim IV:24", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ה", "Orach Chayim, Part IV, Siman 25", "או״ח ח״ד כ״ה", "Orach Chayim IV:25", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ו", "Orach Chayim, Part IV, Siman 26", "או״ח ח״ד כ״ו", "Orach Chayim IV:26", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ז", "Orach Chayim, Part IV, Siman 27", "או״ח ח״ד כ״ז", "Orach Chayim IV:27", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ח", "Orach Chayim, Part IV, Siman 28", "או״ח ח״ד כ״ח", "Orach Chayim IV:28", "OC·IV"],
            ["אורח חיים ח״ד סימן כ״ט", "Orach Chayim, Part IV, Siman 29", "או״ח ח״ד כ״ט", "Orach Chayim IV:29", "OC·IV"],
            ["אורח חיים ח״ד סימן ל׳", "Orach Chayim, Part IV, Siman 30", "או״ח ח״ד ל׳", "Orach Chayim IV:30", "OC·IV"],
            ["אורח חיים ח״ד סימן ל״א", "Orach Chayim, Part IV, Siman 31", "או״ח ח״ד ל״א", "Orach Chayim IV:31", "OC·IV"],
            ["אורח חיים ח״ד סימן ל״ב", "Orach Chayim, Part IV, Siman 32", "או״ח ח״ד ל״ב", "Orach Chayim IV:32", "OC·IV"],
            ["אורח חיים ח״ד סימן ל״ג", "Orach Chayim, Part IV, Siman 33", "או״ח ח״ד ל״ג", "Orach Chayim IV:33", "OC·IV"],
            ["אורח חיים ח״ד סימן ל״ד", "Orach Chayim, Part IV, Siman 34", "או״ח ח״ד ל״ד", "Orach Chayim IV:34", "OC·IV"],
            ["אורח חיים ח״ד סימן ל״ה", "Orach Chayim, Part IV, Siman 35", "או״ח ח״ד ל״ה", "Orach Chayim IV:35", "OC·IV"],
            ["אורח חיים ח״ד סימן ל״ט", "Orach Chayim, Part IV, Siman 39", "או״ח ח״ד ל״ט", "Orach Chayim IV:39", "OC·IV"],
            ["אורח חיים ח״ד סימן מ׳", "Orach Chayim, Part IV, Siman 40", "או״ח ח״ד מ׳", "Orach Chayim IV:40", "OC·IV"],
            ["אורח חיים ח״ד סימן מ״א", "Orach Chayim, Part IV, Siman 41", "או״ח ח״ד מ״א", "Orach Chayim IV:41", "OC·IV"],
            ["אורח חיים ח״ד סימן מ״ב", "Orach Chayim, Part IV, Siman 42", "או״ח ח״ד מ״ב", "Orach Chayim IV:42", "OC·IV"],
            ["אורח חיים ח״ד סימן מ״ג", "Orach Chayim, Part IV, Siman 43", "או״ח ח״ד מ״ג", "Orach Chayim IV:43", "OC·IV"],
            ["קונטרס בית תפלה", "Kuntres Beit Tefillah", "קונטרס בית תפלה", "Kuntres Beit Tefillah", "BT"],
            ["יורה דעה ח״א סימן א׳", "Yoreh Deah, Part I, Siman 1", "יו״ד ח״א א׳", "Yoreh Deah I:1", "YD·I"],
            ["יורה דעה ח״א סימן ב׳", "Yoreh Deah, Part I, Siman 2", "יו״ד ח״א ב׳", "Yoreh Deah I:2", "YD·I"],
            ["יורה דעה ח״א סימן ג׳", "Yoreh Deah, Part I, Siman 3", "יו״ד ח״א ג׳", "Yoreh Deah I:3", "YD·I"],
            ["יורה דעה ח״א סימן ד׳", "Yoreh Deah, Part I, Siman 4", "יו״ד ח״א ד׳", "Yoreh Deah I:4", "YD·I"],
            ["יורה דעה ח״א סימן ה׳", "Yoreh Deah, Part I, Siman 5", "יו״ד ח״א ה׳", "Yoreh Deah I:5", "YD·I"],
            ["יורה דעה ח״א סימן ו׳", "Yoreh Deah, Part I, Siman 6", "יו״ד ח״א ו׳", "Yoreh Deah I:6", "YD·I"],
            ["יורה דעה ח״א סימן ז׳", "Yoreh Deah, Part I, Siman 7", "יו״ד ח״א ז׳", "Yoreh Deah I:7", "YD·I"],
            ["יורה דעה ח״א סימן ח׳", "Yoreh Deah, Part I, Siman 8", "יו״ד ח״א ח׳", "Yoreh Deah I:8", "YD·I"],
            ["יורה דעה ח״א סימן ט׳", "Yoreh Deah, Part I, Siman 9", "יו״ד ח״א ט׳", "Yoreh Deah I:9", "YD·I"],
            ["יורה דעה ח״א סימן י׳", "Yoreh Deah, Part I, Siman 10", "יו״ד ח״א י׳", "Yoreh Deah I:10", "YD·I"],
            ["יורה דעה ח״א סימן י״א", "Yoreh Deah, Part I, Siman 11", "יו״ד ח״א י״א", "Yoreh Deah I:11", "YD·I"],
            ["יורה דעה ח״א סימן י״ב", "Yoreh Deah, Part I, Siman 12", "יו״ד ח״א י״ב", "Yoreh Deah I:12", "YD·I"],
            ["יורה דעה ח״א סימן י״ג", "Yoreh Deah, Part I, Siman 13", "יו״ד ח״א י״ג", "Yoreh Deah I:13", "YD·I"],
            ["יורה דעה ח״א סימן י״ד", "Yoreh Deah, Part I, Siman 14", "יו״ד ח״א י״ד", "Yoreh Deah I:14", "YD·I"],
            ["יורה דעה ח״א סימן ט״ו", "Yoreh Deah, Part I, Siman 15", "יו״ד ח״א ט״ו", "Yoreh Deah I:15", "YD·I"],
            ["יורה דעה ח״א סימן ט״ז", "Yoreh Deah, Part I, Siman 16", "יו״ד ח״א ט״ז", "Yoreh Deah I:16", "YD·I"],
            ["יורה דעה ח״א סימן י״ז", "Yoreh Deah, Part I, Siman 17", "יו״ד ח״א י״ז", "Yoreh Deah I:17", "YD·I"],
            ["יורה דעה ח״א סימן י״ח", "Yoreh Deah, Part I, Siman 18", "יו״ד ח״א י״ח", "Yoreh Deah I:18", "YD·I"],
            ["יורה דעה ח״א סימן י״ט", "Yoreh Deah, Part I, Siman 19", "יו״ד ח״א י״ט", "Yoreh Deah I:19", "YD·I"],
            ["יורה דעה ח״א סימן כ׳", "Yoreh Deah, Part I, Siman 20", "יו״ד ח״א כ׳", "Yoreh Deah I:20", "YD·I"],
            ["יורה דעה ח״א סימן כ״א", "Yoreh Deah, Part I, Siman 21", "יו״ד ח״א כ״א", "Yoreh Deah I:21", "YD·I"],
            ["יורה דעה ח״א סימן כ״ב", "Yoreh Deah, Part I, Siman 22", "יו״ד ח״א כ״ב", "Yoreh Deah I:22", "YD·I"],
            ["יורה דעה ח״א סימן כ״ג", "Yoreh Deah, Part I, Siman 23", "יו״ד ח״א כ״ג", "Yoreh Deah I:23", "YD·I"],
            ["יורה דעה ח״א סימן כ״ד", "Yoreh Deah, Part I, Siman 24", "יו״ד ח״א כ״ד", "Yoreh Deah I:24", "YD·I"],
            ["יורה דעה ח״א סימן כ״ה", "Yoreh Deah, Part I, Siman 25", "יו״ד ח״א כ״ה", "Yoreh Deah I:25", "YD·I"],
            ["יורה דעה ח״א סימן כ״ו", "Yoreh Deah, Part I, Siman 26", "יו״ד ח״א כ״ו", "Yoreh Deah I:26", "YD·I"],
            ["יורה דעה ח״א סימן כ״ז", "Yoreh Deah, Part I, Siman 27", "יו״ד ח״א כ״ז", "Yoreh Deah I:27", "YD·I"],
            ["יורה דעה ח״א סימן כ״ח", "Yoreh Deah, Part I, Siman 28", "יו״ד ח״א כ״ח", "Yoreh Deah I:28", "YD·I"],
            ["יורה דעה ח״א סימן כ״ט", "Yoreh Deah, Part I, Siman 29", "יו״ד ח״א כ״ט", "Yoreh Deah I:29", "YD·I"],
            ["יורה דעה ח״א סימן ל׳", "Yoreh Deah, Part I, Siman 30", "יו״ד ח״א ל׳", "Yoreh Deah I:30", "YD·I"],
            ["יורה דעה ח״א סימן ל״א", "Yoreh Deah, Part I, Siman 31", "יו״ד ח״א ל״א", "Yoreh Deah I:31", "YD·I"],
            ["יורה דעה ח״א סימן ל״ב", "Yoreh Deah, Part I, Siman 32", "יו״ד ח״א ל״ב", "Yoreh Deah I:32", "YD·I"],
            ["יורה דעה ח״א סימן ל״ג", "Yoreh Deah, Part I, Siman 33", "יו״ד ח״א ל״ג", "Yoreh Deah I:33", "YD·I"],
            ["יורה דעה ח״א סימן ל״ד", "Yoreh Deah, Part I, Siman 34", "יו״ד ח״א ל״ד", "Yoreh Deah I:34", "YD·I"],
            ["יורה דעה ח״א סימן ל״ה", "Yoreh Deah, Part I, Siman 35", "יו״ד ח״א ל״ה", "Yoreh Deah I:35", "YD·I"],
            ["יורה דעה ח״א סימן ל״ו", "Yoreh Deah, Part I, Siman 36", "יו״ד ח״א ל״ו", "Yoreh Deah I:36", "YD·I"],
            ["יורה דעה ח״א סימן ל״ז", "Yoreh Deah, Part I, Siman 37", "יו״ד ח״א ל״ז", "Yoreh Deah I:37", "YD·I"],
            ["יורה דעה ח״א סימן ל״ח", "Yoreh Deah, Part I, Siman 38", "יו״ד ח״א ל״ח", "Yoreh Deah I:38", "YD·I"],
            ["יורה דעה ח״א סימן ל״ט", "Yoreh Deah, Part I, Siman 39", "יו״ד ח״א ל״ט", "Yoreh Deah I:39", "YD·I"],
            ["יורה דעה ח״א סימן מ׳", "Yoreh Deah, Part I, Siman 40", "יו״ד ח״א מ׳", "Yoreh Deah I:40", "YD·I"],
            ["יורה דעה ח״א סימן מ״א", "Yoreh Deah, Part I, Siman 41", "יו״ד ח״א מ״א", "Yoreh Deah I:41", "YD·I"],
            ["יורה דעה ח״א סימן מ״ב", "Yoreh Deah, Part I, Siman 42", "יו״ד ח״א מ״ב", "Yoreh Deah I:42", "YD·I"],
            ["יורה דעה ח״א סימן מ״ג", "Yoreh Deah, Part I, Siman 43", "יו״ד ח״א מ״ג", "Yoreh Deah I:43", "YD·I"],
            ["יורה דעה ח״א סימן מ״ד", "Yoreh Deah, Part I, Siman 44", "יו״ד ח״א מ״ד", "Yoreh Deah I:44", "YD·I"],
            ["יורה דעה ח״א סימן מ״ה", "Yoreh Deah, Part I, Siman 45", "יו״ד ח״א מ״ה", "Yoreh Deah I:45", "YD·I"],
            ["יורה דעה ח״א סימן מ״ו", "Yoreh Deah, Part I, Siman 46", "יו״ד ח״א מ״ו", "Yoreh Deah I:46", "YD·I"],
            ["יורה דעה ח״א סימן מ״ז", "Yoreh Deah, Part I, Siman 47", "יו״ד ח״א מ״ז", "Yoreh Deah I:47", "YD·I"],
            ["יורה דעה ח״א סימן מ״ח", "Yoreh Deah, Part I, Siman 48", "יו״ד ח״א מ״ח", "Yoreh Deah I:48", "YD·I"],
            ["יורה דעה ח״א סימן מ״ט", "Yoreh Deah, Part I, Siman 49", "יו״ד ח״א מ״ט", "Yoreh Deah I:49", "YD·I"],
            ["יורה דעה ח״א סימן נ׳", "Yoreh Deah, Part I, Siman 50", "יו״ד ח״א נ׳", "Yoreh Deah I:50", "YD·I"],
            ["יורה דעה ח״א סימן נ״א", "Yoreh Deah, Part I, Siman 51", "יו״ד ח״א נ״א", "Yoreh Deah I:51", "YD·I"],
            ["יורה דעה ח״א סימן נ״ב", "Yoreh Deah, Part I, Siman 52", "יו״ד ח״א נ״ב", "Yoreh Deah I:52", "YD·I"],
            ["יורה דעה ח״א סימן נ״ג", "Yoreh Deah, Part I, Siman 53", "יו״ד ח״א נ״ג", "Yoreh Deah I:53", "YD·I"],
            ["יורה דעה ח״א סימן נ״ד", "Yoreh Deah, Part I, Siman 54", "יו״ד ח״א נ״ד", "Yoreh Deah I:54", "YD·I"],
            ["יורה דעה ח״א סימן נ״ה", "Yoreh Deah, Part I, Siman 55", "יו״ד ח״א נ״ה", "Yoreh Deah I:55", "YD·I"],
            ["יורה דעה ח״א סימן נ״ו", "Yoreh Deah, Part I, Siman 56", "יו״ד ח״א נ״ו", "Yoreh Deah I:56", "YD·I"],
            ["יורה דעה ח״א סימן נ״ז", "Yoreh Deah, Part I, Siman 57", "יו״ד ח״א נ״ז", "Yoreh Deah I:57", "YD·I"],
            ["יורה דעה ח״ב סימן א׳", "Yoreh Deah, Part II, Siman 1", "יו״ד ח״ב א׳", "Yoreh Deah II:1", "YD·II"],
            ["יורה דעה ח״ב סימן ב׳", "Yoreh Deah, Part II, Siman 2", "יו״ד ח״ב ב׳", "Yoreh Deah II:2", "YD·II"],
            ["יורה דעה ח״ב סימן ג׳", "Yoreh Deah, Part II, Siman 3", "יו״ד ח״ב ג׳", "Yoreh Deah II:3", "YD·II"],
            ["יורה דעה ח״ב סימן ד׳", "Yoreh Deah, Part II, Siman 4", "יו״ד ח״ב ד׳", "Yoreh Deah II:4", "YD·II"],
            ["יורה דעה ח״ב סימן ה׳", "Yoreh Deah, Part II, Siman 5", "יו״ד ח״ב ה׳", "Yoreh Deah II:5", "YD·II"],
            ["יורה דעה ח״ב סימן ו׳", "Yoreh Deah, Part II, Siman 6", "יו״ד ח״ב ו׳", "Yoreh Deah II:6", "YD·II"],
            ["יורה דעה ח״ב סימן ז׳", "Yoreh Deah, Part II, Siman 7", "יו״ד ח״ב ז׳", "Yoreh Deah II:7", "YD·II"],
            ["יורה דעה ח״ב סימן ח׳", "Yoreh Deah, Part II, Siman 8", "יו״ד ח״ב ח׳", "Yoreh Deah II:8", "YD·II"],
            ["יורה דעה ח״ב סימן ט׳", "Yoreh Deah, Part II, Siman 9", "יו״ד ח״ב ט׳", "Yoreh Deah II:9", "YD·II"],
            ["יורה דעה ח״ב סימן י׳", "Yoreh Deah, Part II, Siman 10", "יו״ד ח״ב י׳", "Yoreh Deah II:10", "YD·II"],
            ["יורה דעה ח״ב סימן י״א", "Yoreh Deah, Part II, Siman 11", "יו״ד ח״ב י״א", "Yoreh Deah II:11", "YD·II"],
            ["יורה דעה ח״ב סימן י״ב", "Yoreh Deah, Part II, Siman 12", "יו״ד ח״ב י״ב", "Yoreh Deah II:12", "YD·II"],
            ["יורה דעה ח״ב סימן י״ג", "Yoreh Deah, Part II, Siman 13", "יו״ד ח״ב י״ג", "Yoreh Deah II:13", "YD·II"],
            ["יורה דעה ח״ב סימן י״ד", "Yoreh Deah, Part II, Siman 14", "יו״ד ח״ב י״ד", "Yoreh Deah II:14", "YD·II"],
            ["יורה דעה ח״ב סימן ט״ו", "Yoreh Deah, Part II, Siman 15", "יו״ד ח״ב ט״ו", "Yoreh Deah II:15", "YD·II"],
            ["יורה דעה ח״ב סימן ט״ז", "Yoreh Deah, Part II, Siman 16", "יו״ד ח״ב ט״ז", "Yoreh Deah II:16", "YD·II"],
            ["יורה דעה ח״ב סימן י״ז", "Yoreh Deah, Part II, Siman 17", "יו״ד ח״ב י״ז", "Yoreh Deah II:17", "YD·II"],
            ["יורה דעה ח״ב סימן י״ח", "Yoreh Deah, Part II, Siman 18", "יו״ד ח״ב י״ח", "Yoreh Deah II:18", "YD·II"],
            ["יורה דעה ח״ב סימן י״ט", "Yoreh Deah, Part II, Siman 19", "יו״ד ח״ב י״ט", "Yoreh Deah II:19", "YD·II"],
            ["יורה דעה ח״ב סימן כ׳", "Yoreh Deah, Part II, Siman 20", "יו״ד ח״ב כ׳", "Yoreh Deah II:20", "YD·II"],
            ["יורה דעה ח״ב סימן כ״א", "Yoreh Deah, Part II, Siman 21", "יו״ד ח״ב כ״א", "Yoreh Deah II:21", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ב", "Yoreh Deah, Part II, Siman 22", "יו״ד ח״ב כ״ב", "Yoreh Deah II:22", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ג", "Yoreh Deah, Part II, Siman 23", "יו״ד ח״ב כ״ג", "Yoreh Deah II:23", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ד", "Yoreh Deah, Part II, Siman 24", "יו״ד ח״ב כ״ד", "Yoreh Deah II:24", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ה", "Yoreh Deah, Part II, Siman 25", "יו״ד ח״ב כ״ה", "Yoreh Deah II:25", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ו", "Yoreh Deah, Part II, Siman 26", "יו״ד ח״ב כ״ו", "Yoreh Deah II:26", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ז", "Yoreh Deah, Part II, Siman 27", "יו״ד ח״ב כ״ז", "Yoreh Deah II:27", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ח", "Yoreh Deah, Part II, Siman 28", "יו״ד ח״ב כ״ח", "Yoreh Deah II:28", "YD·II"],
            ["יורה דעה ח״ב סימן כ״ט", "Yoreh Deah, Part II, Siman 29", "יו״ד ח״ב כ״ט", "Yoreh Deah II:29", "YD·II"],
            ["יורה דעה ח״ב סימן ל׳", "Yoreh Deah, Part II, Siman 30", "יו״ד ח״ב ל׳", "Yoreh Deah II:30", "YD·II"],
            ["יורה דעה ח״ב סימן ל״א", "Yoreh Deah, Part II, Siman 31", "יו״ד ח״ב ל״א", "Yoreh Deah II:31", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ב", "Yoreh Deah, Part II, Siman 32", "יו״ד ח״ב ל״ב", "Yoreh Deah II:32", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ג", "Yoreh Deah, Part II, Siman 33", "יו״ד ח״ב ל״ג", "Yoreh Deah II:33", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ד", "Yoreh Deah, Part II, Siman 34", "יו״ד ח״ב ל״ד", "Yoreh Deah II:34", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ה", "Yoreh Deah, Part II, Siman 35", "יו״ד ח״ב ל״ה", "Yoreh Deah II:35", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ו", "Yoreh Deah, Part II, Siman 36", "יו״ד ח״ב ל״ו", "Yoreh Deah II:36", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ז", "Yoreh Deah, Part II, Siman 37", "יו״ד ח״ב ל״ז", "Yoreh Deah II:37", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ח", "Yoreh Deah, Part II, Siman 38", "יו״ד ח״ב ל״ח", "Yoreh Deah II:38", "YD·II"],
            ["יורה דעה ח״ב סימן ל״ט", "Yoreh Deah, Part II, Siman 39", "יו״ד ח״ב ל״ט", "Yoreh Deah II:39", "YD·II"],
            ["יורה דעה ח״ב סימן מ׳", "Yoreh Deah, Part II, Siman 40", "יו״ד ח״ב מ׳", "Yoreh Deah II:40", "YD·II"],
            ["יורה דעה ח״ב סימן מ״א", "Yoreh Deah, Part II, Siman 41", "יו״ד ח״ב מ״א", "Yoreh Deah II:41", "YD·II"],
            ["יורה דעה ח״ג סימן א׳", "Yoreh Deah, Part III, Siman 1", "יו״ד ח״ג א׳", "Yoreh Deah III:1", "YD·III"],
            ["יורה דעה ח״ג סימן ב׳", "Yoreh Deah, Part III, Siman 2", "יו״ד ח״ג ב׳", "Yoreh Deah III:2", "YD·III"],
            ["יורה דעה ח״ג סימן ג׳", "Yoreh Deah, Part III, Siman 3", "יו״ד ח״ג ג׳", "Yoreh Deah III:3", "YD·III"],
            ["יורה דעה ח״ג סימן ד׳", "Yoreh Deah, Part III, Siman 4", "יו״ד ח״ג ד׳", "Yoreh Deah III:4", "YD·III"],
            ["יורה דעה ח״ג סימן ה׳", "Yoreh Deah, Part III, Siman 5", "יו״ד ח״ג ה׳", "Yoreh Deah III:5", "YD·III"],
            ["יורה דעה ח״ג סימן ו׳", "Yoreh Deah, Part III, Siman 6", "יו״ד ח״ג ו׳", "Yoreh Deah III:6", "YD·III"],
            ["יורה דעה ח״ג סימן ז׳", "Yoreh Deah, Part III, Siman 7", "יו״ד ח״ג ז׳", "Yoreh Deah III:7", "YD·III"],
            ["יורה דעה ח״ג סימן ח׳", "Yoreh Deah, Part III, Siman 8", "יו״ד ח״ג ח׳", "Yoreh Deah III:8", "YD·III"],
            ["יורה דעה ח״ג סימן ט׳", "Yoreh Deah, Part III, Siman 9", "יו״ד ח״ג ט׳", "Yoreh Deah III:9", "YD·III"],
            ["יורה דעה ח״ג סימן י׳", "Yoreh Deah, Part III, Siman 10", "יו״ד ח״ג י׳", "Yoreh Deah III:10", "YD·III"],
            ["יורה דעה ח״ג סימן י״א", "Yoreh Deah, Part III, Siman 11", "יו״ד ח״ג י״א", "Yoreh Deah III:11", "YD·III"],
            ["יורה דעה ח״ג סימן י״ב", "Yoreh Deah, Part III, Siman 12", "יו״ד ח״ג י״ב", "Yoreh Deah III:12", "YD·III"],
            ["יורה דעה ח״ג סימן י״ג", "Yoreh Deah, Part III, Siman 13", "יו״ד ח״ג י״ג", "Yoreh Deah III:13", "YD·III"],
            ["יורה דעה ח״ג סימן י״ד", "Yoreh Deah, Part III, Siman 14", "יו״ד ח״ג י״ד", "Yoreh Deah III:14", "YD·III"],
            ["יורה דעה ח״ג סימן ט״ו", "Yoreh Deah, Part III, Siman 15", "יו״ד ח״ג ט״ו", "Yoreh Deah III:15", "YD·III"],
            ["יורה דעה ח״ג סימן ט״ז", "Yoreh Deah, Part III, Siman 16", "יו״ד ח״ג ט״ז", "Yoreh Deah III:16", "YD·III"],
            ["יורה דעה ח״ג סימן י״ז", "Yoreh Deah, Part III, Siman 17", "יו״ד ח״ג י״ז", "Yoreh Deah III:17", "YD·III"],
            ["יורה דעה ח״ג סימן י״ח", "Yoreh Deah, Part III, Siman 18", "יו״ד ח״ג י״ח", "Yoreh Deah III:18", "YD·III"],
            ["יורה דעה ח״ג סימן י״ט", "Yoreh Deah, Part III, Siman 19", "יו״ד ח״ג י״ט", "Yoreh Deah III:19", "YD·III"],
            ["יורה דעה ח״ג סימן כ׳", "Yoreh Deah, Part III, Siman 20", "יו״ד ח״ג כ׳", "Yoreh Deah III:20", "YD·III"],
            ["יורה דעה ח״ג סימן כ״א", "Yoreh Deah, Part III, Siman 21", "יו״ד ח״ג כ״א", "Yoreh Deah III:21", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ב", "Yoreh Deah, Part III, Siman 22", "יו״ד ח״ג כ״ב", "Yoreh Deah III:22", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ג", "Yoreh Deah, Part III, Siman 23", "יו״ד ח״ג כ״ג", "Yoreh Deah III:23", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ד", "Yoreh Deah, Part III, Siman 24", "יו״ד ח״ג כ״ד", "Yoreh Deah III:24", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ה", "Yoreh Deah, Part III, Siman 25", "יו״ד ח״ג כ״ה", "Yoreh Deah III:25", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ו", "Yoreh Deah, Part III, Siman 26", "יו״ד ח״ג כ״ו", "Yoreh Deah III:26", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ז", "Yoreh Deah, Part III, Siman 27", "יו״ד ח״ג כ״ז", "Yoreh Deah III:27", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ח", "Yoreh Deah, Part III, Siman 28", "יו״ד ח״ג כ״ח", "Yoreh Deah III:28", "YD·III"],
            ["יורה דעה ח״ג סימן כ״ט", "Yoreh Deah, Part III, Siman 29", "יו״ד ח״ג כ״ט", "Yoreh Deah III:29", "YD·III"],
            ["יורה דעה ח״ג סימן ל׳", "Yoreh Deah, Part III, Siman 30", "יו״ד ח״ג ל׳", "Yoreh Deah III:30", "YD·III"],
            ["יורה דעה ח״ג סימן ל״א", "Yoreh Deah, Part III, Siman 31", "יו״ד ח״ג ל״א", "Yoreh Deah III:31", "YD·III"],
            ["יורה דעה ח״ג סימן ל״ב", "Yoreh Deah, Part III, Siman 32", "יו״ד ח״ג ל״ב", "Yoreh Deah III:32", "YD·III"],
            ["יורה דעה ח״ד סימן א׳", "Yoreh Deah, Part IV, Siman 1", "יו״ד ח״ד א׳", "Yoreh Deah IV:1", "YD·IV"],
            ["יורה דעה ח״ד סימן ב׳", "Yoreh Deah, Part IV, Siman 2", "יו״ד ח״ד ב׳", "Yoreh Deah IV:2", "YD·IV"],
            ["יורה דעה ח״ד סימן ג׳", "Yoreh Deah, Part IV, Siman 3", "יו״ד ח״ד ג׳", "Yoreh Deah IV:3", "YD·IV"],
            ["יורה דעה ח״ד סימן ד׳", "Yoreh Deah, Part IV, Siman 4", "יו״ד ח״ד ד׳", "Yoreh Deah IV:4", "YD·IV"],
            ["יורה דעה ח״ד סימן ה׳", "Yoreh Deah, Part IV, Siman 5", "יו״ד ח״ד ה׳", "Yoreh Deah IV:5", "YD·IV"],
            ["יורה דעה ח״ד סימן ו׳", "Yoreh Deah, Part IV, Siman 6", "יו״ד ח״ד ו׳", "Yoreh Deah IV:6", "YD·IV"],
            ["יורה דעה ח״ד סימן ז׳", "Yoreh Deah, Part IV, Siman 7", "יו״ד ח״ד ז׳", "Yoreh Deah IV:7", "YD·IV"],
            ["יורה דעה ח״ד סימן ח׳", "Yoreh Deah, Part IV, Siman 8", "יו״ד ח״ד ח׳", "Yoreh Deah IV:8", "YD·IV"],
            ["יורה דעה ח״ד סימן ט׳", "Yoreh Deah, Part IV, Siman 9", "יו״ד ח״ד ט׳", "Yoreh Deah IV:9", "YD·IV"],
            ["יורה דעה ח״ד סימן י׳", "Yoreh Deah, Part IV, Siman 10", "יו״ד ח״ד י׳", "Yoreh Deah IV:10", "YD·IV"],
            ["יורה דעה ח״ד סימן י״א", "Yoreh Deah, Part IV, Siman 11", "יו״ד ח״ד י״א", "Yoreh Deah IV:11", "YD·IV"],
            ["יורה דעה ח״ד סימן י״ב", "Yoreh Deah, Part IV, Siman 12", "יו״ד ח״ד י״ב", "Yoreh Deah IV:12", "YD·IV"],
            ["יורה דעה ח״ד סימן י״ג", "Yoreh Deah, Part IV, Siman 13", "יו״ד ח״ד י״ג", "Yoreh Deah IV:13", "YD·IV"],
            ["יורה דעה ח״ד סימן י״ד", "Yoreh Deah, Part IV, Siman 14", "יו״ד ח״ד י״ד", "Yoreh Deah IV:14", "YD·IV"],
            ["יורה דעה ח״ד סימן ט״ו", "Yoreh Deah, Part IV, Siman 15", "יו״ד ח״ד ט״ו", "Yoreh Deah IV:15", "YD·IV"],
            ["יורה דעה ח״ד סימן ט״ז", "Yoreh Deah, Part IV, Siman 16", "יו״ד ח״ד ט״ז", "Yoreh Deah IV:16", "YD·IV"],
            ["יורה דעה ח״ד סימן י״ז", "Yoreh Deah, Part IV, Siman 17", "יו״ד ח״ד י״ז", "Yoreh Deah IV:17", "YD·IV"],
            ["יורה דעה ח״ד סימן י״ח", "Yoreh Deah, Part IV, Siman 18", "יו״ד ח״ד י״ח", "Yoreh Deah IV:18", "YD·IV"],
            ["יורה דעה ח״ד סימן י״ט", "Yoreh Deah, Part IV, Siman 19", "יו״ד ח״ד י״ט", "Yoreh Deah IV:19", "YD·IV"],
            ["יורה דעה ח״ד סימן כ׳", "Yoreh Deah, Part IV, Siman 20", "יו״ד ח״ד כ׳", "Yoreh Deah IV:20", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״א", "Yoreh Deah, Part IV, Siman 21", "יו״ד ח״ד כ״א", "Yoreh Deah IV:21", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ב", "Yoreh Deah, Part IV, Siman 22", "יו״ד ח״ד כ״ב", "Yoreh Deah IV:22", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ג", "Yoreh Deah, Part IV, Siman 23", "יו״ד ח״ד כ״ג", "Yoreh Deah IV:23", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ד", "Yoreh Deah, Part IV, Siman 24", "יו״ד ח״ד כ״ד", "Yoreh Deah IV:24", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ה", "Yoreh Deah, Part IV, Siman 25", "יו״ד ח״ד כ״ה", "Yoreh Deah IV:25", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ו", "Yoreh Deah, Part IV, Siman 26", "יו״ד ח״ד כ״ו", "Yoreh Deah IV:26", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ז", "Yoreh Deah, Part IV, Siman 27", "יו״ד ח״ד כ״ז", "Yoreh Deah IV:27", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ח", "Yoreh Deah, Part IV, Siman 28", "יו״ד ח״ד כ״ח", "Yoreh Deah IV:28", "YD·IV"],
            ["יורה דעה ח״ד סימן כ״ט", "Yoreh Deah, Part IV, Siman 29", "יו״ד ח״ד כ״ט", "Yoreh Deah IV:29", "YD·IV"],
            ["יורה דעה ח״ד סימן ל׳", "Yoreh Deah, Part IV, Siman 30", "יו״ד ח״ד ל׳", "Yoreh Deah IV:30", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״א", "Yoreh Deah, Part IV, Siman 31", "יו״ד ח״ד ל״א", "Yoreh Deah IV:31", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ב", "Yoreh Deah, Part IV, Siman 32", "יו״ד ח״ד ל״ב", "Yoreh Deah IV:32", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ג", "Yoreh Deah, Part IV, Siman 33", "יו״ד ח״ד ל״ג", "Yoreh Deah IV:33", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ד", "Yoreh Deah, Part IV, Siman 34", "יו״ד ח״ד ל״ד", "Yoreh Deah IV:34", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ה", "Yoreh Deah, Part IV, Siman 35", "יו״ד ח״ד ל״ה", "Yoreh Deah IV:35", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ו", "Yoreh Deah, Part IV, Siman 36", "יו״ד ח״ד ל״ו", "Yoreh Deah IV:36", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ז", "Yoreh Deah, Part IV, Siman 37", "יו״ד ח״ד ל״ז", "Yoreh Deah IV:37", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ח", "Yoreh Deah, Part IV, Siman 38", "יו״ד ח״ד ל״ח", "Yoreh Deah IV:38", "YD·IV"],
            ["יורה דעה ח״ד סימן ל״ט", "Yoreh Deah, Part IV, Siman 39", "יו״ד ח״ד ל״ט", "Yoreh Deah IV:39", "YD·IV"],
            ["אבן העזר ח״א סימן א׳", "Even HaEzer, Part I, Siman 1", "אה״ע ח״א א׳", "Even HaEzer I:1", "EH·I"],
            ["אבן העזר ח״א סימן ב׳", "Even HaEzer, Part I, Siman 2", "אה״ע ח״א ב׳", "Even HaEzer I:2", "EH·I"],
            ["אבן העזר ח״א סימן ג׳", "Even HaEzer, Part I, Siman 3", "אה״ע ח״א ג׳", "Even HaEzer I:3", "EH·I"],
            ["אבן העזר ח״א סימן ד׳", "Even HaEzer, Part I, Siman 4", "אה״ע ח״א ד׳", "Even HaEzer I:4", "EH·I"],
            ["אבן העזר ח״א סימן ה׳", "Even HaEzer, Part I, Siman 5", "אה״ע ח״א ה׳", "Even HaEzer I:5", "EH·I"],
            ["אבן העזר ח״א סימן ו׳", "Even HaEzer, Part I, Siman 6", "אה״ע ח״א ו׳", "Even HaEzer I:6", "EH·I"],
            ["אבן העזר ח״א סימן ז׳", "Even HaEzer, Part I, Siman 7", "אה״ע ח״א ז׳", "Even HaEzer I:7", "EH·I"],
            ["אבן העזר ח״א סימן ח׳", "Even HaEzer, Part I, Siman 8", "אה״ע ח״א ח׳", "Even HaEzer I:8", "EH·I"],
            ["אבן העזר ח״א סימן ט׳", "Even HaEzer, Part I, Siman 9", "אה״ע ח״א ט׳", "Even HaEzer I:9", "EH·I"],
            ["אבן העזר ח״א סימן י׳", "Even HaEzer, Part I, Siman 10", "אה״ע ח״א י׳", "Even HaEzer I:10", "EH·I"],
            ["אבן העזר ח״א סימן י״א", "Even HaEzer, Part I, Siman 11", "אה״ע ח״א י״א", "Even HaEzer I:11", "EH·I"],
            ["אבן העזר ח״א סימן י״ב", "Even HaEzer, Part I, Siman 12", "אה״ע ח״א י״ב", "Even HaEzer I:12", "EH·I"],
            ["אבן העזר ח״א סימן י״ג", "Even HaEzer, Part I, Siman 13", "אה״ע ח״א י״ג", "Even HaEzer I:13", "EH·I"],
            ["אבן העזר ח״ב סימן א׳", "Even HaEzer, Part II, Siman 1", "אה״ע ח״ב א׳", "Even HaEzer II:1", "EH·II"],
            ["אבן העזר ח״ב סימן ב׳", "Even HaEzer, Part II, Siman 2", "אה״ע ח״ב ב׳", "Even HaEzer II:2", "EH·II"],
            ["אבן העזר ח״ב סימן ג׳", "Even HaEzer, Part II, Siman 3", "אה״ע ח״ב ג׳", "Even HaEzer II:3", "EH·II"],
            ["אבן העזר ח״ב סימן ד׳", "Even HaEzer, Part II, Siman 4", "אה״ע ח״ב ד׳", "Even HaEzer II:4", "EH·II"],
            ["אבן העזר ח״ב סימן ה׳", "Even HaEzer, Part II, Siman 5", "אה״ע ח״ב ה׳", "Even HaEzer II:5", "EH·II"],
            ["אבן העזר ח״ב סימן ו׳", "Even HaEzer, Part II, Siman 6", "אה״ע ח״ב ו׳", "Even HaEzer II:6", "EH·II"],
            ["אבן העזר ח״ב סימן ז׳", "Even HaEzer, Part II, Siman 7", "אה״ע ח״ב ז׳", "Even HaEzer II:7", "EH·II"],
            ["אבן העזר ח״ב סימן ח׳", "Even HaEzer, Part II, Siman 8", "אה״ע ח״ב ח׳", "Even HaEzer II:8", "EH·II"],
            ["אבן העזר ח״ב סימן ט׳", "Even HaEzer, Part II, Siman 9", "אה״ע ח״ב ט׳", "Even HaEzer II:9", "EH·II"],
            ["אבן העזר ח״ב סימן י׳", "Even HaEzer, Part II, Siman 10", "אה״ע ח״ב י׳", "Even HaEzer II:10", "EH·II"],
            ["אבן העזר ח״ב סימן י״א", "Even HaEzer, Part II, Siman 11", "אה״ע ח״ב י״א", "Even HaEzer II:11", "EH·II"],
            ["אבן העזר ח״ב סימן י״ב", "Even HaEzer, Part II, Siman 12", "אה״ע ח״ב י״ב", "Even HaEzer II:12", "EH·II"],
            ["אבן העזר ח״ב סימן י״ג", "Even HaEzer, Part II, Siman 13", "אה״ע ח״ב י״ג", "Even HaEzer II:13", "EH·II"],
            ["אבן העזר ח״ב סימן י״ד", "Even HaEzer, Part II, Siman 14", "אה״ע ח״ב י״ד", "Even HaEzer II:14", "EH·II"],
            ["אבן העזר ח״ב סימן ט״ו", "Even HaEzer, Part II, Siman 15", "אה״ע ח״ב ט״ו", "Even HaEzer II:15", "EH·II"],
            ["אבן העזר ח״ב סימן ט״ז", "Even HaEzer, Part II, Siman 16", "אה״ע ח״ב ט״ז", "Even HaEzer II:16", "EH·II"],
            ["אבן העזר ח״ב סימן י״ז", "Even HaEzer, Part II, Siman 17", "אה״ע ח״ב י״ז", "Even HaEzer II:17", "EH·II"],
            ["אבן העזר ח״ב סימן י״ח", "Even HaEzer, Part II, Siman 18", "אה״ע ח״ב י״ח", "Even HaEzer II:18", "EH·II"],
            ["אבן העזר ח״ב סימן י״ט", "Even HaEzer, Part II, Siman 19", "אה״ע ח״ב י״ט", "Even HaEzer II:19", "EH·II"],
            ["אבן העזר ח״ב סימן כ׳", "Even HaEzer, Part II, Siman 20", "אה״ע ח״ב כ׳", "Even HaEzer II:20", "EH·II"],
            ["אבן העזר ח״ב סימן כ״א", "Even HaEzer, Part II, Siman 21", "אה״ע ח״ב כ״א", "Even HaEzer II:21", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ב", "Even HaEzer, Part II, Siman 22", "אה״ע ח״ב כ״ב", "Even HaEzer II:22", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ג", "Even HaEzer, Part II, Siman 23", "אה״ע ח״ב כ״ג", "Even HaEzer II:23", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ד", "Even HaEzer, Part II, Siman 24", "אה״ע ח״ב כ״ד", "Even HaEzer II:24", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ה", "Even HaEzer, Part II, Siman 25", "אה״ע ח״ב כ״ה", "Even HaEzer II:25", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ו", "Even HaEzer, Part II, Siman 26", "אה״ע ח״ב כ״ו", "Even HaEzer II:26", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ז", "Even HaEzer, Part II, Siman 27", "אה״ע ח״ב כ״ז", "Even HaEzer II:27", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ח", "Even HaEzer, Part II, Siman 28", "אה״ע ח״ב כ״ח", "Even HaEzer II:28", "EH·II"],
            ["אבן העזר ח״ב סימן כ״ט", "Even HaEzer, Part II, Siman 29", "אה״ע ח״ב כ״ט", "Even HaEzer II:29", "EH·II"],
            ["אבן העזר ח״ב סימן ל׳", "Even HaEzer, Part II, Siman 30", "אה״ע ח״ב ל׳", "Even HaEzer II:30", "EH·II"],
            ["אבן העזר ח״ב סימן ל״א", "Even HaEzer, Part II, Siman 31", "אה״ע ח״ב ל״א", "Even HaEzer II:31", "EH·II"],
            ["אבן העזר ח״ב סימן ל״ב", "Even HaEzer, Part II, Siman 32", "אה״ע ח״ב ל״ב", "Even HaEzer II:32", "EH·II"],
            ["אבן העזר ח״ב סימן ל״ג", "Even HaEzer, Part II, Siman 33", "אה״ע ח״ב ל״ג", "Even HaEzer II:33", "EH·II"],
            ["אבן העזר ח״ב סימן ל״ד", "Even HaEzer, Part II, Siman 34", "אה״ע ח״ב ל״ד", "Even HaEzer II:34", "EH·II"],
            ["אבן העזר ח״ג סימן א׳", "Even HaEzer, Part III, Siman 1", "אה״ע ח״ג א׳", "Even HaEzer III:1", "EH·III"],
            ["אבן העזר ח״ג סימן ב׳", "Even HaEzer, Part III, Siman 2", "אה״ע ח״ג ב׳", "Even HaEzer III:2", "EH·III"],
            ["אבן העזר ח״ג סימן ג׳", "Even HaEzer, Part III, Siman 3", "אה״ע ח״ג ג׳", "Even HaEzer III:3", "EH·III"],
            ["אבן העזר ח״ג סימן ד׳", "Even HaEzer, Part III, Siman 4", "אה״ע ח״ג ד׳", "Even HaEzer III:4", "EH·III"],
            ["אבן העזר ח״ג סימן ה׳", "Even HaEzer, Part III, Siman 5", "אה״ע ח״ג ה׳", "Even HaEzer III:5", "EH·III"],
            ["אבן העזר ח״ג סימן ו׳", "Even HaEzer, Part III, Siman 6", "אה״ע ח״ג ו׳", "Even HaEzer III:6", "EH·III"],
            ["אבן העזר ח״ג סימן ז׳", "Even HaEzer, Part III, Siman 7", "אה״ע ח״ג ז׳", "Even HaEzer III:7", "EH·III"],
            ["אבן העזר ח״ג סימן ח׳", "Even HaEzer, Part III, Siman 8", "אה״ע ח״ג ח׳", "Even HaEzer III:8", "EH·III"],
            ["אבן העזר ח״ג סימן ט׳", "Even HaEzer, Part III, Siman 9", "אה״ע ח״ג ט׳", "Even HaEzer III:9", "EH·III"],
            ["אבן העזר ח״ג סימן י׳", "Even HaEzer, Part III, Siman 10", "אה״ע ח״ג י׳", "Even HaEzer III:10", "EH·III"],
            ["אבן העזר ח״ג סימן י״א", "Even HaEzer, Part III, Siman 11", "אה״ע ח״ג י״א", "Even HaEzer III:11", "EH·III"],
            ["אבן העזר ח״ג סימן י״ב", "Even HaEzer, Part III, Siman 12", "אה״ע ח״ג י״ב", "Even HaEzer III:12", "EH·III"],
            ["אבן העזר ח״ד סימן א׳", "Even HaEzer, Part IV, Siman 1", "אה״ע ח״ד א׳", "Even HaEzer IV:1", "EH·IV"],
            ["אבן העזר ח״ד סימן ב׳", "Even HaEzer, Part IV, Siman 2", "אה״ע ח״ד ב׳", "Even HaEzer IV:2", "EH·IV"],
            ["אבן העזר ח״ד סימן ג׳", "Even HaEzer, Part IV, Siman 3", "אה״ע ח״ד ג׳", "Even HaEzer IV:3", "EH·IV"],
            ["אבן העזר ח״ד סימן ד׳", "Even HaEzer, Part IV, Siman 4", "אה״ע ח״ד ד׳", "Even HaEzer IV:4", "EH·IV"],
            ["אבן העזר ח״ד סימן ה׳", "Even HaEzer, Part IV, Siman 5", "אה״ע ח״ד ה׳", "Even HaEzer IV:5", "EH·IV"],
            ["אבן העזר ח״ד סימן ו׳", "Even HaEzer, Part IV, Siman 6", "אה״ע ח״ד ו׳", "Even HaEzer IV:6", "EH·IV"],
            ["אבן העזר ח״ד סימן ז׳", "Even HaEzer, Part IV, Siman 7", "אה״ע ח״ד ז׳", "Even HaEzer IV:7", "EH·IV"],
            ["אבן העזר ח״ד סימן ח׳", "Even HaEzer, Part IV, Siman 8", "אה״ע ח״ד ח׳", "Even HaEzer IV:8", "EH·IV"],
            ["אבן העזר ח״ד סימן ט׳", "Even HaEzer, Part IV, Siman 9", "אה״ע ח״ד ט׳", "Even HaEzer IV:9", "EH·IV"],
            ["אבן העזר ח״ד סימן י׳", "Even HaEzer, Part IV, Siman 10", "אה״ע ח״ד י׳", "Even HaEzer IV:10", "EH·IV"],
            ["אבן העזר ח״ד סימן י״א", "Even HaEzer, Part IV, Siman 11", "אה״ע ח״ד י״א", "Even HaEzer IV:11", "EH·IV"],
            ["אבן העזר ח״ד סימן י״ב", "Even HaEzer, Part IV, Siman 12", "אה״ע ח״ד י״ב", "Even HaEzer IV:12", "EH·IV"],
            ["אבן העזר ח״ד סימן י״ג", "Even HaEzer, Part IV, Siman 13", "אה״ע ח״ד י״ג", "Even HaEzer IV:13", "EH·IV"],
            ["חושן משפט ח״ב סימן א׳", "Choshen Mishpat, Part II, Siman 1", "חו״מ ח״ב א׳", "Choshen Mishpat II:1", "CM·II"],
            ["חושן משפט ח״ב סימן ב׳", "Choshen Mishpat, Part II, Siman 2", "חו״מ ח״ב ב׳", "Choshen Mishpat II:2", "CM·II"],
            ["חושן משפט ח״ב סימן ג׳", "Choshen Mishpat, Part II, Siman 3", "חו״מ ח״ב ג׳", "Choshen Mishpat II:3", "CM·II"],
            ["חושן משפט ח״ב סימן ד׳", "Choshen Mishpat, Part II, Siman 4", "חו״מ ח״ב ד׳", "Choshen Mishpat II:4", "CM·II"],
            ["חושן משפט ח״ב סימן ה׳", "Choshen Mishpat, Part II, Siman 5", "חו״מ ח״ב ה׳", "Choshen Mishpat II:5", "CM·II"],
            ["חושן משפט ח״ב סימן ו׳", "Choshen Mishpat, Part II, Siman 6", "חו״מ ח״ב ו׳", "Choshen Mishpat II:6", "CM·II"],
            ["חושן משפט ח״ב סימן ז׳", "Choshen Mishpat, Part II, Siman 7", "חו״מ ח״ב ז׳", "Choshen Mishpat II:7", "CM·II"],
            ["חושן משפט ח״ב סימן ח׳", "Choshen Mishpat, Part II, Siman 8", "חו״מ ח״ב ח׳", "Choshen Mishpat II:8", "CM·II"],
            ["חושן משפט ח״ב סימן ט׳", "Choshen Mishpat, Part II, Siman 9", "חו״מ ח״ב ט׳", "Choshen Mishpat II:9", "CM·II"],
            ["חושן משפט ח״ב סימן י׳", "Choshen Mishpat, Part II, Siman 10", "חו״מ ח״ב י׳", "Choshen Mishpat II:10", "CM·II"],
            ["חושן משפט ח״ב סימן י״א", "Choshen Mishpat, Part II, Siman 11", "חו״מ ח״ב י״א", "Choshen Mishpat II:11", "CM·II"],
            ["חושן משפט ח״ב סימן י״ב", "Choshen Mishpat, Part II, Siman 12", "חו״מ ח״ב י״ב", "Choshen Mishpat II:12", "CM·II"],
            ["חושן משפט ח״ב סימן י״ג", "Choshen Mishpat, Part II, Siman 13", "חו״מ ח״ב י״ג", "Choshen Mishpat II:13", "CM·II"],
            ["חושן משפט ח״ב סימן י״ד", "Choshen Mishpat, Part II, Siman 14", "חו״מ ח״ב י״ד", "Choshen Mishpat II:14", "CM·II"],
            ["חושן משפט ח״ב סימן ט״ו", "Choshen Mishpat, Part II, Siman 15", "חו״מ ח״ב ט״ו", "Choshen Mishpat II:15", "CM·II"],
            ["חושן משפט ח״ג סימן א׳", "Choshen Mishpat, Part III, Siman 1", "חו״מ ח״ג א׳", "Choshen Mishpat III:1", "CM·III"],
            ["חושן משפט ח״ג סימן ב׳", "Choshen Mishpat, Part III, Siman 2", "חו״מ ח״ג ב׳", "Choshen Mishpat III:2", "CM·III"],
            ["חושן משפט ח״ג סימן ג׳", "Choshen Mishpat, Part III, Siman 3", "חו״מ ח״ג ג׳", "Choshen Mishpat III:3", "CM·III"],
            ["חושן משפט ח״ג סימן ד׳", "Choshen Mishpat, Part III, Siman 4", "חו״מ ח״ג ד׳", "Choshen Mishpat III:4", "CM·III"],
            ["חושן משפט ח״ג סימן ה׳", "Choshen Mishpat, Part III, Siman 5", "חו״מ ח״ג ה׳", "Choshen Mishpat III:5", "CM·III"],
            ["חושן משפט ח״ג סימן ו׳", "Choshen Mishpat, Part III, Siman 6", "חו״מ ח״ג ו׳", "Choshen Mishpat III:6", "CM·III"],
            ["חושן משפט ח״ג סימן ז׳", "Choshen Mishpat, Part III, Siman 7", "חו״מ ח״ג ז׳", "Choshen Mishpat III:7", "CM·III"],
            ["חושן משפט ח״ג סימן ח׳", "Choshen Mishpat, Part III, Siman 8", "חו״מ ח״ג ח׳", "Choshen Mishpat III:8", "CM·III"],
            ["חושן משפט ח״ד סימן א׳", "Choshen Mishpat, Part IV, Siman 1", "חו״מ ח״ד א׳", "Choshen Mishpat IV:1", "CM·IV"],
            ["חושן משפט ח״ד סימן ב׳", "Choshen Mishpat, Part IV, Siman 2", "חו״מ ח״ד ב׳", "Choshen Mishpat IV:2", "CM·IV"],
            ["חושן משפט ח״ד סימן ג׳", "Choshen Mishpat, Part IV, Siman 3", "חו״מ ח״ד ג׳", "Choshen Mishpat IV:3", "CM·IV"],
            ["חושן משפט ח״ד סימן ד׳", "Choshen Mishpat, Part IV, Siman 4", "חו״מ ח״ד ד׳", "Choshen Mishpat IV:4", "CM·IV"],
            ["חושן משפט ח״ד סימן ה׳", "Choshen Mishpat, Part IV, Siman 5", "חו״מ ח״ד ה׳", "Choshen Mishpat IV:5", "CM·IV"],
            ["חושן משפט ח״ד סימן ו׳", "Choshen Mishpat, Part IV, Siman 6", "חו״מ ח״ד ו׳", "Choshen Mishpat IV:6", "CM·IV"],
            ["חושן משפט ח״ד סימן ז׳", "Choshen Mishpat, Part IV, Siman 7", "חו״מ ח״ד ז׳", "Choshen Mishpat IV:7", "CM·IV"],
            ["חושן משפט ח״ד סימן ח׳", "Choshen Mishpat, Part IV, Siman 8", "חו״מ ח״ד ח׳", "Choshen Mishpat IV:8", "CM·IV"]
        ];
        var out=[],i;
        for(i=0;i<a.length;i++){
            out.push({index:i,he:a[i][0],en:a[i][1],heShort:a[i][2]||"",enShort:a[i][3]||"",group:a[i][4]||"",
                      heKey:normalizeHebrewWords(a[i][0]),enKey:normalizeSectionEn(a[i][1]),enAlias:[]});
        }
        return out;
    }

    function groupByKey(k){
        var i;
        for(i=0;i<PARASHOT.length;i++)if(PARASHOT[i].key===k)return PARASHOT[i];
        return null;
    }

    function sectionKeyMatches(s,key,isHebrew){
        var i;
        if(isHebrew)return s.heKey===key;
        if(s.enKey===key)return true;
        for(i=0;i<s.enAlias.length;i++)if(s.enAlias[i]===key)return true;
        return false;
    }

    function matchSection(text,isHebrew,cursor){
        // Vollstaendige Gleichheit (normalisiert); gleichlautende Titel in Werkfolge ab cursor
        var key=isHebrew?normalizeHebrewWords(text):normalizeSectionEn(text),i;
        if(!key)return null;
        cursor=cursor||0;
        for(i=cursor;i<SECTIONS.length;i++)if(sectionKeyMatches(SECTIONS[i],key,isHebrew))return SECTIONS[i];
        for(i=0;i<cursor&&i<SECTIONS.length;i++)if(sectionKeyMatches(SECTIONS[i],key,isHebrew))return SECTIONS[i];
        return null;
    }

    function parseSourceSections(raw){
        var re=/<section>\s*<he_title>([\s\S]*?)<\/he_title>\s*<en_title>([\s\S]*?)<\/en_title>\s*<\/section>/ig,m,out=[];
        while((m=re.exec(raw))!==null){
            out.push({he:cleanHeadingText(restoreCdata(xmlUnescape(m[1]))),en:cleanHeadingText(restoreCdata(xmlUnescape(m[2])))});
        }
        return out;
    }

    function registerSourceAliases(entries){
        // Englische Titel der Banddatei, die vom Katalog abweichen (spaeter geaenderte Uebersetzung),
        // werden dem ueber den hebraeischen Titel gefundenen Abschnitt als Alias zugeordnet.
        var cursor=0,i,s,k,n=0;
        for(i=0;i<entries.length;i++){
            s=matchSection(entries[i].he,true,cursor);
            if(!s)continue;
            cursor=s.index+1;
            k=normalizeSectionEn(entries[i].en);
            if(k&&!sectionKeyMatches(s,k,false)){s.enAlias.push(k);n++;}
        }
        return n;
    }

    function paragraphAtFrameTop(p){
        // true, wenn vor der Ueberschrift im selben Textrahmen nur Leerraum steht
        try{
            var ip=p.insertionPoints[0],frames=ip.parentTextFrames;
            if(!frames||!frames.length)return false;
            var start=frames[0].insertionPoints[0].index,idx=ip.index;
            if(idx<=start)return true;
            var before=p.parentStory.characters.itemByRange(start,idx-1).contents;
            if(before instanceof Array)before=before.join("");
            return !trim(String(before).replace(/[\r\n\u2028\u2029\u200B\uFEFF]/g," "));
        }catch(_){return false;}
    }

    function buildSectionStarts(headings,isHebrew){
        var out=[],cursor=0,i,h,s,g;
        for(i=0;i<headings.length;i++){
            h=headings[i];
            s=matchSection(h.text,isHebrew,cursor);
            if(s)cursor=s.index+1;
            g=s?groupByKey(s.group):null;
            out.push({pageIndex:h.pageIndex,pageName:h.pageName,textIndex:h.textIndex,atTop:!!h.atTop,
                      title:h.text,kurzTitel:s?(isHebrew?s.heShort:s.enShort):"",
                      otherTitle:s?(isHebrew?s.en:s.he):"",otherShort:s?(isHebrew?s.enShort:s.heShort):"",
                      groupHe:g?g.he:"",groupEn:g?g.en:"",matched:!!s,
                      detection:(isHebrew?"HE":"EN")+(s?" · Katalog":" · nicht im Katalog")});
        }
        return out;
    }

    function mirrorStarts(starts){
        // Fallback, wenn eine Sprache keine Ueberschriften hat: Titel der anderen Sprache ueber den Katalog
        var out=[],i,s;
        for(i=0;i<starts.length;i++){
            s=starts[i];
            out.push({pageIndex:s.pageIndex,pageName:s.pageName,textIndex:s.textIndex,atTop:s.atTop,
                      title:s.otherTitle,kurzTitel:s.otherShort,otherTitle:s.title,otherShort:s.kurzTitel,
                      groupHe:s.groupHe,groupEn:s.groupEn,matched:s.matched,detection:s.detection+" (gespiegelt)"});
        }
        return out;
    }

    function sectionForPage(starts,p,rule){
        // rule 0: Abschnitt am Seitenanfang - beginnt oben auf der Seite eine Ueberschrift, gilt sie,
        //         sonst der Abschnitt, der von der Vorseite weiterlaeuft
        // rule 1: erste auf der Seite beginnende Ueberschrift, sonst der weiterlaufende Abschnitt
        // rule 2: letzte Ueberschrift der Seite, sonst der weiterlaufende Abschnitt
        var before=null,first=null,last=null,i,s;
        for(i=0;i<starts.length;i++){
            s=starts[i];
            if(s.pageIndex<p)before=s;
            else if(s.pageIndex===p){if(!first)first=s;last=s;}
            else break;
        }
        if(rule===1){if(first)return {s:first,start:true};return before?{s:before,start:false}:null;}
        if(rule===2){if(last)return {s:last,start:true};return before?{s:before,start:false}:null;}
        if(first&&first.atTop)return {s:first,start:true};
        if(before)return {s:before,start:false};
        if(first)return {s:first,start:true};
        return null;
    }

    function pageRuleLabel(r){return r===1?"erste Überschrift der Seite":(r===2?"letzte Überschrift der Seite":"Abschnitt am Seitenanfang");}

    function headerTitle(info,lang,useShort){
        var full=lang==="en"?info.enTitle:info.heTitle,sh=lang==="en"?info.enShort:info.heShort;
        return String((useShort&&sh)?sh:(full||""));
    }

    function shortenWords(title,keep){
        // wortweise kuerzen und Auslassungszeichen setzen (letzter Ausweg bei Platzmangel)
        var w=trim(title).split(/\s+/),out;
        if(keep>=w.length)return trim(title);
        if(keep<1)keep=1;
        out=w.slice(0,keep).join(" ").replace(/[\s·:;,.\-–—(]+$/,"");
        return out+"…";
    }

    function templateShowsSection(cfg,lang){
        var t=lang==="en"?cfg.enTemplate:cfg.heTemplate;
        return t.indexOf("{ABSCHNITT")>=0||t.indexOf("{PARASHAH")>=0;
    }

    function headerMatchesTitle(txt,info,lang){
        // Kolumnentitel passt zur Ueberschrift: voller Titel, Kurztitel oder dessen gekuerzter Anfang
        var full=headerTitle(info,lang,false),sh=headerTitle(info,lang,true),cut,k,d;
        txt=String(txt||"");
        if(full&&txt.indexOf(full)>=0)return true;
        if(sh&&txt.indexOf(sh)>=0)return true;
        k=txt.lastIndexOf("…");
        if(k>0){
            cut=txt.substring(0,k);d=cut.lastIndexOf("· ");if(d>=0)cut=cut.substring(d+2);
            cut=trim(cut);
            if(cut&&(full.indexOf(cut)===0||(sh&&sh.indexOf(cut)===0)))return true;
        }
        return false;
    }

    // ---------------------------------------------------------------------
    // v1.0.3: Kopfrahmen neutral setzen, nie mit Ausnahme abbrechen
    // ---------------------------------------------------------------------

    function resetHeaderText(doc,tf,t){
        // Ein neuer oder alter Kopfrahmen erbt sonst Absatz- und Zeichenformat des Dokuments
        // (Grundlinienraster, Einzuege, "Absatzbeginn: naechster Rahmen", Aufzaehlung,
        // Versalien, kein Umbruch ...). Dann laeuft selbst ein einzelnes Wort ueber.
        var basic=null,k,para,chr,frm;
        try{basic=doc.paragraphStyles.item("$ID/NormalParagraphStyle");if(!basic.isValid)basic=null;}catch(_){basic=null;}
        if(!basic){try{basic=doc.paragraphStyles[1];}catch(_){basic=null;}}
        try{if(basic)t.applyParagraphStyle(basic,true);}catch(_){}
        try{t.applyCharacterStyle(doc.characterStyles[0],true);}catch(_){}
        para={leftIndent:0,rightIndent:0,firstLineIndent:0,lastLineIndent:0,spaceBefore:0,spaceAfter:0,
              alignToBaseline:false,keepWithNext:0,keepLinesTogether:false,ruleAbove:false,ruleBelow:false,
              dropCapCharacters:0,dropCapLines:0,paragraphShadingOn:false,paragraphBorderOn:false};
        chr={horizontalScale:100,verticalScale:100,baselineShift:0,skew:0,noBreak:false,
             underline:false,strikeThru:false};
        for(k in para){try{t[k]=para[k];}catch(_){}}
        for(k in chr){try{t[k]=chr[k];}catch(_){}}
        try{t.startParagraph=StartParagraph.ANYWHERE;}catch(_){}
        try{t.bulletsAndNumberingListType=ListType.NO_LIST;}catch(_){}
        try{t.spanColumnType=SpanColumnTypeOptions.SINGLE_COLUMN;}catch(_){}
        try{t.capitalization=Capitalization.NORMAL;}catch(_){}
        try{t.position=Position.NORMAL;}catch(_){}
        frm=null;
        try{frm=tf.textFramePreferences;}catch(_){}
        if(frm){
            try{frm.textColumnCount=1;}catch(_){}
            try{frm.autoSizingType=AutoSizingTypeEnum.OFF;}catch(_){}
            try{frm.firstBaselineOffset=FirstBaseline.ASCENT_OFFSET;}catch(_){}
            try{frm.minimumFirstBaselineOffset=0;}catch(_){}
        }
    }

    function headerFrameUsable(tf){
        // verkettete Kopfrahmen (Text laeuft in einen anderen Rahmen) werden neu angelegt
        try{if(tf.previousTextFrame&&tf.previousTextFrame.isValid)return false;}catch(_){}
        try{if(tf.nextTextFrame&&tf.nextTextFrame.isValid)return false;}catch(_){}
        try{if(tf.parentStory.textContainers.length>1)return false;}catch(_){}
        return true;
    }

    function rund1(x){return String(Math.round(Number(x)*10)/10).replace(".",",");}

    function headerDiagnosis(tf){
        // Warum der Kopfrahmen nicht passt (fuer den Bericht)
        var d=[],t,b,n;
        try{if(tf.overflows)d.push("Übersatz");}catch(_){}
        try{n=tf.parentStory.lines.length;if(n>1)d.push(n+" Zeilen");}catch(_){}
        try{if(!headerFrameUsable(tf))d.push("Rahmen verkettet");}catch(_){}
        try{b=tf.geometricBounds;d.push("Rahmen "+rund1(b[3]-b[1])+" × "+rund1(b[2]-b[0]));}catch(_){}
        try{
            t=tf.texts[0];
            try{d.push("Absatzformat „"+t.appliedParagraphStyle.name+"“");}catch(_){}
            try{d.push(rund1(t.pointSize)+" pt");}catch(_){}
            try{if(t.alignToBaseline)d.push("am Grundlinienraster");}catch(_){}
            try{if(t.leftIndent||t.rightIndent||t.firstLineIndent)d.push("Einzüge "+rund1(t.leftIndent)+"/"+rund1(t.rightIndent)+"/"+rund1(t.firstLineIndent));}catch(_){}
        }catch(_){}
        return d.join(", ");
    }

    function buildParashahCatalogue(){
        // Rav Pe’alim: Gruppen (Abteilung · Teil); Aliase = Siman-Titel der Ausgabe
        var a=[
            ["SY·I", "סוד ישרים · חלק א׳", "Sod Yesharim · Part I", ["sod yesharim · part i", "sod yesharim, siman 1 (part i, siman 1)", "sod yesharim, siman 2 (part i, siman 2)", "sod yesharim, siman 3 (part i, siman 3)", "sod yesharim, siman 4 (part i, siman 4)", "sod yesharim, siman 5 (part i, siman 5)", "sod yesharim, siman 6 (part i, siman 6)", "sod yesharim, siman 7 (part i, siman 7)", "sod yesharim, siman 8 (part i, siman 8)", "sod yesharim, siman 9 (part i, siman 9)", "sod yesharim, siman 10 (part i, siman 10)", "sod yesharim, siman 11 (part i, siman 11)", "sod yesharim, siman 12 (part i, siman 12)", "sod yesharim, siman 13 (part i, siman 13)", "sod yesharim, siman 14 (part i, siman 14)", "sod yesharim, siman 15 (part i, siman 15)", "sod yesharim, siman 16 (part i, siman 16)", "sod yesharim, siman 17 (part i, siman 17)"], ["סוד ישרים סימן א׳ (ח״א סי׳ א׳)", "סוד ישרים סימן ב׳ (ח״א סי׳ ב׳)", "סוד ישרים סימן ג׳ (ח״א סי׳ ג׳)", "סוד ישרים סימן ד׳ (ח״א סי׳ ד׳)", "סוד ישרים סימן ה׳ (ח״א סי׳ ה׳)", "סוד ישרים סימן ו׳ (ח״א סי׳ ו׳)", "סוד ישרים סימן ז׳ (ח״א סי׳ ז׳)", "סוד ישרים סימן ח׳ (ח״א סי׳ ח׳)", "סוד ישרים סימן ט׳ (ח״א סי׳ ט׳)", "סוד ישרים סימן י׳ (ח״א סי׳ י׳)", "סוד ישרים סימן י״א (ח״א סי׳ י״א)", "סוד ישרים סימן י״ב (ח״א סי׳ י״ב)", "סוד ישרים סימן י״ג (ח״א סי׳ י״ג)", "סוד ישרים סימן י״ד (ח״א סי׳ י״ד)", "סוד ישרים סימן ט״ו (ח״א סי׳ ט״ו)", "סוד ישרים סימן ט״ז (ח״א סי׳ ט״ז)", "סוד ישרים סימן י״ז (ח״א סי׳ י״ז)"]],
            ["SY·II", "סוד ישרים · חלק ב׳", "Sod Yesharim · Part II", ["sod yesharim · part ii", "sod yesharim, siman 18 (part ii, siman 1)", "sod yesharim, siman 19 (part ii, siman 2)", "sod yesharim, siman 20 (part ii, siman 3)", "sod yesharim, siman 21 (part ii, siman 4)", "sod yesharim, siman 22 (part ii, siman 5)", "sod yesharim, siman 23 (part ii, siman 6)", "sod yesharim, siman 24 (part ii, siman 7)", "sod yesharim, siman 25 (part ii, siman 8)", "sod yesharim, siman 26 (part ii, siman 9)", "sod yesharim, siman 27 (part ii, siman 10)", "sod yesharim, siman 28 (part ii, siman 11)", "sod yesharim, siman 29 (part ii, siman 12)", "sod yesharim, siman 30 (part ii, siman 13)", "sod yesharim, siman 31 (part ii, siman 14)"], ["סוד ישרים סימן י״ח (ח״ב סי׳ א׳)", "סוד ישרים סימן י״ט (ח״ב סי׳ ב׳)", "סוד ישרים סימן כ׳ (ח״ב סי׳ ג׳)", "סוד ישרים סימן כ״א (ח״ב סי׳ ד׳)", "סוד ישרים סימן כ״ב (ח״ב סי׳ ה׳)", "סוד ישרים סימן כ״ג (ח״ב סי׳ ו׳)", "סוד ישרים סימן כ״ד (ח״ב סי׳ ז׳)", "סוד ישרים סימן כ״ה (ח״ב סי׳ ח׳)", "סוד ישרים סימן כ״ו (ח״ב סי׳ ט׳)", "סוד ישרים סימן כ״ז (ח״ב סי׳ י׳)", "סוד ישרים סימן כ״ח (ח״ב סי׳ י״א)", "סוד ישרים סימן כ״ט (ח״ב סי׳ י״ב)", "סוד ישרים סימן ל׳ (ח״ב סי׳ י״ג)", "סוד ישרים סימן ל״א (ח״ב סי׳ י״ד)"]],
            ["SY·III", "סוד ישרים · חלק ג׳", "Sod Yesharim · Part III", ["sod yesharim · part iii", "sod yesharim, siman 32 (part iii, siman 1)", "sod yesharim, siman 33 (part iii, siman 2)", "sod yesharim, siman 34 (part iii, siman 3)", "sod yesharim, siman 35 (part iii, siman 4)", "sod yesharim, siman 36 (part iii, siman 5)", "sod yesharim, siman 37 (part iii, siman 6)", "sod yesharim, siman 38 (part iii, siman 7)", "sod yesharim, siman 39 (part iii, siman 8)", "sod yesharim, siman 40 (part iii, siman 9)", "sod yesharim, siman 41 (part iii, siman 10)", "sod yesharim, siman 42 (part iii, siman 11)", "sod yesharim, siman 43 (part iii, siman 12)", "sod yesharim, siman 44 (part iii, siman 13)"], ["סוד ישרים סימן ל״ב (ח״ג סי׳ א׳)", "סוד ישרים סימן ל״ג (ח״ג סי׳ ב׳)", "סוד ישרים סימן ל״ד (ח״ג סי׳ ג׳)", "סוד ישרים סימן ל״ה (ח״ג סי׳ ד׳)", "סוד ישרים סימן ל״ו (ח״ג סי׳ ה׳)", "סוד ישרים סימן ל״ז (ח״ג סי׳ ו׳)", "סוד ישרים סימן ל״ח (ח״ג סי׳ ז׳)", "סוד ישרים סימן ל״ט (ח״ג סי׳ ח׳)", "סוד ישרים סימן מ׳ (ח״ג סי׳ ט׳)", "סוד ישרים סימן מ״א (ח״ג סי׳ י׳)", "סוד ישרים סימן מ״ב (ח״ג סי׳ י״א)", "סוד ישרים סימן מ״ג (ח״ג סי׳ י״ב)", "סוד ישרים סימן מ״ד (ח״ג סי׳ י״ג)"]],
            ["SY·IV", "סוד ישרים · חלק ד׳", "Sod Yesharim · Part IV", ["sod yesharim · part iv", "sod yesharim, siman 45 (part iv, siman 1)", "sod yesharim, siman 46 (part iv, siman 2)", "sod yesharim, siman 47 (part iv, siman 3)", "sod yesharim, siman 48 (part iv, siman 4)", "sod yesharim, siman 49 (part iv, siman 5)", "sod yesharim, siman 50 (part iv, siman 6)", "sod yesharim, siman 51 (part iv, siman 7)", "sod yesharim, siman 52 (part iv, siman 8)", "sod yesharim, siman 53 (part iv, siman 9)", "sod yesharim, siman 54 (part iv, siman 10)", "sod yesharim, siman 55 (part iv, siman 11)", "sod yesharim, siman 56 (part iv, siman 12)", "sod yesharim, siman 57 (part iv, siman 13)", "sod yesharim, siman 58 (part iv, siman 14)", "sod yesharim, siman 59 (part iv, siman 15)", "sod yesharim, siman 60 (part iv, siman 16)", "sod yesharim, siman 61 (part iv, siman 17)", "sod yesharim, siman 62 (part iv, siman 18)", "sod yesharim, siman 63 (part iv, siman 19)", "sod yesharim, siman 64 (part iv, siman 20)"], ["סוד ישרים סימן מ״ה (ח״ד סי׳ א׳)", "סוד ישרים סימן מ״ו (ח״ד סי׳ ב׳)", "סוד ישרים סימן מ״ז (ח״ד סי׳ ג׳)", "סוד ישרים סימן מ״ח (ח״ד סי׳ ד׳)", "סוד ישרים סימן מ״ט (ח״ד סי׳ ה׳)", "סוד ישרים סימן נ׳ (ח״ד סי׳ ו׳)", "סוד ישרים סימן נ״א (ח״ד סי׳ ז׳)", "סוד ישרים סימן נ״ב (ח״ד סי׳ ח׳)", "סוד ישרים סימן נ״ג (ח״ד סי׳ ט׳)", "סוד ישרים סימן נ״ד (ח״ד סי׳ י׳)", "סוד ישרים סימן נ״ה (ח״ד סי׳ י״א)", "סוד ישרים סימן נ״ו (ח״ד סי׳ י״ב)", "סוד ישרים סימן נ״ז (ח״ד סי׳ י״ג)", "סוד ישרים סימן נ״ח (ח״ד סי׳ י״ד)", "סוד ישרים סימן נ״ט (ח״ד סי׳ ט״ו)", "סוד ישרים סימן ס׳ (ח״ד סי׳ ט״ז)", "סוד ישרים סימן ס״א (ח״ד סי׳ י״ז)", "סוד ישרים סימן ס״ב (ח״ד סי׳ י״ח)", "סוד ישרים סימן ס״ג (ח״ד סי׳ י״ט)", "סוד ישרים סימן ס״ד (ח״ד סי׳ כ׳)"]],
            ["VOR", "הקדמות", "Introductions", ["introductions", "author’s introduction · part i", "opening of the book · part i", "author’s introduction · part ii", "author’s introduction · part iii"], ["הקדמת המחבר · חלק א׳", "פתיחת הספר · חלק א׳", "הקדמת המחבר · חלק ב׳", "הקדמת המחבר · חלק ג׳"]],
            ["OC·I", "אורח חיים · חלק א׳", "Orach Chayim · Part I", ["orach chayim · part i", "orach chayim, part i, siman 1", "orach chayim, part i, siman 2", "orach chayim, part i, siman 3", "orach chayim, part i, siman 4", "orach chayim, part i, siman 5", "orach chayim, part i, siman 6", "orach chayim, part i, siman 7", "orach chayim, part i, siman 8", "orach chayim, part i, siman 9", "orach chayim, part i, siman 10", "orach chayim, part i, siman 11", "orach chayim, part i, siman 12", "orach chayim, part i, siman 13", "orach chayim, part i, siman 14", "orach chayim, part i, siman 15", "orach chayim, part i, siman 16", "orach chayim, part i, siman 17", "orach chayim, part i, siman 18", "orach chayim, part i, siman 19", "orach chayim, part i, siman 20", "orach chayim, part i, siman 21", "orach chayim, part i, siman 22", "orach chayim, part i, siman 23", "orach chayim, part i, siman 24", "orach chayim, part i, siman 25", "orach chayim, part i, siman 26", "orach chayim, part i, siman 27", "orach chayim, part i, siman 28", "orach chayim, part i, siman 29", "orach chayim, part i, siman 30", "orach chayim, part i, siman 31", "orach chayim, part i, siman 32", "orach chayim, part i, siman 33", "orach chayim, part i, siman 34", "orach chayim, part i, siman 35"], ["אורח חיים ח״א סימן א׳", "אורח חיים ח״א סימן ב׳", "אורח חיים ח״א סימן ג׳", "אורח חיים ח״א סימן ד׳", "אורח חיים ח״א סימן ה׳", "אורח חיים ח״א סימן ו׳", "אורח חיים ח״א סימן ז׳", "אורח חיים ח״א סימן ח׳", "אורח חיים ח״א סימן ט׳", "אורח חיים ח״א סימן י׳", "אורח חיים ח״א סימן י״א", "אורח חיים ח״א סימן י״ב", "אורח חיים ח״א סימן י״ג", "אורח חיים ח״א סימן י״ד", "אורח חיים ח״א סימן ט״ו", "אורח חיים ח״א סימן ט״ז", "אורח חיים ח״א סימן י״ז", "אורח חיים ח״א סימן י״ח", "אורח חיים ח״א סימן י״ט", "אורח חיים ח״א סימן כ׳", "אורח חיים ח״א סימן כ״א", "אורח חיים ח״א סימן כ״ב", "אורח חיים ח״א סימן כ״ג", "אורח חיים ח״א סימן כ״ד", "אורח חיים ח״א סימן כ״ה", "אורח חיים ח״א סימן כ״ו", "אורח חיים ח״א סימן כ״ז", "אורח חיים ח״א סימן כ״ח", "אורח חיים ח״א סימן כ״ט", "אורח חיים ח״א סימן ל׳", "אורח חיים ח״א סימן ל״א", "אורח חיים ח״א סימן ל״ב", "אורח חיים ח״א סימן ל״ג", "אורח חיים ח״א סימן ל״ד", "אורח חיים ח״א סימן ל״ה"]],
            ["OC·II", "אורח חיים · חלק ב׳", "Orach Chayim · Part II", ["orach chayim · part ii", "orach chayim, part ii, siman 1", "orach chayim, part ii, siman 2", "orach chayim, part ii, siman 3", "orach chayim, part ii, siman 4", "orach chayim, part ii, siman 5", "orach chayim, part ii, siman 6", "orach chayim, part ii, siman 7", "orach chayim, part ii, siman 8", "orach chayim, part ii, siman 9", "orach chayim, part ii, siman 10", "orach chayim, part ii, siman 11", "orach chayim, part ii, siman 12", "orach chayim, part ii, siman 13", "orach chayim, part ii, siman 14", "orach chayim, part ii, siman 15", "orach chayim, part ii, siman 16", "orach chayim, part ii, siman 17", "orach chayim, part ii, siman 18", "orach chayim, part ii, siman 19", "orach chayim, part ii, siman 20", "orach chayim, part ii, siman 21", "orach chayim, part ii, siman 22", "orach chayim, part ii, siman 23", "orach chayim, part ii, siman 24", "orach chayim, part ii, siman 25", "orach chayim, part ii, siman 26", "orach chayim, part ii, siman 27", "orach chayim, part ii, siman 28", "orach chayim, part ii, siman 29", "orach chayim, part ii, siman 30", "orach chayim, part ii, siman 31", "orach chayim, part ii, siman 32", "orach chayim, part ii, siman 33", "orach chayim, part ii, siman 34", "orach chayim, part ii, siman 35", "orach chayim, part ii, siman 36", "orach chayim, part ii, siman 37", "orach chayim, part ii, siman 38", "orach chayim, part ii, siman 39", "orach chayim, part ii, siman 40", "orach chayim, part ii, siman 41", "orach chayim, part ii, siman 42", "orach chayim, part ii, siman 43", "orach chayim, part ii, siman 44", "orach chayim, part ii, siman 45", "orach chayim, part ii, siman 46", "orach chayim, part ii, siman 47", "orach chayim, part ii, siman 48", "orach chayim, part ii, siman 49", "orach chayim, part ii, siman 50", "orach chayim, part ii, siman 51", "orach chayim, part ii, siman 52", "orach chayim, part ii, siman 53", "orach chayim, part ii, siman 54", "orach chayim, part ii, siman 55", "orach chayim, part ii, siman 56", "orach chayim, part ii, siman 57", "orach chayim, part ii, siman 58", "orach chayim, part ii, siman 59", "orach chayim, part ii, siman 60", "orach chayim, part ii, siman 61", "orach chayim, part ii, siman 62", "orach chayim, part ii, siman 63", "orach chayim, part ii, siman 64", "orach chayim, part ii, siman 65"], ["אורח חיים ח״ב סימן א׳", "אורח חיים ח״ב סימן ב׳", "אורח חיים ח״ב סימן ג׳", "אורח חיים ח״ב סימן ד׳", "אורח חיים ח״ב סימן ה׳", "אורח חיים ח״ב סימן ו׳", "אורח חיים ח״ב סימן ז׳", "אורח חיים ח״ב סימן ח׳", "אורח חיים ח״ב סימן ט׳", "אורח חיים ח״ב סימן י׳", "אורח חיים ח״ב סימן י״א", "אורח חיים ח״ב סימן י״ב", "אורח חיים ח״ב סימן י״ג", "אורח חיים ח״ב סימן י״ד", "אורח חיים ח״ב סימן ט״ו", "אורח חיים ח״ב סימן ט״ז", "אורח חיים ח״ב סימן י״ז", "אורח חיים ח״ב סימן י״ח", "אורח חיים ח״ב סימן י״ט", "אורח חיים ח״ב סימן כ׳", "אורח חיים ח״ב סימן כ״א", "אורח חיים ח״ב סימן כ״ב", "אורח חיים ח״ב סימן כ״ג", "אורח חיים ח״ב סימן כ״ד", "אורח חיים ח״ב סימן כ״ה", "אורח חיים ח״ב סימן כ״ו", "אורח חיים ח״ב סימן כ״ז", "אורח חיים ח״ב סימן כ״ח", "אורח חיים ח״ב סימן כ״ט", "אורח חיים ח״ב סימן ל׳", "אורח חיים ח״ב סימן ל״א", "אורח חיים ח״ב סימן ל״ב", "אורח חיים ח״ב סימן ל״ג", "אורח חיים ח״ב סימן ל״ד", "אורח חיים ח״ב סימן ל״ה", "אורח חיים ח״ב סימן ל״ו", "אורח חיים ח״ב סימן ל״ז", "אורח חיים ח״ב סימן ל״ח", "אורח חיים ח״ב סימן ל״ט", "אורח חיים ח״ב סימן מ׳", "אורח חיים ח״ב סימן מ״א", "אורח חיים ח״ב סימן מ״ב", "אורח חיים ח״ב סימן מ״ג", "אורח חיים ח״ב סימן מ״ד", "אורח חיים ח״ב סימן מ״ה", "אורח חיים ח״ב סימן מ״ו", "אורח חיים ח״ב סימן מ״ז", "אורח חיים ח״ב סימן מ״ח", "אורח חיים ח״ב סימן מ״ט", "אורח חיים ח״ב סימן נ׳", "אורח חיים ח״ב סימן נ״א", "אורח חיים ח״ב סימן נ״ב", "אורח חיים ח״ב סימן נ״ג", "אורח חיים ח״ב סימן נ״ד", "אורח חיים ח״ב סימן נ״ה", "אורח חיים ח״ב סימן נ״ו", "אורח חיים ח״ב סימן נ״ז", "אורח חיים ח״ב סימן נ״ח", "אורח חיים ח״ב סימן נ״ט", "אורח חיים ח״ב סימן ס׳", "אורח חיים ח״ב סימן ס״א", "אורח חיים ח״ב סימן ס״ב", "אורח חיים ח״ב סימן ס״ג", "אורח חיים ח״ב סימן ס״ד", "אורח חיים ח״ב סימן ס״ה"]],
            ["OC·III", "אורח חיים · חלק ג׳", "Orach Chayim · Part III", ["orach chayim · part iii", "orach chayim, part iii, siman 1", "orach chayim, part iii, siman 2", "orach chayim, part iii, siman 3", "orach chayim, part iii, siman 4", "orach chayim, part iii, siman 5", "orach chayim, part iii, siman 6", "orach chayim, part iii, siman 7", "orach chayim, part iii, siman 8", "orach chayim, part iii, siman 9", "orach chayim, part iii, siman 10", "orach chayim, part iii, siman 11", "orach chayim, part iii, siman 12", "orach chayim, part iii, siman 13", "orach chayim, part iii, siman 14", "orach chayim, part iii, siman 15", "orach chayim, part iii, siman 16", "orach chayim, part iii, siman 17", "orach chayim, part iii, siman 18", "orach chayim, part iii, siman 19", "orach chayim, part iii, siman 20", "orach chayim, part iii, siman 21", "orach chayim, part iii, siman 22", "orach chayim, part iii, siman 23", "orach chayim, part iii, siman 24", "orach chayim, part iii, siman 25", "orach chayim, part iii, siman 26", "orach chayim, part iii, siman 27", "orach chayim, part iii, siman 28", "orach chayim, part iii, siman 29", "orach chayim, part iii, siman 30", "orach chayim, part iii, siman 31", "orach chayim, part iii, siman 32", "orach chayim, part iii, siman 33", "orach chayim, part iii, siman 34", "orach chayim, part iii, siman 35", "orach chayim, part iii, siman 36", "orach chayim, part iii, siman 37", "orach chayim, part iii, siman 38", "orach chayim, part iii, siman 39", "orach chayim, part iii, siman 40", "orach chayim, part iii, siman 41", "orach chayim, part iii, siman 42", "orach chayim, part iii, siman 43", "orach chayim, part iii, siman 44", "orach chayim, part iii, siman 45"], ["אורח חיים ח״ג סימן א׳", "אורח חיים ח״ג סימן ב׳", "אורח חיים ח״ג סימן ג׳", "אורח חיים ח״ג סימן ד׳", "אורח חיים ח״ג סימן ה׳", "אורח חיים ח״ג סימן ו׳", "אורח חיים ח״ג סימן ז׳", "אורח חיים ח״ג סימן ח׳", "אורח חיים ח״ג סימן ט׳", "אורח חיים ח״ג סימן י׳", "אורח חיים ח״ג סימן י״א", "אורח חיים ח״ג סימן י״ב", "אורח חיים ח״ג סימן י״ג", "אורח חיים ח״ג סימן י״ד", "אורח חיים ח״ג סימן ט״ו", "אורח חיים ח״ג סימן ט״ז", "אורח חיים ח״ג סימן י״ז", "אורח חיים ח״ג סימן י״ח", "אורח חיים ח״ג סימן י״ט", "אורח חיים ח״ג סימן כ׳", "אורח חיים ח״ג סימן כ״א", "אורח חיים ח״ג סימן כ״ב", "אורח חיים ח״ג סימן כ״ג", "אורח חיים ח״ג סימן כ״ד", "אורח חיים ח״ג סימן כ״ה", "אורח חיים ח״ג סימן כ״ו", "אורח חיים ח״ג סימן כ״ז", "אורח חיים ח״ג סימן כ״ח", "אורח חיים ח״ג סימן כ״ט", "אורח חיים ח״ג סימן ל׳", "אורח חיים ח״ג סימן ל״א", "אורח חיים ח״ג סימן ל״ב", "אורח חיים ח״ג סימן ל״ג", "אורח חיים ח״ג סימן ל״ד", "אורח חיים ח״ג סימן ל״ה", "אורח חיים ח״ג סימן ל״ו", "אורח חיים ח״ג סימן ל״ז", "אורח חיים ח״ג סימן ל״ח", "אורח חיים ח״ג סימן ל״ט", "אורח חיים ח״ג סימן מ׳", "אורח חיים ח״ג סימן מ״א", "אורח חיים ח״ג סימן מ״ב", "אורח חיים ח״ג סימן מ״ג", "אורח חיים ח״ג סימן מ״ד", "אורח חיים ח״ג סימן מ״ה"]],
            ["OC·IV", "אורח חיים · חלק ד׳", "Orach Chayim · Part IV", ["orach chayim · part iv", "orach chayim, part iv, siman 1", "orach chayim, part iv, siman 2", "orach chayim, part iv, siman 3", "orach chayim, part iv, siman 4", "orach chayim, part iv, siman 5", "orach chayim, part iv, siman 6", "orach chayim, part iv, siman 7", "orach chayim, part iv, siman 8", "orach chayim, part iv, siman 9", "orach chayim, part iv, siman 10", "orach chayim, part iv, siman 11", "orach chayim, part iv, siman 12", "orach chayim, part iv, siman 13", "orach chayim, part iv, siman 14", "orach chayim, part iv, siman 15", "orach chayim, part iv, siman 16", "orach chayim, part iv, siman 17", "orach chayim, part iv, siman 18", "orach chayim, part iv, siman 19", "orach chayim, part iv, siman 20", "orach chayim, part iv, siman 21", "orach chayim, part iv, siman 22", "orach chayim, part iv, siman 23", "orach chayim, part iv, siman 24", "orach chayim, part iv, siman 25", "orach chayim, part iv, siman 26", "orach chayim, part iv, siman 27", "orach chayim, part iv, siman 28", "orach chayim, part iv, siman 29", "orach chayim, part iv, siman 30", "orach chayim, part iv, siman 31", "orach chayim, part iv, siman 32", "orach chayim, part iv, siman 33", "orach chayim, part iv, siman 34", "orach chayim, part iv, siman 35", "orach chayim, part iv, siman 39", "orach chayim, part iv, siman 40", "orach chayim, part iv, siman 41", "orach chayim, part iv, siman 42", "orach chayim, part iv, siman 43"], ["אורח חיים ח״ד סימן א׳", "אורח חיים ח״ד סימן ב׳", "אורח חיים ח״ד סימן ג׳", "אורח חיים ח״ד סימן ד׳", "אורח חיים ח״ד סימן ה׳", "אורח חיים ח״ד סימן ו׳", "אורח חיים ח״ד סימן ז׳", "אורח חיים ח״ד סימן ח׳", "אורח חיים ח״ד סימן ט׳", "אורח חיים ח״ד סימן י׳", "אורח חיים ח״ד סימן י״א", "אורח חיים ח״ד סימן י״ב", "אורח חיים ח״ד סימן י״ג", "אורח חיים ח״ד סימן י״ד", "אורח חיים ח״ד סימן ט״ו", "אורח חיים ח״ד סימן ט״ז", "אורח חיים ח״ד סימן י״ז", "אורח חיים ח״ד סימן י״ח", "אורח חיים ח״ד סימן י״ט", "אורח חיים ח״ד סימן כ׳", "אורח חיים ח״ד סימן כ״א", "אורח חיים ח״ד סימן כ״ב", "אורח חיים ח״ד סימן כ״ג", "אורח חיים ח״ד סימן כ״ד", "אורח חיים ח״ד סימן כ״ה", "אורח חיים ח״ד סימן כ״ו", "אורח חיים ח״ד סימן כ״ז", "אורח חיים ח״ד סימן כ״ח", "אורח חיים ח״ד סימן כ״ט", "אורח חיים ח״ד סימן ל׳", "אורח חיים ח״ד סימן ל״א", "אורח חיים ח״ד סימן ל״ב", "אורח חיים ח״ד סימן ל״ג", "אורח חיים ח״ד סימן ל״ד", "אורח חיים ח״ד סימן ל״ה", "אורח חיים ח״ד סימן ל״ט", "אורח חיים ח״ד סימן מ׳", "אורח חיים ח״ד סימן מ״א", "אורח חיים ח״ד סימן מ״ב", "אורח חיים ח״ד סימן מ״ג"]],
            ["BT", "קונטרס בית תפלה (חלק ג׳)", "Kuntres Beit Tefillah (Part III)", ["kuntres beit tefillah (part iii)", "kuntres beit tefillah"], ["קונטרס בית תפלה"]],
            ["YD·I", "יורה דעה · חלק א׳", "Yoreh Deah · Part I", ["yoreh deah · part i", "yoreh deah, part i, siman 1", "yoreh deah, part i, siman 2", "yoreh deah, part i, siman 3", "yoreh deah, part i, siman 4", "yoreh deah, part i, siman 5", "yoreh deah, part i, siman 6", "yoreh deah, part i, siman 7", "yoreh deah, part i, siman 8", "yoreh deah, part i, siman 9", "yoreh deah, part i, siman 10", "yoreh deah, part i, siman 11", "yoreh deah, part i, siman 12", "yoreh deah, part i, siman 13", "yoreh deah, part i, siman 14", "yoreh deah, part i, siman 15", "yoreh deah, part i, siman 16", "yoreh deah, part i, siman 17", "yoreh deah, part i, siman 18", "yoreh deah, part i, siman 19", "yoreh deah, part i, siman 20", "yoreh deah, part i, siman 21", "yoreh deah, part i, siman 22", "yoreh deah, part i, siman 23", "yoreh deah, part i, siman 24", "yoreh deah, part i, siman 25", "yoreh deah, part i, siman 26", "yoreh deah, part i, siman 27", "yoreh deah, part i, siman 28", "yoreh deah, part i, siman 29", "yoreh deah, part i, siman 30", "yoreh deah, part i, siman 31", "yoreh deah, part i, siman 32", "yoreh deah, part i, siman 33", "yoreh deah, part i, siman 34", "yoreh deah, part i, siman 35", "yoreh deah, part i, siman 36", "yoreh deah, part i, siman 37", "yoreh deah, part i, siman 38", "yoreh deah, part i, siman 39", "yoreh deah, part i, siman 40", "yoreh deah, part i, siman 41", "yoreh deah, part i, siman 42", "yoreh deah, part i, siman 43", "yoreh deah, part i, siman 44", "yoreh deah, part i, siman 45", "yoreh deah, part i, siman 46", "yoreh deah, part i, siman 47", "yoreh deah, part i, siman 48", "yoreh deah, part i, siman 49", "yoreh deah, part i, siman 50", "yoreh deah, part i, siman 51", "yoreh deah, part i, siman 52", "yoreh deah, part i, siman 53", "yoreh deah, part i, siman 54", "yoreh deah, part i, siman 55", "yoreh deah, part i, siman 56", "yoreh deah, part i, siman 57"], ["יורה דעה ח״א סימן א׳", "יורה דעה ח״א סימן ב׳", "יורה דעה ח״א סימן ג׳", "יורה דעה ח״א סימן ד׳", "יורה דעה ח״א סימן ה׳", "יורה דעה ח״א סימן ו׳", "יורה דעה ח״א סימן ז׳", "יורה דעה ח״א סימן ח׳", "יורה דעה ח״א סימן ט׳", "יורה דעה ח״א סימן י׳", "יורה דעה ח״א סימן י״א", "יורה דעה ח״א סימן י״ב", "יורה דעה ח״א סימן י״ג", "יורה דעה ח״א סימן י״ד", "יורה דעה ח״א סימן ט״ו", "יורה דעה ח״א סימן ט״ז", "יורה דעה ח״א סימן י״ז", "יורה דעה ח״א סימן י״ח", "יורה דעה ח״א סימן י״ט", "יורה דעה ח״א סימן כ׳", "יורה דעה ח״א סימן כ״א", "יורה דעה ח״א סימן כ״ב", "יורה דעה ח״א סימן כ״ג", "יורה דעה ח״א סימן כ״ד", "יורה דעה ח״א סימן כ״ה", "יורה דעה ח״א סימן כ״ו", "יורה דעה ח״א סימן כ״ז", "יורה דעה ח״א סימן כ״ח", "יורה דעה ח״א סימן כ״ט", "יורה דעה ח״א סימן ל׳", "יורה דעה ח״א סימן ל״א", "יורה דעה ח״א סימן ל״ב", "יורה דעה ח״א סימן ל״ג", "יורה דעה ח״א סימן ל״ד", "יורה דעה ח״א סימן ל״ה", "יורה דעה ח״א סימן ל״ו", "יורה דעה ח״א סימן ל״ז", "יורה דעה ח״א סימן ל״ח", "יורה דעה ח״א סימן ל״ט", "יורה דעה ח״א סימן מ׳", "יורה דעה ח״א סימן מ״א", "יורה דעה ח״א סימן מ״ב", "יורה דעה ח״א סימן מ״ג", "יורה דעה ח״א סימן מ״ד", "יורה דעה ח״א סימן מ״ה", "יורה דעה ח״א סימן מ״ו", "יורה דעה ח״א סימן מ״ז", "יורה דעה ח״א סימן מ״ח", "יורה דעה ח״א סימן מ״ט", "יורה דעה ח״א סימן נ׳", "יורה דעה ח״א סימן נ״א", "יורה דעה ח״א סימן נ״ב", "יורה דעה ח״א סימן נ״ג", "יורה דעה ח״א סימן נ״ד", "יורה דעה ח״א סימן נ״ה", "יורה דעה ח״א סימן נ״ו", "יורה דעה ח״א סימן נ״ז"]],
            ["YD·II", "יורה דעה · חלק ב׳", "Yoreh Deah · Part II", ["yoreh deah · part ii", "yoreh deah, part ii, siman 1", "yoreh deah, part ii, siman 2", "yoreh deah, part ii, siman 3", "yoreh deah, part ii, siman 4", "yoreh deah, part ii, siman 5", "yoreh deah, part ii, siman 6", "yoreh deah, part ii, siman 7", "yoreh deah, part ii, siman 8", "yoreh deah, part ii, siman 9", "yoreh deah, part ii, siman 10", "yoreh deah, part ii, siman 11", "yoreh deah, part ii, siman 12", "yoreh deah, part ii, siman 13", "yoreh deah, part ii, siman 14", "yoreh deah, part ii, siman 15", "yoreh deah, part ii, siman 16", "yoreh deah, part ii, siman 17", "yoreh deah, part ii, siman 18", "yoreh deah, part ii, siman 19", "yoreh deah, part ii, siman 20", "yoreh deah, part ii, siman 21", "yoreh deah, part ii, siman 22", "yoreh deah, part ii, siman 23", "yoreh deah, part ii, siman 24", "yoreh deah, part ii, siman 25", "yoreh deah, part ii, siman 26", "yoreh deah, part ii, siman 27", "yoreh deah, part ii, siman 28", "yoreh deah, part ii, siman 29", "yoreh deah, part ii, siman 30", "yoreh deah, part ii, siman 31", "yoreh deah, part ii, siman 32", "yoreh deah, part ii, siman 33", "yoreh deah, part ii, siman 34", "yoreh deah, part ii, siman 35", "yoreh deah, part ii, siman 36", "yoreh deah, part ii, siman 37", "yoreh deah, part ii, siman 38", "yoreh deah, part ii, siman 39", "yoreh deah, part ii, siman 40", "yoreh deah, part ii, siman 41"], ["יורה דעה ח״ב סימן א׳", "יורה דעה ח״ב סימן ב׳", "יורה דעה ח״ב סימן ג׳", "יורה דעה ח״ב סימן ד׳", "יורה דעה ח״ב סימן ה׳", "יורה דעה ח״ב סימן ו׳", "יורה דעה ח״ב סימן ז׳", "יורה דעה ח״ב סימן ח׳", "יורה דעה ח״ב סימן ט׳", "יורה דעה ח״ב סימן י׳", "יורה דעה ח״ב סימן י״א", "יורה דעה ח״ב סימן י״ב", "יורה דעה ח״ב סימן י״ג", "יורה דעה ח״ב סימן י״ד", "יורה דעה ח״ב סימן ט״ו", "יורה דעה ח״ב סימן ט״ז", "יורה דעה ח״ב סימן י״ז", "יורה דעה ח״ב סימן י״ח", "יורה דעה ח״ב סימן י״ט", "יורה דעה ח״ב סימן כ׳", "יורה דעה ח״ב סימן כ״א", "יורה דעה ח״ב סימן כ״ב", "יורה דעה ח״ב סימן כ״ג", "יורה דעה ח״ב סימן כ״ד", "יורה דעה ח״ב סימן כ״ה", "יורה דעה ח״ב סימן כ״ו", "יורה דעה ח״ב סימן כ״ז", "יורה דעה ח״ב סימן כ״ח", "יורה דעה ח״ב סימן כ״ט", "יורה דעה ח״ב סימן ל׳", "יורה דעה ח״ב סימן ל״א", "יורה דעה ח״ב סימן ל״ב", "יורה דעה ח״ב סימן ל״ג", "יורה דעה ח״ב סימן ל״ד", "יורה דעה ח״ב סימן ל״ה", "יורה דעה ח״ב סימן ל״ו", "יורה דעה ח״ב סימן ל״ז", "יורה דעה ח״ב סימן ל״ח", "יורה דעה ח״ב סימן ל״ט", "יורה דעה ח״ב סימן מ׳", "יורה דעה ח״ב סימן מ״א"]],
            ["YD·III", "יורה דעה · חלק ג׳", "Yoreh Deah · Part III", ["yoreh deah · part iii", "yoreh deah, part iii, siman 1", "yoreh deah, part iii, siman 2", "yoreh deah, part iii, siman 3", "yoreh deah, part iii, siman 4", "yoreh deah, part iii, siman 5", "yoreh deah, part iii, siman 6", "yoreh deah, part iii, siman 7", "yoreh deah, part iii, siman 8", "yoreh deah, part iii, siman 9", "yoreh deah, part iii, siman 10", "yoreh deah, part iii, siman 11", "yoreh deah, part iii, siman 12", "yoreh deah, part iii, siman 13", "yoreh deah, part iii, siman 14", "yoreh deah, part iii, siman 15", "yoreh deah, part iii, siman 16", "yoreh deah, part iii, siman 17", "yoreh deah, part iii, siman 18", "yoreh deah, part iii, siman 19", "yoreh deah, part iii, siman 20", "yoreh deah, part iii, siman 21", "yoreh deah, part iii, siman 22", "yoreh deah, part iii, siman 23", "yoreh deah, part iii, siman 24", "yoreh deah, part iii, siman 25", "yoreh deah, part iii, siman 26", "yoreh deah, part iii, siman 27", "yoreh deah, part iii, siman 28", "yoreh deah, part iii, siman 29", "yoreh deah, part iii, siman 30", "yoreh deah, part iii, siman 31", "yoreh deah, part iii, siman 32"], ["יורה דעה ח״ג סימן א׳", "יורה דעה ח״ג סימן ב׳", "יורה דעה ח״ג סימן ג׳", "יורה דעה ח״ג סימן ד׳", "יורה דעה ח״ג סימן ה׳", "יורה דעה ח״ג סימן ו׳", "יורה דעה ח״ג סימן ז׳", "יורה דעה ח״ג סימן ח׳", "יורה דעה ח״ג סימן ט׳", "יורה דעה ח״ג סימן י׳", "יורה דעה ח״ג סימן י״א", "יורה דעה ח״ג סימן י״ב", "יורה דעה ח״ג סימן י״ג", "יורה דעה ח״ג סימן י״ד", "יורה דעה ח״ג סימן ט״ו", "יורה דעה ח״ג סימן ט״ז", "יורה דעה ח״ג סימן י״ז", "יורה דעה ח״ג סימן י״ח", "יורה דעה ח״ג סימן י״ט", "יורה דעה ח״ג סימן כ׳", "יורה דעה ח״ג סימן כ״א", "יורה דעה ח״ג סימן כ״ב", "יורה דעה ח״ג סימן כ״ג", "יורה דעה ח״ג סימן כ״ד", "יורה דעה ח״ג סימן כ״ה", "יורה דעה ח״ג סימן כ״ו", "יורה דעה ח״ג סימן כ״ז", "יורה דעה ח״ג סימן כ״ח", "יורה דעה ח״ג סימן כ״ט", "יורה דעה ח״ג סימן ל׳", "יורה דעה ח״ג סימן ל״א", "יורה דעה ח״ג סימן ל״ב"]],
            ["YD·IV", "יורה דעה · חלק ד׳", "Yoreh Deah · Part IV", ["yoreh deah · part iv", "yoreh deah, part iv, siman 1", "yoreh deah, part iv, siman 2", "yoreh deah, part iv, siman 3", "yoreh deah, part iv, siman 4", "yoreh deah, part iv, siman 5", "yoreh deah, part iv, siman 6", "yoreh deah, part iv, siman 7", "yoreh deah, part iv, siman 8", "yoreh deah, part iv, siman 9", "yoreh deah, part iv, siman 10", "yoreh deah, part iv, siman 11", "yoreh deah, part iv, siman 12", "yoreh deah, part iv, siman 13", "yoreh deah, part iv, siman 14", "yoreh deah, part iv, siman 15", "yoreh deah, part iv, siman 16", "yoreh deah, part iv, siman 17", "yoreh deah, part iv, siman 18", "yoreh deah, part iv, siman 19", "yoreh deah, part iv, siman 20", "yoreh deah, part iv, siman 21", "yoreh deah, part iv, siman 22", "yoreh deah, part iv, siman 23", "yoreh deah, part iv, siman 24", "yoreh deah, part iv, siman 25", "yoreh deah, part iv, siman 26", "yoreh deah, part iv, siman 27", "yoreh deah, part iv, siman 28", "yoreh deah, part iv, siman 29", "yoreh deah, part iv, siman 30", "yoreh deah, part iv, siman 31", "yoreh deah, part iv, siman 32", "yoreh deah, part iv, siman 33", "yoreh deah, part iv, siman 34", "yoreh deah, part iv, siman 35", "yoreh deah, part iv, siman 36", "yoreh deah, part iv, siman 37", "yoreh deah, part iv, siman 38", "yoreh deah, part iv, siman 39"], ["יורה דעה ח״ד סימן א׳", "יורה דעה ח״ד סימן ב׳", "יורה דעה ח״ד סימן ג׳", "יורה דעה ח״ד סימן ד׳", "יורה דעה ח״ד סימן ה׳", "יורה דעה ח״ד סימן ו׳", "יורה דעה ח״ד סימן ז׳", "יורה דעה ח״ד סימן ח׳", "יורה דעה ח״ד סימן ט׳", "יורה דעה ח״ד סימן י׳", "יורה דעה ח״ד סימן י״א", "יורה דעה ח״ד סימן י״ב", "יורה דעה ח״ד סימן י״ג", "יורה דעה ח״ד סימן י״ד", "יורה דעה ח״ד סימן ט״ו", "יורה דעה ח״ד סימן ט״ז", "יורה דעה ח״ד סימן י״ז", "יורה דעה ח״ד סימן י״ח", "יורה דעה ח״ד סימן י״ט", "יורה דעה ח״ד סימן כ׳", "יורה דעה ח״ד סימן כ״א", "יורה דעה ח״ד סימן כ״ב", "יורה דעה ח״ד סימן כ״ג", "יורה דעה ח״ד סימן כ״ד", "יורה דעה ח״ד סימן כ״ה", "יורה דעה ח״ד סימן כ״ו", "יורה דעה ח״ד סימן כ״ז", "יורה דעה ח״ד סימן כ״ח", "יורה דעה ח״ד סימן כ״ט", "יורה דעה ח״ד סימן ל׳", "יורה דעה ח״ד סימן ל״א", "יורה דעה ח״ד סימן ל״ב", "יורה דעה ח״ד סימן ל״ג", "יורה דעה ח״ד סימן ל״ד", "יורה דעה ח״ד סימן ל״ה", "יורה דעה ח״ד סימן ל״ו", "יורה דעה ח״ד סימן ל״ז", "יורה דעה ח״ד סימן ל״ח", "יורה דעה ח״ד סימן ל״ט"]],
            ["EH·I", "אבן העזר · חלק א׳", "Even HaEzer · Part I", ["even haezer · part i", "even haezer, part i, siman 1", "even haezer, part i, siman 2", "even haezer, part i, siman 3", "even haezer, part i, siman 4", "even haezer, part i, siman 5", "even haezer, part i, siman 6", "even haezer, part i, siman 7", "even haezer, part i, siman 8", "even haezer, part i, siman 9", "even haezer, part i, siman 10", "even haezer, part i, siman 11", "even haezer, part i, siman 12", "even haezer, part i, siman 13"], ["אבן העזר ח״א סימן א׳", "אבן העזר ח״א סימן ב׳", "אבן העזר ח״א סימן ג׳", "אבן העזר ח״א סימן ד׳", "אבן העזר ח״א סימן ה׳", "אבן העזר ח״א סימן ו׳", "אבן העזר ח״א סימן ז׳", "אבן העזר ח״א סימן ח׳", "אבן העזר ח״א סימן ט׳", "אבן העזר ח״א סימן י׳", "אבן העזר ח״א סימן י״א", "אבן העזר ח״א סימן י״ב", "אבן העזר ח״א סימן י״ג"]],
            ["EH·II", "אבן העזר · חלק ב׳", "Even HaEzer · Part II", ["even haezer · part ii", "even haezer, part ii, siman 1", "even haezer, part ii, siman 2", "even haezer, part ii, siman 3", "even haezer, part ii, siman 4", "even haezer, part ii, siman 5", "even haezer, part ii, siman 6", "even haezer, part ii, siman 7", "even haezer, part ii, siman 8", "even haezer, part ii, siman 9", "even haezer, part ii, siman 10", "even haezer, part ii, siman 11", "even haezer, part ii, siman 12", "even haezer, part ii, siman 13", "even haezer, part ii, siman 14", "even haezer, part ii, siman 15", "even haezer, part ii, siman 16", "even haezer, part ii, siman 17", "even haezer, part ii, siman 18", "even haezer, part ii, siman 19", "even haezer, part ii, siman 20", "even haezer, part ii, siman 21", "even haezer, part ii, siman 22", "even haezer, part ii, siman 23", "even haezer, part ii, siman 24", "even haezer, part ii, siman 25", "even haezer, part ii, siman 26", "even haezer, part ii, siman 27", "even haezer, part ii, siman 28", "even haezer, part ii, siman 29", "even haezer, part ii, siman 30", "even haezer, part ii, siman 31", "even haezer, part ii, siman 32", "even haezer, part ii, siman 33", "even haezer, part ii, siman 34"], ["אבן העזר ח״ב סימן א׳", "אבן העזר ח״ב סימן ב׳", "אבן העזר ח״ב סימן ג׳", "אבן העזר ח״ב סימן ד׳", "אבן העזר ח״ב סימן ה׳", "אבן העזר ח״ב סימן ו׳", "אבן העזר ח״ב סימן ז׳", "אבן העזר ח״ב סימן ח׳", "אבן העזר ח״ב סימן ט׳", "אבן העזר ח״ב סימן י׳", "אבן העזר ח״ב סימן י״א", "אבן העזר ח״ב סימן י״ב", "אבן העזר ח״ב סימן י״ג", "אבן העזר ח״ב סימן י״ד", "אבן העזר ח״ב סימן ט״ו", "אבן העזר ח״ב סימן ט״ז", "אבן העזר ח״ב סימן י״ז", "אבן העזר ח״ב סימן י״ח", "אבן העזר ח״ב סימן י״ט", "אבן העזר ח״ב סימן כ׳", "אבן העזר ח״ב סימן כ״א", "אבן העזר ח״ב סימן כ״ב", "אבן העזר ח״ב סימן כ״ג", "אבן העזר ח״ב סימן כ״ד", "אבן העזר ח״ב סימן כ״ה", "אבן העזר ח״ב סימן כ״ו", "אבן העזר ח״ב סימן כ״ז", "אבן העזר ח״ב סימן כ״ח", "אבן העזר ח״ב סימן כ״ט", "אבן העזר ח״ב סימן ל׳", "אבן העזר ח״ב סימן ל״א", "אבן העזר ח״ב סימן ל״ב", "אבן העזר ח״ב סימן ל״ג", "אבן העזר ח״ב סימן ל״ד"]],
            ["EH·III", "אבן העזר · חלק ג׳", "Even HaEzer · Part III", ["even haezer · part iii", "even haezer, part iii, siman 1", "even haezer, part iii, siman 2", "even haezer, part iii, siman 3", "even haezer, part iii, siman 4", "even haezer, part iii, siman 5", "even haezer, part iii, siman 6", "even haezer, part iii, siman 7", "even haezer, part iii, siman 8", "even haezer, part iii, siman 9", "even haezer, part iii, siman 10", "even haezer, part iii, siman 11", "even haezer, part iii, siman 12"], ["אבן העזר ח״ג סימן א׳", "אבן העזר ח״ג סימן ב׳", "אבן העזר ח״ג סימן ג׳", "אבן העזר ח״ג סימן ד׳", "אבן העזר ח״ג סימן ה׳", "אבן העזר ח״ג סימן ו׳", "אבן העזר ח״ג סימן ז׳", "אבן העזר ח״ג סימן ח׳", "אבן העזר ח״ג סימן ט׳", "אבן העזר ח״ג סימן י׳", "אבן העזר ח״ג סימן י״א", "אבן העזר ח״ג סימן י״ב"]],
            ["EH·IV", "אבן העזר · חלק ד׳", "Even HaEzer · Part IV", ["even haezer · part iv", "even haezer, part iv, siman 1", "even haezer, part iv, siman 2", "even haezer, part iv, siman 3", "even haezer, part iv, siman 4", "even haezer, part iv, siman 5", "even haezer, part iv, siman 6", "even haezer, part iv, siman 7", "even haezer, part iv, siman 8", "even haezer, part iv, siman 9", "even haezer, part iv, siman 10", "even haezer, part iv, siman 11", "even haezer, part iv, siman 12", "even haezer, part iv, siman 13"], ["אבן העזר ח״ד סימן א׳", "אבן העזר ח״ד סימן ב׳", "אבן העזר ח״ד סימן ג׳", "אבן העזר ח״ד סימן ד׳", "אבן העזר ח״ד סימן ה׳", "אבן העזר ח״ד סימן ו׳", "אבן העזר ח״ד סימן ז׳", "אבן העזר ח״ד סימן ח׳", "אבן העזר ח״ד סימן ט׳", "אבן העזר ח״ד סימן י׳", "אבן העזר ח״ד סימן י״א", "אבן העזר ח״ד סימן י״ב", "אבן העזר ח״ד סימן י״ג"]],
            ["CM·II", "חושן משפט · חלק ב׳", "Choshen Mishpat · Part II", ["choshen mishpat · part ii", "choshen mishpat, part ii, siman 1", "choshen mishpat, part ii, siman 2", "choshen mishpat, part ii, siman 3", "choshen mishpat, part ii, siman 4", "choshen mishpat, part ii, siman 5", "choshen mishpat, part ii, siman 6", "choshen mishpat, part ii, siman 7", "choshen mishpat, part ii, siman 8", "choshen mishpat, part ii, siman 9", "choshen mishpat, part ii, siman 10", "choshen mishpat, part ii, siman 11", "choshen mishpat, part ii, siman 12", "choshen mishpat, part ii, siman 13", "choshen mishpat, part ii, siman 14", "choshen mishpat, part ii, siman 15"], ["חושן משפט ח״ב סימן א׳", "חושן משפט ח״ב סימן ב׳", "חושן משפט ח״ב סימן ג׳", "חושן משפט ח״ב סימן ד׳", "חושן משפט ח״ב סימן ה׳", "חושן משפט ח״ב סימן ו׳", "חושן משפט ח״ב סימן ז׳", "חושן משפט ח״ב סימן ח׳", "חושן משפט ח״ב סימן ט׳", "חושן משפט ח״ב סימן י׳", "חושן משפט ח״ב סימן י״א", "חושן משפט ח״ב סימן י״ב", "חושן משפט ח״ב סימן י״ג", "חושן משפט ח״ב סימן י״ד", "חושן משפט ח״ב סימן ט״ו"]],
            ["CM·III", "חושן משפט · חלק ג׳", "Choshen Mishpat · Part III", ["choshen mishpat · part iii", "choshen mishpat, part iii, siman 1", "choshen mishpat, part iii, siman 2", "choshen mishpat, part iii, siman 3", "choshen mishpat, part iii, siman 4", "choshen mishpat, part iii, siman 5", "choshen mishpat, part iii, siman 6", "choshen mishpat, part iii, siman 7", "choshen mishpat, part iii, siman 8"], ["חושן משפט ח״ג סימן א׳", "חושן משפט ח״ג סימן ב׳", "חושן משפט ח״ג סימן ג׳", "חושן משפט ח״ג סימן ד׳", "חושן משפט ח״ג סימן ה׳", "חושן משפט ח״ג סימן ו׳", "חושן משפט ח״ג סימן ז׳", "חושן משפט ח״ג סימן ח׳"]],
            ["CM·IV", "חושן משפט · חלק ד׳", "Choshen Mishpat · Part IV", ["choshen mishpat · part iv", "choshen mishpat, part iv, siman 1", "choshen mishpat, part iv, siman 2", "choshen mishpat, part iv, siman 3", "choshen mishpat, part iv, siman 4", "choshen mishpat, part iv, siman 5", "choshen mishpat, part iv, siman 6", "choshen mishpat, part iv, siman 7", "choshen mishpat, part iv, siman 8"], ["חושן משפט ח״ד סימן א׳", "חושן משפט ח״ד סימן ב׳", "חושן משפט ח״ד סימן ג׳", "חושן משפט ח״ד סימן ד׳", "חושן משפט ח״ד סימן ה׳", "חושן משפט ח״ד סימן ו׳", "חושן משפט ח״ד סימן ז׳", "חושן משפט ח״ד סימן ח׳"]]
        ];
        var out=[],i,j,aliases;
        for(i=0;i<a.length;i++){
            aliases=[a[i][1]];
            if(a[i].length>4&&a[i][4])for(j=0;j<a[i][4].length;j++)aliases.push(a[i][4][j]);
            // Rav Pe’alim: Gruppenname allein ist kein Abschnittstitel
            aliases.shift();
            out.push({key:a[i][0],he:a[i][1],en:a[i][2],enAliases:a[i][3],heAliases:aliases});
        }
        return out;
    }

    function findParashahByHebrewTitle(s){
        var t=" "+normalizeHebrewWords(s)+" ",i,j,p,a;
        if(!trim(t))return null;
        for(i=0;i<PARASHOT.length;i++){
            p=PARASHOT[i];
            // Rav Pe’alim: nur vollstaendige Gleichheit mit einem Siman-Titel
            for(j=0;j<p.heAliases.length;j++){
                a=" "+normalizeHebrewWords(p.heAliases[j])+" ";
                if(t===a)return p;
            }
        }
        return null;
    }

    function findParashahByEnglishTitle(s){
        var t=" "+normalizeEnglishWords(s)+" ",i,j,p,a;
        if(!trim(t))return null;
        for(i=0;i<PARASHOT.length;i++){
            p=PARASHOT[i];
            for(j=0;j<p.enAliases.length;j++){
                a=" "+normalizeEnglishWords(p.enAliases[j])+" ";if(t===a)return p;
            }
        }
        return null;
    }

    function extractProjectEnglishTitle(enRaw,fallback){
        var t=cleanHeadingText(enRaw);
        if(!t||containsHebrew(t))return fallback;
        var parts=t.split(/\s*[·|]\s*/g),i,c;
        for(i=parts.length-1;i>=0;i--){
            c=trim(parts[i]).replace(/^(parashah|parashat)\s+/i,"");
            if(!c)continue;
            if(/^(first|second)\s+year$/i.test(c))continue;
            if(findParashahByEnglishTitle(c))return c;
        }
        var p=findParashahByEnglishTitle(t);
        if(p)return cleanEnglishParashaFromRaw(t,p.en);
        return fallback;
    }

    function cleanEnglishParashaFromRaw(raw,fallback){
        var s=trim(String(raw||"")).replace(/^(parashah|parashat)\s+/i,"");
        s=s.replace(/\b(first|second)\s+year\b/ig,"").replace(/^[\s·|:-]+|[\s·|:-]+$/g,"");
        return s&&s.length<50?s:fallback;
    }

    function detectYearMarker(s){
        s=String(s||"");
        if(/שנה\s+ראשונ(?:ה|הּ)?/.test(stripHebrewMarks(s))||/\bfirst\s+year\b/i.test(s))return 1;
        if(/שנה\s+שנ(?:יה|ייה|י)/.test(stripHebrewMarks(s))||/\bsecond\s+year\b/i.test(s))return 2;
        return null;
    }

    function yearLabel(y){return y===1?"First Year / שנה ראשונה":(y===2?"Second Year / שנה שנייה":(y===0?"ohne Jahr":"Jahr ungeklärt"));}

    // =====================================================================
    // Safety / generic helpers
    // =====================================================================

    function createInDesignBackup(doc,suffix){
        var original;
        try{original=doc.fullName;}catch(_){original=null;}
        if(!original||!original.exists)throw new Error("Der aktive InDesign-Band muss vor der Änderung einmal gespeichert werden.");
        var base=original.displayName.replace(/\.indd$/i,"");
        var backup=uniqueFile(new File(original.parent.fsName+"/"+base+"_backup_"+suffix+"_"+timestamp()+".indd"));
        try{doc.saveACopy(backup);}catch(e){throw new Error("INDD-Sicherung konnte nicht angelegt werden: "+errorText(e));}
        if(!backup.exists)throw new Error("INDD-Sicherung wurde nicht gefunden. Änderung wurde nicht begonnen.");
        try{doc.insertLabel(DOC_LAST_BACKUP_LABEL,backup.fsName);}catch(_){}
        return backup;
    }

    function runUndoable(name,fn){
        var result;
        try{
            app.doScript(function(){result=fn();},ScriptLanguage.JAVASCRIPT,undefined,UndoModes.ENTIRE_SCRIPT,name);
            return result;
        }catch(e){
            // If the exception is from inside the operation, do not re-run it.
            throw e;
        }
    }

    function requireHeaderFonts(cfg){
        requireFont(cfg.enFont,cfg.enStyle);
        requireFont(cfg.heFont,cfg.heStyle);
        requireFont(cfg.numFont,cfg.numStyle);
        requireFont(cfg.numFont,"Regular");
    }

    function requireFont(family,style){
        var f=app.fonts.itemByName(family+"\t"+style);
        if(f&&f.isValid)return f;
        f=app.fonts.itemByName(family);
        if(f&&f.isValid)return f;
        throw new Error("Erforderliche Schrift fehlt: "+family+" "+style+".");
    }

    function blackSwatch(doc){
        var s=doc.swatches.itemByName("Black");if(s&&s.isValid)return s;
        s=doc.swatches.itemByName("$ID/Black");if(s&&s.isValid)return s;
        return doc.swatches[doc.swatches.length-1];
    }

    function setFrameInsets(tf,v){try{tf.textFramePreferences.insetSpacing=[v,v,v,v];}catch(_){} }

    function templateNeedsYear(cfg){return cfg.enTemplate.indexOf("{YEAR}")>=0||cfg.heTemplate.indexOf("{YEAR_HE}")>=0;}

    function parsePhysicalPageRange(text,count){
        var flags=[],i;for(i=0;i<count;i++)flags[i]=false;
        text=trim(text);if(!text)return flags;
        var parts=text.split(/[;,]+/),p,m,a,b,n,j;
        for(i=0;i<parts.length;i++){
            p=trim(parts[i]);if(!p)continue;
            m=/^(\d+)\s*-\s*(\d+)$/.exec(p);
            if(m){a=parseInt(m[1],10);b=parseInt(m[2],10);if(a>b){n=a;a=b;b=n;}for(j=a;j<=b;j++)if(j>=1&&j<=count)flags[j-1]=true;continue;}
            n=parseInt(p,10);if(!isNaN(n)&&n>=1&&n<=count)flags[n-1]=true;
        }
        return flags;
    }

    function countTrue(a){var n=0,i;for(i=0;i<a.length;i++)if(a[i])n++;return n;}

    function formatNumberList(a){return a&&a.length?a.join(", "):"keine";}

    function cleanHeadingText(s){
        s=restoreCdata(xmlUnescape(String(s||"")));
        s=s.replace(/[\r\n\t]+/g," ").replace(/<[^>]+>/g,"");
        s=s.replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069]/g,"");
        return trim(s.replace(/\s+/g," "));
    }

    function normalizeTitle(s){return cleanHeadingText(s).toLowerCase().replace(/[׳״'’“”".,:;()\[\]{}\-–—]+/g," ").replace(/\s+/g," ").replace(/^\s+|\s+$/g,"");}

    function stripHebrewMarks(s){return String(s||"").replace(/[\u0591-\u05C7]/g,"");}

    function normalizeHebrewWords(s){
        s=stripHebrewMarks(cleanHeadingText(s));
        s=s.replace(/[^\u05D0-\u05EA ]+/g," ").replace(/\s+/g," ");
        return trim(s);
    }

    function normalizeEnglishWords(s){
        s=cleanHeadingText(s).toLowerCase();
        s=s.replace(/parashah|parashat/g," ");
        s=s.replace(/[^a-z]+/g," ").replace(/\s+/g," ");
        return trim(s);
    }

    function containsHebrew(s){return /[\u0590-\u05FF]/.test(String(s||""));}

    function cleanTemplateSeparators(s){
        s=String(s||"").replace(/\s+/g," ");
        s=s.replace(/·\s*·+/g,"·");
        s=s.replace(/^\s*·\s*|\s*·\s*$/g,"");
        return trim(s);
    }

    function replaceAllLiteral(s,find,repl){return String(s).split(find).join(String(repl));}

    function mm(v){return String(Number(v))+" mm";}
    function toMm(v){var n=Number(v);if(isNaN(n))return 0;return n/2.834645669291339;}
    function horizontalNearMm(y1,y2,target,tol){
        var a=Number(y1),b=Number(y2),pt=2.834645669291339;
        if(isNaN(a)||isNaN(b))return false;
        if(Math.abs(a-b)<tol && Math.abs(((a+b)/2)-target)<tol)return true;
        if(Math.abs((a-b)/pt)<tol && Math.abs((((a+b)/2)/pt)-target)<tol)return true;
        return false;
    }
    function spanAtLeastMm(x1,x2,minMm){
        var d=Math.abs(Number(x2)-Number(x1)),pt=2.834645669291339;
        if(isNaN(d))return false;
        return d>=minMm || (d/pt)>=minMm;
    }

    function numberValue(v,fallback){var n=parseFloat(String(v||"").replace(",","."));return isNaN(n)?fallback:n;}
    function positiveNumber(v,fallback){var n=numberValue(v,fallback);return n>0?n:fallback;}
    function clamp(n,a,b){return Math.max(a,Math.min(b,n));}
    function trim(s){return String(s||"").replace(/^\s+|\s+$/g,"");}
    function timestamp(){var d=new Date();return d.getFullYear()+pad2(d.getMonth()+1)+pad2(d.getDate())+"-"+pad2(d.getHours())+pad2(d.getMinutes())+pad2(d.getSeconds());}
    function pad2(n){n=String(n);return n.length<2?"0"+n:n;}
    function errorText(e){return e&&e.message?e.message:String(e);}

    function readUTF8(file){file.encoding="UTF-8";if(!file.open("r"))throw new Error("Datei kann nicht geöffnet werden: "+file.fsName);var s=file.read();file.close();if(s.charCodeAt(0)===0xFEFF)s=s.substring(1);return s;}
    function xmlUnescape(s){return String(s||"").replace(/&quot;/g,'"').replace(/&gt;/g,">").replace(/&lt;/g,"<").replace(/&amp;/g,"&");}
    function restoreCdata(s){s=trim(String(s||""));if(/^<!\[CDATA\[/.test(s)&&/\]\]>$/.test(s)){s=s.replace(/^<!\[CDATA\[/,"").replace(/\]\]>$/,"").replace(/\]\]\]\]><!\[CDATA\[>/g,"]]>");}return s;}

    function uniqueFile(file){
        if(!file.exists)return file;
        var name=file.displayName,match=/^(.*?)(\.[^.]+)?$/.exec(name),base=match?match[1]:name,ext=(match&&match[2])?match[2]:"",n=2,candidate;
        do{candidate=new File(file.parent.fsName+"/"+base+"_"+n+ext);n++;}while(candidate.exists);
        return candidate;
    }

    // =====================================================================
    // UI styling helpers
    // =====================================================================

    function addWorkflowLegend(parent,items){
        var p=parent.add("panel",undefined,"Farblegende · gleicher Ablauf = gleiche Farbe");
        p.orientation="row";p.alignChildren=["left","center"];p.margins=7;p.spacing=16;
        var i,item,st;
        for(i=0;i<items.length;i++){
            item=items[i];st=p.add("statictext",undefined,"● "+item.label);
            styleWorkflowText(st,item.color,item.tip||"");
        }
        return p;
    }

    function styleWorkflowText(control,color,tip){
        if(tip)control.helpTip=tip;
        try{
            var g=control.graphics;
            g.foregroundColor=g.newPen(g.PenType.SOLID_COLOR,color,1);
            try{g.font=ScriptUI.newFont(g.font.name,"BOLD",g.font.size);}catch(_font){}
        }catch(_){}
        return control;
    }

    function styleWorkflowButton(btn,color,tip){
        btn.__bihWorkflowColor=color;
        if(tip)btn.helpTip=tip;
        try{
            var gg=btn.graphics;
            gg.backgroundColor=gg.newBrush(gg.BrushType.SOLID_COLOR,color);
            gg.foregroundColor=gg.newPen(gg.PenType.SOLID_COLOR,UI_TEXT_LIGHT,1);
        }catch(_direct){}
        btn.onDraw=function(){
            try{
                var g=this.graphics;
                var ww=(this.size&&this.size.width!==undefined)?this.size.width:this.size[0];
                var hh=(this.size&&this.size.height!==undefined)?this.size.height:this.size[1];
                var c=this.enabled?this.__bihWorkflowColor:UI_DISABLED;
                var brush=g.newBrush(g.BrushType.SOLID_COLOR,c);
                var border=g.newPen(g.PenType.SOLID_COLOR,[0.12,0.12,0.12,1],1);
                var textPen=g.newPen(g.PenType.SOLID_COLOR,this.enabled?UI_TEXT_LIGHT:[0.72,0.72,0.72,1],1);
                g.rectPath(0,0,ww,hh);g.fillPath(brush);g.strokePath(border);
                var txt=String(this.text||"");var m=g.measureString(txt);var x=Math.max(4,(ww-m[0])/2);var y=Math.max(2,(hh-m[1])/2);
                g.drawString(txt,textPen,x,y);
            }catch(_draw){}
        };
        return btn;
    }

})();
