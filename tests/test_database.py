import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from data import conf
from tests.db_system import AsyncDatabase
from tests.model import User



@pytest_asyncio.fixture(scope="function")
async def db():
    db = AsyncDatabase(db_url=conf.db.build_db_url())
    await db.init()
    yield db
    await db.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(db: AsyncDatabase):
    async with db.get_session() as session:
        yield session


@pytest.mark.asyncio
async def test_create_and_retrieve_user(session: AsyncSession):
    chat_id = 987654321
    username = "test_user"
    first_name = "Test"
    language = "en"
    added_by = "admin"

    user = await User.create_user(
        session=session,
        chat_id=chat_id,
        username=username,
        first_name=first_name,
        language=language,
        added_by=added_by,
    )

    assert user is not None
    assert user.chat_id == chat_id
    assert user.username == username

    retrieved_user = await User.get_user(session=session, chat_id=chat_id)
    assert retrieved_user is not None
    assert retrieved_user.chat_id == chat_id
    assert retrieved_user.username == username
