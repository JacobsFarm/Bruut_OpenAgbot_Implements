// Builds (1) "implement ideas/<slug>/README.md" + an index README and (2) docs/bruut_implements.html.
// The PDF is printed from the HTML with Edge/Chrome headless: node build_docs.mjs --pdf
// Run from anywhere: node docs/build_docs.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { ideas } from "./data_ideas.mjs";
import { implementsList } from "./data_implements.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const ideasDir = path.join(root, "implement ideas");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const enc = (p) => p.split("/").map(encodeURIComponent).join("/");

// ---------------------------------------------------------------- idea READMEs
const categories = [...new Set(ideas.map((i) => i.category))];

function ideaReadme(i) {
  return `# ${i.name}

**Status: idea, not worked out yet.** Category: ${i.category}.

## What it does

${i.does}

## Concept (first thoughts)

${i.concept}

## Reuse from existing implements

${i.reuse}

## Open questions

${i.open.map((o) => `- ${o}`).join("\n")}

## To do when this is worked out

Follow [AGENTS.md](../../AGENTS.md): make a folder per variant (\`simple/\`, \`advanced/\`) with \`<p>_params.py\`, \`<p>_parts.py\`,
\`build_<p>.py\`, \`<p>_calc.py\`, \`README.md\` and \`RATIONALE.md\`, mount on the 50 mm hole grid of the beams, and list what is
estimated and not measured. Then move the folder out of \`implement ideas/\` and add it to the table in the main
[README](../../README.md) and to [docs](../../docs/).

${i.extra ? "Source: own brainstorm, not on the website list." : "Source: the attachments list of the website (functionality's.json)."}
`;
}

fs.mkdirSync(ideasDir, { recursive: true });
for (const i of ideas) {
  const d = path.join(ideasDir, i.slug);
  fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, "README.md"), ideaReadme(i));
}
const indexMd = `# Implement ideas

Attachments that are **not worked out
yet**: those from the website's list ([openagbot.com](https://openagbot.com), functionality's.json) and extra ideas from brainstorming (marked in their README). Each folder holds a \`README.md\` with what the implement does, a first concept, what can be reused from the finished
implements and the open questions, so it can be worked out later in the layout described in [AGENTS.md](../AGENTS.md).

${categories
  .map(
    (c) =>
      `## ${c}\n\n| Idea | What it does |\n|---|---|\n${ideas
        .filter((i) => i.category === c)
        .map((i) => `| [${i.name}](${enc(i.slug)}/README.md) | ${i.does.split(". ")[0].replace(/\.$/, "")}. |`)
        .join("\n")}\n`,
  )
  .join("\n")}
Already worked out (in the folders next to this one): overseeder, liquid fertilizer applicator, feed pusher auger, disc brushes
(broom), dockweed drill (CNC weed driller), trencher, spot sprayer (atomising boom), in-row weeder (finger weeders), around-pole
mower (mowing arm), weed picker, irrigation (hose reel), field marker, mobile refiller, belt rake, weeds burner,
push blade (also the manure scraper job), fertilizer spreader, grassland harrow (molehill spreader), soil sampler, inter-row hoe, grassland aerator, three-point hitch (with the small cultivator), crate carrier (also the tool cart), counterweights, battery pack, solar canopy, compost spreader, stone picker, mulch layer, grass meter (NIR sensor), soil compaction meter, charging dock, UV-C mildew light, sawdust spreader, bedding rake, dumper barrow, biocontrol spreader and bag trailer.

Covered elsewhere: the tow hitch (50 mm tow ball) and the patch seeder (drop seeder that a camera switches on over
bare soil) are in [overseeding/](../overseeding/) (cambridge roll and overseeder).
`;
fs.writeFileSync(path.join(ideasDir, "README.md"), indexMd);

// ---------------------------------------------------------------- HTML document
const img = (p, alt) => `<img src="../${enc(p)}" alt="${esc(alt)}">`;
let pages = [];
let toc = [];
const page = (html, cls = "") => pages.push(`<section class="page ${cls}">${html}</section>`);

