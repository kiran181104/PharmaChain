import asyncio
from app.database import get_database, connect_to_mongo

async def check_db():
    await connect_to_mongo()
    db = get_database()

    # Check drug storage
    drugs = await db.drug_composition_storage.find().to_list(length=None)
    print(f'Found {len(drugs)} drugs in storage:')
    for d in drugs:
        print(f'  Batch: {d["batchId"]}, Name: {d.get("drugName", "Unknown")}')

    # Check users
    users = await db.users.find().to_list(length=None)
    print(f'\nFound {len(users)} users:')
    for u in users:
        print(f'  {u.get("name", "Unknown")}: {u.get("role", "Unknown")}')

asyncio.run(check_db())