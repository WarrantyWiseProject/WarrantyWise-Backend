from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from app.db.mongodb import get_database
from app.models import ItemCreate, ItemPublic, ItemUpdate
from app.security import get_current_user, new_id
from app.services.google_drive import upload_photo

router = APIRouter(tags=["items"])

def public_item(item: dict) -> ItemPublic:
    return ItemPublic(**{key: item.get(key) for key in ("id", "item_name", "date_purchased", "warranty_date", "photo", "photo_url")})

@router.post("/create", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
async def create_item(request: Request, current_user: dict = Depends(get_current_user), photo: UploadFile | None = File(None)):
    if request.headers.get("content-type", "").startswith("application/json"):
        payload = ItemCreate.model_validate(await request.json())
    else:
        form = await request.form()
        payload = ItemCreate(item_name=form.get("item_name", ""), date_purchased=form.get("date_purchased", ""), warranty_date=form.get("warranty_date", ""), photo_url=form.get("photo_url"))
    photo_url = payload.photo_url
    if photo:
        try:
            photo_url = await upload_photo(photo)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    item = {**payload.model_dump(), "id": new_id(), "owner_id": current_user["id"], "photo": bool(photo_url), "photo_url": photo_url}
    await get_database().items.insert_one(item)
    return public_item(item)

@router.get("/get-all", response_model=list[ItemPublic])
async def get_all_items(current_user: dict = Depends(get_current_user)):
    return [public_item(item) async for item in get_database().items.find({"owner_id": current_user["id"]}).sort("date_purchased", 1)]

@router.get("/get-one", response_model=ItemPublic)
async def get_one_item(item_id: str = Query(..., alias="id"), current_user: dict = Depends(get_current_user)):
    item = await get_database().items.find_one({"id": item_id, "owner_id": current_user["id"]})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return public_item(item)

@router.put("/update", response_model=ItemPublic)
async def update_item(payload: ItemUpdate, item_id: str = Query(..., alias="id"), current_user: dict = Depends(get_current_user)):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="At least one field is required")
    if "photo_url" in changes:
        changes["photo"] = bool(changes["photo_url"])
    result = await get_database().items.update_one({"id": item_id, "owner_id": current_user["id"]}, {"$set": changes})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Item not found")
    return public_item(await get_database().items.find_one({"id": item_id, "owner_id": current_user["id"]}))

@router.delete("/delete")
async def delete_item(item_id: str = Query(..., alias="id"), current_user: dict = Depends(get_current_user)):
    result = await get_database().items.delete_one({"id": item_id, "owner_id": current_user["id"]})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

@router.delete("/bulk-delete")
async def bulk_delete_items(ids: list[str], current_user: dict = Depends(get_current_user)):
    result = await get_database().items.delete_many({"id": {"$in": ids}, "owner_id": current_user["id"]})
    return {"message": "Items deleted", "deleted_count": result.deleted_count}
