"""Compare an original master with its translated copy without altering either.
Usage: python3 english_audit.py ORIGINAL TRANSLATED [OUTPUT_JSON]
Exit 0: all checks pass; exit 1: findings. Python standard library only.
"""
import sys,re,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
original,translated=map(lambda p:Path(p).read_bytes(),sys.argv[1:3])
def strip_targets(b):
 return re.sub(rb'(<(?:en|band_en)><!\[CDATA\[).*?(\]\]></(?:en|band_en)>)',lambda m:m[1]+m[2],b,flags=re.S)
def parse(b):
 ET.fromstring(b.decode('utf-8-sig'))
 result=[]
 for m in re.finditer(rb'<segment\b([^>]*)>(.*?)</segment>',b,re.S):
  d={'attrs':m[1]}
  d['id']=re.search(rb'\bid="([^"]+)"',m[1])[1].decode()
  for tag in ['he','band_he','en','band_en']:
   d[tag]=re.search(rb'<'+tag.encode()+rb'><!\[CDATA\[(.*?)\]\]></'+tag.encode()+rb'>',m[2],re.S)[1].decode()
  result.append(d)
 return result
old,new=parse(original),parse(translated)
findings=[]
def bad(sid,code,text):findings.append({'id':sid,'code':code,'detail':text})
if strip_targets(original)!=strip_targets(translated):bad('-','protected_bytes','Bytes outside English field contents differ.')
if [d['id'] for d in old]!=[d['id'] for d in new]:bad('-','id_order','ID order/count differs.')
if len({d['id'] for d in new})!=len(new):bad('-','duplicate_ids','Duplicate IDs.')
for a,b in zip(old,new):
 sid=a['id']
 for tag in ['en','band_en']:
  if a[tag].strip() and a[tag]!=b[tag]:bad(sid,'prefilled_english',tag)
  if not b[tag].strip():bad(sid,'empty_target',tag)
 be=b['band_en'];en=b['en'];bh=a['band_he'].strip()
 if re.search(r'[\u0590-\u05ff]|<fn\b',be):bad(sid,'band_forbidden','Hebrew or footnote in band_en.')
 if bh.startswith('…') and not be.strip().startswith('…'):bad(sid,'leading_ellipsis','Missing.')
 if bh.endswith('…') and not be.strip().endswith('…'):bad(sid,'trailing_ellipsis','Missing.')
 lemmas=re.findall(r'<lemma>(.*?)</lemma>',en,re.S)
 expected=len(re.findall(r'<lemma>',a['he']))
 if len(lemmas)!=expected:bad(sid,'lemma_count',str(len(lemmas)))
 if a['he'].startswith('<lemma>') and not en.startswith('<lemma>'):bad(sid,'lemma_position','Not at start.')
 for l in lemmas:
  if l not in be:bad(sid,'lemma_band_mismatch',l)
 if re.search(r'\b(?:YHWH|Yahweh|Jehovah|Adonai|God)\b|Bible:|Tanach:|```|\[TRAKTAT\]|\[NR\]',en+' '+be,re.I):bad(sid,'forbidden_english','Forbidden spelling or placeholder.')
 for tag in ['en','band_en']:
  stack=[]
  for m in re.finditer(r'<(/?)(\w+)\s*(/?)>',b[tag]):
   close,name,selfclose=m.groups()
   if name=='br':continue
   if name not in {'lemma','fn','b','i','small','sup'}:bad(sid,'unknown_tag',name)
   if close:
    if not stack or stack.pop()!=name:bad(sid,'tag_balance',name)
   elif not selfclose:
    if name=='fn' and name in stack:bad(sid,'nested_footnote','fn')
    stack.append(name)
  if stack:bad(sid,'unclosed_tags',str(stack))
result={'original_sha256':hashlib.sha256(original).hexdigest(),'translated_sha256':hashlib.sha256(translated).hexdigest(),'segments':len(new),'filled_en':sum(bool(d['en'].strip()) for d in new),'filled_band_en':sum(bool(d['band_en'].strip()) for d in new),'protected_bytes_equal':strip_targets(original)==strip_targets(translated),'findings':findings,'exit_code':int(bool(findings))}
payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
if len(sys.argv)>3:Path(sys.argv[3]).write_text(payload)
print(payload)
sys.exit(result['exit_code'])
