/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

function initFeatureFlipCards() {
  const cards = document.querySelectorAll(
    ".feature-flip-card:not([data-flip-ready])",
  );

  cards.forEach((card) => {
    card.dataset.flipReady = "true";
    card.setAttribute("role", "button");
    card.setAttribute("aria-pressed", "false");

    const setFlipped = (flipped) => {
      card.classList.toggle("is-flipped", flipped);
      card.setAttribute("aria-pressed", flipped ? "true" : "false");
      card.classList.toggle("is-unflipping", !flipped);
    };

    const toggle = () => {
      setFlipped(!card.classList.contains("is-flipped"));
    };

    const isInteractiveTarget = (target) =>
      Boolean(
        target instanceof Element &&
          target.closest("a, .feature-flip-hint"),
      );

    card.addEventListener("click", (event) => {
      if (isInteractiveTarget(event.target)) {
        return;
      }
      toggle();
    });

    card.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }
      if (isInteractiveTarget(event.target)) {
        return;
      }
      event.preventDefault();
      toggle();
    });

    card.addEventListener("mouseleave", () => {
      card.classList.remove("is-unflipping");
    });
  });
}

initFeatureFlipCards();

if (typeof window.document$ !== "undefined") {
  window.document$.subscribe(initFeatureFlipCards);
}
