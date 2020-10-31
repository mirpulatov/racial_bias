import os
import uuid

from typing import List
from werkzeug.utils import secure_filename

def get_app_name() -> str:
    """
    Возращает название приложения, объявленное в 
    docker-compose.yml для сервиса
    """

    return os.getenv("APP_NAME")

def validate_file(file_name: str) -> bool:
    """
    Вспомогательная функция для проверки расширения файла
    """

    # Проверяем имя файла. Оно не должно быть пустым
    if file_name == '':
        return False
    
    # Допустимые расширения (возможно лучше записать в конфиги)
    extentions = set(['.jpg', '.png', '.gif'])

    # Получаем расширение файла
    fl_ext = os.path.splitext(file_name)[1]
    
    # Проверяем, что расширение файла входит в допустимые
    if fl_ext in extentions:
        return True
    
    return False

def proccess_files(files, path: str, count: int = 2) -> dict:
    """
    Функция обработки файлов
    """
    
    status, code, result = True, 200, []

    # Обрабатываем каждый файл
    for fl in files:
        # Получаем текущий файл
        upload_file = files[fl]

        # Получаем имя файла 
        file_name = uuid.uuid4() + '_' + secure_filename(upload_file.filename)
        
        # Валидируем файл
        if validate_file(file_name):
            # Сохраняем путь где будет лежать наш файл
            file_path = os.path.join(path, file_name)

            # Сохраняем файл 
            with open(file_path, 'wb') as fl:
                upload_file.write(upload_file.read())

            # Записываем путь в результат
            result.append(file_path)
        else:
            status, code = False, 400
            break
    
    return {
        'status': status,
        'code': code,
        'result': result
    }


def message_by_code(code: int) -> str:
    """
    Функция возвращает страницу в зависимости от кода
    """
    if not code:
        return ''
    if code == 200:
        return 'Файлы успешно загружены'

    if code == 400:
        return 'Файлы не прошли валидацию'

    if code == 413:
        return 'Слишком большой размер файлов'
