import fs from 'node:fs';
import path from 'node:path';

const items = [
  { name: '01-man-standing-behind-wooden-desk', url: 'https://lh3.googleusercontent.com/asb/AB-nOUafTcONN5obfphPP1wR8StcChMPNhvCd5uyIvBfNs7q-eDIXto-9UUuT3vC_U3fYB9EdpIpq6Ru0sJf5Xd6JnP_6OZVJw5XnZGEMSSlTkscziUBuEy4_Vne-u_IF_DCN8wTL5ZSOrGPDiT6qJh58bwIskbLUyW07zJtuSBh' },
  { name: '02-character-standing-at-shipping-terminal', url: 'https://lh3.googleusercontent.com/asb/AB-nOUYhQGStJgdJ_l0MFZU__VtS5Hw1X0ISRmIM2hU2gWEhLWbxv5I0KyS6gjEuQVyYeYKOrC69XPEqRcdGPlE-RsK-Aaj_JP4aV0oeK6tCriPuP41X-wemds6efKGjf9XqPTKXzNZ1mfXXODRqth7bLiVbIEXG9iVwXwZOrMgCBA' },
  { name: '03-character-observing-television', url: 'https://lh3.googleusercontent.com/asb/AB-nOUZdWloXpeIZPtxY9NONMjzLA0FqFESf9wlt4AHtEFhadeKOQC_mABNsdG2iOrb3fzey8dy1MubIcRWhzWwSGucOIbUNB8In5NJNaqJWzWSTBE8K84Lw4gGWOhNWPALyIizo8Ter-wwV9lQRpIeaRrWDodlsyZzbvK7hRH32' },
  { name: '04-analyst-standing-at-desk', url: 'https://lh3.googleusercontent.com/asb/AB-nOUbZKsQaDxlih-vNNNp024wNXcPKiDDNVeyQnWWJxVoK26tq70fngMAujKL5H9YnkopFsm3pbt-8yEbfoaAYzCOBruwa7Jb_t4rbwrRJ3_oQeQhobh5BnJK4VhIJo-uxKPUSKcCyHQ1iviIdnsIo6gCFSbi37YuuXkMxXtFOUw' },
  { name: '05-stick-figure-working-at-desk', url: 'https://lh3.googleusercontent.com/asb/AB-nOUZhCbYHvAK4gqxUe3n3FEr7dJ3clmnUztdYRh9AK6hzPIVT4ObuJC63NKxc6U1h2Gf3yRSFqEDKcb7Njfs5cWTvAGf40mSnHhpi4ggIYZMRH_mn3JFaH_J0vLU9-oJtVw4dPwuj57WUr5uzdCtq9xOy0ezkZKF2FyIl81OF2w' },
  { name: '06-stick-figure-viewing-data-table', url: 'https://lh3.googleusercontent.com/asb/AB-nOUakzQWxRM3JzQTw5ZHXPipDkqa9VPDHOE5UZbgWuKX_jn5B2MCHjn1ubRmbNcEiBEerm6lia4ZMiZzGbU-fq64X2MkUKochCK01x7bcVsl0bPKFwNJzcoLyPp1ipIBqaYcY5qe7kLAa6IuH08EciJs14ouvNLD-NAayc1YqKQ' }
];

const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\stills\\inspect';
fs.mkdirSync(outDir, { recursive: true });

for (const item of items) {
  try {
    const res = await fetch(item.url);
    const buf = Buffer.from(await res.arrayBuffer());
    const outPath = path.join(outDir, `${item.name}.png`);
    fs.writeFileSync(outPath, buf);
    console.log(`Saved ${outPath} (${buf.length} bytes)`);
  } catch (err) {
    console.error(`Failed ${item.name}:`, err.message);
  }
}
