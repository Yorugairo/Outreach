import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const urls = [
    { name: 'man-standing-behind-wooden-desk', src: 'https://lh3.googleusercontent.com/asb/AB-nOUafTcONN5obfphPP1wR8StcChMPNhvCd5uyIvBfNs7q-eDIXto-9UUuT3vC_U3fYB9EdpIpq6Ru0sJf5Xd6JnP_6OZVJw5XnZGEMSSlTkscziUBuEy4_Vne-u_IF_DCN8wTL5ZSOrGPDiT6qJh58bwIskbLUyW07zJtuSBh' },
    { name: 'analyst-standing-at-desk', src: 'https://lh3.googleusercontent.com/asb/AB-nOUbZKsQaDxlih-vNNNp024wNXcPKiDDNVeyQnWWJxVoK26tq70fngMAujKL5H9YnkopFsm3pbt-8yEbfoaAYzCOBruwa7Jb_t4rbwrRJ3_oQeQhobh5BnJK4VhIJo-uxKPUSKcCyHQ1iviIdnsIo6gCFSbi37YuuXkMxXtFOUw' }
  ];

  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\stills\\inspect';
  fs.mkdirSync(outDir, { recursive: true });

  for (const item of urls) {
    const bytes = await flow.evaluate(async (u) => {
      const resp = await fetch(u);
      const buf = await resp.arrayBuffer();
      return Array.from(new Uint8Array(buf));
    }, item.src);
    fs.writeFileSync(path.join(outDir, `${item.name}.png`), Buffer.from(bytes));
    console.log(`Saved ${item.name}.png (${bytes.length} bytes)`);
  }

  await browser.close();
}

main().catch(err => console.error(err));
