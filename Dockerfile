FROM python:3.10-bullseye

WORKDIR /app

# Копируем requirements.txt первым, чтобы воспользоваться кэшем Docker
COPY requirements.txt .

# Устанавливаем системные зависимости и обновляем pip
RUN apt update --fix-missing && \
    apt install -y python3-pip libffi-dev && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    apt clean && \
    apt autoremove

# Копируем остальные файлы проекта
COPY . .

# Назначаем права
RUN chmod -R 740 /app

EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "src.quest_ans:app", "--host", "0.0.0.0", "--port", "8000"]
