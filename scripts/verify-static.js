const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const D=process.env.DIST||path.join(__dirname,'..','dist');const BP=(process.env.BASE_PATH||'').replace(/\/$/,'');
const pages=[];(function walk(p){for(const f of fs.readdirSync(p)){const q=path.join(p,f);if(fs.statSync(q).isDirectory())walk(q);else if(f==='index.html')pages.push(q)}})(D);
const problems=[];const titles=new Map();let linkCount=0;
for(const p of pages){
  const rel=path.relative(D,p);const isRoot=rel==='index.html';const isLanding=rel.startsWith('uk/skineform');if(isLanding){/* landing checked separately */}
  const html=fs.readFileSync(p,'utf8');
  const errs=[];const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://usefulhabit.net/'+rel.replace('index.html',''),virtualConsole:new (require('jsdom').VirtualConsole)().on('jsdomError',e=>errs.push(e.message))});
  const d=dom.window.document;
  const h1=d.querySelectorAll('h1').length;
  if(h1!==1)problems.push([rel,'h1',h1]);if(isLanding){const r=d.querySelector('meta[name=robots]');console.log('landing robots:',r&&r.content);dom.window.close();continue}
  if(!d.querySelector('link[rel=canonical]'))problems.push([rel,'no canonical']);
  const hl=d.querySelectorAll('link[rel=alternate][hreflang]').length;
  if(hl!==29)problems.push([rel,'hreflang',hl]);
  if(!isRoot){
    if(!d.querySelector('meta[name=description]')?.content)problems.push([rel,'no desc']);
    if(d.querySelectorAll('script:not([type="application/ld+json"])').length!==1)problems.push([rel,'scripts']);
    if(html.includes('var LOGO')||html.includes('data:image/png'))problems.push([rel,'base64 left']);
    if(d.querySelector('#home')&&rel.includes('privacy'))problems.push([rel,'home in legal']);
    const t=d.title;if(titles.has(t))problems.push([rel,'dup title with',titles.get(t)]);titles.set(t,rel);
    const lang=rel.split('/')[0];if(d.documentElement.lang!==lang)problems.push([rel,'lang attr',d.documentElement.lang]);
    const dir=d.documentElement.dir;if(((lang==='ar'||lang==='ur')?'rtl':'ltr')!==dir)problems.push([rel,'dir',dir]);
    if(d.querySelectorAll('a[href^="#"]').length>0&&[...d.querySelectorAll('a[href^="#"]')].some(a=>a.getAttribute('href')==='#'))problems.push([rel,'dead # link']);
  }
  // internal links exist
  d.querySelectorAll('a[href^="/"]').forEach(a=>{linkCount++;let href=a.getAttribute('href').split('#')[0];if(BP&&href.startsWith(BP+'/'))href=href.slice(BP.length);else if(BP&&href===BP)href='/';let f=path.join(D,href);if(href.endsWith('/'))f=path.join(f,'index.html');if(!fs.existsSync(f))problems.push([rel,'broken link',href])});
  // in-page anchors exist on home
  if(rel.split('/').length===2&&!isRoot){['about','articles','tips','how','important'].forEach(id=>{if(!d.getElementById(id))problems.push([rel,'missing #'+id])})}
  if(errs.length)problems.push([rel,'js errors',errs.slice(0,1)]);
  dom.window.close();
}
console.log('pages:',pages.length,'internal links checked:',linkCount,'unique titles:',titles.size);
console.log('problems:',problems.length);problems.slice(0,15).forEach(x=>console.log(JSON.stringify(x)));
const sm=fs.readFileSync(D+'/sitemap.xml','utf8');console.log('sitemap urls:',(sm.match(/<url>/g)||[]).length,'robots:',fs.readFileSync(D+'/robots.txt','utf8').split('\n')[0]);