let n = 0;
for (const imp of implementsList) {
  n++;
  const id = `imp${n}`;
  toc.push({ id, label: imp.name, level: 1, cat: imp.category });
  const thumbs = imp.variants
    .map(
      (v) =>
        `<figure>${img(v.hero, imp.name + " " + v.name)}<figcaption><b>${esc(v.name)}</b></figcaption></figure>`,
    )
    .join("");
  page(
    `<p class="kicker">Implement · ${esc(imp.category)}</p><h2 id="${id}">${esc(imp.name)}</h2>
<p class="lead">${esc(imp.summary)}</p>
<div class="thumbs t${Math.min(imp.variants.length, 3)}">${thumbs}</div>
<p class="meta">${imp.variants.length} variant${imp.variants.length > 1 ? "s" : ""}: ${imp.variants.map((v) => esc(v.name)).join(" · ")}<br>Folder: <code>${esc(imp.folder)}/</code></p>`,
    "implement",
  );
  // single variant: the implement page already shows it, but the variant still gets its own page
  imp.variants.forEach((v, k) => {
    page(
      `<p class="kicker">${esc(imp.name)} · variant ${k + 1} of ${imp.variants.length}</p><h3>${esc(v.name)}</h3>
<div class="hero">${img(v.hero, imp.name + " " + v.name)}</div>
<p>${esc(v.text)}</p>
<ul class="facts">${v.facts.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>
<p class="meta">Folder: <code>${esc(v.folder)}/</code></p>`,
      "variant",
    );
  });
}

toc.push({ id: "ideas", label: "Implement ideas (not worked out yet)", level: 1, cat: "" });
page(
  `<p class="kicker">Implement ideas</p><h2 id="ideas">Ideas not worked out yet</h2>
<p class="lead">${ideas.length} attachments from the website's list that have no model yet. Each has a folder in <code>implement ideas/</code> with a <code>README.md</code> describing what it does, so it can be worked out later.</p>
${categories
  .map(
    (c) =>
      `<h4>${esc(c)}</h4><ul class="idx">${ideas
        .filter((i) => i.category === c)
        .map((i) => `<li><b>${esc(i.name)}</b></li>`)
        .join("")}</ul>`,
  )
  .join("")}`,
  "implement",
);
for (const i of ideas) {
  page(
    `<p class="kicker">Idea · ${esc(i.category)}</p><h3>${esc(i.name)}</h3>
<p class="status">Not worked out yet</p>
<h5>What it does</h5><p>${esc(i.does)}</p>
<h5>Concept (first thoughts)</h5><p>${esc(i.concept)}</p>
<h5>Reuse from existing implements</h5><p>${esc(i.reuse)}</p>
<h5>Open questions</h5><ul>${i.open.map((o) => `<li>${esc(o)}</li>`).join("")}</ul>
<p class="meta">Folder: <code>implement ideas/${esc(i.slug)}/</code></p>`,
    "idea",
  );
}

const tocHtml = toc
  .map((t) => `<li><a href="#${t.id}">${esc(t.label)}</a>${t.cat ? `<span>${esc(t.cat)}</span>` : ""}</li>`)
  .join("");
const cover = `<section class="page cover"><p class="kicker">Bruut OpenAgbot</p><h1>Implements</h1>
<p class="lead">Overview of all implements for the Bruut OpenAgbot: the ${implementsList.length} that are worked out in FreeCAD, with every variant on its own page, followed by the ${ideas.length} ideas from the website that are not worked out yet.</p>
<p class="meta">Generated from the repository READMEs · ${new Date().toISOString().slice(0, 10)} · <a href="https://openagbot.com">openagbot.com</a></p></section>
<section class="page"><h2>Contents</h2><ol class="toc">${tocHtml}</ol></section>`;

