from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError
from app.db.mongodb import get_database
from app.models import LoginRequest, RegisterRequest, TokenResponse, UserPublic, UserUpdate
from app.security import create_access_token, get_current_user, hash_password, new_id, verify_password

router = APIRouter(tags=["authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    user = {"id": new_id(), "name": payload.name.strip(), "email": str(payload.email).lower(), "password": hash_password(payload.password)}
    try:
        await get_database().users.insert_one(user)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email is already registered") from exc
    return TokenResponse(access_token=create_access_token(user["id"]), user=UserPublic(**user))

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await get_database().users.find_one({"email": str(payload.email).lower()})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user["id"]), user=UserPublic(**user))

@router.put("/user/update", response_model=UserPublic)
async def update_user(payload: UserUpdate, current_user: dict = Depends(get_current_user)):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="At least one field is required")
    if "name" in changes:
        changes["name"] = changes["name"].strip()
    if "email" in changes:
        changes["email"] = str(changes["email"]).lower()
    if "password" in changes:
        changes["password"] = hash_password(changes["password"])
    try:
        await get_database().users.update_one({"id": current_user["id"]}, {"$set": changes})
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email is already registered") from exc
    updated_user = await get_database().users.find_one({"id": current_user["id"]})
    return UserPublic(**updated_user)

@router.delete("/user/delete")
async def delete_user(current_user: dict = Depends(get_current_user)):
    database = get_database()
    await database.items.delete_many({"owner_id": current_user["id"]})
    result = await database.users.delete_one({"id": current_user["id"]})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User and associated items deleted"}
