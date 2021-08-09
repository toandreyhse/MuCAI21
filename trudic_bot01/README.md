# trudic_bot 

Vlasov, Karavaev, Bakaev et al., 2021. CC BY-NC-ND License 

Для запуска бота нужно:

1. Установить pipenv
    pip install pipenv

2. Установить необходимые библиотеки
    зайти в директорию с файлом Pipfile и ввести команду
    pipenv install 

3. Нужен docker-compose для создания контейнеров баз данных
    зайти в корень проекта и написать
    docker-compose up

4. Зайти в директорию data/db и запустить файл database.py (При первом запуске для создания баз данных)

5. Создать в pgadmin таблицу gino и пользователя

6. Изменить POSTGRESURI в файле databaase.py на ваш

7. Запусть файл app.py в корне проекта

Token бота находится в файле data/config.py
