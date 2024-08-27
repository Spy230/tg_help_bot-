import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Импорт функций из файла bot.py
from bot import (
    get_db_connection,
    save_user_issue,
    update_issue_status,
    get_product_info,
    start,
    question,
    info_product, 
    support,
    problems,
    message_handler,
    button,
    handle_reply,
    handle_issue
)

class TestBotFunctions(unittest.TestCase):

    @patch('bot.mysql.connector.connect')
    def test_get_db_connection(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        conn = get_db_connection()
        self.assertEqual(conn, mock_conn)
        mock_connect.assert_called_once_with(
            host="localhost",
            user="root",
            password="",
            database="products_db"
        )

    @patch('bot.get_db_connection')
    def test_save_user_issue(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        user_id = 123
        username = 'test_user'
        category = 'Test Category'
        issue_description = 'Test issue'
        
        #  фиксированное время
        fixed_time = datetime(2024, 8, 26, 16, 5, 12)
        with patch('bot.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_time
            save_user_issue(user_id, username, category, issue_description)
            mock_cursor.execute.assert_called_once_with(
                "INSERT INTO user_issues (user_id, username, issue_text, created_at, category, status) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, username, issue_description, fixed_time, category, 'активный')
            )
            mock_conn.commit.assert_called_once()

    @patch('bot.get_db_connection')
    def test_update_issue_status(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        user_id = 123
        status = 'Задача решена'
        update_issue_status(user_id, status)
        mock_cursor.execute.assert_called_once_with(
            "UPDATE user_issues SET status = %s WHERE user_id = %s AND status = 'активный'",
            (status, user_id)
        )
        mock_conn.commit.assert_called_once()

    @patch('bot.get_db_connection')
    def test_get_product_info(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        mock_cursor.fetchall.return_value = [{
            'name': 'Test Product',
            'description': 'Product Description',
            'price': 123.45,
            'photo_url': 'http://example.com/photo.jpg'
        }]
        result = get_product_info('test')
        expected_result = {
            'response': 'Название: Test Product\nОписание: Product Description\nЦена: $123.45\n\n',
            'photo_url': 'http://example.com/photo.jpg'
        }
        self.assertEqual(result, expected_result)

@patch('bot.context.bot.send_message')
@patch('bot.update_issue_status')
def test_handle_reply(self, mock_update_issue_status, mock_send_message):
    update = MagicMock()
    context = MagicMock()
    context.user_data = {'reply_to_user_id': 123}
    update.message.text = 'Test reply'
    
    handle_reply(update, context )
    
    mock_send_message.assert_called_once_with(
        chat_id=123,
        text='Ответ от оператора: Test reply',
        reply_markup=MagicMock() 
    )
    mock_update_issue_status.assert_called_once_with(123, 'активный')
 

if __name__ == '__main__':
    unittest.main(verbosity=2)
