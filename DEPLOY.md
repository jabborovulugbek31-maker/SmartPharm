# SmartPharm Online v2 — joylashtirish

Bu loyiha Flask + SQLite + Gunicorn bilan online hostingga tayyorlangan.

## Render kabi Python hostingda
1. GitHub'ga loyiha fayllarini yuklang.
2. Web Service yarating.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Deploy qiling.
6. Berilgan HTTPS manzilni telefon va kompyuterdan oching.

## Lokal test
`python app.py`
Keyin `http://127.0.0.1:5000`

## Muhim
SQLite kichik demo uchun. Ko'p foydalanuvchi uchun PostgreSQL kabi production DB va login/auth kerak.
Interaction ma'lumotlari demo; real klinik foydalanishdan oldin ekspert va rasmiy manbalar bilan validatsiya shart.
