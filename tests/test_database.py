import pytest
import pytest_asyncio
import os
import aiosqlite
from database import AnnoyanceDB

# Use a temporary file for the test database
TEST_DB = "test_annoy_o_matic.db"

@pytest_asyncio.fixture
async def db():
    # Setup: Create DB instance
    database = AnnoyanceDB(db_name=TEST_DB)
    # Ensure table is created (it's done in __init__ but async connection happens in methods)
    # We might need to yield it after a brief wait or just use it.
    # actually AnnoyanceDB in my refactor has an awaitable connect or init?
    # Wait, my previous refactor for database.py was:
    # async def _connect(self): ...
    # async def initialize(self): ...
    # So I need to call initialize()
    
    await database.initialize()
    yield database
    
    # Teardown: Close and remove file
    await database.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.mark.asyncio
async def test_add_and_get_target(db):
    user_id = 123456789
    
    # Test Adding
    result = await db.add_target(user_id)
    assert result is True, "Failed to add new target"
    
    # Test Adding Duplicate
    result_dup = await db.add_target(user_id)
    assert result_dup is False, "Should return False for duplicate target"
    
    # Test Retrieving
    settings = await db.get_target_settings(user_id)
    assert settings is not None
    assert settings['user_id'] == user_id
    assert settings['annoy_methods'] == ['message', 'reaction'] # Default

@pytest.mark.asyncio
async def test_update_settings(db):
    user_id = 987654321
    await db.add_target(user_id)
    
    # Test Update Messages
    msgs = ["Test 1", "Test 2"]
    await db.update_specific_reply(user_id, msgs)
    settings = await db.get_target_settings(user_id)
    assert settings['specific_reply'] == msgs
    
    # Test Update Methods
    methods = ['reaction']
    await db.update_annoy_methods(user_id, methods)
    settings = await db.get_target_settings(user_id)
    assert settings['annoy_methods'] == methods

@pytest.mark.asyncio
async def test_remove_target(db):
    user_id = 111222333
    await db.add_target(user_id)
    
    result = await db.remove_target(user_id)
    assert result is True
    
    settings = await db.get_target_settings(user_id)
    assert settings is None
