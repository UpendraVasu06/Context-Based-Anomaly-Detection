import os
import cv2

# ==============================
# CONFIGURATION
# ==============================

CONTEXT = "night_mode"   # change if needed
RAW_VIDEO_DIR = f"data/raw/{CONTEXT}"
FRAME_OUTPUT_DIR = f"data/frames/{CONTEXT}"

TARGET_FPS = 10


# ==============================
# Frame Extraction
# ==============================

def extract_frames_from_video(video_path, output_folder):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    original_fps = cap.get(cv2.CAP_PROP_FPS)

    if original_fps == 0:
        print(f"Warning: FPS not detected for {video_path}")
        return

    frame_interval = max(1, int(original_fps / TARGET_FPS))

    frame_count = 0
    saved_count = 0

    os.makedirs(output_folder, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_name = f"frame_{saved_count:05d}.jpg"
            frame_path = os.path.join(output_folder, frame_name)
            cv2.imwrite(frame_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Extracted {saved_count} frames from {os.path.basename(video_path)}")


def main():
    os.makedirs(FRAME_OUTPUT_DIR, exist_ok=True)

    video_files = [
        f for f in os.listdir(RAW_VIDEO_DIR)
        if f.endswith(".mp4")
    ]

    for video_file in video_files:
        video_path = os.path.join(RAW_VIDEO_DIR, video_file)
        video_name = os.path.splitext(video_file)[0]

        output_folder = os.path.join(FRAME_OUTPUT_DIR, video_name)

        print(f"\nProcessing: {video_file}")
        extract_frames_from_video(video_path, output_folder)

    print("\n✅ Frame extraction completed.")


if __name__ == "__main__":
    main()