# ایمیج پایه
FROM python:3.11-slim

# تنظیم متغیرها برای جلوگیری از کش شدن پایتون
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ساخت دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های نیازمند نصب
COPY requirements.txt /app/

# نصب وابستگی‌ها
RUN pip install --upgrade pip && pip install -r requirements.txt

# کپی کل پروژه به داخل کانتینر
COPY . /app/

# باز کردن پورت جنگو
EXPOSE 8000

# دستور پیش‌فرض برای اجرای سرور توسعه جنگو
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
