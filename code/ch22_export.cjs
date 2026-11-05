'use strict';
const fs=require('fs'),path=require('path'),a=require('../assets/ch22-model.js'),root=path.resolve(__dirname,'..');
for(const mode of ['route','reflex'])fs.writeFileSync(path.join(root,'assets/ch22-'+mode+'.svg'),a.render(100,mode));
fs.writeFileSync(path.join(root,'assets/ch22-pathway-states.json'),JSON.stringify({scope:'Original presentation clock and synthetic constant-delay example; not observed kinetics',parameters:a.defaults,arrivals:a.latency(),frames:Array.from({length:101},(_,t)=>a.state(t,'reflex'))},null,2)+'\n');
