"use strict";

const slides = [...document.querySelectorAll(".deck-slide")];
const previous = document.querySelector("#previous");
const next = document.querySelector("#next");
const select = document.querySelector("#slide-select");
const status = document.querySelector("#slide-status");
let current = 0;

function showSlide(index, focus = false) {
  current = Math.max(0, Math.min(slides.length - 1, index));
  for (const [number, slide] of slides.entries()) slide.hidden = number !== current;
  previous.disabled = current === 0;
  next.disabled = current === slides.length - 1;
  select.value = slides[current].id;
  const title = slides[current].querySelector("h1, h2");
  status.textContent = `第 ${current + 1} 頁，共 ${slides.length} 頁：${title.textContent}`;
  history.replaceState(null, "", `#${slides[current].id}`);
  if (focus) {
    title.focus({ preventScroll: true });
    slides[current].scrollIntoView({ block: "start" });
  }
}

function readHash() {
  const index = slides.findIndex(slide => `#${slide.id}` === location.hash);
  showSlide(index < 0 ? 0 : index);
}

previous.addEventListener("click", () => showSlide(current - 1, true));
next.addEventListener("click", () => showSlide(current + 1, true));
select.addEventListener("change", () => showSlide(slides.findIndex(slide => slide.id === select.value), true));
document.addEventListener("keydown", event => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target.closest("input, textarea, select, button, a, [contenteditable]")) return;
  const target = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 }[event.key];
  if (target === undefined) return;
  event.preventDefault();
  showSlide(target, true);
});
window.addEventListener("hashchange", readHash);
document.querySelector(".deck-controls").hidden = false;
readHash();
