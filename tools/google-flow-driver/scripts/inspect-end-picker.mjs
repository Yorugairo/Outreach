import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const endBtn = flow.locator('button.empty-chip:has-text("End")').first();
  await endBtn.click();
  await flow.waitForTimeout(1000);

  const items = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('[role="option"], .asset-item')).map(el => ({
      text: el.innerText.trim(),
      className: el.className
    }));
  });

  console.log('[asset options in End picker]:', JSON.stringify(items.slice(0, 10), null, 2));

  // Click the first item
  const item = flow.locator('[role="option"], .asset-item').first();
  await item.click();
  await flow.waitForTimeout(1000);

  const buttons = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent !== null).map(b => ({
      text: b.innerText.trim(),
      aria: b.getAttribute('aria-label') || '',
      className: b.className
    }));
  });

  console.log('[Visible buttons after selecting asset]:', JSON.stringify(buttons, null, 2));

  // Screenshot to see what is on screen
  await flow.screenshot({ path: 'C:\\Users\\Snipe\\.gemini\\antigravity\\brain\\3291f626-ecee-49f8-99ec-d148e4069076\\.tempmediaStorage\\end_picker_click.png' });
  console.log('Saved end_picker_click.png');

  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