const css = `
@page { size: A4; margin: 0 }
*{box-sizing:border-box}
body{margin:0;font:11pt/1.5 "Segoe UI",system-ui,sans-serif;color:#1d2b21;background:#e9ece8}
.page{width:210mm;height:296mm;margin:8mm auto;padding:18mm 18mm 16mm;background:#fff;overflow:hidden;page-break-after:always;break-after:page;position:relative}
@media print{body{background:#fff}.page{margin:0}}
.kicker{margin:0 0 4mm;text-transform:uppercase;letter-spacing:.12em;font-size:8.5pt;color:#4d7a32;font-weight:600}
h1{font-size:44pt;margin:30mm 0 6mm;line-height:1}
h2{font-size:26pt;margin:0 0 5mm;line-height:1.1}
h3{font-size:22pt;margin:0 0 5mm;line-height:1.15}
h4{margin:5mm 0 1mm;font-size:11pt;color:#4d7a32}
h5{margin:5mm 0 1mm;font-size:10pt;text-transform:uppercase;letter-spacing:.08em;color:#4d7a32}
.lead{font-size:13pt;color:#34463a}
p,li{orphans:3}
.meta{position:absolute;left:18mm;right:18mm;bottom:12mm;margin:0;font-size:8.5pt;color:#6b786f}
code{font:9pt Consolas,monospace;background:#eef2ec;padding:1px 4px;border-radius:3px}
img{max-width:100%;display:block}
.hero img{width:100%;max-height:120mm;object-fit:contain;background:#fff;border:1px solid #dfe5dc;border-radius:4px}
.thumbs{display:grid;gap:5mm;margin-top:8mm}
.t1{grid-template-columns:1fr}.t2{grid-template-columns:1fr 1fr}.t3{grid-template-columns:1fr 1fr}
.thumbs figure{margin:0;border:1px solid #dfe5dc;border-radius:4px;padding:2mm}
.thumbs img{width:100%;height:62mm;object-fit:contain}
.t1 img{height:110mm}
.thumbs figcaption{font-size:9.5pt;padding-top:1mm}
.facts{margin:5mm 0;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:2mm 6mm}
.facts li{border-left:3px solid #7fb35a;padding:1mm 3mm;font-size:10.5pt;background:#f4f8f1}
.status{display:inline-block;margin:0 0 3mm;padding:1mm 3mm;background:#fff1d6;color:#8a5a00;border-radius:3px;font-size:9pt;font-weight:600}
.toc{columns:2;column-gap:10mm;font-size:10.5pt;padding-left:6mm}
.toc li{break-inside:avoid;margin:0 0 2mm}.toc a{color:inherit;text-decoration:none;font-weight:600}
.toc span{display:block;font-size:8.5pt;color:#6b786f}
.idx{columns:2;padding-left:5mm;margin:0;font-size:10pt}
a{color:#2f6b1e}
`;
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Bruut OpenAgbot implements</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body>${cover}${pages.join("\n")}</body></html>`;
const htmlPath = path.join(here, "bruut_implements.html");
fs.writeFileSync(htmlPath, html);
console.log(`ideas: ${ideas.length} folders; html pages: ${pages.length + 2}; ${htmlPath}`);

// missing images?
const missing = [];
for (const imp of implementsList) for (const v of imp.variants) if (!fs.existsSync(path.join(root, v.hero))) missing.push(v.hero);
if (missing.length) console.log("MISSING IMAGES:\n" + missing.join("\n"));

// ---------------------------------------------------------------- PDF
if (process.argv.includes("--pdf")) {
  const cands = [
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
  ];
  const exe = cands.find((c) => fs.existsSync(c));
  if (!exe) throw new Error("no Edge/Chrome found");
  const pdfPath = path.join(here, "bruut_implements.pdf");
  execFileSync(exe, [
    "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    `--print-to-pdf=${pdfPath}`, "file:///" + htmlPath.replace(/\\/g, "/"),
  ], { stdio: "inherit", timeout: 180000 });
  console.log("pdf:", pdfPath, fs.statSync(pdfPath).size);
}
