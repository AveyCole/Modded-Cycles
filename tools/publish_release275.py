"""Publication2.75 : pins Full/Lite/Optional, recettes et cache coherent."""
from pathlib import Path
import argparse,json,hashlib,re,shutil,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from gen_governor_recovery_test import read
from sparse_loader_relocations import collect
p=argparse.ArgumentParser();p.add_argument('--assets-only',action='store_true');p.add_argument('--asset-commit');p.add_argument('--preview-root',type=Path);a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
def jread(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def jwrite(p,o):write(p,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def jsread(p):s=p.read_text(encoding='utf-8');return json.loads(s[s.index('=')+1:].strip().rstrip(';'))
def jswrite(p,name,o):write(p,'window.'+name+'='+json.dumps(o,ensure_ascii=False,separators=(',',':'))+';\n')
docroot=R/'docs'
if a.preview_root:
 docroot=a.preview_root.resolve()
 assert docroot!=R/'docs' and R not in docroot.parents
 for folder in ['flasher','flasher-optional','assets','guide','bugs']:shutil.copytree(R/'docs'/folder,docroot/folder,dirs_exist_ok=True)
 shutil.copyfile(R/'docs/index.html',docroot/'index.html')
site=docroot/'flasher';opt=docroot/'flasher-optional';main=jread(site/'BUILD.json');optional=jread(opt/'BUILD.json');entries={};metadata={}
for scope,ed in [('main','full'),('main','lite'),('optional','full'),('optional','lite')]:
 folder=R.parent/('control-all-latch-stock-screen-test/full' if (scope,ed)==('main','full') else 'release275/final/'+scope+'/'+ed)
 raw=next(folder.glob('*.syx')).read_bytes();m=jread(folder/'BUILD.json');assert sha(raw)==m['sha256']
 if (scope,ed)==('main','full'):assert sha(raw)=='9028789da5ca04f29a251a540c1fc83c52d1831d44cd4f2c74db3be830de2762'
 e=dict((main['editions'] if scope=='main' else optional['base_editions'])[ed]);name='Supermodel_'+('Optional_' if scope=='optional' else '')+ed.title()+'_2.75_'+sha(raw)[:12]+'.syx'
 (site/name).write_bytes(raw)
 e.update(release='2.75',file=name,syxSha256=sha(raw),mainOsSha=m['main_os_sha256'],startup_title=m['title_screen'],control_all_latch=True,stock_machine_punch=True,activity_masks=True,wizard_usb_main_independent=True,machine_confirmation=True,hardware_verified=False)
 entries[(scope,ed)]=e;metadata[(scope,ed)]=m
if a.assets_only:
 jwrite(site/'release275-assets.json',{'release':'2.75','editions':{scope:{ed:entries[(scope,ed)] for ed in ['full','lite']} for scope in ['main','optional']}});print('Prepared four pinned image assets');sys.exit(0)
assert a.preview_root or (a.asset_commit and re.fullmatch('[0-9a-f]{40}',a.asset_commit) and int(a.asset_commit,16)!=0)
# Les pages reutilisent le chargement verifie et les deux catalogues existants.
oldmain=main['stamp'];oldopt=optional['stamp'];stamp='2026-10-31-main275';ostamp='2026-10-31-optional275';guide='2026-10-31-guide275'
for root,old,new in [(site,oldmain,stamp),(opt,oldopt,ostamp)]:
 for f in root.iterdir():
  if f.is_file() and f.suffix in ['.html','.js','.md']:
   s=f.read_text(encoding='utf-8');s=s.replace(old,new).replace('2026-10-30-guide264',guide).replace('2026-10-29-md262','2026-10-31-md275').replace('8a10633b3ab20937a363ece8c9e36683d1e5efe3',a.asset_commit or '8a10633b3ab20937a363ece8c9e36683d1e5efe3')
   if f.suffix=='.html':s=s.replace('release-notes-2.64.html','release-notes-2.75.html')
   write(f,s)
main.update(stamp=stamp,release='2.75',editions={ed:entries[('main',ed)] for ed in ['full','lite']},fixed_image=entries[('main','full')]['file'],approved_source=entries[('main','full')]['file'],fixed_image_sha256=entries[('main','full')]['syxSha256'],main_os_sha256=entries[('main','full')]['mainOsSha'],startup_release_version='2.75',optional_release='2.75',release_notes='release-notes-2.75.html',guide_version=guide,asset_source_commit=a.asset_commit,delivery_source_commit=a.asset_commit,control_all_latch=True,stock_machine_punch=True,activity_masks=True,wizard_usb_main_independent=True,machine_confirmation=True)
main['fixed_image_legacy']=main['fixed_image']
optional.update(stamp=ostamp,release='2.75',base_editions={ed:entries[('optional',ed)] for ed in ['full','lite']},asset_source_commit=a.asset_commit,guide_version=guide,control_all_latch=True,stock_machine_punch=True,activity_masks=True,wizard_usb_main_independent=True,machine_confirmation=True)
loader=site/'fixed-main-image.js';s=loader.read_text(encoding='utf-8');start=s.index('const catalogue=')+len('const catalogue=');end=s.index(';',start);s=s[:start]+json.dumps(main['editions'],ensure_ascii=False,indent=2)+s[end:];write(loader,s)
jswrite(opt/'editions.js','MCOptionalBaseEditions',optional['base_editions'])
recipe=jread(R.parent/'release275/selection/manifest.json');recipe['source_release']='2.75';jswrite(opt/'recipe.js','MCOptionalRecipe',recipe);optional['recipe_sha256']=sha((opt/'recipe.js').read_bytes())
md=jsread(opt/'machinedrum-data.js');md.update(source_sha256=entries[('optional','full')]['syxSha256'],release='2.75',title=entries[('optional','full')]['startup_title'],title_edits=[])
source=read(site/entries[('optional','full')]['file'])[2];md['base_loader_relocations']=collect(source,metadata[('optional','full')]);jswrite(opt/'machinedrum-data.js','MCOptionalMDData',md)
changes=[{'en':'Double-tap TRACK to latch CTRL-ALL parameter edits. Press TRACK once or BACK to exit. Track and trig selection remain momentary.','fr':'Double tap TRACK pour verrouiller les editions CTRL-ALL. TRACK ou BACK quitte. Selection des pistes et trigs momentanee.'},{'en':'Machine browsing uses the stock screen. Global > Mac selects Sil (press DATA to commit) or Stk (apply while browsing). Full, Lite and Machine Optional share the activity masks, stock-machine PUNCH handling and independent Sample Wizard USB outputs.','fr':'Parcours des machines avec affichage natif. Global > Mac : Sil (clic DATA pour valider) ou Stk (application pendant le parcours). Full, Lite et Optional partagent les masques d activite, PUNCH stock et les sorties USB Wizard independantes.'}]
for f in [docroot/'assets/release.js',site/'midi-machine-release.js',opt/'release.js']:
 history=jsread(f);history=[x for x in history if x['version']!='2.75'];history.insert(0,dict(version='2.75',date='2026-10-31',changes=changes));jswrite(f,'MC_RELEASES',history)
jwrite(site/'BUILD.json',main);jwrite(opt/'BUILD.json',optional)
html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Supermodel2.75</title><style>body{max-width:760px;margin:3rem auto;padding:0 1rem;font:18px/1.6 system-ui}h1{line-height:1.2}</style><a href="./">Flasher</a><h1>Supermodel2.75</h1>'
for c in changes:html+='<p>'+c['en']+'</p><p lang="fr">'+c['fr']+'</p>'
html+='<p>Optional keeps its extra machine choices. Hardware coverage varies by combination.</p><p><a href="shortcut-guide.html">Feature and shortcut guide</a></p></html>'
write(site/'release-notes-2.75.html',html)
for f in [docroot/'index.html',opt/'README.md']+([] if a.preview_root else [R/'README.md']):
 s=f.read_text(encoding='utf-8').replace('2.64','2.75').replace('2026-10-30-guide264',guide);write(f,s)
print('Prepared local preview2.75' if a.preview_root else 'Published metadata, exact assets, recipes, releases and stamps2.75')
