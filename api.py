from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
import redis
import json

# Redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

app = FastAPI()


class User(BaseModel):
    id: int
    name: str
    city: str = None
    age: int = None

    class Config:
        extra = "ignore"  # ignore additional fields


@app.put("/user/{user_id}")
def register_user(user_id: int = Path(...), user: User):
    # Verify path id matches the payload id
    if user.id != user_id:
        raise HTTPException(status_code=400, detail="Path id and user.id must match.")

    # Save user to Redis as a JSON string using key 'user:{id}'
    key = f"user:{user_id}"
    redis_client.set(key, user.json())
    return {"msg": "User registered", "id": user_id}


@app.get("/user")
def get_users(size: int = Query(None)):
    # Get all users stored in Redis with key pattern 'user:*'
    keys = redis_client.keys("user:*")
    users = []
    for key in keys:
        data = redis_client.get(key)
        if data:
            user_data = json.loads(data)
            users.append(user_data)

    if size is not None:
        # Return only id and name for the first 'size' users
        users = [{"id": u["id"], "name": u["name"]} for u in users[:size]]
    return users