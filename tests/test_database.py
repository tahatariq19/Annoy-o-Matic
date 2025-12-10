import pytest
import pytest_asyncio
import os
from database import AnnoyanceDB

# Use an in-memory database for testing
TEST_DB = ":memory:"

@pytest_asyncio.fixture
async def db():
    database = AnnoyanceDB(db_name=TEST_DB)
    yield database
    await database.close()

@pytest.mark.asyncio
async def test_add_target(db):
    user_id = 12345
    result = await db.add_target(user_id)
    assert result is True
    
    # Verify persistence
    settings = await db.get_target_settings(user_id)
    assert settings is not None
    assert settings['user_id'] == user_id

@pytest.mark.asyncio
async def test_add_duplicate_target(db):
    user_id = 999
    await db.add_target(user_id)
    result = await db.add_target(user_id)
    assert result is False  # Should fail on duplicate

@pytest.mark.asyncio
async def test_update_specific_reply(db):
    user_id = 111
    await db.add_target(user_id)
    
    replies = ["Test Reply 1", "Test Reply 2"]
    await db.update_specific_reply(user_id, replies)
    
    settings = await db.get_target_settings(user_id)
    assert settings['specific_reply'] == replies

@pytest.mark.asyncio
async def test_remove_target(db):
    user_id = 555
    await db.add_target(user_id)
    
    result = await db.remove_target(user_id)
    assert result is True
    
    settings = await db.get_target_settings(user_id)
    assert settings is None
