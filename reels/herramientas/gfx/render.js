// usage: node render.js <layer front|back> <outdir> <hook A|B|C> <guides 0|1> <t1,t2,...|from:to:fps>
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [layer, outdir, hook, guides, spec] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  let times = [];
  if (spec.includes(':')) { const [a, b, step] = spec.split(':').map(Number); for (let f = a; f < b; f += step) times.push([f, f / 30]); }
  else times = spec.split(',').map(x => [x, Number(x)]);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'overlay.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(p => window.setup(p), { hook, layer, guides: guides === '1' });
  const stage = await page.$('#stage');
  for (const [name, t] of times) {
    await page.evaluate(t => window.render(t), t);
    await stage.screenshot({ path: path.join(outdir, `${name}.png`), omitBackground: true });
  }
  await browser.close();
  console.log('rendered', times.length);
})();
