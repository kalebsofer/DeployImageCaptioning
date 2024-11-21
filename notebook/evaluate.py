# %%
import random
import torch
import evaluate
from transformers import BlipForConditionalGeneration, BlipProcessor
from datasets import Dataset
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# %%
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

# %%
test_ds = Dataset.load_from_disk("./notebook/data/test_ds.json")

# %%

# Inspect the shape of pixel values for the first example
first_example = test_ds[0]
pixel_values = first_example["pixel_values"]
# %%
# Print the shape
print("Pixel values shape:", np.array(pixel_values).shape)

# %%
image_array = np.moveaxis(pixel_values, 0, -1)
image = Image.fromarray(image_array.astype(np.uint8))

# %%
plt.imshow(image)
plt.axis("off")
plt.show()


# %%
def generate_caption(model, processor, pixel_values):
    output = model.generate(pixel_values=pixel_values, max_new_tokens=50)
    return processor.decode(output[0], skip_special_tokens=True)


# %%
def display_image_with_captions(pixel_values, generated_caption, references):
    if len(pixel_values.shape) == 3 and pixel_values.shape[0] in [1, 3]:
        image_array = np.moveaxis(pixel_values, 0, -1)
    elif len(pixel_values.shape) == 3 and pixel_values.shape[-1] in [1, 3]:
        image_array = pixel_values
    elif len(pixel_values.shape) == 2:
        image_array = np.expand_dims(pixel_values, axis=-1)
        image_array = np.repeat(image_array, 3, axis=-1)
    else:
        return

    image_array = (image_array - np.min(image_array)) / (
        np.max(image_array) - np.min(image_array)
    )
    image_array = (image_array * 255).astype(np.uint8)

    try:
        image = Image.fromarray(image_array)
        plt.imshow(image)
        plt.axis("off")
        plt.title(f"Generated: {generated_caption}\nReference: {references}")
        plt.show()
    except Exception as e:
        print(f"Failed to display image: {e}")


# %%
def evaluate_model(test_dataset, model, processor):
    generated_captions = []
    reference_captions = []

    for example in random.sample(list(test_dataset), 1):
        pixel_values = example["pixel_values"]

        # Debug display the image before generating caption
        debug_display_image(np.array(pixel_values))

        # Proceed with generating the caption
        pixel_values_tensor = torch.tensor(pixel_values).unsqueeze(0).to(device)
        generated_caption = generate_caption(model, processor, pixel_values_tensor)

        references = example.get("caption", ["No reference available"])
        generated_captions.append(generated_caption)
        reference_captions.append([references])

        print(f"Image ID: {example['img_id']}")
        print(f"Generated Caption: {generated_caption}")
        print(f"Reference Captions: {references}")
        print("-" * 50)

    evaluator = evaluate.load("bleu")
    results = evaluator.compute(
        predictions=generated_captions, references=reference_captions
    )
    print(f"BLEU Score: {results['bleu']}")


# %%
evaluate_model(test_ds, model, processor)

# %%
