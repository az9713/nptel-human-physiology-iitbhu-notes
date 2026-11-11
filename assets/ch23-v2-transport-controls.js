/* Display controls only; original source frames and their source clocks are unchanged. */
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
})();
