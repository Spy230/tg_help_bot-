import logging
import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import config
from datetime import datetime

# логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

 
WAITING_FOR_REPLY, WAITING_FOR_ISSUE, WAITING_FOR_CATEGORY = range(3)

# Подключение к базе данных
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="products_db"
    )

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я бот техподдержки. Используйте команды для получения информации или связи с поддержкой.'
    )

# Обработчик команды  
async def question(update: Update, context: CallbackContext) -> None:
    response = (
        "Часто задаваемые вопросы:\n"
        "1. Какие у вас есть продукты?\n"
        "2. Как проверить наличие товара на складе?\n"
        "3. Какова ваша политика возврата товаров?\n"
    )
    await update.message.reply_text(response)

# Обработчик команды /info_product
async def info_product(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Введите название продукта, чтобы получить информацию о нём.")

# Обработчик команды /support
async def support(update: Update, context: CallbackContext) -> None:
    response = "Вы можете связаться с нами по электронной почте shesterikovon@gmail.com или по телефону +7951965121.\n\nЕсли у вас есть вопросы или проблемы, оставьте заявку, и мы свяжемся с вами."
    keyboard = [[InlineKeyboardButton("Оставить заявку", callback_data="leave_request")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)

# Обработчик команды /problems  
async def problems(update: Update, context: CallbackContext) -> None:
    response = (
        "Если у вас есть проблемы с товаром, пожалуйста, выберите категорию проблемы и опишите её.\n\n"
        "1. Проблемы с установкой ПО\n"
        "2. Проблема с комплектующими\n"
    )
    keyboard = [
        [InlineKeyboardButton("Проблемы с установкой ПО", callback_data="issue_installation")],
        [InlineKeyboardButton("Проблема с комплектующими", callback_data="issue_components")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)

# Обработчик сообщений от пользователей
async def message_handler(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if context.user_data.get('waiting_for_issue'):
        category = context.user_data.get('issue_category')
        user_issue = text
        user_id = update.message.from_user.id
        username = update.message.from_user.username

        save_user_issue(user_id, username, category, user_issue)

        operator_id = config.OPERATOR_ID
        keyboard = [[InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=operator_id, text=f"Пользователь @{username} оставил заявку по категории '{category}':\n{user_issue}", reply_markup=reply_markup)

        await update.message.reply_text("Спасибо за описание вашей проблемы. Мы постараемся помочь вам как можно скорее.")
        context.user_data['waiting_for_issue'] = False
        return

    product_info = get_product_info(text)
    if product_info:
        await update.message.reply_photo(photo=product_info['photo_url'], caption=product_info['response'])
    else:
        await update.message.reply_text("Продукт не найден. Попробуйте другой запрос.")

# Обработчик нажатий на кнопки
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("reply_"):
        user_id = int(query.data.split("_")[1])
        context.user_data['reply_to_user_id'] = user_id
        await query.message.reply_text("Пожалуйста, введите ваш ответ:", reply_markup=ForceReply())
        return WAITING_FOR_REPLY

    if query.data.startswith("issue_"):
        category = query.data.split("_")[1].replace("installation", "Проблемы с установкой ПО").replace("components", "Проблема с комплектующими")
        await query.edit_message_text(text=f"Пожалуйста, опишите вашу проблему в категории '{category}':", reply_markup=None)
        context.user_data['issue_category'] = category
        context.user_data['waiting_for_issue'] = True
        return WAITING_FOR_ISSUE

    if query.data.startswith("resolved_"):
        user_id = int(query.data.split("_")[1])
        update_issue_status(user_id, 'Задача решена')
        await query.message.reply_text("Спасибо! Мы рады, что ваша проблема решена.")
        return ConversationHandler.END

    if query.data.startswith("not_resolved_"):
        user_id = int(query.data.split("_")[1])
        update_issue_status(user_id, 'Не решена')
        await query.message.reply_text("Спасибо за ваш отзыв. Мы постараемся решить проблему как можно скорее.")
        return ConversationHandler.END

# Обработчик для   ответа от оператора
async def handle_reply(update: Update, context: CallbackContext) -> int:
    user_id = context.user_data.get('reply_to_user_id')
    if user_id:
        reply_text = update.message.text
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Задача решена", callback_data=f"resolved_{user_id}")],
            [InlineKeyboardButton("Не решена", callback_data=f"not_resolved_{user_id}")]
        ])
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Ответ от оператора: {reply_text}",
            reply_markup=reply_markup
        )
        await update.message.reply_text("Ваш ответ отправлен пользователю.")
        context.user_data['reply_to_user_id'] = None
        return ConversationHandler.END
    else:
        await update.message.reply_text("Ошибка: не удалось определить, кому отправить ответ.")
        return ConversationHandler.END

# Обработчик для получения заявки от пользователя
async def handle_issue(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    issue_description = update.message.text
    category = context.user_data.get('issue_category')

    save_user_issue(user_id, username, category, issue_description)

    operator_id = config.OPERATOR_ID
    keyboard = [[InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=operator_id, text=f"Пользователь @{username} оставил заявку по категории '{category}':\n{issue_description}", reply_markup=reply_markup)

    await update.message.reply_text("Ваша заявка отправлена. Мы свяжемся с вами как можно скорее.")
    context.user_data['waiting_for_issue'] = False
    return ConversationHandler.END

# Функция для сохранения заявки пользователя в бд
def save_user_issue(user_id, username, category, issue_description):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_issues (user_id, username, issue_text, created_at, category, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, username, issue_description, datetime.now(), category, 'активный')
        )
        conn.commit()
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения к базе данных: {err}")
    finally:
        if conn:
            conn.close()

#   обновления статуса задачи
def update_issue_status(user_id, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_issues SET status = %s WHERE user_id = %s AND status = 'активный'",
            (status, user_id)
        )
        conn.commit()
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения к базе данных: {err}")
    finally:
        if conn:
            conn.close()

#   получения информации о продукте
def get_product_info(query):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "%" + query.lower() + "%"
        cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE LOWER(%s)", (query,))
        result = cursor.fetchall()

        if result:
            product = result[0]
            response = f"Название: {product['name']}\nОписание: {product['description']}\nЦена: ${product['price']}\n\n"
            return {'response': response, 'photo_url': product['photo_url']}
        else:
            return None

    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения к базе данных: {err}")
        return None

    finally:
        if conn:
            conn.close()

def main() -> None:
    
    app = ApplicationBuilder().token(config.TOKEN).build()

    # обработчик состояний и команд
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            WAITING_FOR_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply)],
            WAITING_FOR_ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("question", question))
    app.add_handler(CommandHandler("info_product", info_product))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("problems", problems))  # Обработчик для новой команды /problems
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
