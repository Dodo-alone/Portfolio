document.querySelectorAll('.shot[data-src]').forEach((slot) => {
  const img = new Image();
  img.alt = slot.dataset.alt || slot.textContent.trim();
  // no loading="lazy" here - a detached lazy image never starts loading
  img.decoding = 'async';
  img.onload = () => {
    slot.textContent = '';
    slot.appendChild(img);
    slot.classList.add('has-img');
  };
  img.src = slot.dataset.src;
});

// Title decode effect
(() => {
  try {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  } catch (e) { /* don't care */ }
  const glyphs = '!<>-_|\\/[]{}=+%&$*^?#01';
  const noise = () => glyphs[Math.floor(Math.random() * glyphs.length)];
  document.querySelectorAll('.decode').forEach((el, i) => {
    const node = el.firstChild;
    if (!node || node.nodeType !== 3) return;
    const final = node.nodeValue;
    const delay = 150 + i * 110;
    const dur = 500 + final.length * 30;
    let start = null;
    node.nodeValue = final.replace(/\S/g, noise);
    const tick = (now) => {
      if (start === null) start = now + delay;
      const t = Math.max(0, Math.min(1, (now - start) / dur));
      const shown = Math.floor(t * final.length);
      let out = '';
      for (let k = 0; k < final.length; k++) {
        const c = final[k];
        out += (k < shown || c === ' ') ? c : noise();
      }
      node.nodeValue = out;
      if (t < 1) requestAnimationFrame(tick);
      else node.nodeValue = final;
    };
    requestAnimationFrame(tick);
  });
})();
