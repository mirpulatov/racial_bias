FROM nginx

# Удаляем дефолтный файл с конфигами
RUN rm /etc/nginx/conf.d/default.conf

# Подкидываем наши конфиги из nginx.conf
COPY nginx.conf /etc/nginx/conf.d/