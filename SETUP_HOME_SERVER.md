# Настройка домашнего сервера

## 1. Настройка Dynamic DNS (No-IP)

1. Зарегистрируйтесь на сайте [No-IP](https://www.noip.com/)
2. Создайте бесплатное доменное имя (например, yourname.ddns.net)
3. Скачайте и установите [No-IP DUC](https://www.noip.com/download)
4. Войдите в программу используя данные вашей учетной записи

## 2. Настройка проброса портов на роутере

1. Узнайте локальный IP-адрес вашего ноутбука:
   - Откройте командную строку (Win+R, cmd)
   - Введите команду: `ipconfig`
   - Найдите IPv4-адрес в разделе вашего сетевого адаптера

2. Настройте проброс портов на роутере:
   - Войдите в панель управления роутером (обычно http://192.168.0.1 или http://192.168.1.1)
   - Найдите раздел "Проброс портов" (Port Forwarding)
   - Добавьте новое правило:
     * Внешний порт: 80
     * Внутренний порт: 5000
     * IP-адрес: [ваш локальный IP]
     * Протокол: TCP

## 3. Настройка файрвола Windows

1. Откройте "Брандмауэр Защитника Windows"
2. Нажмите "Дополнительные параметры"
3. Выберите "Правила для входящих подключений"
4. Нажмите "Создать правило"
5. Выберите:
   - Тип правила: Для порта
   - Протокол TCP, порт 5000
   - Действие: Разрешить подключение
   - Профиль: Все
   - Имя: Flask Web Server

## 4. Запуск сервера

1. Откройте PowerShell от имени администратора
2. Перейдите в директорию проекта:
   ```powershell
   cd D:\face_attendance
   ```
3. Активируйте виртуальное окружение:
   ```powershell
   .\venv_new\Scripts\activate
   ```
4. Запустите сервер:
   ```powershell
   python app.py
   ```

## Проверка доступа

1. Локальный доступ:
   - http://localhost:5000
   - http://[ваш_локальный_IP]:5000

2. Внешний доступ:
   - http://[ваше_имя].ddns.net

## Важные замечания

1. Убедитесь, что ваш ноутбук:
   - Подключен к интернету
   - Не уходит в спящий режим
   - Имеет стабильное питание

2. Безопасность:
   - Используйте сложные пароли
   - Регулярно обновляйте Windows
   - Следите за безопасностью сети

3. Ограничения:
   - Скорость зависит от вашего интернет-подключения
   - При перезагрузке ноутбука нужно перезапускать сервер
   - Возможны проблемы с доступом при смене IP-адреса 