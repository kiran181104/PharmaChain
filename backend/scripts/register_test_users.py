import asyncio
from app.database import get_database, connect_to_mongo
from app.schemas import UserCreate, RoleEnum

users = [
    {
        "walletAddress": "0x992e98ff8098a6b23e96e8b8b2a49ddc020264c34580362bc3a2d406cf13577e", # Account 1 from Ganache
        "role": RoleEnum.MANUFACTURER,
        "name": "ABC Pharmaceuticals"
    },
    {
        "walletAddress": "0x59c0241f49df5ad53f3a2248c11a7a9bf05468e5ffdce3d1590f49a1f5dd564c", # Account 2
        "role": RoleEnum.DISTRIBUTOR,
        "name": "XYZ Distributors"
    },
    {
        "walletAddress": "0xBc36A1AE6f454ce4250f04F1dA901AaF87Cd6b36", # Account 3
        "role": RoleEnum.PHARMACY,
        "name": "HealthCare Pharmacy"
    },
    {
        "walletAddress": "0x2a2df084243741966fbaf5150f019b7e64d7e1bd7bbc62e4b9ad9b977b0fd3f7", # Account 4
        "role": RoleEnum.CONSUMER,
        "name": "John Doe"
    },
    {
        "walletAddress": "0xf79676a0d7169dc5521014c3062fab289622fa1bc72d7714e36f61d068999593", # Account 5
        "role": RoleEnum.REGULATOR,
        "name": "Drug Regulatory Authority"
    }
]

async def register_users():
    await connect_to_mongo()
    db = get_database()
    
    for user in users:
        await db.users.insert_one({
            "walletAddress": user["walletAddress"],
            "role": user["role"].value,
            "name": user["name"],
            "isRegistered": True
        })
        print(f"Registered: {user['name']}")

asyncio.run(register_users())