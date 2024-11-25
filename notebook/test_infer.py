# %%
import os
import io
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


# %%
def load_blip_model(dir):
    if not os.path.exists(dir):
        raise FileNotFoundError(f"The directory '{dir}' does not exist.")

    processor = BlipProcessor.from_pretrained(dir)
    model = BlipForConditionalGeneration.from_pretrained(dir)

    return processor, model


# %%
# To perform inference
def generate_caption(image_bytes: bytes, processor, model) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(torch.device("cpu"))

    caption_ids = model.generate(**inputs)
    caption = processor.decode(caption_ids[0], skip_special_tokens=True)
    return caption


# %%
# Example inference

processor, model = load_blip_model("minio/data")

with open("data/test_img.jpg", "rb") as f:
    image_bytes = f.read()

caption = generate_caption(image_bytes, processor, model)
print(caption)

# %%
