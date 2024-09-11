from datetime import datetime
import logging
from typing import List
from app.database.models.post import Post
from fastapi import APIRouter, File, Form, HTTPException, Depends, UploadFile
from odmantic import AIOEngine, ObjectId
from app.database.conn import db
from app.database.models.user import User
from app.utils.settings import UPLOAD_DIRECTORY
import os
from app.dtos.post import PostUpdate
from app.utils.user_utils import get_user_by_object_id
from app.utils.token_utils import get_current_user_id

router = APIRouter(prefix="/post")
MAX_VIDEO_SIZE = 30 * 1024 * 1024  # 50MB


# Create - 게시글 생성
@router.post("/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    tags: List[str] = Form(...),
    files: List[UploadFile] = File(...),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: str = Depends(get_current_user_id),
):
    # 이미지 파일의 개수 제한
    image_files = [file for file in files if file.content_type.startswith("image/")]
    if len(image_files) > 5:
        raise HTTPException(
            status_code=400, detail="최대 5개의 이미지 파일만 업로드할 수 있습니다."
        )

    file_urls = []
    for file in files:
        # 파일 MIME 타입 확인
        file_type = file.content_type

        if file_type.startswith("video/"):
            # 파일 크기 검사
            contents = await file.read()
            file_size = len(contents)
            await file.seek(0)  # 파일 포인터를 다시 처음으로 이동

            if file_size > MAX_VIDEO_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Video file size exceeds the maximum limit of {MAX_VIDEO_SIZE // (1024 * 1024)}MB.",
                )

        # 이름 중복 제거 위한 시간 접두사
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{file.filename}"

        # 중복된 파일명 처리하기
        if file_type.startswith("image/"):
            file_path = os.path.join(UPLOAD_DIRECTORY, "images", new_filename)
            file_url = f"/static/images/{new_filename}"
        elif file_type.startswith("video/"):
            file_path = os.path.join(UPLOAD_DIRECTORY, "videos", new_filename)
            file_url = f"/static/videos/{new_filename}"
        else:
            raise HTTPException(
                status_code=400, detail=f"{file_type} is an unsupported file type"
            )

        # 파일 저장
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        file_urls.append(file_url)

    # 작성자 정보
    user = await engine.find_one(User, User.id == user_id)

    new_post = Post(
        title=title,
        content=content,
        file_urls=file_urls,
        tags=tags,
        user_id=user.id,
        nick_name=user.nick_name,
    )

    new_post = await engine.save(new_post)

    # 로그 출력
    logging.info(
        f"새 게시글이 생성되었습니다: 제목 - {new_post.title}, 작성자 - {new_post.nick_name}, 파일 URL - {new_post.file_urls}"
    )

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
    post_id: ObjectId,
    post_update: PostUpdate,
    engine: AIOEngine = Depends(db.get_engine),
):
    # 수정할 게시글 정보
    post = await engine.find_one(Post, Post.id == post_id)

    # 존재하지 않을 시
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 업데이트할 필드 설정
    post.title = post_update.title
    post.content = post_update.content
    post.tags = post_update.tags

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


# 게시글 좋아요
@router.post("/{post_id}/like")
async def like_post(
    post_id: ObjectId,
    engine: AIOEngine = Depends(db.get_engine),
    user_email: str = Depends(get_current_user_id),  # 현재 사용자 이메일
):
    # 현재 사용자 가져오기
    user = await get_user_by_object_id(user_email)

    # 게시글 정보 가져오기
    post = await engine.find_one(Post, Post.id == post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 이미 좋아요를 눌렀는지 확인
    if user.id in post.liked_by:
        # 이미 좋아요를 눌렀다면, 좋아요 취소
        post.liked_by.remove(user.id)
        post.likes_count -= 1
        liked = False
    else:
        # 좋아요 추가
        post.liked_by.append(user.id)
        post.likes_count += 1
        liked = True

    await engine.save(post)

    return {"liked": liked, "post": post}
