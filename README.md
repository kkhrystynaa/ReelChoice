# ReelChoice – вебзастосунок для рекомендацій фільмів

## 1. Назва проєкту

**ReelChoice** – вебзастосунок для рекомендацій фільмів на основі користувацьких оцінок.

## 2. Опис проєкту

ReelChoice — це вебзастосунок, який дозволяє користувачам взаємодіяти з фільмами: оцінювати, коментувати та отримувати персоналізовані рекомендації. Застосунок реалізований з використанням класичної архітектури Django MVT.

## 3. Основні функції

- Реєстрація та авторизація користувачів
- Перегляд фільмів по категоріях
- Оцінювання та коментування фільмів
- Отримання рекомендацій

## 4. Налаштування середовища

Клонування репозиторію
```bash
git clone https://github.com/kkhrystynaa/ReelChoice
```
```bash
cd ReelChoice
```

Створення та активація віртуального середовища
```bash
python -m venv .venv
```  
```bash
source .venv/bin/activate # Linux/Mac  
.venv\Scripts\activate # Windows
```  

Встановлення залежностей
```bash
pip install -r requirements.txt
```

Налаштування бази даних
```bash
python manage.py migrate
```

Запуск сервера
```bash
python manage.py runserver
```
