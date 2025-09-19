# 🛠️ Управление ботом на сервере Beget

## 📂 Структура файлов на сервере

```
/home/v/vokhma1v/lingua_bot/
├── venv/                 # Виртуальное окружение
├── data/                 # База данных SQLite
├── logs/                 # Логи бота
├── exports/              # Экспортированные файлы
├── .env                  # Конфигурация (секретные ключи)
├── main.py               # Основной файл бота
├── start_beget.sh        # Скрипт запуска
├── stop_beget.sh         # Скрипт остановки
├── delete_webhook.py     # Удаление webhook
└── requirements.txt      # Зависимости Python
```

## 🚀 Основные команды управления

### Запуск бота
```bash
cd /home/v/vokhma1v/lingua_bot
./start_beget.sh
```

### Остановка бота
```bash
cd /home/v/vokhma1v/lingua_bot
./stop_beget.sh
```

### Перезапуск бота
```bash
cd /home/v/vokhma1v/lingua_bot
./stop_beget.sh && ./start_beget.sh
```

### Проверка статуса
```bash
# Проверить, запущен ли бот
ps aux | grep "main.py"

# Посмотреть логи в реальном времени
tail -f /home/v/vokhma1v/lingua_bot/logs/bot.log

# Последние 20 строк логов
tail -20 /home/v/vokhma1v/lingua_bot/logs/bot.log
```

## 📊 Мониторинг и диагностика

### Проверка процессов
```bash
# Найти все Python процессы
ps aux | grep python

# Проверить конкретно процесс бота
ps aux | grep "main.py"

# Показать дерево процессов
pstree -p $(pgrep -f "main.py")
```

### Анализ логов
```bash
# Следить за логами
tail -f logs/bot.log

# Найти ошибки в логах
grep -i error logs/bot.log | tail -10

# Найти последние запуски
grep -i "starting" logs/bot.log | tail -5

# Очистить старые логи (делать осторожно!)
echo "" > logs/bot.log
```

### Проверка ресурсов
```bash
# Использование CPU и памяти ботом
top -p $(pgrep -f "main.py")

# Размер файлов
du -sh data/ logs/ exports/

# Свободное место на диске
df -h
```

## ⚙️ Автозапуск через Cron

### Настройка автозапуска при перезагрузке

1. **Откройте редактор cron:**
```bash
crontab -e
```

2. **Добавьте строку для автозапуска:**
```bash
@reboot cd /home/v/vokhma1v/lingua_bot && ./start_beget.sh
```

3. **Сохраните и выйдите** (в nano: Ctrl+X, Y, Enter)

### Настройка автоматического мониторинга

Добавьте в cron проверку каждые 5 минут:
```bash
crontab -e

# Добавьте строку:
*/5 * * * * cd /home/v/vokhma1v/lingua_bot && pgrep -f "main.py" > /dev/null || ./start_beget.sh
```

### Полная настройка cron
```bash
# Откройте cron
crontab -e

# Добавьте эти строки:
@reboot cd /home/v/vokhma1v/lingua_bot && ./start_beget.sh
*/5 * * * * cd /home/v/vokhma1v/lingua_bot && pgrep -f "main.py" > /dev/null || ./start_beget.sh
0 2 * * 0 echo "" > /home/v/vokhma1v/lingua_bot/logs/bot.log
```

**Объяснение:**
- `@reboot` - запуск при перезагрузке сервера
- `*/5 * * * *` - проверка каждые 5 минут, перезапуск если бот упал
- `0 2 * * 0` - очистка логов каждое воскресенье в 2:00

### Проверка настроек cron
```bash
# Посмотреть текущие задания cron
crontab -l

# Проверить логи cron
tail -f /var/log/cron.log
# или
tail -f /var/log/syslog | grep CRON
```

## 🔧 Ручное управление процессами

### Если скрипты не работают

**Остановка:**
```bash
# Найти PID процесса
ps aux | grep "main.py"

# Остановить по PID (замените XXXX)
kill XXXX

# Принудительная остановка
kill -9 XXXX

# Остановить все Python процессы с main.py
pkill -f "python.*main.py"
```

**Запуск:**
```bash
cd /home/v/vokhma1v/lingua_bot
source venv/bin/activate
nohup python3 main.py > logs/bot.log 2>&1 &
```

## 🚨 Решение проблем

### Бот не запускается

1. **Проверьте конфигурацию:**
```bash
cat .env | grep -E "(BOT_TOKEN|OPENAI_API_KEY)"
```

2. **Проверьте зависимости:**
```bash
source venv/bin/activate
pip list | grep -E "(aiogram|openai|aiohttp)"
```

3. **Удалите webhook:**
```bash
source venv/bin/activate
python3 delete_webhook.py
```

### Конфликт webhook

```bash
# Удалить webhook через скрипт
python3 delete_webhook.py

# Или через API
curl -X POST "https://api.telegram.org/bot7833039830:AAFtpgWKphLaFxGnxExkWn6aG6Mm2EQC6wg/deleteWebhook?drop_pending_updates=true"
```

### Ошибки в логах

```bash
# Посмотреть последние ошибки
tail -50 logs/bot.log | grep -i error

# Проверить подключение к API
curl -s "https://api.telegram.org/bot7833039830:AAFtpgWKphLaFxGnxExkWn6aG6Mm2EQC6wg/getMe"
```

### Высокое потребление ресурсов

```bash
# Проверить использование CPU/памяти
top -p $(pgrep -f "main.py")

# Перезапустить бота
./stop_beget.sh && ./start_beget.sh
```

## 🔄 Обновление бота

### Обновление через Git
```bash
cd /home/v/vokhma1v/lingua_bot

# Остановить бота
./stop_beget.sh

# Получить обновления
git pull origin master

# Обновить зависимости (если нужно)
source venv/bin/activate
pip install -r requirements.txt

# Запустить бота
./start_beget.sh
```

### Бэкап перед обновлением
```bash
# Создать бэкап базы данных
cp data/bot.db data/bot.db.backup.$(date +%Y%m%d)

# Создать бэкап логов
cp logs/bot.log logs/bot.log.backup.$(date +%Y%m%d)
```

## 📋 Чек-лист для администратора

### Ежедневно
- [ ] Проверить статус бота: `ps aux | grep main.py`
- [ ] Посмотреть логи: `tail -20 logs/bot.log`

### Еженедельно
- [ ] Проверить размер логов: `ls -lh logs/`
- [ ] Проверить свободное место: `df -h`
- [ ] Очистить старые логи при необходимости

### Ежемесячно
- [ ] Обновить бота: `git pull`
- [ ] Создать бэкап базы данных
- [ ] Проверить автозапуск: `crontab -l`

## 🆘 Контакты поддержки

При критических проблемах:
1. Проверьте логи: `tail -f logs/bot.log`
2. Перезапустите бота: `./stop_beget.sh && ./start_beget.sh`
3. Удалите webhook: `python3 delete_webhook.py`
4. Проверьте cron: `crontab -l`

**Бот работает стабильно при правильной настройке!** 🎉