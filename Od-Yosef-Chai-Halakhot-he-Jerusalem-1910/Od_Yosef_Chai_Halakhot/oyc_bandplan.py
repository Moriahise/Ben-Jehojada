# -*- coding: utf-8 -*-
"""
Schritt 4 — Bandplan mit der Bandgroesse von Ben Ish Chai Halakha, Banddatei.

Die Planung bildet planVolumes()/estimatedBodyPages() aus
Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17 genau nach:

    Seiten(Text) = ceil(max(HE/1050, HE*1,95/2000))
    Band         = Seiten(Text) + 12 Reserve, Ziel 540, harte Grenze 600
    neuer Band   , wenn Seiten(Text) des naechsten Abschnitts 528 ueberschreiten
                   (Abschnitt = Parascha; zu grosse Abschnitte nur zwischen Segmenten)

HE zaehlt wie visibleLength() im JSX (Text ohne Tags, getrimmt). Bei
vokalisiertem Text zaehlt das JSX jedes Vokalzeichen mit; der Bericht nennt
deshalb beide Werte. Planungsgrundlage ist die Konsonantenzahl, weil die
Kalibrierung 1050 Z./S. an unvokalisiertem Satz gemessen wurde.

Ausgabe (BIC-Dateiform, vom Buchmanager v1.0.17 direkt lesbar)
    Od_Yosef_Chai_Halakhot_Band_01_BILINGUAL.txt
    Od_Yosef_Chai_Halakhot_Bandplan.txt
    Od_Yosef_Chai_Halakhot_Segmentkontrolle.tsv

--he-quelle basis   Sefaria-Text (unvokalisiert) – Planungs- und Pruefstand
--he-quelle meine   Vokalzeichen aus "Meiner Fassung" auf den Basiskonsonanten
--he-quelle nakdan  Vokalzeichen aus dem Nakdan-Zeugen
"""
import argparse
import math
import re
import sys
from pathlib import Path

import oyc_common as C


def estimated_body_pages(he_chars, he_cpp=C.HE_CHARS_PER_PAGE):
    he_pages = he_chars / float(he_cpp)
    en_pages = (he_chars * C.EN_EXPANSION) / float(C.EN_CHARS_PER_PAGE)
    return int(math.ceil(max(he_pages, en_pages)))


def split_oversize_section(title, segs, he_cpp):
    out, cur = [], {'title': title, 'part': 1, 'segments': [], 'he_chars': 0}
    for s in segs:
        nxt = cur['he_chars'] + s['plan_chars']
        if cur['segments'] and estimated_body_pages(nxt, he_cpp) > C.BODY_TARGET:
            out.append(cur)
            cur = {'title': title, 'part': cur['part'] + 1, 'segments': [], 'he_chars': 0}
        cur['segments'].append(s)
        cur['he_chars'] += s['plan_chars']
    if cur['segments']:
        out.append(cur)
    return out


def plan_volumes(segs, he_cpp=C.HE_CHARS_PER_PAGE):
    """planVolumes() des BIC-JSX. segs brauchen 'section_he' und 'plan_chars'."""
    sections, cur = [], None
    for s in segs:
        if cur is None or s['section_he'] != cur[0]:
            cur = (s['section_he'], [])
            sections.append(cur)
        cur[1].append(s)
    groups = []
    for title, ss in sections:
        groups.extend(split_oversize_section(title, ss, he_cpp))
    vols, v = [], None
    for g in groups:
        if v is None:
            v = {'number': 1, 'groups': [], 'segments': [], 'he_chars': 0}
        if v['segments'] and estimated_body_pages(v['he_chars'] + g['he_chars'], he_cpp) > C.BODY_TARGET:
            vols.append(v)
            v = {'number': len(vols) + 1, 'groups': [], 'segments': [], 'he_chars': 0}
        v['groups'].append(g)
        v['segments'].extend(g['segments'])
        v['he_chars'] += g['he_chars']
    if v and v['segments']:
        vols.append(v)
    for v in vols:
        v['estimated_en_chars'] = int(math.ceil(v['he_chars'] * C.EN_EXPANSION))
        v['estimated_body_pages'] = estimated_body_pages(v['he_chars'], he_cpp)
        v['estimated_pages'] = v['estimated_body_pages'] + C.RESERVED_PAGES
        if v['estimated_pages'] > C.TARGET_PAGES:
            raise SystemExit('Band {} ueberschreitet schon in der Planung {} Seiten.'.format(
                v['number'], C.TARGET_PAGES))
    return vols


