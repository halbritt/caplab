const fs = require('fs');
const { chromium } = require('/playwright');

(async () => {
  const browser = await chromium.launch({executablePath:'/browser/chrome-headless-shell-linux64/chrome-headless-shell',
    headless:true, args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
  const context = await browser.newContext({locale:'en-US', timezoneId:'UTC', deviceScaleFactor:1});
  const errors = [], requests = [], views = [];
  try {
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => requests.push(request.url()));
    for (const width of [320,768,1280]) {
      await page.setViewportSize({width,height:900});
      await page.goto('http://127.0.0.1:3913/', {waitUntil:'networkidle'});
      await page.evaluate(() => document.fonts.ready);
      const state = await page.evaluate(() => {
        const nameplate = document.querySelector('.nameplate');
        const mark = nameplate.querySelector('.mark');
        const rect = el => { const r=el.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}; };
        const style = el => {const s=getComputedStyle(el); return {display:s.display,color:s.color,background:s.backgroundColor,font:s.font,whiteSpace:s.whiteSpace};};
        return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
          nameplate:{text:nameplate.innerText,href:nameplate.getAttribute('href'),rect:rect(nameplate),style:style(nameplate)},
          mark:mark?{text:mark.innerText,rect:rect(mark),style:style(mark)}:null,
          icon:document.querySelector('link[rel="icon"]')?.getAttribute('href')??null,
          scriptElements:document.scripts.length,bodyText:document.body.innerText};
      });
      state.accessibility = await page.locator('.nameplate').ariaSnapshot();
      await page.locator('header').screenshot({path:`/capture/header-${width}.png`});
      await page.screenshot({path:`/capture/page-${width}.png`,fullPage:true});
      views.push(state);
    }
    let icon = null;
    if (views[0].icon) {
      await page.setViewportSize({width:64,height:64});
      const response = await page.goto('http://127.0.0.1:3913'+views[0].icon, {waitUntil:'networkidle'});
      icon = {status:response.status(),contentType:response.headers()['content-type'],
              root:await page.evaluate(()=>document.documentElement.localName),
              text:await page.locator('svg text').textContent()};
      await page.screenshot({path:'/capture/icon.png'});
    }
    fs.writeFileSync('/capture/browser.json',JSON.stringify({browser:browser.version(),node:process.version,views,icon,errors,requests},null,2)+'\n');
  } finally {await context.close();await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
