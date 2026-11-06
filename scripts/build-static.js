/*
 * Static build for Useful Habit.
 * Takes the current single-file site (public/index.html), renders every language and
 * every legal page in jsdom, and writes real pages:
 *   dist/index.html                  language chooser (root)
 *   dist/{lang}/index.html           home
 *   dist/{lang}/privacy/index.html   Privacy Policy
 *   dist/{lang}/terms/index.html     Terms of Use
 *   dist/sitemap.xml, dist/robots.txt, dist/404.html, dist/assets/*
 * Usage: npm install && npm run build
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'public', 'index.html');
const OUT = path.join(ROOT, 'dist');
const BASE = process.env.SITE_URL || 'https://usefulhabit.net';
const BP = (process.env.BASE_PATH || '').replace(/\/$/, '');
const NOINDEX = process.env.NOINDEX === '1';
const LANDING_INDEX = process.env.LANDING_INDEX === '1';
const LASTMOD = process.env.LASTMOD || new Date().toISOString().slice(0, 10);

const html = fs.readFileSync(SRC, 'utf8');
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });

function boot() {
  return new JSDOM(html, {
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    url: BASE + '/',
    beforeParse(w) { w.scrollTo = () => {}; w.Element.prototype.scrollIntoView = () => {}; },
  });
}

// language list + logo come from the source page itself
const probe = boot();
const LANGS = probe.window.eval('LANGS.map(function(x){return x[0]})');
const LANG_NAMES = Object.fromEntries(probe.window.eval('LANGS').map(x => [x[0], x[1]]));
const logoDataUri = probe.window.eval('LOGO');
fs.writeFileSync(path.join(OUT, 'assets', 'logo.png'), Buffer.from(logoDataUri.split(',')[1], 'base64'));
probe.window.close();
for (const f of ['og.png', 'favicon.png', 'favicon-32.png']) {
  const p = path.join(ROOT, 'assets', f);
  if (fs.existsSync(p)) fs.copyFileSync(p, path.join(OUT, 'assets', f));
}

const MINI_JS = "(function(){var b=document.getElementById('bg'),n=document.getElementById('nav'),lb=document.getElementById('lb'),lm=document.getElementById('lm');" +
  "if(b&&n)b.addEventListener('click',function(){n.classList.toggle('open')});" +
  "if(lb&&lm){lb.addEventListener('click',function(e){e.stopPropagation();var o=lm.classList.toggle('open');lb.setAttribute('aria-expanded',o)});" +
  "document.addEventListener('click',function(){lm.classList.remove('open')})}})();";

function addMeta(d, attr, key, content) {
  const m = d.createElement('meta');
  m.setAttribute(attr, key);
  m.setAttribute('content', content);
  d.head.appendChild(m);
}
function addLink(d, rel, href, extra) {
  const l = d.createElement('link');
  l.setAttribute('rel', rel);
  l.setAttribute('href', href);
  Object.entries(extra || {}).forEach(([k, v]) => l.setAttribute(k, v));
  d.head.appendChild(l);
}
const urlOf = (lang, page) => `${BASE}/${lang}/${page ? page + '/' : ''}`;

function renderPage(lang, page) {
  const dom = boot();
  const w = dom.window;
  const d = w.document;
  w.eval(`render(${JSON.stringify(lang)})`);
  w.location.hash = page || '';
  w.eval('route()');

  const title = d.title;
  let desc = d.querySelector('meta[name=description]').getAttribute('content');
  if (page) desc = title;

  // keep only the matching view
  if (page) { const h = d.getElementById('home'); if (h) h.remove(); }
  else { const l = d.getElementById('legal'); if (l) l.remove(); }

  // links -> real URLs
  d.querySelectorAll('a').forEach(a => {
    const go = a.getAttribute('data-go');
    const href = a.getAttribute('href');
    if (go) {
      a.setAttribute('href', go === 'top' ? `${BP}/${lang}/` : `${BP}/${lang}/#${go}`);
      a.removeAttribute('data-go');
    } else if (href === '#privacy') a.setAttribute('href', `${BP}/${lang}/privacy/`);
    else if (href === '#terms') a.setAttribute('href', `${BP}/${lang}/terms/`);
  });

  // language menu: buttons -> links (same page in the other language)
  const menu = d.getElementById('lm');
  menu.querySelectorAll('button').forEach(b => {
    const code = b.getAttribute('data-l');
    const a = d.createElement('a');
    a.setAttribute('role', 'menuitem');
    a.setAttribute('href', `${BP}/${code}/${page ? page + '/' : ''}`);
    a.setAttribute('hreflang', code);
    a.setAttribute('lang', code);
    if (b.className) a.className = b.className;
    a.innerHTML = b.innerHTML;
    b.replaceWith(a);
  });
  // style menu links like the old buttons
  const st = d.createElement('style');
  st.textContent = '.menu a{padding:8px 10px;border-radius:10px;font-size:14px;display:flex;gap:6px;align-items:baseline;text-decoration:none;color:inherit}.menu a b{font-size:11px;color:var(--g2);min-width:24px}.menu a:hover{background:var(--chip)}.menu a.cur{background:var(--g1);color:#fff}.menu a.cur b{color:#fff}';
  d.head.appendChild(st);

  // logos: file instead of base64
  d.querySelectorAll('img.logo').forEach(i => { i.setAttribute('src', BP + '/assets/logo.png'); i.setAttribute('alt', 'Useful Habit'); });

  // head: canonical, hreflang, og, icons, robots, schema
  addMeta(d, 'name', 'robots', NOINDEX ? 'noindex,nofollow' : 'index,follow');
  addLink(d, 'canonical', urlOf(lang, page));
  LANGS.forEach(c => addLink(d, 'alternate', urlOf(c, page), { hreflang: c }));
  addLink(d, 'alternate', urlOf('en', page), { hreflang: 'x-default' });
  addLink(d, 'icon', BP + '/assets/favicon-32.png', { type: 'image/png', sizes: '32x32' });
  addLink(d, 'apple-touch-icon', BP + '/assets/favicon.png');
  d.querySelector('meta[name=description]').setAttribute('content', desc);
  let ogt = d.querySelector('meta[property="og:title"]');
  if (ogt) ogt.setAttribute('content', title);
  d.querySelector('meta[property="og:description"]').setAttribute('content', desc);
  addMeta(d, 'property', 'og:url', urlOf(lang, page));
  addMeta(d, 'property', 'og:site_name', 'Useful Habit');
  addMeta(d, 'property', 'og:image', BASE + '/assets/og.png');
  addMeta(d, 'name', 'twitter:card', 'summary_large_image');
  const ld = d.querySelector('script[type="application/ld+json"]');
  if (ld) ld.textContent = JSON.stringify({ '@context': 'https://schema.org', '@type': 'WebSite', name: 'Useful Habit', url: urlOf(lang), inLanguage: lang });

  // remove the app script (data + renderer), add tiny menu script
  d.querySelectorAll('script').forEach(s => { if (s.type !== 'application/ld+json') s.remove(); });
  const comment = [...d.head.childNodes].filter(n => n.nodeType === 8);
  comment.forEach(n => n.remove());
  const s = d.createElement('script');
  s.textContent = MINI_JS;
  d.body.appendChild(s);

  // lazy-load decorative sections is not needed; keep markup as rendered
  const out = '<!DOCTYPE html>\n' + d.documentElement.outerHTML;
  w.close();
  return out;
}

function write(rel, content) {
  const p = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content);
}

const urls = [];
for (const lang of LANGS) {
  for (const page of ['', 'privacy', 'terms']) {
    write(`${lang}/${page ? page + '/' : ''}index.html`, renderPage(lang, page));
    urls.push([lang, page]);
  }
}

// root: language chooser
const links = LANGS.map(c => `<li><a href="${BP}/${c}/" hreflang="${c}" lang="${c}">${LANG_NAMES[c]}</a></li>`).join('');
write('index.html', `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Useful Habit</title><meta name="description" content="Useful Habit — choose your language."><meta name="robots" content="${NOINDEX ? 'noindex,nofollow' : 'index,follow'}"><link rel="canonical" href="${BASE}/">${LANGS.map(c => `<link rel="alternate" hreflang="${c}" href="${urlOf(c)}">`).join('')}<link rel="alternate" hreflang="x-default" href="${urlOf('en')}"><link rel="icon" href="${BP}/assets/favicon-32.png"><style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#f4fbf6;color:#12342a;margin:0;padding:48px 20px;text-align:center}img{height:90px;width:auto}ul{list-style:none;display:flex;flex-wrap:wrap;gap:10px;justify-content:center;max-width:760px;margin:28px auto;padding:0}a{display:block;padding:10px 16px;border:1px solid #d3e8da;border-radius:99px;text-decoration:none;color:inherit;background:#fff;font-weight:600}a:hover{background:#0f7a57;color:#fff}</style></head><body><img src="${BP}/assets/logo.png" alt="Useful Habit"><h1>Useful Habit</h1><ul>${links}</ul></body></html>`);

// sitemap with alternates
const xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'];
xml.push(`<url><loc>${BASE}/</loc><lastmod>${LASTMOD}</lastmod></url>`);
for (const [lang, page] of urls) {
  xml.push(`<url><loc>${urlOf(lang, page)}</loc><lastmod>${LASTMOD}</lastmod>` +
    LANGS.map(c => `<xhtml:link rel="alternate" hreflang="${c}" href="${urlOf(c, page)}"/>`).join('') +
    `<xhtml:link rel="alternate" hreflang="x-default" href="${urlOf('en', page)}"/></url>`);
}
xml.push('</urlset>');
write('sitemap.xml', xml.join('\n'));
write('robots.txt', NOINDEX ? 'User-agent: *\nDisallow: /\n' : `User-agent: *\nAllow: /\n\nSitemap: ${BASE}/sitemap.xml\n`);
write('.nojekyll', '');
write('404.html', `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>404 — Useful Habit</title></head><body style="font-family:system-ui,Arial,sans-serif;text-align:center;padding:60px 20px;background:#f4fbf6;color:#12342a"><h1>404</h1><p>Page not found / Сторінку не знайдено</p><p><a href="${BP}/" style="color:#0f7a57">Useful Habit</a></p></body></html>`);

// landing pages (paid-traffic pages, kept out of the sitemap)
const LDIR = path.join(ROOT, 'landings');
if (fs.existsSync(LDIR)) {
  for (const name of fs.readdirSync(LDIR)) {
    const f = path.join(LDIR, name, 'index.html');
    if (!fs.existsSync(f)) continue;
    let h = fs.readFileSync(f, 'utf8');
    h = h.split('href="/uk/').join('href="' + BP + '/uk/');
    const robots = (NOINDEX || !LANDING_INDEX) ? 'noindex,nofollow' : 'index,follow';
    h = h.replace('<meta name="robots" content="index,follow">', '<meta name="robots" content="' + robots + '"><link rel="canonical" href="' + BASE + '/uk/' + name + '/"><link rel="icon" href="' + BP + '/assets/favicon-32.png">');
    write('uk/' + name + '/index.html', h);
    console.log('Landing: /uk/' + name + '/ (' + robots + ')');
  }
}

console.log(`Built ${urls.length} pages for ${LANGS.length} languages into ${OUT}`);
