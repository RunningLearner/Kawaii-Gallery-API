import cv2
import ffmpeg

def create_video_thumbnail(video_path: str, thumbnail_path: str, time: float = 1.0):
    """
    이 함수는 썸네일을 생성하는 유틸리티 함수이며, 발생하는 예외는 상위로 던집니다.
    """
    video = cv2.VideoCapture(video_path)

    fps = video.get(cv2.CAP_PROP_FPS)  # 프레임 속도(FPS) 얻기
    frame_number = int(fps * time)  # 지정된 시간에 해당하는 프레임 번호 계산

    # 해당 프레임으로 이동
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = video.read()

    if success:
        # 프레임을 이미지로 저장
        cv2.imwrite(thumbnail_path, frame)
        return True
    else:
        raise ValueError("프레임을 추출할 수 없습니다.")  # 에러를 상위로 던짐

    video.release()

def convert_mov_to_mp4(input_path: str, output_path: str):
    """
    이 함수는 비디오 파일을 변환하는 유틸리티 함수이며, 발생하는 예외는 상위로 던집니다.
    """
    ffmpeg.input(input_path).output(output_path, vcodec='h264', acodec='aac').run()
    return True
