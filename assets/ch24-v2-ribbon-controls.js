/* Sizing and playback rate only; source frames remain unchanged. */
(() => {
  'use strict';
  document.querySelectorAll('button[data-size]').forEach(button => {
    button.addEventListener('click', () => {
      const video = document.getElementById(button.dataset.target);
      const player = video.closest('.player');
      player.classList.toggle('native-mode', button.dataset.size === 'native');
      if (button.dataset.size === 'fit') { player.scrollLeft = 0; player.scrollTop = 0; }
      player.focus();
    });
  });
  document.querySelectorAll('select[data-rate]').forEach(select => {
    select.addEventListener('change', () => {
      document.getElementById(select.dataset.rate).playbackRate = Number(select.value);
    });
  });
  const rotation = document.getElementById('ribbon-space-video');
  const group = rotation?.closest('.player')?.nextElementSibling;
  const help = group?.classList.contains('observed-video-controls')
    ? group.querySelector('.observed-video-help') : null;
  if (help) help.textContent = 'Steps inspect 0.5 seconds of the published camera rotation and pause playback. This spatial reconstruction is not a physiological time series.';
})();
