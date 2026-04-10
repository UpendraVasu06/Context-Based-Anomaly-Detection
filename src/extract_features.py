import os
import torch
import numpy as np
from torchvision import transforms
from PIL import Image
from tqdm import tqdm
import timm

# ==============================
# CONFIGURATION
# ==============================

CONTEXT = "night_mode"
CLIP_DIR = f"data/clips/{CONTEXT}"
FEATURE_DIR = f"data/features/{CONTEXT}"

MODEL_NAME = "vit_base_patch16_224"
DEVICE = torch.device("cpu")

# Motion weight (IMPORTANT for running/falling detection)
MOTION_SCALE = 3.0

# ==============================
# Load ViT Model
# ==============================

def load_vit_model():
    model = timm.create_model(MODEL_NAME, pretrained=True)
    model.reset_classifier(0)
    model.eval()
    model.to(DEVICE)
    return model


# ==============================
# Image Transform
# ==============================

def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225)
        )
    ])


# ==============================
# Feature Extraction Per Clip
# ==============================

def extract_clip_feature(model, transform, clip_path):

    frame_files = sorted([
        f for f in os.listdir(clip_path)
        if f.endswith(".jpg")
    ])

    embeddings = []
    raw_frames = []

    with torch.no_grad():
        for frame_file in frame_files:
            img_path = os.path.join(clip_path, frame_file)

            image = Image.open(img_path).convert("RGB")
            raw_frames.append(np.array(image))

            image_tensor = transform(image).unsqueeze(0).to(DEVICE)
            feature = model(image_tensor)

            embeddings.append(feature.squeeze(0).cpu().numpy())

    # -------- Hybrid Pooling --------
    mean_feat = np.mean(embeddings, axis=0)
    max_feat = np.max(embeddings, axis=0)
    vit_feature = 0.7 * mean_feat + 0.3 * max_feat

    # -------- Motion Feature --------
    motion_values = []

    for i in range(1, len(raw_frames)):
        diff = np.abs(
            raw_frames[i].astype(np.float32) -
            raw_frames[i - 1].astype(np.float32)
        )

        diff = diff / 255.0
        motion_values.append(np.mean(diff))

    motion_intensity = np.mean(motion_values) if motion_values else 0.0

    # Scale motion to make it meaningful
    motion_intensity *= MOTION_SCALE

    # -------- Final Feature --------
    final_feature = np.concatenate([vit_feature, np.array([motion_intensity])])

    return final_feature


# ==============================
# Main
# ==============================

def main():
    os.makedirs(FEATURE_DIR, exist_ok=True)

    model = load_vit_model()
    transform = get_transform()

    video_folders = [
        f for f in os.listdir(CLIP_DIR)
        if os.path.isdir(os.path.join(CLIP_DIR, f))
    ]

    for video_name in video_folders:

        video_clip_dir = os.path.join(CLIP_DIR, video_name)
        video_feature_dir = os.path.join(FEATURE_DIR, video_name)
        os.makedirs(video_feature_dir, exist_ok=True)

        clip_folders = sorted([
            f for f in os.listdir(video_clip_dir)
            if os.path.isdir(os.path.join(video_clip_dir, f))
        ])

        print(f"\nProcessing video: {video_name}")

        for clip_name in tqdm(clip_folders):

            clip_path = os.path.join(video_clip_dir, clip_name)
            feature = extract_clip_feature(model, transform, clip_path)

            save_path = os.path.join(video_feature_dir, clip_name + ".npy")
            np.save(save_path, feature)

    print("\n✅ Feature extraction completed.")


if __name__ == "__main__":
    main()