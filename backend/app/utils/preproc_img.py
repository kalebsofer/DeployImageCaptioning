"""
Define image preprocessing here
"""

import torch


def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image for captioning, update per preprocessing
    """
    # create random tensor
    random_tensor = torch.randn(3, 256, 256)
    image = random_tensor
    return image
