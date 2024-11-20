import torch.nn as nn
import torchvision


class ImageEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        weights = torchvision.models.ViT_B_16_Weights.IMAGENET1K_V1
        self.model = torchvision.models.vit_b_16(weights=weights)
        self.img_embeds = None
        self._register_hooks()

    def _register_hooks(self):
        self.model.encoder.layers[-1].register_forward_hook(self._hook)

    def _hook(self, module, input, output):
        self.img_embeds = output[:, 1:, :]

    def forward(self, x):
        _ = self.model(x)
        return self.img_embeds
