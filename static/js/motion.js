document.addEventListener("DOMContentLoaded", () => {
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  if (!motion.matches && finePointer.matches) {
    document.querySelectorAll("[data-tilt]").forEach((card) => {
      let frame = 0;
      card.addEventListener("pointermove", (event) => {
        if (motion.matches || document.hidden || frame) return;
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        frame = requestAnimationFrame(() => {
          card.style.transform = `perspective(900px) rotateX(${-y * 6}deg) rotateY(${x * 6}deg) translateY(-3px)`;
          frame = 0;
        });
      });
      card.addEventListener("pointerleave", () => {
        if (frame) cancelAnimationFrame(frame);
        frame = 0;
        card.style.transform = "";
      });
      motion.addEventListener("change", () => { if (motion.matches) card.style.transform = ""; });
    });
  }
});
