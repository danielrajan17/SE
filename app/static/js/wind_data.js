/**
 * wind_data.js — Wind particle layer for CycloneOPS PRO
 * Manages canvas-based wind streamline animation.
 */

const WindLayer = (() => {
  let canvas, ctx, animId;
  let particles = [];
  let active    = true;
  let color     = "#ffb400";
  const COUNT   = 200;

  function init() {
    canvas = document.getElementById("windCanvas");
    ctx    = canvas.getContext("2d");
    resize();
    window.addEventListener("resize", resize);
    spawnAll();
    loop();
  }

  function resize() {
    if (!canvas) return;
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function spawn(p) {
    p.x      = Math.random() * canvas.width;
    p.y      = Math.random() * canvas.height;
    p.age    = 0;
    p.maxAge = 80 + Math.random() * 120;
    p.speed  = 0.5 + Math.random() * 0.9;
    p.angle  = Math.PI * 0.25 + (Math.random() - 0.5) * 0.7; // NE→SW bias
    p.len    = 2 + Math.random() * 4;
  }

  function spawnAll() {
    particles = Array.from({ length: COUNT }, () => {
      const p = {};
      spawn(p);
      p.age = Math.random() * p.maxAge; // stagger
      return p;
    });
  }

  function loop() {
    if (!active) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      animId = requestAnimationFrame(loop);
      return;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
      p.x += Math.cos(p.angle) * p.speed * 1.6;
      p.y += Math.sin(p.angle) * p.speed * 1.6;
      p.age++;

      if (
        p.age > p.maxAge ||
        p.x < -10 || p.x > canvas.width + 10 ||
        p.y < -10 || p.y > canvas.height + 10
      ) {
        spawn(p);
        return;
      }

      const alpha = Math.sin((p.age / p.maxAge) * Math.PI) * 0.45;
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(
        p.x - Math.cos(p.angle) * p.len * p.speed * 3.5,
        p.y - Math.sin(p.angle) * p.len * p.speed * 3.5
      );
      ctx.strokeStyle = color;
      ctx.globalAlpha = alpha;
      ctx.lineWidth   = 1.2;
      ctx.stroke();
    });

    ctx.globalAlpha = 1;
    animId = requestAnimationFrame(loop);
  }

  return {
    init,
    setActive(flag) { active = !!flag; },
    setColor(c)     { color = c; spawnAll(); },
    isActive()      { return active; },
  };
})();