def serialize_volume(v):
    """serializeVolume() des BIC-JSX; project-Attribut werkspezifisch."""
    out = ['<book project="{}" volume="{:02d}" max_pages="{}">'.format(C.PROJECT_ATTR, v['number'], C.MAX_PAGES),
           '<planning estimated_pages="{}" target_pages="{}" reserved_pages="{}" he_quelle="{}" />'.format(
               v['estimated_pages'], C.TARGET_PAGES, C.RESERVED_PAGES, v.get('he_quelle', 'basis'))]
    last = None
    for s in v['segments']:
        if s['section_he'] != last:
            out += ['', '<section>', '<he_title>' + C.xml_escape(s['section_he']) + '</he_title>',
                    '<en_title></en_title>', '</section>']
            last = s['section_he']
        out += ['', '<segment id="{}" n="{}">'.format(s['id'], s['n']),
                '<he>' + C.protect_cdata(s['he']) + '</he>', '<en></en>', '</segment>']
    out += ['', '</book>']
    return '\r\n'.join(out)


def master_hat_uebersetzung(path):
    if not Path(path).exists():
        return False
    raw = Path(path).read_text(encoding='utf-8-sig')
    for m in re.finditer(r'<en>(.*?)</en>', raw, re.S):
        inner = re.sub(r'^<!\[CDATA\[|\]\]>$', '', m.group(1).strip())
        if C.strip_tags(inner).strip():
            return True
    for m in re.finditer(r'<en_title>(.*?)</en_title>', raw, re.S):
        if m.group(1).strip():
            return True
    return False


def he_texte(werk, quelle, unvollstaendig_erlaubt=False):
    if quelle == 'basis':
        return None, {}
    import oyc_kollation as K
    import oyc_nakdan as N
    texte = N.lese_zeuge(N.ZEUGEN[quelle])
    if not texte:
        raise SystemExit('Zeuge "{}" ist leer – zuerst oyc_nakdan.py ({}).'.format(
            quelle, 'api/import' if quelle == 'nakdan' else 'vorlage, dann bearbeiten'))
    out, fehlend, offen = K.vokalisierte_texte(werk, texte, unvollstaendig_erlaubt)
    return out, {'fehlende_absaetze': len(fehlend), 'woerter_ohne_uebertragung': offen}


