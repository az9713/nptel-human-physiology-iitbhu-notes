/* Original teaching model; synthetic coefficients, no patient calibration. */
(function(scope){'use strict';
function simulate(sensitivity=1,meal=30,duration=240,dt=.1){
if(![sensitivity,meal,duration,dt].every(Number.isFinite)||sensitivity<0||sensitivity>2||meal<0||meal>60||duration<0||duration>240||dt<=0||dt>.5)throw Error('input outside teaching domain');
let d=meal,b=9,liver=60,precursor=30,used=0,insulin=1,glucagon=1,t=0;const total=d+b+liver+precursor+used,rows=[];
while(true){const absorption=.03*d,storage=.003*insulin*b,release=.002*glucagon*liver,synthesis=.001*glucagon*precursor,utilization=(.008+.006*sensitivity*insulin)*b;
rows.push({t,gut:d,blood:b,liver,precursor,used,glucose:b/1.8,insulin,glucagon,absorption,storage,release,synthesis,utilization,residual:d+b+liver+precursor+used-total});if(t>=duration-1e-9)break;
const h=Math.min(dt,duration-t),it=.3+.35*Math.max(b-7,0),ct=1/(.3+.7*insulin);
d-=h*absorption;b+=h*(absorption+release+synthesis-storage-utilization);liver+=h*(storage-release);precursor-=h*synthesis;used+=h*utilization;insulin+=h*(it-insulin)/5;glucagon+=h*(ct-glucagon)/10;t=Math.min(duration,t+h);
}return rows;
}
scope.Ch09={simulate};})(typeof window==='undefined'?globalThis:window);
