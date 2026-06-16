const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 6 });
const pct = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });

fetch("data.json")
  .then((response) => response.json())
  .then((data) => {
    renderSummary(data.summary);
    renderGroupedBars("validation-chart", data.validation, "metric", ["value", "benchmark"]);
    renderLine(
      "convergence-chart",
      data.convergence.map((d) => ({ x: d.num_paths, y: d.standard_error })),
      "standard error",
      true,
    );
    renderBars(
      "variance-chart",
      data.varianceReduction,
      "method",
      "variance_reduction_pct",
      "variance reduction %",
    );
    renderTwoLine(
      "asian-chart",
      data.asian.map((d) => ({ x: d.monitoring_steps, y: d.asian_call })),
      data.asian.map((d) => ({ x: d.monitoring_steps, y: d.geometric_asian_call })),
    );
    renderTable("greeks-table", data.greeks, ["greek", "method", "monte_carlo_fd", "black_scholes", "abs_error"]);
    renderTable("extensions-table", data.extensions, ["feature", "value"]);
    attachLab();
  });

function renderSummary(summary) {
  const cards = [
    ["Call MC price", summary.callPrice],
    ["Black-Scholes error", summary.callAbsError],
    ["Antithetic variance reduction", `${pct.format(summary.antitheticReduction)}%`],
    ["Control-variate variance reduction", `${pct.format(summary.controlVariateReduction)}%`],
  ];
  document.getElementById("summary").innerHTML = cards
    .map(
      ([label, value]) => `
      <div class="metric-card">
        <span class="metric-label">${label}</span>
        <span class="metric-value">${typeof value === "number" ? fmt.format(value) : value}</span>
      </div>`,
    )
    .join("");
}

function bounds(points) {
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  return {
    xMin: Math.min(...xs),
    xMax: Math.max(...xs),
    yMin: Math.min(0, ...ys),
    yMax: Math.max(...ys) * 1.12,
  };
}

function svgFrame(id) {
  const element = document.getElementById(id);
  element.innerHTML = `<svg viewBox="0 0 640 280" role="img"></svg>`;
  const svg = element.querySelector("svg");
  const margin = { left: 58, right: 20, top: 18, bottom: 44 };
  return { svg, margin, width: 640, height: 280 };
}

function drawAxes(svg, margin, width, height) {
  const x0 = margin.left;
  const y0 = height - margin.bottom;
  svg.insertAdjacentHTML(
    "beforeend",
    `<line class="axis" x1="${x0}" y1="${margin.top}" x2="${x0}" y2="${y0}"></line>
     <line class="axis" x1="${x0}" y1="${y0}" x2="${width - margin.right}" y2="${y0}"></line>`,
  );
}

function renderLine(id, points, label, logX = false) {
  const { svg, margin, width, height } = svgFrame(id);
  const domain = bounds(points.map((p) => ({ x: logX ? Math.log10(p.x) : p.x, y: p.y })));
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const sx = (x) => margin.left + (((logX ? Math.log10(x) : x) - domain.xMin) / (domain.xMax - domain.xMin)) * plotW;
  const sy = (y) => height - margin.bottom - ((y - domain.yMin) / (domain.yMax - domain.yMin)) * plotH;
  drawAxes(svg, margin, width, height);
  const path = points.map((p, i) => `${i ? "L" : "M"} ${sx(p.x)} ${sy(p.y)}`).join(" ");
  svg.insertAdjacentHTML("beforeend", `<path class="series" d="${path}"></path>`);
  points.forEach((p) => {
    svg.insertAdjacentHTML("beforeend", `<circle cx="${sx(p.x)}" cy="${sy(p.y)}" r="4" fill="#2563eb"></circle>`);
  });
  svg.insertAdjacentHTML("beforeend", `<text class="tick" x="${margin.left}" y="266">${label}</text>`);
}

function renderTwoLine(id, a, b) {
  const { svg, margin, width, height } = svgFrame(id);
  const all = [...a, ...b];
  const domain = bounds(all);
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const sx = (x) => margin.left + ((x - domain.xMin) / (domain.xMax - domain.xMin)) * plotW;
  const sy = (y) => height - margin.bottom - ((y - domain.yMin) / (domain.yMax - domain.yMin)) * plotH;
  drawAxes(svg, margin, width, height);
  const path = (series) => series.map((p, i) => `${i ? "L" : "M"} ${sx(p.x)} ${sy(p.y)}`).join(" ");
  svg.insertAdjacentHTML("beforeend", `<path class="series" d="${path(a)}"></path><path class="series-alt" d="${path(b)}"></path>`);
  svg.insertAdjacentHTML("beforeend", `<text class="tick" x="70" y="32">arithmetic</text><text class="tick" x="160" y="32">geometric</text>`);
}

