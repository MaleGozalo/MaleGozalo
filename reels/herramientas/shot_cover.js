const { chromium } = require('playwright');
(async () => {
  const [html, out] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + html); await p.waitForSelector('body[data-ready]');
  console.log('scale', await p.evaluate(() => window.__k), 'title box y', await p.evaluate(() => window.__box));
  await (await p.$('#c')).screenshot({ path: out, type: 'png' });
  await b.close();
})();
