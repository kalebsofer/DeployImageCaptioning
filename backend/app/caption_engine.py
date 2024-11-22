import io
import torch
from PIL import Image
from minio import Minio

from .config.settings import get_settings
from .utils.preproc_img import preprocess_image
from .models.transformer import Transformer
from .models.tokeniser import GPT2TokeniserPlus
from .models.generate import CaptionGenerator
from .models.params import decoder_params

settings = get_settings()


class CaptionEngine:
    def __init__(self):
        self._initialize_minio_client()
        self._initialize_resources()

    def _initialize_minio_client(self):
        self.minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def _get_file_from_minio(self, bucket: str, object_name: str) -> bytes:
        try:
            response = self.minio_client.get_object(bucket, object_name)
            data = response.read()
            print(f"Retrieved {object_name} of size {len(data)} bytes")
            return data
        except Exception as e:
            raise Exception(f"Error loading {object_name} from MinIO: {str(e)}")

    def _initialize_resources(self):
        model_data = self._get_file_from_minio("data", "transformer_latest.pth")

        self.model = Transformer(decoder_params=decoder_params)

        # TODO finish once model is trained

        self.model.load_state_dict(
            torch.load(io.BytesIO(model_data), map_location=torch.device("cpu"))
        )
        self.model.eval()
        # tokeniser_data = self._get_file_from_minio("data", "tokenizer.model")
        self.tokeniser = GPT2TokeniserPlus()

        self.generator = CaptionGenerator(model=self.model, tokeniser=self.tokeniser)

    def get_caption(self, image_bytes: bytes, temperature) -> str:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # image_tensor = preprocess_image(image)

        # # Run image through model to get caption embedding
        # with torch.no_grad():
        #     caption_embedding = self.model(image_tensor)

        # Decode caption embedding using the tokeniser
        # caption = self.tokeniser.decode(caption_embedding)

        # You should be able to send PIL Images directly to generator
        _, caption = self.generator.generate(image, temperature=temperature)

        return caption
