from datetime import datetime
import logging
from typing import List
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Depends,
    Path,
    Request,
    UploadFile,
)
from odmantic import AIOEngine, ObjectId
import redis.asyncio as aioredis
from app.database.conn import db
from app.database.models.post import MediaFile, Post
from app.database.models.user import User
from app.database.models.comment import Comment
from app.utils.media_utils import create_video_thumbnail
from app.utils.settings import UPLOAD_DIRECTORY
import os
from app.dtos.post import CreateComment, PostUpdate, UpdateComment
from app.utils.time_util import get_seconds_until_midnight_kst
from app.utils.user_utils import (
    decrement_feather,
    get_user_by_object_id,
    increment_feather,
)
from app.utils.token_utils import get_current_user_id, verify_admin

# 로거 설정
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/post")
MAX_VIDEO_SIZE = 30 * 1024 * 1024  # 50MB


# FastAPI의 Request 객체를 통해 Redis 인스턴스에 접근
async def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


# Create - 게시글 생성
@router.post("/")
async def create_post(
    title: str = Form(..., description="게시글의 제목", example="새로운 게시글"),
    content: str = Form(
        ..., description="게시글의 내용", example="이것은 게시글의 내용입니다."
    ),
    tags: List[str] = Form(
        ..., description="게시글에 추가할 태그들", example=["Python", "FastAPI"]
    ),
    files: List[UploadFile] = File(
        ..., description="업로드할 이미지 또는 비디오 파일들"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: ObjectId = Depends(get_current_user_id),
):
    try:
        # 이미지 파일의 개수 제한
        image_files = [file for file in files if file.content_type.startswith("image/")]
        if len(image_files) > 5:
            raise HTTPException(
                status_code=400, detail="최대 5개의 이미지 파일만 업로드할 수 있습니다."
            )

        file_objects = []
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
                        detail=f"비디오 파일은 {MAX_VIDEO_SIZE // (1024 * 1024)}MB를 초과할 수 없습니다.",
                    )

            # 이름 중복 제거 위한 시간 접두사
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = f"{timestamp}_{file.filename}"

            # 중복된 파일명 처리하기
            if file_type.startswith("image/"):
                file_path = os.path.join(UPLOAD_DIRECTORY, "images", new_filename)
                file_url = f"/static/images/{new_filename}"
                thumbnail_url = None

            elif file_type.startswith("video/"):
                file_path = os.path.join(UPLOAD_DIRECTORY, "videos", new_filename)
                file_url = f"/static/videos/{new_filename}"

                # 비디오일 경우 썸네일 URL 생성
                thumbnail_path = os.path.join(
                    UPLOAD_DIRECTORY, "thumbnails", f"{new_filename}_thumbnail.jpg"
                )
                thumbnail_url = f"/static/thumbnails/{new_filename}_thumbnail.jpg"
            else:
                raise HTTPException(
                    status_code=400, detail=f"{file_type} is an unsupported file type"
                )

            # 파일 저장
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            # 파일이 저장된 후 비디오일 경우 썸네일 생성
            if file_type.startswith("video/"):
                create_video_thumbnail(file_path, thumbnail_path)

            # MediaFile 객체 생성 및 리스트에 추가
            file_object = MediaFile(
                url=file_url,
                file_type=file_type.split("/")[0],
                thumbnail_url=thumbnail_url,
            )
            file_objects.append(file_object)

        # 작성자 정보
        user = await engine.find_one(User, User.id == user_id)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"ID가 '{user_id}'인 사용자를 찾을 수 없습니다."
            )

        new_post = Post(
            title=title,
            content=content,
            files=file_objects,
            tags=tags,
            user_id=user.id,
            nick_name=user.nick_name,
        )

        # 게시글 작성 시 깃털 증가
        await increment_feather(user.id)

        new_post = await engine.save(new_post)

        # 로그 출력
        logger.info(
            f"새 게시글이 생성되었습니다: 제목 - {new_post.title}, 작성자 - {new_post.nick_name}"
        )

        return new_post
    except HTTPException as http_ex:
        logger.error(
            f"게시글 생성 실패: {user_id} ({user.email if user.email else '이메일 정보 찾을 수 없음'})",
            exc_info=True,
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"게시글 생성 실패: {user_id} ({user.email if user.email else '이메일 정보 찾을 수 없음'})",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Read - 모든 게시글 조회
@router.get("/")
async def read_post(engine: AIOEngine = Depends(db.get_engine)):
    """
    이 엔드포인트는 모든 게시글을 조회합니다.
    결과는 생성일 기준으로 정렬됩니다.
    """
    try:
        posts = await engine.find(Post, sort=Post.created_at)
        if not posts:
            raise HTTPException(status_code=404, detail="Post not found")
        return posts
    except HTTPException as http_ex:
        logger.error(f"게시글 전체 조회 실패", exc_info=True)

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(f"게시글 전체 조회 실패", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# 인기 게시글 상위 n+1개를 반환하는 엔드포인트
@router.get("/popular", response_model=List[Post])
async def get_popular_posts(
    engine: AIOEngine = Depends(db.get_engine),
    redis: aioredis.Redis = Depends(get_redis),  # Redis 인스턴스 의존성
):
    """
    일간 인기순위 상위의 게시글을 반환합니다.
    상위 n개는 내부적으로 고정된 값입니다.
    """
    try:
        # 상위 고정 값
        n = 4

        # Redis에서 상위 n+1개의 인기 게시글 ID 가져오기
        popular_post_ids = await redis.zrevrange("popular_posts", 0, n)

        if not popular_post_ids:
            raise HTTPException(status_code=404, detail="인기 게시글이 없습니다.")

        # 가져온 인기 게시글 ID 리스트로 DB에서 게시글 정보 조회
        popular_posts = []
        for post_id in popular_post_ids:
            post = await engine.find_one(Post, Post.id == ObjectId(post_id))
            if post:
                popular_posts.append(post)

        if not popular_posts:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        return popular_posts
    except HTTPException as http_ex:
        logger.error(f"인기글 조회 실패", exc_info=True)

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(f"인기글 조회 실패", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


@router.put("/comment/{comment_id}")
async def read_post(
    comment: UpdateComment,
    comment_id: ObjectId = Path(
        ..., description="수정할 댓글글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: ObjectId = Depends(get_current_user_id),
):
    """
    이 엔드포인트는 특정 게시글에 특정 댓글을 수정합니다.
    """
    try:
        # 사용자가 존재하는지 확인
        user = await engine.find_one(User, User.id == user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail="사용자의 정보를 찾을 수 없습니다."
            )

        # 수정할 댓글이 존재하는지 확인
        existing_comment = await engine.find_one(Comment, Comment.id == comment_id)
        if not existing_comment:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

        # 댓글 작성자가 맞는지 확인
        if existing_comment.user_id != user.id:
            raise HTTPException(status_code=403, detail="댓글 작성자가 아닙니다.")

        # 댓글 수정 (기존 댓글 내용 업데이트)
        existing_comment.content = comment.content  # 새로운 댓글 내용으로 업데이트

        # 댓글 저장 (업데이트)
        await engine.save(existing_comment)

        # 댓글 수정 시 깃털 감소
        await decrement_feather(user.id)

        return existing_comment
    except HTTPException as http_ex:
        logger.error(
            f"댓글 수정 실패 사용자ID:{user_id} (댓글ID:{comment_id})", exc_info=True
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"댓글 수정 실패 사용자ID:{user_id} (댓글ID:{comment_id})", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


@router.delete("/comment/{comment_id}")
async def read_post(
    comment_id: ObjectId = Path(
        ..., description="수정할 댓글글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    is_admin: bool = Depends(verify_admin),
):
    """
    이 엔드포인트는 특정 게시글에 특정 댓글을 블라인드합니다.
    """
    try:
        # 블라인드할 댓글이 존재하는지 확인
        existing_comment = await engine.find_one(Comment, Comment.id == comment_id)
        if not existing_comment:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

        # 관리자가 아닐시
        if not is_admin:
            raise HTTPException(status_code=403, detail="관리자가 아닙니다.")

        # 댓글 블라인드 처리
        existing_comment.content = "관리자에 의해 블라인드 처리된 댓글입니다."

        # 댓글 저장 (업데이트)
        await engine.save(existing_comment)

        return existing_comment
    except HTTPException as http_ex:
        logger.error(f"댓글 블라인드 처리 실패 사용댓글ID:{comment_id}", exc_info=True)

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(f"댓글 블라인드 처리 실패 사용댓글ID:{comment_id}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# 게시글 좋아요
@router.post("/{post_id}/like")
async def like_post(
    post_id: ObjectId = Path(
        ..., description="수정할 게시글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: ObjectId = Depends(get_current_user_id),  # 현재 사용자 ID
    redis: aioredis.Redis = Depends(get_redis),  # Redis 인스턴스 의존성
):
    """
    이 엔드포인트는 특정 게시글에 좋아요를 추가하거나 취소합니다.
    """
    try:
        # 현재 사용자 가져오기
        user = await get_user_by_object_id(user_id)

        # 게시글 정보 가져오기
        post = await engine.find_one(Post, Post.id == post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

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

            # 24시간 이내에 동일 사용자가 좋아요를 눌렀는지 확인
            notification_exists = await redis.hexists(
                f"post:{post_id}:like_user", user_id
            )

            # 캐싱되지 않았다면 추가
            if not notification_exists:
                # TODO: 게시글 작성자에게 좋아요 알림 보내기 (이 부분은 구현 필요)
                print(f"게시글 {post_id}에 좋아요 알림이 전송되었습니다.")

                # HSET으로 유저 정보를 저장
                await redis.hset(f"post:{post_id}:like_user", user_id, "notified")

                # 한국 시간 기준으로 자정까지 남은 시간 계산
                seconds_until_midnight = get_seconds_until_midnight_kst()

                # 다음 00시까지 남은 시간 동안 만료 설정
                await redis.expire(f"post:{post_id}:like_user", seconds_until_midnight)

                # ZSET에 좋아요 증가 기록 추가
                await redis.zincrby("popular_posts", 1, f"{post_id}")

                # ZSET 만료 시간 설정 (자정까지 남은 시간)
                await redis.expire("popular_posts", seconds_until_midnight)

        await engine.save(post)

        return {"liked": liked, "post": post}
    except HTTPException as http_ex:
        logger.error(
            f"게시글 좋아요 처리 실패 게시글ID:{post_id} 사용자ID:{user_id}",
            exc_info=True,
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"게시글 좋아요 처리 실패 게시글ID:{post_id} 사용자ID:{user_id}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


@router.get("/{post_id}/comments")
async def read_post(
    post_id: ObjectId = Path(
        ..., description="수정할 게시글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
):
    """
    이 엔드포인트는 특정 게시글의 모든 댓글 목록을 반환합니다.
    """
    try:
        # 게시글 ID로 가져오기
        post = await engine.find_one(Post, Post.id == post_id)

        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        # 게시글 ID를 가지는 모든 댓글 가져오기
        comments = await engine.find(
            Comment, Comment.post_id == post_id, sort=Comment.created_at
        )

        return comments
    except HTTPException as http_ex:
        logger.error(f"댓글 가져오기 처리 실패 게시글ID:{post_id}", exc_info=True)

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(f"댓글 가져오기 실패 게시글ID:{post_id}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


@router.post("/{post_id}/comment")
async def read_post(
    comment: CreateComment,
    post_id: ObjectId = Path(
        ..., description="수정할 게시글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: ObjectId = Depends(get_current_user_id),
):
    """
    이 엔드포인트는 특정 게시글에 댓글을 생성합니다.
    """
    try:
        # 게시글 ID로 가져오기
        post = await engine.find_one(Post, Post.id == post_id)

        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        user = await engine.find_one(User, User.id == user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail="사용자의 정보를 찾을 수 없습니다."
            )

        # 댓글 생성
        new_comment = Comment(
            **comment.model_dump(),
            nick_name=user.nick_name,
            user_id=user.id,
            post_id=post_id,
        )
        await engine.save(new_comment)

        # 댓글 작성 시 깃털 감소
        await decrement_feather(user.id)

        return new_comment
    except HTTPException as http_ex:
        logger.error(
            f"댓글 작성 처리 실패 게시글ID:{post_id} 사용자ID:{user_id}", exc_info=True
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"댓글 작성 실패 게시글ID:{post_id} 사용자ID:{user_id}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Read - 게시글 조회 (ID 기반)
@router.get("/{post_id}")
async def read_post(
    post_id: ObjectId = Path(
        ..., description="조회할 게시글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
):
    try:
        """
        이 엔드포인트는 특정 게시글을 조회합니다.
        """
        post = await engine.find_one(Post, Post.id == post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except HTTPException as http_ex:
        logger.error(
            f"게시글 세부 정보 가져오기 실패 게시글ID:{post_id}", exc_info=True
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"게시글 세부 정보 가져오기 실패 게시글ID:{post_id}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Update - 게시글 수정
@router.put("/{post_id}")
async def update_post(
    post_update: PostUpdate,
    post_id: ObjectId = Path(
        ..., description="수정할 게시글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: ObjectId = Depends(get_current_user_id),
):
    """
    이 엔드포인트는 특정 게시글의 내용을 수정합니다.

    - **post_update**: 업데이트할 게시글 정보 (제목, 내용, 태그)
    """
    try:
        # 수정할 게시글 정보
        post = await engine.find_one(Post, Post.id == post_id)

        # 존재하지 않을 시
        if not post:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")

        # 작성자가 아닐 시
        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="작성자가 아닙니다.")

        # 업데이트할 필드 설정
        post.title = post_update.title
        post.content = post_update.content
        post.tags = post_update.tags

        await engine.save(post)
        return post
    except HTTPException as http_ex:
        logger.error(
            f"게시글 수정 실패 게시글ID:{post_id} 사용자ID:{user_id}", exc_info=True
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"게시글 수정 실패 게시글ID:{post_id} 사용자ID:{user_id}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Delete - 게시글 삭제
@router.delete("/{post_id}")
async def delete_post(
    post_id: ObjectId = Path(
        ..., description="수정할 게시글의 고유 ID", example="614c1b5f27f3b87636d1c2a5"
    ),
    engine: AIOEngine = Depends(db.get_engine),
    user_id: ObjectId = Depends(get_current_user_id),
    is_admin: bool = Depends(verify_admin),
):
    """
    이 엔드포인트는 특정 게시글을 삭제합니다.
    """
    try:
        post = await engine.find_one(Post, Post.id == post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")

        # 작성자가 아니고, 관리자도 아닌 경우
        if post.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=403, detail="작성자가 아니거나 관리자 권한이 없습니다."
            )

        await engine.delete(post)
        return post
    except HTTPException as http_ex:
        logger.error(
            f"게시글 삭제 실패 게시글ID:{post_id} 사용자ID:{user_id}", exc_info=True
        )

        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"게시글 삭제 실패 게시글ID:{post_id} 사용자ID:{user_id}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )
