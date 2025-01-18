from db import db
from tests.model import User


async def test_user_creation():
    await db.init()

    async with db.get_session() as session:
        try:
            user = await User.create_user(
                session=session,
                chat_id=123456789,
                username="test_user",
                first_name="Test",
                language="en",
                added_by="admin",
            )
            print(f"User created: {user.chat_id}")
            retrieved_user = await User.get_user(session=session, chat_id=123456789)
            if retrieved_user:
                print(f"Retrieved user: {retrieved_user.chat_id}")
        finally:
            await db.dispose()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_user_creation())
