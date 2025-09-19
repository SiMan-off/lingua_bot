# 🚀 Развертывание LinguaBot на Beget

## 📋 Требования

### 1. Тариф Beget
- **Нужен SSH доступ** (тарифы от ~300₽/мес)
- **Python 3.8+** (обычно уже установлен)
- **Минимум 1GB места** на диске

### 2. API ключи
- **OpenAI API** (обязательно) - $5-20/мес
- **Yandex/DeepL** (опционально) - для улучшения переводов
- **YooKassa** (опционально) - для приема платежей

## 📦 Установка

### Шаг 1: Загрузка файлов

1. **Скачайте архив** `lingua_bot_beget.tar.gz` (75KB)
2. **Загрузите через cPanel** в корень аккаунта:
   - Файловый менеджер → Загрузить файлы
   - Или через FTP клиент

### Шаг 2: Распаковка через SSH

```bash
# Подключитесь по SSH к серверу Beget
ssh ваш_логин@ваш_домен.beget.tech

# Распакуйте архив
tar -xzf lingua_bot_beget.tar.gz

# Переименуйте папку (если нужно)
mv lingua_bot_beget lingua_bot

# Перейдите в папку проекта
cd lingua_bot
```

### Шаг 3: Создание виртуального окружения

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

```bash
# Скопируйте шаблон конфигурации
cp .env.beget .env

# Отредактируйте файл .env
nano .env
```

**Обязательно заполните:**
```env
BOT_TOKEN=7833039830:AAFtpgWKphLaFxGnxExkWn6aG6Mm2EQC6wg
OPENAI_API_KEY=sk-proj-ваш_ключ_openai
ADMIN_IDS=ваш_telegram_user_id
```

**Опционально:**
```env
YANDEX_API_KEY=ваш_ключ_yandex
DEEPL_API_KEY=ваш_ключ_deepl
YOOKASSA_SHOP_ID=ваш_shop_id
YOOKASSA_SECRET_KEY=ваш_secret_key
```

### Шаг 5: Создание папок

```bash
# Создайте необходимые папки
mkdir -p data logs exports

# Дайте права на запись
chmod 755 data logs exports
```

### Шаг 6: Запуск бота

```bash
# Сделайте скрипт исполняемым
chmod +x start_beget.sh stop_beget.sh

# Запустите бота
./start_beget.sh
```

## 🔧 Управление ботом

### Запуск
```bash
./start_beget.sh
```

### Остановка
```bash
./stop_beget.sh
```

### Просмотр логов
```bash
tail -f logs/bot.log
```

### Перезапуск
```bash
./stop_beget.sh && ./start_beget.sh
```

## 🤖 Автозапуск при перезагрузке

Добавьте задачу в cron:
```bash
crontab -e

# Добавьте строку:
@reboot cd ~/lingua_bot && ./start_beget.sh
```

## 🐛 Решение проблем

### Проблема: "python3: command not found"
```bash
# Попробуйте разные версии Python
python --version
python3.8 --version
python3.9 --version

# Используйте найденную версию в скриптах
```

### Проблема: "Permission denied"
```bash
# Дайте права на выполнение
chmod +x start_beget.sh stop_beget.sh
chmod 755 -R data logs exports
```

### Проблема: "Module not found"
```bash
# Переустановите зависимости
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Проблема: Бот не отвечает
```bash
# Проверьте логи
tail -f logs/bot.log

# Проверьте процессы
ps aux | grep python

# Проверьте токен бота
curl "https://api.telegram.org/bot<ВАШ_ТОКЕН>/getMe"
```

## 📊 Мониторинг

### Проверка статуса бота
```bash
# Проверить запущен ли процесс
ps aux | grep "python main.py"

# Посмотреть последние логи
tail -20 logs/bot.log

# Проверить использование ресурсов
top -p $(cat bot.pid)
```

### Ротация логов
```bash
# Очистить старые логи (раз в неделю)
echo "" > logs/bot.log
```

## 💰 Стоимость содержания

- **Beget хостинг**: 300-800₽/мес
- **OpenAI API**: $10-30/мес (~1000₽)
- **Итого**: ~1300-2200₽/мес

## 🎯 Проверка работы

1. **Найдите бота в Telegram**: @PolyglotAI44_bot
2. **Отправьте команду**: `/start`
3. **Протестируйте перевод**: отправьте любой текст
4. **Проверьте логи**: `tail -f logs/bot.log`

## 🆘 Поддержка

При проблемах проверьте:
1. Правильность заполнения `.env`
2. Наличие средств на OpenAI аккаунте
3. SSH доступ к серверу
4. Логи в `logs/bot.log`

**Готово! Ваш бот работает на Beget 24/7** 🎉