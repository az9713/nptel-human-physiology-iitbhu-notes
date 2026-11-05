/* Original synthetic teaching accounting, no patient or device calibration. */
(function(scope){
'use strict';
function finite(x, name){if(!Number.isFinite(x))throw Error(name+' must be finite');}
function range(x,lo,hi,name){finite(x,name);if(x<lo||x>hi)throw Error(name+' out of range');}
function volumes(vt=.5,irv=3,erv=1.1,rv=1.2){[vt,irv,erv,rv].forEach(x=>range(x,0,20,'volume'));return {vt,irv,erv,rv,ic:vt+irv,frc:erv+rv,vc:vt+irv+erv,tlc:vt+irv+erv+rv};}
function lung(phase,vt=.5){range(phase,0,1,'phase');const v=volumes(vt);let value;if(phase<.4)value=v.frc+v.vt*(1-Math.cos(phase/.4*6*Math.PI))/2;else if(phase<.6)value=v.frc+(v.tlc-v.frc)*(phase-.4)/.2;else if(phase<.8)value=v.tlc-(v.tlc-v.rv)*(phase-.6)/.2;else value=v.rv+(v.frc-v.rv)*(phase-.8)/.2;return {...v,value};}
function content(hb,sat,p,k=1.31,unit='mmHg'){range(hb,0,30,'Hb');range(sat,0,1,'saturation');range(p,0,1000,'pressure');range(k,0,2,'capacity coefficient');if(!['mmHg','kPa'].includes(unit))throw Error('pressure unit');let alpha=unit==='mmHg'?.003:.003*7.500616827;return {bound:k*hb*sat,dissolved:alpha*p,total:k*hb*sat+alpha*p};}
function balance(ca,cv,q){range(ca,0,100,'arterial content');range(cv,0,ca,'venous content');range(q,0,100,'flow');return {delivery:10*q*ca,consumption:10*q*(ca-cv),returned:10*q*cv,extraction:ca>0&&q>0?(ca-cv)/ca:null};}
function optical(acRed,dcRed,acIR,dcIR){[acRed,dcRed,acIR,dcIR].forEach(x=>{finite(x,'signal');if(x<=0)throw Error('signal must be positive');});return {r:(acRed/dcRed)/(acIR/dcIR),illustrativePercent:130-30*((acRed/dcRed)/(acIR/dcIR))};}
function occupancy(co,functional=.98){range(co,0,1,'CO fraction');range(functional,0,1,'functional saturation');return {co,oxy:(1-co)*functional,deoxy:(1-co)*(1-functional)};}
scope.Ch08={volumes,lung,content,balance,optical,occupancy};
})(typeof window==='undefined'?globalThis:window);
