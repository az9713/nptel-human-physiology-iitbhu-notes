/* Source-coordinate NET-transfer illustration. No diffusion kinetics or molar flux. */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory;
  else root.GasTransferModel = factory(root.d3);
})(typeof window === 'object' ? window : this, function (d3) {
  'use strict';
  if (!d3 || typeof d3.interpolateNumber !== 'function') throw Error('Local D3 interpolation library missing');
  const duration = 8;
  const presets = Object.freeze({
    o2: Object.freeze({loading:[100,40],equal:[40,40],reversed:[40,100]}),
    co2: Object.freeze({loading:[40,46],equal:[40,40],reversed:[46,40]})
  });
  function validatePressures(value) {
    if (!value || !['o2','co2'].every(g => Array.isArray(value[g]) && value[g].length === 2 && value[g].every(x => typeof x === 'number' && Number.isFinite(x) && x >= 0))) {
      throw new TypeError('Each gas needs two finite, nonnegative pressures: [air, blood] in mmHg.');
    }
    return {o2:value.o2.slice(),co2:value.co2.slice()};
  }
  function position(progress, start, middle, end) {
    return progress <= .5 ? d3.interpolateNumber(start,middle)(2*progress) : d3.interpolateNumber(middle,end)(2*progress-1);
  }
  function gasState(gas, progress, pair) {
    const delta = pair[0]-pair[1];
    const sign = Math.sign(delta);
    const air = gas === 'o2' ? 390 : 430;
    const blood = gas === 'o2' ? 165 : 180;
    const middle = gas === 'o2' ? 240 : 350;
    const start = sign >= 0 ? air : blood;
    const end = sign >= 0 ? blood : air;
    return {
      gas, airPressure:pair[0], bloodPressure:pair[1], delta, sign,
      direction:sign > 0 ? 'air → blood' : sign < 0 ? 'blood → air' : 'no net transfer',
      equilibriumText:sign !== 0 ? '' : pair[0] === 0 ? 'Gas absent at the specified boundaries; no net transfer.' : 'No net transfer; microscopic exchange continues.',
      visible:sign !== 0, x:gas === 'o2' ? 180 : 330,
      y:position(progress,start,middle,end), start, middle, end,
      path:`M${gas === 'o2' ? 180 : 330} ${start}V${end}`
    };
  }
  function computeState(seconds, pressures) {
    if (typeof seconds !== 'number' || !Number.isFinite(seconds)) throw TypeError('Presentation time must be finite.');
    const values = validatePressures(pressures);
    const time = Math.max(0,Math.min(duration,seconds));
    const progress = time/duration;
    const o2 = gasState('o2',progress,values.o2), co2 = gasState('co2',progress,values.co2);
    const phase = !o2.visible && !co2.visible ? (values.o2[0] > 0 && values.co2[0] > 0 ? 'No net transfer; microscopic exchange continues' : 'No net transfer; see the separate gas conditions') : progress === 0 ? 'Starting compartments' : progress === .5 ? 'Within the barrier: illustration keyframe' : progress === 1 ? 'Receiving compartments: illustration complete' : 'Transfer illustration in progress';
    return {time,progress,duration,phase,o2,co2};
  }
  return Object.freeze({duration,presets,validatePressures,computeState});
});
