"use strict";

const form = document.querySelector("#wiki-search");
const input = document.querySelector("#wiki-query");
const passages = [...document.querySelectorAll("[data-passage]")];
const list = document.querySelector(".passage-list");
const count = document.querySelector("#wiki-count");
const gap = document.querySelector("#wiki-gap");

function tokens(text) {
  const normalized = text.normalize("NFKC").toLowerCase();
  const terms = normalized.match(/[a-z0-9]+/gu) || [];
  for (const run of normalized.match(/[\u3400-\u9fff]+/gu) || []) {
    for (let i = 0; i < Math.max(1, run.length - 1); i++) terms.push(run.slice(i, i + 2));
  }
  return [...new Set(terms)];
}

function search() {
  const terms = tokens(input.value);
  let shown = 0;
  const ranked = passages.map((passage, index) => {
    const text = passage.dataset.text.normalize("NFKC").toLowerCase();
    const score = terms.filter(term => text.includes(term)).length;
    passage.hidden = terms.length > 0 && score === 0;
    if (!passage.hidden) shown++;
    return { passage, score, index };
  }).sort((a, b) => b.score - a.score || a.index - b.index);
  for (const { passage } of ranked) list.append(passage);
  count.textContent = `${shown} 個段落`;
  gap.hidden = shown !== 0;
}

form.addEventListener("submit", event => { event.preventDefault(); search(); });
input.addEventListener("input", search);
form.hidden = false;
search();
