#!/usr/bin/env node
// Render each screen of a grouped ui-prototype HTML to PNG, so notes can embed them.
//
// Usage: node screens-to-png.mjs <grouped.html> [out_dir] [--theme dark|light] [--chrome <path>]
//
// Every <section class="spec" id="..."> becomes:
//   <out_dir>/<name>-mobile.png        the row of phones (.phones), when present
//   <out_dir>/<name>-desktop[-N].png   each desktop frame (.desk-fig .desk), when present
// where <name> is "<data-task>-<id>" (or "<id>" without data-task). out_dir defaults to the HTML
// path without extension. PNGs that no longer match a screen are removed, so embeds never go stale.
// The grouped HTML stays the source of truth: re-run after every edit.
import { existsSync, mkdirSync, readdirSync, unlinkSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright-core';

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(name);
  if (i === -1) return fallback;
  const value = args[i + 1];
  args.splice(i, 2);
  return value;
};
const theme = flag('--theme', 'dark');
const chromePath = flag('--chrome', process.env.CHROME_PATH || '/usr/bin/google-chrome');
const [src, outArg] = args;
if (!src || !['dark', 'light'].includes(theme)) {
  console.error('usage: node screens-to-png.mjs <grouped.html> [out_dir] [--theme dark|light] [--chrome <path>]');
  process.exit(2);
}
const htmlPath = path.resolve(src);
const outDir = path.resolve(outArg || htmlPath.replace(/\.html?$/i, ''));
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ executablePath: existsSync(chromePath) ? chromePath : undefined, channel: existsSync(chromePath) ? undefined : 'chrome' });
const page = await browser.newPage({ viewport: { width: 1320, height: 1000 }, deviceScaleFactor: 2, colorScheme: theme, reducedMotion: 'reduce' });
// Pin the prototype's theme switcher too, in case it remembers another choice.
await page.addInitScript((t) => { try { localStorage.setItem('prototype-theme', t); } catch (e) {} }, theme);
await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
// Hide page chrome that is not part of the screens.
await page.addStyleTag({ content: '.theme-toggle { display: none !important; }' });

const sections = await page.$$('main section.spec[id]');
const written = new Set();
for (const section of sections) {
  const id = await section.getAttribute('id');
  const task = await section.getAttribute('data-task');
  const name = task ? `${task}-${id}` : id;

  const phones = await section.$(':scope > .phones');
  if (phones) {
    await phones.scrollIntoViewIfNeeded();
    // Give entry effects (e.g. a toast that appears when the frame is visible) time to settle.
    await page.waitForTimeout(600);
    const file = path.join(outDir, `${name}-mobile.png`);
    await phones.screenshot({ path: file, animations: 'disabled' });
    written.add(path.basename(file));
    console.log(file);
  }

  const desks = await section.$$(':scope > .desk-fig .desk');
  for (let i = 0; i < desks.length; i++) {
    await desks[i].scrollIntoViewIfNeeded();
    const file = path.join(outDir, `${name}-desktop${desks.length > 1 ? `-${i + 1}` : ''}.png`);
    await desks[i].screenshot({ path: file, animations: 'disabled' });
    written.add(path.basename(file));
    console.log(file);
  }
}
await browser.close();

for (const f of readdirSync(outDir)) {
  if (f.endsWith('.png') && !written.has(f)) {
    unlinkSync(path.join(outDir, f));
    console.log(`removed ${path.join(outDir, f)}`);
  }
}
