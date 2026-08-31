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

(function () {
  const BRANDED_FILLS = [
    ["#fdebd0", "#6d4c2a"],
    ["#d6eaf8", "#1a4a6b"],
    ["rgb(253, 235, 208)", "#6d4c2a"],
    ["rgb(214, 234, 248)", "#1a4a6b"],
  ];

  const DEFAULT_LIGHT_FILLS = [
    "#ececff",
    "#fff4dd",
    "#ffffff",
    "#ffffde",
    "#f4f4f4",
    "white",
    "lightgrey",
    "rgb(236, 236, 255)",
    "rgb(255, 244, 221)",
  ];

  const DARK_DEFAULT_FILL = "#323748";
  const DARK_STROKE = "#8fa4e0";
  const DARK_TEXT = "#f0f0f0";
  const DARK_EDGE = "#e0e0e0";
  const DARK_CLUSTER_FILL = "#252836";
  const DARK_LABEL_BG = "#252836";

  const CONTRAST_STYLE_ID = "a2a-mermaid-contrast";
  const STYLE_LINE =
    /((?:classDef|style) \w+ fill:#[0-9a-fA-F]{3,8},stroke:#[0-9a-fA-F]{3,8},stroke-width:\d+px)(?:,color:#[0-9a-fA-F]{3,8})?/g;

  const sourcesById = new Map();
  const pendingSourceIds = [];
  let hooksInstalled = false;
  let originalRender = null;

  function isDarkMode() {
    return (document.body.getAttribute("data-md-color-scheme") || "default") === "slate";
  }

  function stripContrastStyles(value) {
    return value.replace(
      new RegExp(`<style id="${CONTRAST_STYLE_ID}">[\\s\\S]*?<\\/style>`, "g"),
      "",
    );
  }

  function swapBrandedFills(value) {
    let swapped = value;
    for (const [light, dark] of BRANDED_FILLS) {
      swapped = swapped.split(light).join(dark);
    }
    return swapped;
  }

  function replaceDefaultLightFills(value) {
    let replaced = value;
    for (const light of DEFAULT_LIGHT_FILLS) {
      const escaped = light.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      replaced = replaced.replace(new RegExp(`fill="${escaped}"`, "gi"), `fill="${DARK_DEFAULT_FILL}"`);
      replaced = replaced.replace(new RegExp(`fill:${escaped}`, "gi"), `fill:${DARK_DEFAULT_FILL}`);
    }

    return replaced.replace(/style="([^"]*)"/gi, (match, styles) => {
      let updated = styles;
      for (const light of DEFAULT_LIGHT_FILLS) {
        updated = updated.replace(new RegExp(`fill:${light}`, "gi"), `fill:${DARK_DEFAULT_FILL}`);
      }
      return `style="${updated}"`;
    });
  }

  function adaptDiagramSource(source) {
    if (!isDarkMode()) {
      return source;
    }

    let adapted = swapBrandedFills(source);
    adapted = adapted.replace(STYLE_LINE, `$1,color:${DARK_TEXT}`);
    return adapted;
  }

  function buildDarkContrastStyleBlock() {
    return (
      `<style id="${CONTRAST_STYLE_ID}">` +
      `.node rect,.node circle,.node ellipse,.node polygon,.node path:not(.flowchart-link)` +
      `{stroke:${DARK_STROKE}!important;}` +
      `.node .label,.node .label p,.node .label span,.node .label div,.node .label foreignObject div` +
      `{color:${DARK_TEXT}!important;}` +
      `.node .label span,.nodeLabel{fill:${DARK_TEXT}!important;}` +
      `.cluster rect{fill:${DARK_CLUSTER_FILL}!important;stroke:${DARK_STROKE}!important;}` +
      `.cluster span,.cluster .nodeLabel{color:${DARK_TEXT}!important;fill:${DARK_TEXT}!important;}` +
      `.edgeLabel,.edgeLabel p,.edgeLabel span,.label div .edgeLabel` +
      `{color:${DARK_EDGE}!important;fill:${DARK_LABEL_BG}!important;background-color:${DARK_LABEL_BG}!important;}` +
      `.edgePath .path,.flowchart-link{stroke:${DARK_EDGE}!important;}` +
      `.edgePath .arrowheadPath{fill:${DARK_EDGE}!important;stroke:none!important;}` +
      `.actor{fill:${DARK_DEFAULT_FILL}!important;stroke:${DARK_STROKE}!important;}` +
      `.actor-line{stroke:${DARK_STROKE}!important;}` +
      `.actor-box{fill:${DARK_DEFAULT_FILL}!important;stroke:${DARK_STROKE}!important;}` +
      `text.actor,tspan.actor-box{fill:${DARK_TEXT}!important;}` +
      `text.messageText,text.loopText,text.sequenceNumber,text.noteText,text.legendText` +
      `{fill:${DARK_TEXT}!important;}` +
      `.messageLine0,.messageLine1{stroke:${DARK_EDGE}!important;}` +
      `.note rect,.note path{fill:${DARK_CLUSTER_FILL}!important;stroke:${DARK_STROKE}!important;}` +
      `.labelBox,.labelText,.loopText,.loopLine{fill:${DARK_TEXT}!important;stroke:${DARK_STROKE}!important;color:${DARK_TEXT}!important;}` +
      `.activation0,.activation1,.activation2{fill:${DARK_CLUSTER_FILL}!important;stroke:${DARK_STROKE}!important;}` +
      `</style>`
    );
  }

  function patchRenderedSvg(svg) {
    const cleaned = stripContrastStyles(svg);

    if (!isDarkMode()) {
      return cleaned;
    }

    let patched = swapBrandedFills(cleaned);
    patched = replaceDefaultLightFills(patched);

    const contrastStyle = buildDarkContrastStyleBlock();
    return patched.includes("</style>")
      ? patched.replace("</style>", `${contrastStyle}</style>`)
      : patched.replace(/(<svg[^>]*>)/, `$1${contrastStyle}`);
  }

  function renderDiagram(id, source) {
    return originalRender(id, source).then((result) => {
      result.svg = patchRenderedSvg(result.svg);
      return result;
    });
  }

  function wrappedRender(id, text, container) {
    if (!sourcesById.has(id)) {
      sourcesById.set(id, text);
    }

    pendingSourceIds.push(id);
    return renderDiagram(id, adaptDiagramSource(sourcesById.get(id)));
  }

  function refreshMermaidDiagrams() {
    document.querySelectorAll(".mermaid").forEach((host) => {
      const sourceId = host.dataset.mermaidSourceId;
      const source = sourceId ? sourcesById.get(sourceId) : null;
      if (!source) {
        return;
      }

      const renderId = `${sourceId}_${Date.now()}`;
      renderDiagram(renderId, adaptDiagramSource(source)).then(({ svg, bindFunctions }) => {
        const nextHost = document.createElement("div");
        nextHost.className = "mermaid";
        nextHost.dataset.mermaidSourceId = sourceId;

        const shadow = nextHost.attachShadow({ mode: "closed" });
        shadow.innerHTML = svg;
        bindFunctions?.(shadow);

        host.replaceWith(nextHost);
      });
    });
  }

  function installMermaidHooks() {
    if (hooksInstalled || typeof mermaid === "undefined" || typeof mermaid.render !== "function") {
      return hooksInstalled;
    }

    if (mermaid.render.__a2aPatched) {
      hooksInstalled = true;
      return true;
    }

    originalRender = mermaid.render.bind(mermaid);
    mermaid.render = function (id, text, container) {
      return wrappedRender(id, text, container);
    };
    mermaid.render.__a2aPatched = true;

    hooksInstalled = true;
    return true;
  }

  installMermaidHooks();

  if (!hooksInstalled) {
    const retryTimer = window.setInterval(() => {
      if (installMermaidHooks()) {
        window.clearInterval(retryTimer);
      }
    }, 50);
    window.setTimeout(() => window.clearInterval(retryTimer), 10000);
    window.addEventListener("load", installMermaidHooks);
  }

  const hostObserver = new MutationObserver((mutations) => {
    installMermaidHooks();

    for (const mutation of mutations) {
      mutation.addedNodes.forEach((node) => {
        if (!(node instanceof HTMLElement) || !node.classList.contains("mermaid")) {
          return;
        }
        if (pendingSourceIds.length) {
          node.dataset.mermaidSourceId = pendingSourceIds.shift();
        }
      });
    }
  });
  hostObserver.observe(document.body, { childList: true, subtree: true });

  const themeObserver = new MutationObserver(() => {
    if (document.body.hasAttribute("data-md-color-switching")) {
      return;
    }
    window.setTimeout(refreshMermaidDiagrams, 0);
  });
  themeObserver.observe(document.body, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme"],
  });

  if (typeof window.document$ !== "undefined") {
    window.document$.subscribe(() => {
      installMermaidHooks();
      pendingSourceIds.length = 0;
    });
  }

  document.addEventListener(
    "toggle",
    (event) => {
      if (event.target instanceof HTMLDetailsElement && event.target.open) {
        window.setTimeout(refreshMermaidDiagrams, 50);
      }
    },
    true,
  );
})();
