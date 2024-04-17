import asyncpg
import requests
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'manager_service/app'))
sys.path.append(str(BASE_DIR / 'messenger_service/app'))

from manager_service.app.main import service_alive as manager_status
from messenger_service.app.main import service_alive as messenger_status

@pytest.mark.asyncio
async def test_database_connection():
    try:
        connection = await asyncpg.connect("postgresql://secUREusER:StrongEnoughPassword)@51.250.26.59:5432/query")
        assert connection
        await connection.close()
    except Exception as e:
        assert False, f"Не удалось подключиться к базе данных: {e}"

@pytest.mark.asyncio
async def test_manager_service_connection():
    r = await manager_status()
    assert r == {'message': 'service alive'}

@pytest.mark.asyncio
async def test_messenger_service_connection():
    r = await messenger_status()
    assert r == {'message': 'service alive'}