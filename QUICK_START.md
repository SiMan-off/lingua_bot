# 🚀 Быстрый запуск LinguaBot

## Способ 1: Простой запуск (Python)

### Требования:
- Python 3.11 или выше
- Windows/Linux/MacOS

### Шаги:

1. **Распакуйте архив с файлами бота**

2. **Настройте бота:**
   - Откройте файл `.env` в любом текстовом редакторе
   - Замените данные на свои:
     ```
     BOT_TOKEN=ваш_токен_от_BotFather
     OPENAI_API_KEY=ваш_ключ_от_OpenAI
     ADMIN_ID=ваш_telegram_id
     ```

3. **Установите Python** (если еще не установлен):
   - Скачайте с https://www.python.org/downloads/
   - При установке отметьте "Add Python to PATH"

4. **Запустите бота:**

   **Windows:**
   - Дважды кликните на файл `start_bot.bat`
   - Или откройте командную строку в папке бота и выполните:
     ```
     python -m pip install -r requirements.txt
     python main.py
     ```

   **Linux/MacOS:**
   - Откройте терминал в папке бота
   - Выполните:
     ```bash
     chmod +x start_bot.sh
     ./start_bot.sh
     ```
   - Или вручную:
     ```bash
     python3 -m pip install -r requirements.txt
     python3 main.py
     ```

## Способ 2: Запуск через Docker (рекомендуется)

### Требования:
- Docker Desktop (скачать с https://www.docker.com/products/docker-desktop/)

### Шаги:

1. **Установите Docker Desktop**
   - Скачайте и установите для вашей ОС
   - Запустите Docker Desktop

2. **Настройте бота:**
   - Откройте файл `.env` и укажите свои данные

3. **Запустите бота:**

   **Windows:**
   - Дважды кликните на `docker-start.bat`

   **Linux/MacOS:**
   ```bash
   chmod +x docker-start.sh
   ./docker-start.sh
   ```

   **Или вручную:**
   ```bash
   docker compose up -d
   ```

## Способ 3: Быстрый запуск в Docker (одна команда)

```bash
docker run -d --name lingua_bot \
  -v $(pwd):/app \
  -w /app \
  --env-file .env \
  python:3.11-slim \
  sh -c "pip install -r requirements.txt && python main.py"
```

## 🔧 Получение необходимых ключей:

### Bot Token:
1. Откройте @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

### OpenAI API Key:
1. Зарегистрируйтесь на https://platform.openai.com
2. Перейдите в https://platform.openai.com/api-keys
3. Создайте новый ключ

### Ваш Telegram ID:
1. Напишите боту @userinfobot
2. Он покажет ваш ID
3. Добавьте его в ADMIN_ID в файле .env

## ❓ Проверка работы:

1. После запуска в консоли должно появиться:
   ```
   🎉 LinguaBot started successfully!
   ```

2. Найдите вашего бота в Telegram по имени
3. Отправьте команду `/start`
4. Бот должен ответить приветствием

## 🛑 Остановка бота:

- **Консоль:** Нажмите `Ctrl+C`
- **Docker:** `docker stop lingua_bot`

## ⚠️ Возможные проблемы:

### "Conflict: terminated by other getUpdates"
- Остановите все другие экземпляры бота
- Убедитесь, что бот запущен только в одном месте

### "Module not found"
- Установите зависимости: `pip install -r requirements.txt`

### "Permission denied"
- Linux/Mac: добавьте `sudo` перед командами
- Windows: запустите от имени администратора

## 📱 Команды бота:

- `/start` - Начать работу
- `/help` - Помощь
- `/settings` - Настройки
- `/admin` - Админ панель (только для администраторов)

## 💡 Совет:
Для постоянной работы бота рекомендуется использовать VPS/сервер или облачные платформы (Railway, Heroku, etc.)