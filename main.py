from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# For Random String Generation
import random
import string

# Async monogodb connection
from motor.motor_asyncio import AsyncIOMotorClient

# For redirecting to the main URL
from fastapi.responses import RedirectResponse

# For Model Creations
from pydantic import BaseModel

# For Environment Variables
from dotenv import load_dotenv
import os

load_dotenv()


con_str = os.getenv("DATABASE_URL")
client = AsyncIOMotorClient(con_str)
db = client["url_shortner"]
collection = db["url"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLItem(BaseModel):
    mainURL: str

@app.post("/")
async def shortenURL(item: URLItem):
    mainURL = item.mainURL  # Extract mainURL from request body
    SLUG = createSLUG()
    
    find = await collection.find_one({"mainURL": mainURL})
    if find:
        return {"mainURL": find["mainURL"], "shortURL": find["shortURL"]}
    else:
        shortURL = f"http://localhost:8000/{SLUG}"
        await collection.insert_one({"mainURL": mainURL, "shortURL": shortURL})
        return {"mainURL": mainURL, "shortURL": shortURL}


# class Item(BaseModel):
#     name: str
#     age: int



# @app.post("/")
#async def shortenURL(item: Item):
# async def shortenURL(mainURL):
#     SLUG = createSLUG()
#     find = await collection.find_one({"mainURL": mainURL})
#     if find:
#         if mainURL == find["mainURL"]:
#             return find["shortURL"]
#     else:
#         await collection.insert_one({"mainURL": mainURL, "shortURL": SLUG})
#         return {"mainURL": mainURL, "shortURL": f"http://localhost:8000/{SLUG}"}

    # await collection.insert_one(item.model_dump())
    # return item
    
def createSLUG():
    length = 5
    randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))
    return randomString

@app.get("/{SLUG}")
async def redirectURL(SLUG):
    result = await collection.find_one({"shortURL": f"http://localhost:8000/{SLUG}"})
    return RedirectResponse(url=result["mainURL"])
