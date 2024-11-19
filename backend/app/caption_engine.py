import torch
import torchvision.transforms as transforms
from PIL import Image
from .models import ImageCaptioningModel


class ImageCaptioningService:
    def __init__(self):
        self._initialize_model()

    def _initialize_model(self):
        self.model = ImageCaptioningModel()
        self.model.load_state_dict(
            torch.load(MODEL_PATH, map_location=torch.device("cpu"))
        )
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def generate_caption(self, image_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        image_tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            # caption = self.model.generate_caption(image_tensor)
            caption = "test caption"

        return caption
