FROM python:3.8

# Устанавливаем рабочую директорию
WORKDIR /app

# Закидываем наше приложение Flask в контейнер
ADD . /app

# Устанавливаем зависимости 
RUN pip install -r requirements.txt

# Запускаем uWSGI
CMD ["uwsgi", "app.ini"]