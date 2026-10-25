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

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  carousels.forEach((carousel) => {
    carousel.dataset.ready = "true";

    const slides = Array.from(carousel.querySelectorAll(".hero-tagline"));
    if (slides.length < 2) {
      return;
    }

    const interval = Number.parseInt(carousel.dataset.interval || "6000", 10);
    let activeIndex = 0;
    let timerId = null;

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
        showSlide(dotIndex);
        startAutoRotate();
      });
      dotsContainer.appendChild(dot);
      return dot;
    });

    carousel.appendChild(dotsContainer);

    function showSlide(index) {
      activeIndex = (index + slides.length) % slides.length;

      slides.forEach((slide, slideIndex) => {
        slide.classList.toggle("is-active", slideIndex === activeIndex);
      });

      dots.forEach((dot, dotIndex) => {
        const isActive = dotIndex === activeIndex;
        dot.classList.toggle("is-active", isActive);
        dot.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }

    function stopAutoRotate() {
      if (timerId !== null) {
        window.clearInterval(timerId);
        timerId = null;
      }
    }

    function startAutoRotate() {
      if (prefersReducedMotion) {
        return;
      }

      stopAutoRotate();
      timerId = window.setInterval(() => {
        showSlide(activeIndex + 1);
      }, interval);
    }

    showSlide(0);
    startAutoRotate();
  });
}

initHeroTaglineCarousels();

if (typeof window.document$ !== "undefined") {
  window.document$.subscribe(initHeroTaglineCarousels);
}
