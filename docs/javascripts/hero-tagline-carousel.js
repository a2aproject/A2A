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

function initHeroTaglineCarousels() {
  const carousels = document.querySelectorAll(
    ".hero-tagline-carousel:not([data-ready])",
  );
  if (!carousels.length) {
    return;
  }

  carousels.forEach((carousel) => {
    carousel.dataset.ready = "true";

    const slides = Array.from(carousel.querySelectorAll(".hero-tagline"));
    if (slides.length < 2) {
      return;
    }

    const interval = Number.parseInt(carousel.dataset.interval || "6000", 10);
    let activeIndex = 0;

    const dotsContainer = document.createElement("div");
    dotsContainer.className = "hero-tagline-dots";
    dotsContainer.setAttribute("role", "tablist");
    dotsContainer.setAttribute("aria-label", "Select tagline");

    const dots = slides.map((_, dotIndex) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "hero-tagline-dot";
      dot.setAttribute("role", "tab");
      dot.setAttribute(
        "aria-label",
        `Tagline ${dotIndex + 1} of ${slides.length}`,
      );
      dot.addEventListener("click", () => {
        updateDots(dotIndex);
      });
      dotsContainer.appendChild(dot);
      return dot;
    });

    carousel.appendChild(dotsContainer);

    function updateDots(index) {
      activeIndex = index;
      dots.forEach((dot, dotIndex) => {
        const isActive = dotIndex === activeIndex;
        dot.classList.toggle("is-active", isActive);
        dot.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }

    updateDots(0);
    window.setInterval(() => {
      updateDots((activeIndex + 1) % slides.length);
    }, interval);
  });
}

initHeroTaglineCarousels();

if (typeof window.document$ !== "undefined") {
  window.document$.subscribe(initHeroTaglineCarousels);
}
