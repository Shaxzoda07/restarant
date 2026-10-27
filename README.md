# NOVZA restaurant (Django)

## Kompyuterda ishga tushirish
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py makemigrations restaurant
python manage.py migrate
python manage.py seed_menu       # namunaviy menyu va stollar
python manage.py createsuperuser # admin yaratish
python manage.py runserver
```
Sayt: http://127.0.0.1:8000  ·  Admin: http://127.0.0.1:8000/admin

## GitHub
```bash
git init
git add .
git commit -m "NOVZA restaurant"
git branch -M main
git remote add origin https://github.com/USERNAME/novza.git
git push -u origin main
```

## Render
1. render.com → New → Blueprint → GitHub repo'ni tanlang (render.yaml avtomatik o'qiladi).
2. `ADMIN_PASSWORD` qiymatini kiriting (admin login: `admin`).
3. Deploy tugagach: https://novza-restaurant.onrender.com/admin

Eslatma: Render'ning bepul disklari doimiy emas — yuklangan rasmlar o'chib ketadi,
shuning uchun adminda «rasm havolasi» maydonidan foydalaning yoki Cloudinary ulang.
