import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from autoencoder import Autoencoder
from tqdm import tqdm

# ==============================
# CONFIGURATION
# ==============================

CONTEXT = "night_mode"
FEATURE_DIR = f"data/features/{CONTEXT}"

MODEL_SAVE_PATH = f"models/{CONTEXT}_autoencoder.pth"
THRESHOLD_SAVE_PATH = f"models/{CONTEXT}_threshold.npy"
ERROR_SAVE_PATH = f"models/{CONTEXT}_train_errors.npy"

BATCH_SIZE = 16
EPOCHS = 50
LEARNING_RATE = 1e-3

DEVICE = torch.device("cpu")


# ==============================
# Load Features
# ==============================

def load_features():
    features = []

    video_folders = [
        os.path.join(FEATURE_DIR, f)
        for f in os.listdir(FEATURE_DIR)
        if os.path.isdir(os.path.join(FEATURE_DIR, f))
    ]

    for video_folder in video_folders:
        for file in os.listdir(video_folder):
            if file.endswith(".npy"):
                feature = np.load(os.path.join(video_folder, file))
                features.append(feature)

    features = np.array(features)
    return features


# ==============================
# Main
# ==============================

def main():
    os.makedirs("models", exist_ok=True)

    print("Loading features...")
    features = load_features()

    print(f"Total training samples: {features.shape[0]}")

    dataset = torch.tensor(features, dtype=torch.float32)
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    model = Autoencoder(input_dim=769, latent_dim=128).to(DEVICE)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print("\nStarting training...\n")

    for epoch in range(EPOCHS):
        epoch_loss = 0

        for batch in dataloader:
            batch = batch.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(batch)
            loss = criterion(outputs, batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        print(f"Epoch [{epoch+1}/{EPOCHS}] - Loss: {epoch_loss:.6f}")

    # ==============================
    # Compute Training Errors
    # ==============================

    print("\nComputing training reconstruction errors...")

    model.eval()
    all_errors = []

    with torch.no_grad():
        for x in dataset:
            x = x.unsqueeze(0).to(DEVICE)
            recon = model(x)
            error = nn.MSELoss()(recon, x)
            all_errors.append(error.item())

    errors = np.array(all_errors)

    # Save error distribution
    np.save(ERROR_SAVE_PATH, errors)

    # ==============================
    # Percentile Threshold (95%)
    # ==============================

    threshold = np.percentile(errors, 95)

    print(f"Computed Threshold (95th percentile): {threshold:.6f}")

    np.save(THRESHOLD_SAVE_PATH, np.array([threshold]))

    # Save model
    torch.save(model.state_dict(), MODEL_SAVE_PATH)

    print("\n✅ Model and threshold saved successfully.")


if __name__ == "__main__":
    main()