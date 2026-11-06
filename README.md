# Useful Habit

Інформаційний портал про харчові добавки (огляди, склад, порівняння). Поточна версія — статичний сайт (`public/index.html`).

## Структура
- `public/` — поточна збірка (один файл, 28 мов).
- `src/locales/*.json` — тексти головної сторінки по мовах.
- `src/legal/*.json` — Політика конфіденційності й Умови по мовах.
- `src/config/geos.json` — країни, мова, правовий режим, статус перевірки.
- `src/config/site.json` — бренд, домен, контакти (дані власника не заповнено).
- `lead-form/` — форма EnsoTraffic (PHP-проксі + фрагмент форми), не підключена.
- `docs/` — AUDIT.md, SOLUTIONS.md, COMPLIANCE.md, ROADMAP.md.
- `.env.example` — шаблон змінних (GA4, GTM, Pixel, EnsoTraffic). `.env` не комітити.

## Лендинги
- `landings/skineform/index.html` — чесна сторінка про продукт (варіанти тексту `?v=a|b|c`). Після збірки лежить на `/uk/skineform/`, за замовчуванням `noindex`; індексація — змінна `LANDING_INDEX=1`. Форма в демо-режимі: підключіть `ENDPOINT` у файлі та `lead-form/lead.php`.
- Аудит партнерських лендингів: `docs/LANDERS-AUDIT.md`.

## Збірка статичного сайту
```
npm install
npm run build          # створює dist/ (85 сторінок)
node scripts/verify-static.js   # перевірка (h1, canonical, hreflang, посилання)
```
Змінні: `SITE_URL` — домен; `BASE_PATH=/UsefulHabit` — якщо сайт відкривається за адресою github.io/назва-репозиторію; `NOINDEX=1` — закрити від індексації (для перегляду); `LANDING_INDEX=1` — дозволити індексацію лендингів. Змінна `SITE_URL` задає домен (за замовчуванням https://usefulhabit.net). Папку `dist/` можна завантажити на будь-який статичний хостинг (Cloudflare Pages, Netlify, GitHub Pages).

## Як залити в GitHub
1. На github.com: New repository → `useful-habit` → Private → без README.
2. У терміналі в цій папці:

```
git init
git add .
git commit -m "Initial import of Useful Habit"
git branch -M main
git remote add origin https://github.com/<ваш-логін>/useful-habit.git
git push -u origin main
```

Авторизація GitHub виконується на вашому комп'ютері. Не надсилайте токени в чат.