def run(json_path=None, out='out', he_quelle='basis', unvollstaendig_erlaubt=False,
        konkordanz=None, ueberschreiben=False, quiet=False):
    out = Path(out) / 'band'
    werk = C.load_werk_korrigiert(json_path)
    texts, vinfo = he_texte(werk, he_quelle, unvollstaendig_erlaubt)
    segs = C.build_segments(werk, texts)
    for s in segs:
        s['bic_chars'] = s['he_chars']                       # wie das JSX zaehlt
        s['plan_chars'] = C.visible_length(C.strip_nikud(s['he']))  # Konsonanten
    vols = plan_volumes(segs)
    hoch = 14
    vols_hoch = plan_volumes(segs, he_cpp=C.HE_CHARS_PER_PAGE * C.HE_LEADING_PT / float(hoch))

    # Scanseiten je Abschnitt aus der Konkordanz (falls schon erfasst)
    import oyc_abschnitte as A
    konk = A.lade_konkordanz(konkordanz or C.HERE / 'scan_konkordanz.tsv')
    scan_of = {}
    for r in konk:
        if r['art'] in A.HALACHA_ARTEN:
            for ab in A.abschn(r):
                scan_of.setdefault(ab, []).append(r['seq'])

    written = []
    for v in vols:
        v['he_quelle'] = he_quelle
        f = out / '{}_Band_{:02d}_BILINGUAL.txt'.format(C.WERK_TAG, v['number'])
        if master_hat_uebersetzung(f) and not ueberschreiben:
            raise SystemExit('Abbruch ohne Ueberschreiben: {} enthaelt bereits Englisch.'.format(f))
        C.write_bic_text(f, serialize_volume(v))
        written.append(f)
    rows = []
    for v in vols:
        for s in v['segments']:
            sp = scan_of.get(s['abschnitt'], [])
            rows.append([v['number'], s['id'], s['n'], s['section_he'], s['bic_chars'], 'offen',
                         s['ref'], s['absaetze'], s['plan_chars'],
                         A.kurzliste(sp) if sp else '', s.get('rolle', '')])
    C.write_tsv(out / (C.WERK_TAG + '_Segmentkontrolle.tsv'),
                ['volume', 'segment_id', 'visible_number', 'section', 'he_chars', 'status',
                 'sefaria_ref', 'absaetze', 'he_konsonanten', 'scanseiten_abschnitt', 'gliederung'], rows)

    total_plan = sum(s['plan_chars'] for s in segs)
    total_bic = sum(s['bic_chars'] for s in segs)
    gross = [s for s in segs if s['plan_chars'] > C.BATCH_MAX_CHARS]
    L = ['OD YOSEF CHAI · HALAKHOT · BANDPLAN (BANDGROESSE BEN ISH CHAI HALAKHA)', '',
         'Quelle: {} Segmente · {} Abschnitte · HE-Quelle: {}'.format(
             len(segs), len({s['section_he'] for s in segs}), he_quelle),
         'Format: {} × {} mm · Keter YG 10/{} pt · Cambria 9/10,8 pt (Ben Ish Chai v1.0.17)'.format(
             C.PAGE_W_MM, C.PAGE_H_MM, C.HE_LEADING_PT),
         'Kalibrierung: HE {} Zeichen/Seite · EN {} Zeichen/Seite · erwartete EN-Laenge {:.2f} × HE'.format(
             C.HE_CHARS_PER_PAGE, C.EN_CHARS_PER_PAGE, C.EN_EXPANSION),
         'Grenzen: Ziel {} Seiten (davon {} Reserve) · Textseiten hoechstens {} · absolute Sperre {}'.format(
             C.TARGET_PAGES, C.RESERVED_PAGES, C.BODY_TARGET, C.MAX_PAGES),
         'HE-Zeichen: {} Konsonantentext (Planung){}'.format(
             total_plan, '' if total_bic == total_plan else ' · {} wie das JSX zaehlt (mit Vokalzeichen)'.format(total_bic)),
         '', 'Plan: {} Band/Baende'.format(len(vols))]
    for v in vols:
        first, last = v['segments'][0], v['segments'][-1]
        hep = v['he_chars'] / float(C.HE_CHARS_PER_PAGE)
        enp = v['he_chars'] * C.EN_EXPANSION / float(C.EN_CHARS_PER_PAGE)
        L += ['Band {:02d}: ca. {} Seiten (davon {} Reserve) · {} Segmente · {} bis {}'.format(
                  v['number'], v['estimated_pages'], C.RESERVED_PAGES, len(v['segments']), first['id'], last['id']),
              '    {}  →  {}'.format(first['section_he'], last['section_he']),
              '    HE {} Zeichen = {:.1f} Seiten · EN geschaetzt {} Zeichen = {:.1f} Seiten · massgeblich {}'.format(
                  v['he_chars'], hep, v['estimated_en_chars'], enp, 'EN' if enp >= hep else 'HE'),
              '    Reserve bis Ziel {}: {} Seiten · bis Sperre {}: {} Seiten'.format(
                  C.TARGET_PAGES, C.TARGET_PAGES - v['estimated_pages'], C.MAX_PAGES,
                  C.MAX_PAGES - v['estimated_pages'])]
    L += ['', 'EMPFINDLICHKEIT',
          '  Vokalisierter Satz mit {} statt {} pt Zeilenabstand (HE {:.0f} Z./S.): {} Band/Baende, Band 01 ca. {} Seiten'.format(
              hoch, C.HE_LEADING_PT, C.HE_CHARS_PER_PAGE * C.HE_LEADING_PT / float(hoch), len(vols_hoch),
              vols_hoch[0]['estimated_pages'])]
    if len(vols) == 1:
        v = vols[0]
        for f in (1.10, 1.25):
            L.append('  EN-Laenge {:.2f} statt {:.2f} × HE: ca. {} Seiten'.format(
                C.EN_EXPANSION * f, C.EN_EXPANSION,
                int(math.ceil(max(v['he_chars'] / float(C.HE_CHARS_PER_PAGE),
                                  v['he_chars'] * C.EN_EXPANSION * f / float(C.EN_CHARS_PER_PAGE)))) + C.RESERVED_PAGES))
    gl = C.lade_gliederung()
    if gl:
        L += ['', 'GLIEDERUNG (Lektoratsentscheidungen, gliederung.json)']
        for t in gl.get('teilen', []):
            L.append('  {} geteilt ({}):'.format(t['ref'], t.get('beleg', '')))
            for x in [x for x in segs if x['ref'].startswith('{}, {}:'.format(C.WERK_EN, t['ref']))]:
                L.append('    {} [{}] {} · {} · {}'.format(x['id'], x['n'], x['ref'].split(', ', 1)[1],
                                                      x['section_he'], x['rolle']))
        for u in gl.get('unterabschnitte', []):
            ids = [x['id'] for x in segs if x['abschnitt'] == u['abschnitt']]
            L.append('  {} unter {}: Abschnittstitel "{}" · {} bis {} ({})'.format(
                u['abschnitt'], u['unter'], u['abschnitt_he'], ids[0], ids[-1], u.get('beleg', '')))
        if any(x['n'] == 0 for x in segs):
            L.append('  n = 0: im Druck ungezaehlter Text; der Buchmanager setzt dafuer "[0]".')
    L += ['', 'HINWEISE']
    for s in gross:
        L.append('  {} ({}) hat {} Zeichen > Batch-Kontingent {}: wird als Einzelbatch exportiert'.format(
            s['id'], s['ref'], s['plan_chars'], C.BATCH_MAX_CHARS))
    if total_bic != total_plan:
        L.append('  Der Ben-Ish-Chai-Buchmanager v1.0.17 wuerde Vokalzeichen mitzaehlen ({} statt {} Zeichen); '
                 'der Od-Yosef-Chai-Buchmanager v1.0.0 zaehlt ohne Nikud und plant nicht neu (Reiter 1 gesperrt).'.format(
                     total_bic, total_plan))
    if he_quelle == 'basis':
        L.append('  HE-Quelle "basis": Planungsstand. Der Produktionsmaster entsteht nach abgeschlossener '
                 'Kollation mit --he-quelle meine; <he> ist danach geschuetzt.')
    if vinfo:
        L.append('  Vokalisierung: {} Absaetze ohne Zeugentext, {} Woerter ohne uebertragene Vokale.'.format(
            vinfo['fehlende_absaetze'], vinfo['woerter_ohne_uebertragung']))
    L.append('  Der Buchmanager laesst beim Zusammenfuehren die Zeile <planning> weg (reserializeParsedBook); '
             'die HE-Quelle steht dann nur noch im Pipeline-Master und im Quellenmanifest.')
    L.append('  InDesign: indesign/Od_Yosef_Chai_Bilingual_Book_Manager_v1_0_0.jsx (Reiter 2/3) und '
             'indesign/Od_Yosef_Chai_Running_Header_Manager_v1_0_0.jsx.')
    L += ['', 'Dateien:'] + ['  ' + str(f.name) for f in written]
    txt = '\n'.join(L) + '\n'
    C.write_bic_text(out / (C.WERK_TAG + '_Bandplan.txt'), txt)
    if not quiet:
        print(txt)
    return {'baende': len(vols), 'band_seiten': [v['estimated_pages'] for v in vols],
            'segmente': len(segs), 'he_zeichen': total_plan, 'he_zeichen_bic': total_bic,
            'dateien': [str(f) for f in written], 'bericht': txt, 'vols': vols, 'segs': segs}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Bandplan nach Ben-Ish-Chai-Bandgroesse und Banddatei')
    ap.add_argument('--json', default=str(C.SOURCE_JSON))
    ap.add_argument('--out', default=str(C.HERE / 'out'))
    ap.add_argument('--he-quelle', choices=['basis', 'meine', 'nakdan'], default='basis')
    ap.add_argument('--unvollstaendig-erlaubt', action='store_true',
                    help='fehlende Zeugenabsaetze bleiben unvokalisiert (nur fuer Proben)')
    ap.add_argument('--ueberschreiben', action='store_true',
                    help='auch einen Master mit Englisch ueberschreiben (nie fuer Produktion)')
    a = ap.parse_args(argv)
    run(a.json, a.out, a.he_quelle, a.unvollstaendig_erlaubt, ueberschreiben=a.ueberschreiben)
    return 0


if __name__ == '__main__':
    sys.exit(main())