function renderBars(id, rows, labelKey, valueKey, label) {
  const { svg, margin, width, height } = svgFrame(id);
  const max = Math.max(...rows.map((r) => r[valueKey]));
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const barW = plotW / rows.length - 14;
  drawAxes(svg, margin, width, height);
  rows.forEach((row, index) => {
    const x = margin.left + index * (plotW / rows.length) + 8;
    const h = max === 0 ? 0 : (row[valueKey] / max) * plotH;
    const y = height - margin.bottom - h;
    svg.insertAdjacentHTML(
      "beforeend",
      `<rect class="${index === rows.length - 1 ? "bar-alt" : "bar"}" x="${x}" y="${y}" width="${barW}" height="${h}"></rect>
       <text class="tick" x="${x}" y="${height - 24}" transform="rotate(20 ${x} ${height - 24})">${row[labelKey]}</text>`,
    );
  });
  svg.insertAdjacentHTML("beforeend", `<text class="tick" x="${margin.left}" y="16">${label}</text>`);
}

function renderGroupedBars(id, rows, labelKey, keys) {
  const { svg, margin, width, height } = svgFrame(id);
  const max = Math.max(...rows.flatMap((r) => keys.map((k) => r[k])));
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  drawAxes(svg, margin, width, height);
  rows.forEach((row, index) => {
    keys.forEach((key, kIndex) => {
      const groupW = plotW / rows.length;
      const x = margin.left + index * groupW + 24 + kIndex * 28;
      const h = (row[key] / max) * plotH;
      const y = height - margin.bottom - h;
      svg.insertAdjacentHTML("beforeend", `<rect class="${kIndex ? "bar-alt" : "bar"}" x="${x}" y="${y}" width="22" height="${h}"></rect>`);
    });
    svg.insertAdjacentHTML("beforeend", `<text class="tick" x="${margin.left + index * (plotW / rows.length) + 10}" y="${height - 20}">${row[labelKey]}</text>`);
  });
}

function renderTable(id, rows, columns) {
  document.getElementById(id).innerHTML = `
    <table>
      <thead><tr>${columns.map((c) => `<th>${c}</th>`).join("")}</tr></thead>
      <tbody>
        ${rows
          .map(
            (row) => `<tr>${columns
              .map((c) => `<td>${typeof row[c] === "number" ? fmt.format(row[c]) : row[c]}</td>`)
              .join("")}</tr>`,
          )
          .join("")}
      </tbody>
    </table>`;
}

function normalCdf(x) {
  return 0.5 * (1 + erf(x / Math.sqrt(2)));
}

function erf(x) {
  const sign = x >= 0 ? 1 : -1;
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;
  const t = 1 / (1 + p * Math.abs(x));
  const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
  return sign * y;
}

function blackScholesCall(s, k, r, sigma, t) {
  const d1 = (Math.log(s / k) + (r + 0.5 * sigma * sigma) * t) / (sigma * Math.sqrt(t));
  const d2 = d1 - sigma * Math.sqrt(t);
  return s * normalCdf(d1) - k * Math.exp(-r * t) * normalCdf(d2);
}

function randn(seed) {
  let value = seed;
  return () => {
    value = (1664525 * value + 1013904223) % 4294967296;
    const u1 = (value + 1) / 4294967297;
    value = (1664525 * value + 1013904223) % 4294967296;
    const u2 = (value + 1) / 4294967297;
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  };
}

function browserMonteCarlo(s, k, r, sigma, t) {
  const normal = randn(42);
  let total = 0;
  for (let i = 0; i < 10000; i++) {
    const z = normal();
    const terminal = s * Math.exp((r - 0.5 * sigma * sigma) * t + sigma * Math.sqrt(t) * z);
    total += Math.max(terminal - k, 0);
  }
  return Math.exp(-r * t) * (total / 10000);
}

function attachLab() {
  const ids = ["spot", "strike", "vol", "maturity"];
  const update = () => {
    const s = Number(document.getElementById("spot").value);
    const k = Number(document.getElementById("strike").value);
    const sigma = Number(document.getElementById("vol").value) / 100;
    const t = Number(document.getElementById("maturity").value) / 12;
    const bs = blackScholesCall(s, k, 0.03, sigma, t);
    const mc = browserMonteCarlo(s, k, 0.03, sigma, t);
    document.getElementById("lab-bs").textContent = fmt.format(bs);
    document.getElementById("lab-mc").textContent = fmt.format(mc);
    document.getElementById("lab-error").textContent = fmt.format(Math.abs(bs - mc));
  };
  ids.forEach((id) => document.getElementById(id).addEventListener("input", update));
  update();
}
