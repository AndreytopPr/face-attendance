# Инструкция по развертыванию Face Attendance System

## 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install python3-pip python3-venv nginx git supervisor -y
```

## 2. Настройка проекта

```bash
# Создание директории проекта
sudo mkdir -p /var/www/face_attendance
sudo chown -R $USER:$USER /var/www/face_attendance

# Клонирование репозитория
cd /var/www/face_attendance
git clone [URL_ВАШЕГО_РЕПОЗИТОРИЯ] .

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание директории для логов
mkdir logs
```

## 3. Настройка Nginx

```bash
# Копирование конфигурации Nginx
sudo cp nginx.conf /etc/nginx/sites-available/face_attendance
sudo ln -s /etc/nginx/sites-available/face_attendance /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Удаление дефолтной конфигурации

# Проверка конфигурации и перезапуск Nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 4. Настройка systemd сервиса

```bash
# Копирование файла сервиса
sudo cp face_attendance.service /etc/systemd/system/

# Перезагрузка systemd и запуск сервиса
sudo systemctl daemon-reload
sudo systemctl start face_attendance
sudo systemctl enable face_attendance
```

## 5. SSL сертификат (опционально)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com
```

## 6. Проверка статуса

```bash
# Проверка статуса сервисов
sudo systemctl status nginx
sudo systemctl status face_attendance

# Просмотр логов
tail -f logs/error.log
tail -f logs/access.log
```

## Важные замечания

1. Замените `your-domain.com` в nginx.conf на ваш домен или IP-адрес
2. Убедитесь, что порты 80 и 443 открыты в файрволле
3. Для работы с камерой может потребоваться установка дополнительных пакетов:
   ```bash
   sudo apt install libopencv-dev python3-opencv
   ```
4. При использовании на production сервере рекомендуется:
   - Отключить debug режим в Flask
   - Настроить безопасные заголовки в Nginx
   - Регулярно обновлять систему и зависимости
   - Настроить резервное копирование базы данных

## Обновление приложения

```bash
cd /var/www/face_attendance
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart face_attendance
``` 