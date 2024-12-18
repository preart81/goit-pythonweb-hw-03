# Docker-команда FROM вказує базовий образ контейнера
# slim - мінімальний образ
FROM python:3.12-slim

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Скопіюємо інші файли в робочу директорію контейнера
COPY ./goit_pythonweb_hw_03 $APP_HOME
COPY ./poetry.lock $APP_HOME
COPY ./pyproject.toml $APP_HOME

# Оновлюємо pip
RUN pip install --upgrade pip

# Встановлюємо залежності
RUN pip install poetry
RUN poetry install

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 3000

# Запустимо наш застосунок всередині контейнера
ENTRYPOINT ["poetry", "run", "python", "main.py"]
