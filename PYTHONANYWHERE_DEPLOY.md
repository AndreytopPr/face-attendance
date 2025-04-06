# Развертывание на Python Anywhere

## 1. Регистрация и настройка

1. Зарегистрируйтесь на [PythonAnywhere](https://www.pythonanywhere.com)
2. После входа в систему перейдите в раздел "Web"
3. Нажмите "Add a new web app"
4. Выберите:
   - Python 3.8
   - Manual configuration (не выбирайте Django)

## 2. Настройка виртуального окружения

В консоли Python Anywhere выполните:

```bash
# Создание виртуального окружения
mkvirtualenv --python=/usr/bin/python3.8 face_attendance_env

# Активация виртуального окружения
workon face_attendance_env

# Установка зависимостей
pip install flask sqlalchemy opencv-python-headless numpy gunicorn
```

## 3. Загрузка кода

1. В разделе "Files" создайте новую директорию:
   ```bash
   mkdir face_attendance
   cd face_attendance
   ```

2. Загрузите все файлы проекта через веб-интерфейс PythonAnywhere:
   - app.py
   - config.py
   - requirements.txt
   - Директорию templates/
   - Директорию static/ (если есть)

## 4. Настройка WSGI файла

1. Откройте WSGI configuration file (ссылка будет в разделе Web)
2. Замените содержимое на:

```python
import os
import sys

# Добавляем путь к вашему приложению
path = '/home/ваш_username/face_attendance'
if path not in sys.path:
    sys.path.append(path)

# Устанавливаем переменную окружения
os.environ['FLASK_ENV'] = 'production'

# Импортируем ваше приложение
from app import app as application
```

## 5. Настройка веб-приложения

В разделе "Web":

1. Установите "Source code" и "Working directory":
   - Source code: /home/ваш_username/face_attendance
   - Working directory: /home/ваш_username/face_attendance

2. Укажите путь к виртуальному окружению:
   - Virtualenv: /home/ваш_username/.virtualenvs/face_attendance_env

3. В разделе "Static files" добавьте:
   - URL: /static/
   - Directory: /home/ваш_username/face_attendance/static/

## 6. Запуск приложения

1. Перейдите в раздел "Web"
2. Нажмите "Reload" для перезапуска приложения

## 7. Проверка работы

1. Откройте ваш сайт по адресу: username.pythonanywhere.com
2. Проверьте:
   - Открывается ли главная страница
   - Работает ли камера через браузер
   - Можно ли регистрировать студентов
   - Работает ли журнал посещаемости

## Важные замечания

1. На бесплатном тарифе:
   - Сайт будет доступен по адресу username.pythonanywhere.com
   - Есть ограничения на CPU время
   - Сайт может "засыпать" после периода неактивности

2. Для работы с камерой:
   - Убедитесь, что пользователи дают разрешение на доступ к камере в браузере
   - Проверьте работу на разных устройствах (ПК, телефоны)

3. База данных:
   - SQLite база данных будет храниться в директории проекта
   - Регулярно делайте резервные копии базы

## Обновление приложения

1. Загрузите новые файлы через веб-интерфейс
2. Перейдите в раздел "Web"
3. Нажмите "Reload" для применения изменений 