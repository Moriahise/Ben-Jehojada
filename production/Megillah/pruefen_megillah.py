#!/usr/bin/env python3
"""Verify the completed Megillah master against the supplied, protected source."""
import re,json,hashlib,csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ORIG=ROOT/'Audit/Ben_Yehoyada_Megillah_Band_01_Ausgangsmaster.txt'
FINAL=ROOT/'Ben_Yehoyada_Megillah_Band_01_BILINGUAL_EN_FERTIG.txt'
a=ORIG.read_bytes();b=FINAL.read_bytes()
pat=rb'<segment\b[^>]*>.*?</segment>'
asg=re.findall(pat,a,re.S);bsg=re.findall(pat,b,re.S)
errors=[];rows=[]
def check(ok,sid,code):
 if not ok:errors.append({'segment_id':sid,'check':code})
def field(t,k):return re.search(rb'<'+k.encode()+rb'>(.*?)</'+k.encode()+rb'>',t,re.S).group(1)
def decode(x):
 s=x.decode('utf-8');m=re.fullmatch(r'<!\[CDATA\[(.*)\]\]>',s,re.S);return m.group(1) if m else s
mask=lambda s:re.sub(rb'<(en|band_en)>.*?</\1>',rb'<\1>ENGLISH_FIELD</\1>',s,flags=re.S)
check(len(asg)==len(bsg)==247,None,'segment_count')
check(mask(a)==mask(b),None,'all_protected_bytes')
check(a.startswith(b'\xef\xbb\xbf')==b.startswith(b'\xef\xbb\xbf'),None,'BOM')
for x,y in zip(asg,bsg):
 sid=re.search(rb'\bid="([^"]+)"',x).group(1).decode()
 check(x[:x.index(b'>')+1]==y[:y.index(b'>')+1],sid,'all_segment_attributes')
 for k in ['band_he','he']:check(field(x,k)==field(y,k),sid,k+'_byte_equality')
 for k in ['en','band_en']:
  if decode(field(x,k)).strip():check(field(x,k)==field(y,k),sid,'prefilled_'+k)
 en=decode(field(y,'en'));be=decode(field(y,'band_en'));bh=decode(field(y,'band_he'))
 check(bool(en.strip()),sid,'en_filled');check(bool(be.strip()),sid,'band_en_filled')
 lem=re.findall('<lemma>(.*?)</lemma>',en,re.S)
 check(len(lem)==1,sid,'one_lemma');check(en.startswith('<lemma>'),sid,'lemma_position')
 check(len(lem)==1 and lem[0] in be,sid,'verbatim_lemma_in_band')
 check(not re.search('[\u0590-\u05ff]',be),sid,'no_hebrew_in_band')
 check('<fn' not in be,sid,'no_footnotes_in_band')
 check(bh.strip().startswith('…')==be.strip().startswith('…'),sid,'leading_ellipsis')
 check(bh.strip().endswith('…')==be.strip().endswith('…'),sid,'trailing_ellipsis')
 check(not re.search(r'\b(?:God|YHWH|Yahweh|Jehovah|Adonai)\b',en+' '+be,re.I),sid,'divine_name_rules')
 check(not re.search(r'\b(?:Senlake|Dicta|HE lemma|band)\b',en,re.I),sid,'no_workshop_notes')
 check(not re.search(r'\[(?:TODO|TBD|TRANSLATE|TRAKTAT|NR)\]',en+' '+be,re.I),sid,'no_placeholders')
 stack=[]
 for m in re.finditer(r'<(/?)([a-z]+)(?:\s[^>]*)?>',en):
  close,tag=m.groups()
  if tag=='br':continue
  check(tag in ['lemma','fn','b','i','small','sup'],sid,'supported_tag_'+tag)
  if close:
   check(bool(stack) and stack[-1]==tag,sid,'tag_order_'+tag)
   if stack:stack.pop()
  else:
   check(not(tag=='fn' and 'fn' in stack),sid,'no_nested_fn');stack.append(tag)
 check(not stack,sid,'tag_balance')
 rows.append({'segment_id':sid,'attributes_identical':True,'he_identical':True,'band_he_identical':True,'en_filled':bool(en.strip()),'band_en_filled':bool(be.strip()),'lemmas':len(lem),'lemma_verbatim':bool(lem and lem[0] in be)})
for tag in [b'he_title',b'en_title']:
 check(re.findall(rb'<'+tag+rb'>.*?</'+tag+rb'>',a,re.S)==re.findall(rb'<'+tag+rb'>.*?</'+tag+rb'>',b,re.S),None,tag.decode()+'_all_unchanged')
# Exact TSV–JSON correspondence, including explicitly scoped translation-only entries.
g=json.loads((ROOT/'glossary_he.json').read_text());tsv=list(csv.DictReader((ROOT/'Ben_Yehoyada_Megillah_GLOSSAR.tsv').open(),delimiter='\t'));scope=g['_meta']['megillah_band_01_translation']['contextual_abbreviations']
check(len(tsv)==289,None,'glossary_rows')
for r in tsv:
 v=g['abbreviations'].get(r['abbr']) or scope.get(r['abbr'])
 check(bool(v) and v['he']==r['hebrew'] and v['en']==r['english'],None,'glossary_match_'+r['abbr'])
report={'source_sha256':hashlib.sha256(a).hexdigest(),'final_sha256':hashlib.sha256(b).hexdigest(),'segments':len(bsg),'en_filled':sum(r['en_filled'] for r in rows),'band_en_filled':sum(r['band_en_filled'] for r in rows),'verbatim_lemmas':sum(r['lemma_verbatim'] for r in rows),'all_protected_bytes_identical':mask(a)==mask(b),'headings_he':len(re.findall(rb'<he_title>',a)),'headings_en':len(re.findall(rb'<en_title>',a)),'glossary_global_entries':len(g['abbreviations']),'glossary_scoped_entries':len(scope),'tsv_rows':len(tsv),'errors':errors,'per_segment':rows}
(ROOT/'Ben_Yehoyada_Megillah_Band_01_Strukturvergleich.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='per_segment'},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
