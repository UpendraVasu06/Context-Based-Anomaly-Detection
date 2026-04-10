import os
import shutil

# ==============================
# CONFIGURATION
# ==============================

CONTEXT = "night_mode"   # change if needed
FRAME_DIR = f"data/frames/{CONTEXT}"
CLIP_OUTPUT_DIR = f"data/clips/{CONTEXT}"

CLIP_LENGTH = 16
STRIDE = 8


# ==============================
# Clip Generation
# ==============================

def generate_clips_for_video(video_frame_dir, video_clip_dir):
    os.makedirs(video_clip_dir, exist_ok=True)

    frame_files = sorted([
        f for f in os.listdir(video_frame_dir)
        if f.endswith(".jpg")
    ])

    total_frames = len(frame_files)

    clip_index = 0

    for start in range(0, total_frames - CLIP_LENGTH + 1, STRIDE):
        clip_folder = os.path.join(video_clip_dir, f"clip_{clip_index:05d}")
        os.makedirs(clip_folder, exist_ok=True)

        for i in range(CLIP_LENGTH):
            frame_name = frame_files[start + i]
            src = os.path.join(video_frame_dir, frame_name)
            dst = os.path.join(clip_folder, frame_name)
            shutil.copy(src, dst)

        clip_index += 1

    print(f"Generated {clip_index} clips from {os.path.basename(video_frame_dir)}")


def main():
    os.makedirs(CLIP_OUTPUT_DIR, exist_ok=True)

    video_folders = [
        f for f in os.listdir(FRAME_DIR)
        if os.path.isdir(os.path.join(FRAME_DIR, f))
    ]

    for video_name in video_folders:
        video_frame_dir = os.path.join(FRAME_DIR, video_name)
        video_clip_dir = os.path.join(CLIP_OUTPUT_DIR, video_name)

        print(f"\nProcessing: {video_name}")
        generate_clips_for_video(video_frame_dir, video_clip_dir)

    print("\n✅ Clip generation completed.")


if __name__ == "__main__":
    main()