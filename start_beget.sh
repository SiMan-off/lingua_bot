#!/bin/bash

# Скрипт для запуска бота на Beget
# Поместите этот файл в корень проекта на сервере

# Переходим в директорию проекта
cd ~/lingua_bot

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем существование папки данных
if [ ! -d "data" ]; then
    mkdir data
    echo "Создана папка data"
fi

# Проверяем существование папки логов
if [ ! -d "logs" ]; then
    mkdir logs
    echo "Создана папка logs"
fi

# Проверяем существование .env файла
if [ ! -f ".env" ]; then
    echo "ОШИБКА: Файл .env не найден!"
    echo "Скопируйте .env.beget в .env и заполните переменные"
    exit 1
fi

# Убиваем предыдущий процесс если он запущен
pkill -f "python.*main"
pkill -f "python3.*main"

# Небольшая пауза после остановки
sleep 2

# Запускаем рабочую версию бота в фоне
nohup python3 main_fixed_middleware.py > logs/bot.log 2>&1 &

# Получаем PID процесса
BOT_PID=$!
echo "Бот запущен с PID: $BOT_PID"
echo $BOT_PID > bot.pid

echo "✅ Бот PolyglotAI44 запущен успешно!"
echo "📋 Логи: tail -f logs/bot.log"
echo "🛑 Остановка: ./stop_beget.sh"