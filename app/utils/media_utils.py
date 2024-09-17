import cv2


def create_video_thumbnail(video_path: str, thumbnail_path: str, time: float = 1.0):
    video = cv2.VideoCapture(video_path)
    try:
        fps = video.get(cv2.CAP_PROP_FPS)  # 프레임 속도(FPS) 얻기
        frame_number = int(fps * time)  # 지정된 시간에 해당하는 프레임 번호 계산

        # 해당 프레임으로 이동
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = video.read()

        if success:
            # 프레임을 이미지로 저장
            cv2.imwrite(thumbnail_path, frame)
            print(f"썸네일이 생성되었습니다: {thumbnail_path}")
            return True
        else:
            print("프레임을 추출할 수 없습니다.")
            return False
    finally:
        # 무조건 video.release() 호출
        video.release()
