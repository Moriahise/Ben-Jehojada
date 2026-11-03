# -*- coding: utf-8 -*-
"""
Schritt 3 — Glossar aus Ben Jehojada uebernehmen, neue Termini markieren.

Grundlage ist unveraendert die Ben-Jehojada-Pipeline v3.2.1 (by_parse.find_abbrs,
by_glossary.Glossary aus dem Repository-ZIP) mit der jeweils neuesten
glossary_he.json des Repositorys. Die Datei glossary_he.json wird hier nicht
veraendert: neue Eintraege gehoeren nach Pruefung mit Beleg dorthin
(Arbeitsanleitung 1.5, Schritt 5), nicht automatisch.

Status je Kuerzel
    UEBERNOMMEN      kuratierter BY-Eintrag (auch kontextabhaengig)
    ABGELEITET       Praefix + BY-Eintrag oder Buchstabenname
    ZAHLWERT         Gematria nur mit unmittelbarem Zahlenkontext
    INLINE           Erklaerung steht im Text selbst
    NEU              im BY-Glossar nicht aufloesbar  -> neuer Terminus, kuratieren
Hinweisspalte
    KONTEXT PRUEFEN  BY-Lesart passt im halachischen Zitierkontext evtl. nicht
                     (Regeln in kontextregeln.json)

Kuerzel mit einfachem Geresch (סי', הנז', וכו') erkennt der BY-Mechanismus
nicht; sie werden gesondert als GERESCH gelistet (nur Liste, keine Fussnote).

Ausgaben (out/glossar/)
    Od_Yosef_Chai_Halakhot_GLOSSAR.tsv        Uebersetzerhilfe mit Status
    Od_Yosef_Chai_Halakhot_Glossar_NEU.json   neue Termini mit Kontexten, he/en leer
    Od_Yosef_Chai_Halakhot_Glossar_Bericht.txt
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

import oyc_common as C

KONTEXTREGELN = C.HERE / 'kontextregeln.json'
GERESH_RE = re.compile(r'(?<![א-ת"\'])([א-ת]{2,})[\'׳](?![א-ת])')
STATUS = {'curated': 'UEBERNOMMEN', 'context': 'UEBERNOMMEN', 'prefix': 'ABGELEITET',
          'letter': 'ABGELEITET', 'gematria_context': 'ZAHLWERT', 'inline': 'INLINE',
          'inline_numeric': 'INLINE', 'stellenzahl': 'STELLENZAHL', None: 'NEU'}


def lade_regeln(path=None):
    path = Path(path or KONTEXTREGELN)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding='utf-8')).get('regeln', [])


def regel_treffer(regeln, abbr, en, vortext, folgetext):
    out = []
    for r in regeln:
        if r.get('abbr') and r['abbr'] != abbr:
            continue
        if abbr in (r.get('ausser') or []):
            continue
        if r.get('nur_en_klein') and not (en and en[:1].islower()):
            continue
        if r.get('folgt') and not re.match(r['folgt'], folgetext or ''):
            continue
        if r.get('vorher') and not re.search(r['vorher'], vortext or ''):
            continue
        out.append(r['hinweis'])
    return out


# Stellenangaben, hinter denen ein Kuerzel eine Zahl ist (סי' י"א, דף כ"ב, ס"ק ג').
STELLE_VOR = re.compile(r'(?:סי\'|סימן|דף|ס"ק|סעיף|סעי\'|אות|כלל|פרק|פ\'|שער|נתיב|מצוה|ח"[א-ה]|תשובה|סק"|ע"[אבגד])\s*$')


def stellenzahl(glossary, abbr, vortext):
    """Zahlwert eines unaufgeloesten Kuerzels direkt hinter einer Stellenangabe
    (OYC-Erweiterung; der BY-Mechanismus kennt nur Gematria-Kontextwoerter)."""
    import by_glossary
    if not STELLE_VOR.search(vortext[-24:]):
        return None
    return glossary._gematria(by_glossary.norm(abbr))


def occ_re(abbr):
    return re.compile(r'(?<![\u05D0-\u05EA"])' + re.escape(abbr) + r'(?![\u05D0-\u05EA"])')


def sammle(werk, glossary, by_parse, regeln):
    """Je Vorkommen aufloesen (lokaler Kontext wie in by_parse). -> {abbr: record}"""
    import by_glossary
    rec = collections.OrderedDict()
    for a, h, p in C.iter_absaetze(werk):
        text = C.strip_tags(p['html'])
        for x in by_parse.find_abbrs(text):
            key = x['abbr']
            e = rec.get(key)
            if e is None:
                v = glossary.idx.get(by_glossary.norm(key))
                e = rec[key] = {'abbr': key, 'treffer': 0, 'absaetze': [], 'quellen': collections.Counter(),
                                'he': None, 'en': None, 'alt': (v or {}).get('alt'), 'kontexte': [],
                                'hinweise': collections.Counter(), 'abschnitte': collections.Counter(),
                                'zahlen': collections.Counter()}
            e['absaetze'].append(p['ref'])
            occs = list(occ_re(key).finditer(text)) or [None]
            for m in occs:
                lo, hi = (m.start(), m.end()) if m else (0, len(text))
                ctx = by_parse.strip_tags(text[max(0, lo - 120):hi + 120])
                r = glossary.resolve(key, context=ctx,
                                     inline_expansion=x.get('inline_expansion') if m is occs[0] else None)
                src = r['source'] if r else None
                if r is None:
                    z = stellenzahl(glossary, key, text[:lo])
                    if z:
                        src = 'stellenzahl'
                        e['zahlen'][z] += 1
                e['treffer'] += 1
                e['abschnitte'][a['key']] += 1
                e['quellen'][src] += 1
                if r and e['he'] is None:
                    e['he'], e['en'] = r.get('he'), r.get('en')
                for hw in regel_treffer(regeln, key, (r or {}).get('en'), text[max(0, lo - 30):lo],
                                        text[hi:hi + 40]):
                    e['hinweise'][hw] += 1
            if len(e['kontexte']) < 3:
                e['kontexte'].append('{}: {}'.format(p['ref'], (x.get('context') or '')[:160]))
    return rec


def stamm_von(abbr, rec, glossary):
    """Kuerzester bekannter Stamm nach Praefixabtrennung (בש"ץ -> ש"ץ)."""
    import by_glossary
    for pfx in sorted(by_glossary.PREFIXES, key=len, reverse=True):
        if abbr.startswith(pfx) and len(abbr) > len(pfx) + 2:
            rest = abbr[len(pfx):]
            if rest in rec or by_glossary.norm(rest) in glossary.idx:
                return rest
    return abbr


def sammle_geresh(werk, glossary):
    c, stellen = collections.Counter(), {}
    for a, h, p in C.iter_absaetze(werk):
        for m in GERESH_RE.finditer(C.strip_tags(p['html'])):
            t = m.group(1) + "'"
            c[t] += 1
            stellen.setdefault(t, p['ref'])
    import by_glossary
    return [(t, n, stellen[t], 'ja' if by_glossary.norm(t) in glossary.idx else 'nein')
            for t, n in c.most_common()]


def status_von(e):
    """Hauptstatus; gemischte Faelle als 'A+B' in fester Rangfolge."""
    namen = sorted({STATUS.get(k, k) for k in e['quellen']},
                   key=lambda n: ['UEBERNOMMEN', 'ABGELEITET', 'INLINE', 'ZAHLWERT', 'STELLENZAHL', 'NEU'].index(n))
    return '+'.join(namen)


def run(json_path=None, glossary_path=None, out='out', pipeline=None, regeln_path=None, quiet=False):
    C.import_pipeline(pipeline)
    import by_glossary
    import by_parse
    gpath = Path(glossary_path or C.GLOSSARY)
    glossary = by_glossary.Glossary(str(gpath))
    graw = json.loads(gpath.read_text(encoding='utf-8'))
    werk = C.load_werk_korrigiert(json_path)
    regeln = lade_regeln(regeln_path)
    rec = sammle(werk, glossary, by_parse, regeln)
    out = Path(out) / 'glossar'
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for e in sorted(rec.values(), key=lambda e: (-e['treffer'], e['abbr'])):
        st = status_von(e)
        e['status'] = st
        e['stamm'] = stamm_von(e['abbr'], rec, glossary) if 'NEU' in st else ''
        rows.append([e['abbr'], e['he'] or '', e['en'] or '', st, e['stamm'],
                     ', '.join('{}:{}'.format(k or 'offen', v) for k, v in e['quellen'].most_common()),
                     e['treffer'], len(e['absaetze']), e['absaetze'][0],
                     '; '.join('{} ({}x)'.format(k, v) for k, v in e['hinweise'].items()),
                     e['alt'] or '', e['kontexte'][0] if e['kontexte'] else ''])
    C.write_tsv(out / (C.WERK_TAG + '_GLOSSAR.tsv'),
                ['abbr', 'hebrew', 'english', 'status', 'neu_stamm', 'mechanismus', 'treffer', 'absaetze',
                 'erste_stelle', 'hinweis', 'alt_by', 'kontext'], rows)

    neu = collections.OrderedDict()
    for e in sorted(rec.values(), key=lambda e: (-e['quellen'].get(None, 0), e['abbr'])):
        if None not in e['quellen']:
            continue
        neu[e['abbr']] = {'he': '', 'en': '', 'neu': True, 'status': e['status'], 'stamm': e['stamm'],
                          'treffer_offen': e['quellen'][None], 'treffer': e['treffer'],
                          'abschnitte': dict(e['abschnitte']), 'stellen': e['absaetze'][:8],
                          'kontexte': e['kontexte']}
    pruefen = {e['abbr']: dict(e['hinweise']) for e in rec.values() if e['hinweise']}
    meta = {'werk': C.WERK_EN, 'json_sha256': werk['meta']['sha256'],
            'basis_glossar': str(gpath), 'basis_glossar_sha256': C.sha256_file(gpath),
            'basis_eintraege': len(graw.get('abbreviations', {})),
            'basis_stand': (graw.get('_meta') or {}).get('stand', '')[:300] + ' …',
            'pipeline': 'ben-yehoyada-pipeline v3.2.1 (by_parse.find_abbrs, by_glossary.Glossary)',
            'hinweis': 'he/en der neuen Termini erst nach Beleg fuellen und dann in die '
                       'Repository-glossary_he.json uebernehmen (_meta.stand: "Od Yosef Chai Halakhot").'}
    C.write_json(out / (C.WERK_TAG + '_Glossar_NEU.json'),
                 {'_meta': meta, 'neu': neu, 'kontext_pruefen': pruefen})
    geresh = sammle_geresh(werk, glossary)
    C.write_tsv(out / (C.WERK_TAG + '_Geresch_Kuerzel.tsv'),
                ['kuerzel', 'treffer', 'erste_stelle', 'im_by_glossar'], geresh)

    tot = sum(e['treffer'] for e in rec.values())
    by_src = collections.Counter()
    for e in rec.values():
        by_src.update({STATUS.get(k, k): v for k, v in e['quellen'].items()})
    aufgeloest = tot - by_src.get('NEU', 0) - by_src.get('STELLENZAHL', 0)
    st_count = collections.Counter(e['status'] for e in rec.values())
    used_curated = sum(1 for e in rec.values() if e['quellen'].get('curated') or e['quellen'].get('context'))
    L = ['OD YOSEF CHAI · HALAKHOT · GLOSSAR (BASIS: BEN JEHOJADA)', '',
         'Glossar: {} · {} Eintraege · sha256 {}'.format(gpath.name, meta['basis_eintraege'], meta['basis_glossar_sha256']),
         'Pipeline: ' + meta['pipeline'], '',
         'Kuerzel (Gershajim) gesamt: {} Treffer · {} verschiedene'.format(tot, len(rec)),
         'aufgeloest mit BY-Glossar: {} Treffer = {:.1f} %'.format(aufgeloest, 100.0 * aufgeloest / tot if tot else 0),
         'Zahlen hinter Stellenangaben (STELLENZAHL, OYC-Erweiterung, keine Fussnote): {}'.format(by_src.get('STELLENZAHL', 0)),
         'nach Mechanismus: ' + ', '.join('{} {}'.format(k, v) for k, v in by_src.most_common()),
         'BY-Eintraege im Werk benutzt: {} von {}'.format(used_curated, meta['basis_eintraege']),
         'Status (verschiedene Kuerzel): ' + ', '.join('{} {}'.format(k, v) for k, v in st_count.most_common()), '',
         'NEUE TERMINI nach Stamm (im BY-Glossar nicht aufloesbar; Praefixformen zusammengefasst), haeufigste 40:']
    staemme = collections.OrderedDict()
    for k, v in neu.items():
        s_ = staemme.setdefault(v['stamm'] or k, {'treffer': 0, 'formen': [], 'stelle': v['stellen'][0]})
        s_['treffer'] += v['treffer_offen']
        s_['formen'].append(k)
    staemme = collections.OrderedDict(sorted(staemme.items(), key=lambda kv: -kv[1]['treffer']))
    for k, v in list(staemme.items())[:40]:
        L.append('  {:>4}  {:<10} {:<22} {}'.format(v['treffer'], k, v['stelle'],
                                                      ' '.join(f for f in v['formen'] if f != k)[:60]))
    L += ['  … insgesamt {} neue Formen / {} Staemme, vollstaendig in {}_Glossar_NEU.json'.format(
        len(neu), len(staemme), C.WERK_TAG), '',
          'KONTEXT PRUEFEN (BY-Lesart im halachischen Zitierkontext fraglich):']
    for k, v in sorted(pruefen.items(), key=lambda kv: -sum(kv[1].values())):
        L.append('  {:<10} {}'.format(k, '; '.join('{} ({}x)'.format(h, n) for h, n in v.items())))
    if not pruefen:
        L.append('  keine')
    L += ['', 'GERESCH-KUERZEL (vom BY-Mechanismus nicht erfasst), haeufigste 15:']
    for t, n, st, im in geresh[:15]:
        L.append('  {:>4}  {:<8} im BY-Glossar: {}'.format(n, t, im))
    txt = '\n'.join(L) + '\n'
    (out / (C.WERK_TAG + '_Glossar_Bericht.txt')).write_text(txt, encoding='utf-8')
    if not quiet:
        print(txt)
    return {'treffer': tot, 'aufgeloest': aufgeloest, 'verschieden': len(rec), 'neu': len(neu),
            'neu_staemme': len(staemme), 'nach_mechanismus': dict(by_src),
            'pruefen': len(pruefen), 'status': dict(st_count), 'bericht': txt,
            'glossar_sha256': meta['basis_glossar_sha256'], 'glossar_eintraege': meta['basis_eintraege']}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Glossar aus Ben Jehojada uebernehmen, neue Termini markieren')
    ap.add_argument('--json', default=str(C.SOURCE_JSON))
    ap.add_argument('--glossary', default=str(C.GLOSSARY), help='glossary_he.json des Repositorys')
    ap.add_argument('--pipeline', default=str(C.PIPELINE_ZIP), help='Pipeline v3.2.1 (ZIP oder Ordner)')
    ap.add_argument('--regeln', default=str(KONTEXTREGELN))
    ap.add_argument('--out', default=str(C.HERE / 'out'))
    a = ap.parse_args(argv)
    run(a.json, a.glossary, a.out, a.pipeline, a.regeln)
    return 0


if __name__ == '__main__':
    sys.exit(main())
