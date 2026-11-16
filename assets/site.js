"use strict";

const query = document.querySelector("#query");
const filters = [...document.querySelectorAll("button[data-filter]")];
const cards = [...document.querySelectorAll("[data-search]")];
const count = document.querySelector("#result-count");
const empty = document.querySelector("#no-results");
let category = "";

function normalize(text) {
  return text.normalize("NFKC").toLowerCase();
}

function updateResults() {
  const terms = normalize(query.value).trim().split(/\s+/u).filter(Boolean);
  let shown = 0;
  for (const card of cards) {
    const text = normalize(card.dataset.search);
    const matches = (!category || card.dataset.category === category)
      && terms.every(term => text.includes(term));
    card.hidden = !matches;
    shown += Number(matches);
  }
  count.textContent = `${shown} 篇文章`;
  empty.hidden = shown !== 0;
}

for (const button of filters) {
  button.addEventListener("click", () => {
    category = button.dataset.filter;
    for (const filter of filters) {
      filter.setAttribute("aria-pressed", String(filter === button));
    }
    updateResults();
  });
}

query.addEventListener("input", updateResults);
document.querySelector(".search").hidden = false;
document.querySelector(".filter-bar").hidden = false;
updateResults();
