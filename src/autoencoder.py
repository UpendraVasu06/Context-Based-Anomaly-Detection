import torch
import torch.nn as nn


class Autoencoder(nn.Module):
    def __init__(self, input_dim=769, latent_dim=128):
        super(Autoencoder, self).__init__()

        # -------- Encoder --------
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),

            nn.Linear(512, 256),
            nn.ReLU(),

            nn.Linear(256, latent_dim)
        )

        # -------- Decoder --------
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),

            nn.Linear(256, 512),
            nn.ReLU(),

            nn.Linear(512, input_dim)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed