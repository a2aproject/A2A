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
  const BRANDED_LIGHT_FILLS = ["#fdebd0", "#d6eaf8"];
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
  const LIGHT_TEXT = "#1a1a1a";

  const CONTRAST_STYLE_ID = "a2a-mermaid-contrast";
  const STYLE_LINE =
    /((?:classDef|style) \w+ fill:#[0-9a-fA-F]{3,8},stroke:#[0-9a-fA-F]{3,8},stroke-width:\d+px)(?:,color:#[0-9a-fA-F]{3,8})?/g;

  const sourcesById = new Map();
  const orderedSources = [];
  const pendingSourceIds = [];
  let hooksInstalled = false;
  let originalRender = null;
  let refreshTimer = null;

  function isDarkMode() {
    return (document.body.getAttribute("data-md-color-scheme") || "default") === "slate";
  }

  function rememberSource(id, source) {
    const normalized = source.trim();
    sourcesById.set(id, normalized);

    const existingIndex = orderedSources.findIndex((entry) => entry.source === normalized);
    if (existingIndex >= 0) {
      orderedSources[existingIndex].id = id;
      return;
    }

    orderedSources.push({ id, source: normalized });
  }

  function snapshotMermaidSources() {
    document.querySelectorAll("pre.mermaid").forEach((pre, index) => {
      const source = pre.textContent?.trim();
      if (!source) {
        return;
      }

      const id = pre.dataset.a2aMermaidSource || `__a2a_snapshot_${index}`;
      pre.dataset.a2aMermaidSource = id;
      rememberSource(id, source);
    });
  }

  function stripContrastStyles(value) {
    return value.replace(
      new RegExp(`<style id="${CONTRAST_STYLE_ID}">[\\s\\S]*?<\\/style>`, "g"),
      "",
    );
  }

  function hasBrandedFills(value) {
    return BRANDED_LIGHT_FILLS.some((fill) => value.toLowerCase().includes(fill));
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

  function injectContrastStyle(svg, styleBlock) {
    return svg.includes("</style>")
      ? svg.replace("</style>", `${styleBlock}</style>`)
      : svg.replace(/(<svg[^>]*>)/, `$1${styleBlock}`);
  }

  function buildLightBrandedStyleBlock() {
    return (
      `<style id="${CONTRAST_STYLE_ID}">` +
      `.node .label,.node .label p,.node .label span,.node .label div,.node .label foreignObject div` +
      `{color:${LIGHT_TEXT}!important;}` +
      `.node .label span,.nodeLabel{fill:${LIGHT_TEXT}!important;}` +
      `</style>`
    );
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
      if (hasBrandedFills(cleaned)) {
        return injectContrastStyle(cleaned, buildLightBrandedStyleBlock());
      }
      return cleaned;
    }

    let patched = swapBrandedFills(cleaned);
    patched = replaceDefaultLightFills(patched);
    return injectContrastStyle(patched, buildDarkContrastStyleBlock());
  }

  function renderDiagram(id, source) {
    return originalRender(id, source).then((result) => {
      result.svg = patchRenderedSvg(result.svg);
      return result;
    });
  }

  function wrappedRender(id, text, container) {
    rememberSource(id, text);
    pendingSourceIds.push(id);
    return renderDiagram(id, adaptDiagramSource(sourcesById.get(id)));
  }

  function resolveHostSource(host, index) {
    const sourceId = host.dataset.mermaidSourceId;
    if (sourceId && sourcesById.has(sourceId)) {
      return { sourceId, source: sourcesById.get(sourceId) };
    }

    const ordered = orderedSources[index];
    if (ordered) {
      host.dataset.mermaidSourceId = ordered.id;
      return ordered;
    }

    return null;
  }

  function refreshMermaidDiagrams() {
    if (!originalRender) {
      return;
    }

    document.querySelectorAll(".mermaid").forEach((host, index) => {
      const resolved = resolveHostSource(host, index);
      if (!resolved) {
        return;
      }

      const { sourceId, source } = resolved;
      const renderId = `${sourceId}_${Date.now()}_${index}`;

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

  function scheduleRefreshMermaidDiagrams() {
    window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(refreshMermaidDiagrams, 100);
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

  snapshotMermaidSources();
  installMermaidHooks();

  if (!hooksInstalled) {
    const retryTimer = window.setInterval(() => {
      if (installMermaidHooks()) {
        window.clearInterval(retryTimer);
      }
    }, 50);
    window.setTimeout(() => window.clearInterval(retryTimer), 10000);
    window.addEventListener("load", () => {
      snapshotMermaidSources();
      installMermaidHooks();
    });
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
    scheduleRefreshMermaidDiagrams();
  });
  themeObserver.observe(document.body, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme", "data-md-color-switching"],
  });

  if (typeof window.document$ !== "undefined") {
    window.document$.subscribe(() => {
      orderedSources.length = 0;
      pendingSourceIds.length = 0;
      sourcesById.clear();
      snapshotMermaidSources();
      installMermaidHooks();
    });
  }

  document.addEventListener(
    "toggle",
    (event) => {
      if (event.target instanceof HTMLDetailsElement && event.target.open) {
        scheduleRefreshMermaidDiagrams();
      }
    },
    true,
  );
})();
