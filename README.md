# Telegram Support Bot

Telegram Support Bot — это телеграмм бот,   для обработки заявок и вопросов пользователей. Бот позволяет пользователям оставлять заявки, общаться с операторами и получать информацию о продуктах.

## Технологический стек

- **Python** 
- **python-telegram-bot** 
- **MySQL** 
- **Logging**
- **Asyncio**

## Основные функции

1. **Начало работы**: Команда `/start`  
2. **Часто задаваемые вопросы**: Команда `/question`  
3. **Информация о продукте**: Команда `/info_product` 
4. **Связь с поддержкой**: Команда `/support`  
5. **Обработка проблем**: Команда `/problems`  
6. **Обработка заявок и ответов операторов**

## Установка

1. **Клонирование репозитория:**

    ```bash
    git clone https://github.com/ваш-пользователь/telegram-support-bot.git
    ```

5. **Настройка файла `config.py`:**
   
   - Создать файл `config.py` для сохранение токена бота и id оператора.
     ```bash
     TOKEN = ' '
     OPERATOR_ID = ''
     ```
   id своего профиля телеграмма,можно узнать с помощью бота @userinfobot
6. **база данных MySQL:**

   - название  базы данных `products_db`.

   - названиек таблицы для сохранение заявок пользователя : `user_issues`:

    ```sql
    CREATE TABLE user_issues (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        username VARCHAR(255) NOT NULL,
        issue_text TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        category VARCHAR(255),
        status VARCHAR(50) DEFAULT 'активный'
    );
    ```

   - название таблицы для хранения информации : `products` :

    ```sql
    CREATE TABLE products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2),
        photo_url VARCHAR(255)
    );
    ```



## Примеры использования

- **Запуск бота**
  ![image](https://github.com/user-attachments/assets/0001e85d-bb68-47c2-95ca-c7879cde7a97)
- **Получение информации о продукте**
  ![image](https://github.com/user-attachments/assets/f0568912-2699-4941-8d2d-b126fe11f649)
- **обращение в техподдержку**
  ![image](https://github.com/user-attachments/assets/976b9215-e9f7-404d-91ea-17dfc58805f9)
- **Оставление заявки**
![image](https://github.com/user-attachments/assets/73cda6b2-4338-40ad-b233-b7bb296948a4)
- **Описание проблемы**
  ![image](https://github.com/user-attachments/assets/53c8808c-c888-45d3-a3f8-fa779c1262e2)
- **уведомление оператору**
  ![image](https://github.com/user-attachments/assets/cb172c09-aaff-45e9-a471-8d9fa4ad6be9)
- **Ответ оператора**
  ![image](https://github.com/user-attachments/assets/e5e15fd6-2dd7-4393-8596-234bcb540d57)
- **уведомление пользователю**
  ![image](https://github.com/user-attachments/assets/4b4ac384-42e6-473a-b8e8-eea2b8efa3ef)
- **Запись в бд**
  ![image](https://github.com/user-attachments/assets/15e9bcf8-12aa-478b-84e1-ae53fe764e20)

## Лицензия

Этот проект находится под лицензией MIT License. Подробности смотрите в файле LICENSE.
