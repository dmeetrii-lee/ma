import requests

# URL-адреса для сервисов сообщений
service_url_8001 = 'http://localhost:8001'
service_url_8000 = 'http://localhost:8000'

# Эндпоинты сервиса на порту 8001
login_url = f'{service_url_8001}/login'
send_message_url = f'{service_url_8001}/send_message'
get_messages_with_user_url = f'{service_url_8001}/get_messages_with_user'
get_messages_to_user_url = f'{service_url_8001}/get_messages_to_user'

# Эндпоинты сервиса на порту 8000
get_messages_url = f'{service_url_8000}/get_messages'
get_messages_by_sender_url = f'{service_url_8000}/get_messages_by_sender'
get_messages_by_receiver_url = f'{service_url_8000}/get_messages_by_reciever'
delete_message_url = f'{service_url_8000}/delete_message'

# Тестовые данные
user_name = "JohnDoe"
receiver_name = "JaneDoe"
message_text = "Hello, this is a test message."

def test_login():
    res = requests.post(f"{login_url}", params={"name": user_name})
    assert res.status_code == 200
    assert f"You logged in as {user_name}" in res.text

def test_send_message():
    res = requests.post(f"{send_message_url}", params={"receiver_name": receiver_name, "text": message_text})
    assert res.status_code == 200
    assert res.text == '"Success"'

def test_get_messages_with_user():
    res = requests.get(f"{get_messages_with_user_url}", params={"username": receiver_name})
    assert res.status_code == 200
    messages = res.json()
    assert any(msg for msg in messages if msg['sender_name'] == user_name and msg['receiver_name'] == receiver_name)

def test_get_messages_to_user():
    res = requests.get(f"{get_messages_to_user_url}", params={"username": receiver_name})
    assert res.status_code == 200
    messages = res.json()
    assert any(msg for msg in messages if msg['sender_name'] == user_name and msg['receiver_name'] == receiver_name)

def test_get_messages():
    res = requests.get(f"{get_messages_url}")
    assert res.status_code == 200
    messages = res.json()
    assert len(messages) > 0

def test_get_messages_by_sender():
    res = requests.get(f"{get_messages_by_sender_url}", params={"name": user_name})
    assert res.status_code == 200
    messages = res.json()
    assert any(msg for msg in messages if msg['sender_name'] == user_name and msg['receiver_name'] == receiver_name)

def test_get_messages_by_receiver():
    res = requests.get(f"{get_messages_by_receiver_url}", params={"name": receiver_name})
    assert res.status_code == 200
    messages = res.json()
    assert any(msg for msg in messages if msg['sender_name'] == user_name and msg['receiver_name'] == receiver_name)

def test_delete_message():
    # Предварительно получаем ID сообщения для удаления
    messages = requests.get(f"{get_messages_url}").json()
    message_id = next((msg['id'] for msg in messages if msg['sender_name'] == user_name and msg['receiver_name'] == receiver_name), None)
    res = requests.delete(f"{delete_message_url}?message_id={message_id}")
    assert res.status_code == 200
    assert res.text == '"Success"'