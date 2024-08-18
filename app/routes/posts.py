from app.database.models.post import Post
from fastapi import APIRouter, File, Form, HTTPException, Depends, UploadFile
from odmantic import AIOEngine, ObjectId
from app.database.conn import db
from app.main import UPLOAD_DIRECTORY
import os
from app.utils.user_utils import get_user_by_object_id
from app.utils.token_utils import get_current_user_email

router = APIRouter(prefix="/post")


# Create - 게시글 생성
@router.post("/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(...),
    engine: AIOEngine = Depends(db.get_engine),
    user_email: str = Depends(get_current_user_email),
):
    print("hi")
    print(user_email)
    image_path = os.path.join(UPLOAD_DIRECTORY, image.filename)

    # 이미지 파일 저장
    with open(image_path, "wb") as buffer:
        buffer.write(image.file.read())

    image_url = f"/static/images/{image.filename}"

    user = await get_user_by_object_id(user_email)

    new_post = Post(
        title=title,
        content=content,
        image_url=image_url,
        user_id=user.id,
        nick_name=user.nick_name,
    )

    new_post = await engine.save(new_post)
    return new_post


# Read - 게시글 조회 (ID 기반)
@router.get("/{post_id}")
async def read_post(post_id: ObjectId, engine: AIOEngine = Depends(db.get_engine)):
    post = await engine.find_one(Post, Post.id == post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# Read - 모든 게시글 조회
@router.get("/")
async def read_post(engine: AIOEngine = Depends(db.get_engine)):
    posts = await engine.find(Post)
    if not posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts


# Update - 게시글 수정
@router.put("/{post_id}")
async def update_post(
    post_id: ObjectId, updated_post: Post, engine: AIOEngine = Depends(db.get_engine)
):
    post = await engine.find_one(Post, Post.id == post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    updated_data = updated_post.dict(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(post, key, value)
    await engine.save(post)
    return post


# Delete - 게시글 삭제
@router.delete("/{post_id}")
async def delete_post(post_id: ObjectId, engine: AIOEngine = Depends(db.get_engine)):
    post = await engine.find_one(Post, Post.id == post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await engine.delete(post)
    return post
