import cv2
import torch
import torch.nn as nn
import numpy as np
import timm
from torchvision import transforms
from PIL import Image
from src.autoencoder import Autoencoder

# ==============================
# CONFIGURATION
# ==============================

CONTEXT = "office"

VIDEO_PATH = "data/raw/office_testing/abnormal_scene_4_scenario_7.mp4"
MODEL_PATH = f"models/{CONTEXT}_autoencoder.pth"
THRESHOLD_PATH = f"models/{CONTEXT}_threshold.npy"

CLIP_LENGTH = 16
STRIDE = 8
TARGET_FPS = 10

DEVICE = torch.device("cpu")

# ==============================
# Load Models
# ==============================

def load_models():

    vit = timm.create_model("vit_base_patch16_224", pretrained=True)
    vit.reset_classifier(0)
    vit.eval()
    vit.to(DEVICE)

    ae = Autoencoder(input_dim=769, latent_dim=128)
    ae.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    ae.eval()
    ae.to(DEVICE)

    return vit, ae


# ==============================
# Image Transform
# ==============================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])


# ==============================
# Feature Extraction
# ==============================

def extract_embedding(vit_model, frames):

    embeddings = []
    raw_frames = []

    with torch.no_grad():

        for frame in frames:

            raw_frames.append(frame.copy())

            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image = transform(image).unsqueeze(0).to(DEVICE)

            feature = vit_model(image)

            embeddings.append(feature.squeeze(0).cpu().numpy())

    # Hybrid pooling
    mean_feat = np.mean(embeddings, axis=0)
    max_feat = np.max(embeddings, axis=0)

    vit_feature = 0.7 * mean_feat + 0.3 * max_feat

    # Motion feature
    motion_values = []

    for i in range(1, len(raw_frames)):

        diff = np.abs(
            raw_frames[i].astype(np.float32) -
            raw_frames[i - 1].astype(np.float32)
        )

        diff = diff / 255.0
        motion_values.append(np.mean(diff))

    motion_intensity = np.mean(motion_values) if motion_values else 0.0

    final_feature = np.concatenate([vit_feature, np.array([motion_intensity])])

    return final_feature


# ==============================
# Reconstruction Error
# ==============================

def compute_reconstruction_error(ae_model, feature_vector):

    with torch.no_grad():

        x = torch.tensor(feature_vector, dtype=torch.float32).unsqueeze(0).to(DEVICE)

        reconstructed = ae_model(x)

        loss = nn.MSELoss()(reconstructed, x)

    return loss.item()


# ==============================
# Streaming Inference (Terminal)
# ==============================

def main():

    vit_model, ae_model = load_models()

    threshold = np.load(THRESHOLD_PATH)[0]

    print(f"Loaded Threshold: {threshold:.6f}\n")

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print("Failed to open video.")
        return

    original_fps = cap.get(cv2.CAP_PROP_FPS)

    frame_interval = max(1, int(original_fps / TARGET_FPS))

    buffer = []
    frame_idx = 0
    clip_index = 0

    consecutive_anomalies = 0

    print("Starting streaming inference...\n")
    print(VIDEO_PATH)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_idx % frame_interval == 0:

            buffer.append(frame)

            if len(buffer) == CLIP_LENGTH:

                embedding = extract_embedding(vit_model, buffer)

                score = compute_reconstruction_error(ae_model, embedding)

                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                if score > threshold:

                    consecutive_anomalies += 1
                    status = "ANOMALY 🔴"

                else:

                    consecutive_anomalies = 0
                    status = "NORMAL ✅"

                print(
                    f"Time: {timestamp:.2f}s | "
                    f"Clip {clip_index} | "
                    f"Score: {score:.4f} | "
                    f"{status}"
                )

                clip_index += 1
                buffer = buffer[STRIDE:]

        frame_idx += 1

    cap.release()

    print("\nStreaming inference completed.")


# ==============================
# Streaming Generator (API)
# ==============================

def run_stream(video_path, context):

    global VIDEO_PATH, CONTEXT, MODEL_PATH, THRESHOLD_PATH

    VIDEO_PATH = video_path
    CONTEXT = context

    MODEL_PATH = f"models/{context}_autoencoder.pth"
    THRESHOLD_PATH = f"models/{context}_threshold.npy"

    vit_model, ae_model = load_models()

    threshold = np.load(THRESHOLD_PATH)[0]
    yield {
        "type": "meta",
        "threshold": round(float(threshold), 4)
    }

    cap = cv2.VideoCapture(VIDEO_PATH)

    original_fps = cap.get(cv2.CAP_PROP_FPS)

    frame_interval = max(1, int(original_fps / TARGET_FPS))

    buffer = []
    frame_idx = 0
    clip_index = 0
    consecutive_anomalies = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_idx % frame_interval == 0:

            buffer.append(frame)

            if len(buffer) == CLIP_LENGTH:

                embedding = extract_embedding(vit_model, buffer)

                score = compute_reconstruction_error(ae_model, embedding)

                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                anomaly = bool(score > threshold)

                if anomaly:
                    consecutive_anomalies += 1
                else:
                    consecutive_anomalies = 0

                yield {
                    "type": "point",
                    "time": round(float(timestamp), 2),
                    "score": round(float(score), 4),
                    "anomaly": bool(anomaly),
                    "alert": bool(consecutive_anomalies >= 3)
                }

                clip_index += 1
                buffer = buffer[STRIDE:]

        frame_idx += 1

    cap.release()


if __name__ == "__main__":
    main()