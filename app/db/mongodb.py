from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase[Any] | None = None

async def connect_to_mongodb() -> None:
    global client, database
    client = AsyncIOMotorClient(settings.mongo_uri)
    await client.admin.command("ping")
    database = client[settings.mongo_db_name]
    await database.users.create_index("email", unique=True)
    await database.items.create_index([("owner_id", 1), ("id", 1)], unique=True)

async def close_mongodb() -> None:
    if client is not None:
        client.close()

def get_database() -> AsyncIOMotorDatabase[Any]:
    if database is None:
        raise RuntimeError("MongoDB has not been initialized")
    return database
