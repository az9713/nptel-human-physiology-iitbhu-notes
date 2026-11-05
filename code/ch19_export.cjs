// Static source views use the exact browser renderer; no separate drawing implementation.
const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'..');
const m=require(path.join(root,'assets/ch19-model.js'));
for(const [file,bytes] of [['ch19-stages.svg',m.stageSVG(3)],['ch19-cycle.svg',m.cycleSVG(13)],['ch19-lactation.svg',m.lactationSVG(5,'both')]]) fs.writeFileSync(path.join(root,'assets',file),bytes);
