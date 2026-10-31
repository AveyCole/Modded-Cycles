/* 2026-10-31-main275 : images verifiees par edition, caches et sources independants. */
(()=>{
 "use strict";
 const catalogue={
  "full": {
    "id": "full",
    "productName": "Supermodel",
    "release": "2.75",
    "file": "Supermodel_Full_2.75_9028789da5ca.syx",
    "syxSha256": "9028789da5ca04f29a251a540c1fc83c52d1831d44cd4f2c74db3be830de2762",
    "mainOsSha": "4f2ab61b343df86fce8de3d7ae56f7fc1e1fbe2e69d0853073eee0aae79454c4",
    "requiresSyntakt": true,
    "source_build": 215,
    "new_clear_filter_defaults": true,
    "ui_idle_saves": true,
    "hardware_verified": false,
    "status": "experimental",
    "per_track_fx": true,
    "inactive_fx_zero_bypass": true,
    "startup_title": {
      "name": "Supermodel",
      "version": "2.75",
      "edition": "2.75",
      "code": 1074084460,
      "code_bytes": 794,
      "sha256": "003d2623f06d4d85f5afce0bb9a83c91d060da61f458bdb64c09b244ca5db610",
      "native_os_protocol_version_unchanged": true,
      "hardware_tested": false
    },
    "legacy_removed": true,
    "vinyl_removed": true,
    "chordkeys_removed": true,
    "unique_machine_punch": true,
    "unassigned_secondary_lfos_pause": true,
    "filter_deferred_new_sound_low": true,
    "double_stop_fx_reset": true,
    "per_track_fx_code_bytes": 60238,
    "acid_envelope_global": true,
    "acid_envelope_modes": [
      "A",
      "F",
      "AF"
    ],
    "acid_envelope_default": "F",
    "pots_delay": true,
    "delay_selector_order": [
      "PHASER",
      "DUCK",
      "DUB",
      "POTS",
      "PING PONG",
      "DELAY",
      "CRUSH 1",
      "CRUSH 2"
    ],
    "direct_pattern_jump": true,
    "trig_select": true,
    "track_selection_momentary": true,
    "wizard_plock_priority": true,
    "song_mode": true,
    "acid_articulation": true,
    "acid_arp_retrigger": true,
    "control_all_latch": true,
    "stock_machine_punch": true,
    "activity_masks": true,
    "wizard_usb_main_independent": true,
    "machine_confirmation": true
  },
  "lite": {
    "id": "lite",
    "productName": "Supermodel Lite",
    "release": "2.75",
    "file": "Supermodel_Lite_2.75_583082a68cfe.syx",
    "syxSha256": "583082a68cfef346ba4bb236fe19b4f8a2e3983a8e1956af4604a8430082682f",
    "mainOsSha": "a29e13fe4f56f2bde2b4ba963235953bbb7e35cf9c41cb9787279d2314f9b90b",
    "requiresSyntakt": false,
    "source_build": 216,
    "new_clear_filter_defaults": true,
    "ui_idle_saves": true,
    "hardware_verified": false,
    "status": "experimental",
    "per_track_fx": true,
    "inactive_fx_zero_bypass": true,
    "startup_title": {
      "name": "Supermodel Lite",
      "version": "2.75",
      "edition": "LITE 2.75",
      "code": 1074084460,
      "code_bytes": 856,
      "sha256": "ccf54172e3c0aca18ad24a987c5e4c4a683fd8741647c44359dbd573381132f1",
      "native_os_protocol_version_unchanged": true,
      "hardware_tested": false
    },
    "legacy_removed": true,
    "vinyl_removed": true,
    "chordkeys_removed": true,
    "unique_machine_punch": true,
    "unassigned_secondary_lfos_pause": true,
    "filter_deferred_new_sound_low": true,
    "double_stop_fx_reset": true,
    "per_track_fx_code_bytes": 43766,
    "acid_envelope_global": false,
    "pots_delay": true,
    "delay_selector_order": [
      "PHASER",
      "DUCK",
      "DUB",
      "POTS",
      "PING PONG",
      "DELAY",
      "CRUSH 1",
      "CRUSH 2"
    ],
    "direct_pattern_jump": true,
    "trig_select": true,
    "track_selection_momentary": true,
    "wizard_plock_priority": true,
    "song_mode": true,
    "acid_articulation": false,
    "acid_arp_retrigger": false,
    "control_all_latch": true,
    "stock_machine_punch": true,
    "activity_masks": true,
    "wizard_usb_main_independent": true,
    "machine_confirmation": true
  }
};
 for(const meta of Object.values(catalogue))Object.freeze(meta);
 Object.freeze(catalogue);
 const pending=new Map();
 async function load(meta){
  const sources=[new URL(meta.file,window.location.href).href,
   "https://raw.githubusercontent.com/AveyCole/Supermodel/e29cc9bbd09ccd2ee0a5bdce556d12dfdd41c954/docs/flasher/"+meta.file];
  let failure;
  for(const url of sources)try{
   const response=await fetch(url,{cache:"no-store"});
   if(!response.ok)throw new Error("Verified main firmware image could not be loaded");
   const raw=new Uint8Array(await response.arrayBuffer());
   if(window.MCBuilder.hex(window.MCBuilder.sha256(raw))!==meta.syxSha256)throw new Error("Verified main firmware image checksum mismatch");
   const checked=window.MCFlasher.verify(raw);
   if(!checked.count)throw new Error("Verified main firmware image has no valid SYX packets");
   return raw;
  }catch(error){failure=error}
  throw failure;
 }
 function get(edition="full"){
  const meta=catalogue[edition];
  if(!meta)return Promise.reject(new Error("Unknown firmware edition"));
  if(!pending.has(edition))pending.set(edition,load(meta).catch(error=>{pending.delete(edition);throw error}));
  return pending.get(edition).then(raw=>raw.slice());
 }
 window.MCFirmwareImages=catalogue;
 window.MCFirmwareImageLoad=get;
 window.MCFirmwareEdition="full";
 window.MCFixedMainImageMeta=catalogue.full;
 window.MCFixedMainImageLoad=()=>get("full");
 window.MCFixedMainImageReady=get("full");
 window.MCFixedMainImageReady.catch(()=>{});
})();
