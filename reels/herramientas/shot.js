const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  for (const [w, name] of [[1200, 'desk'], [390, 'mob']]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    await p.goto('file:///home/user/edicion-reel/storyboard.html'); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: process.argv[2] + '/sb_' + name + '.png', fullPage: true });
    const ow = await p.evaluate(() => document.documentElement.scrollWidth); console.log(name, 'scrollWidth', ow);
  }
  await b.close();
})();
