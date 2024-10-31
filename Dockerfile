# Використовуйте базовий образ Python
FROM python:3.12-slim

# Встановіть робочу директорію
WORKDIR /usr/src/app

# Скопіюйте всі файли до контейнера
COPY . ./

# Встановіть залежності
RUN pip install --no-cache-dir -r requirements.txt

# Вкажіть команду для запуску бота
CMD ["python", "./bot.py"]
