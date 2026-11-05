/* Export static equivalents from exactly the controlled-view renderer/data. */
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),R=require('../assets/ch25-render.js');
const data=JSON.parse(fs.readFileSync(path.join(root,'assets/ch25-data.json'),'utf8'));
for(const [mode,index] of [['barrier',80],['recycling',40],['photo',80],['field',50],['conduction',125]])
 fs.writeFileSync(path.join(root,`assets/ch25-${mode}.svg`),R.render(mode,index,data));
fs.writeFileSync(path.join(root,'assets/ch25-eye-ear.svg'),R.context());
console.log('Exported six static reconstructions from shared renderer');
