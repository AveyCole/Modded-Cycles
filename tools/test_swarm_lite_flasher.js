// Note 106 : builds gardes, choix SY et mode lite facultatif.
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');process.env.RETROSYN_PAGE='docs/flasher-sy-load-test';
const {open,change}=require('./test_retrosyn_flasher'),out=path.resolve(__dirname,'../build/swarm-lite');fs.mkdirSync(out,{recursive:true});
const raw=Uint8Array.from(fs.readFileSync(path.resolve(__dirname,'../firmware/model-cycles_OS1.13.syx'))),st=Uint8Array.from(fs.readFileSync(path.resolve(__dirname,'../firmware/Syntakt_OS1.42.syx')));
(async()=>{const only=process.argv[2],rows=only?JSON.parse(fs.readFileSync(path.join(out,'cases.json'))).filter(r=>r.name!==only):[];for(const p of [{name:'all-midi-off',midi:true},{name:'all-no-midi-off'},{name:'all-midi-meter',midi:true,meter:true},{name:'all-midi-lite',midi:true,lite:true,meter:true},{name:'all-no-midi-lite',lite:true,meter:true},{name:'all-no-midi-lite-no-wizard',lite:true,meter:true,noWizard:true},...['toy','bits','swarm'].flatMap(code=>[{name:code+'-off',code},{name:code+'-exact',code,exact:true}])]){
 if(only&&p.name!==only)continue;const {w,errors}=open();await new Promise(r=>setTimeout(r,40));try{
 w.document.getElementById('select-all').click();change(w,'swarm-lite',false);change(w,'sy-load-opt',false);change(w,'sy-load-meter',false);change(w,'midi-out-bank',!!p.midi);
 if(p.code){w.document.getElementById('super-clear').click();change(w,'syntakt',true);change(w,'track-filter',true);change(w,'control-all-beat-repeat',true);}if(p.code)for(const code of ['sd','cp','toy','bits','swarm']){const el=w.document.getElementById('eng-'+code);el.checked=code===p.code;el.dispatchEvent(new w.Event('change',{bubbles:true}));}
 if(p.noWizard)change(w,'sample-wizard',false);if(p.meter)change(w,'sy-load-meter',true);if(p.lite)change(w,'swarm-lite',true);else if(p.exact)change(w,'sy-load-opt',true);
 const result=w.MCMidiBankCompose(w.MCFlasherApp.chosenTweaks(),raw,st),built=w.MCBuilder.build(raw,w.MC_TWEAKS.device,result.tweaks,{syntakt:st,refMods:result.refMods});assert(built.modsChecked);assert(w.MCFlasher.verify(built.raw).count>0);assert.equal(errors.length,0,errors.join('\n'));
 if(p.name==='all-midi-off')assert.equal(built.mainOsSha,'2b7768d44d33b9bdcfec1b52f7cabbd6bd738693b93e1107b62ee5ea39dae766');
 if(p.name==='all-no-midi-off')assert.equal(built.mainOsSha,'a9c4fa7f6c6ac4c233050f758ad8a804aa561750da613e4750805be18789a132');
 if(p.lite)assert.equal(w.MCSyLoadApplied,6);
 fs.writeFileSync(path.join(out,p.name+'.json'),JSON.stringify({tweaks:result.tweaks,mainOsSha:built.mainOsSha}));fs.writeFileSync(path.join(out,p.name+'.syx'),built.raw);rows.push({name:p.name,sha:built.mainOsSha,edits:w.MCSyLoadApplied||0});console.log('PASS SY build',p.name,built.mainOsSha,'edits',w.MCSyLoadApplied||0);
 }finally{w.close();}
}fs.writeFileSync(path.join(out,'cases.json'),JSON.stringify(rows));})().catch(e=>{console.error(e.stack);process.exitCode=1});
