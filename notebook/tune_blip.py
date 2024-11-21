# %%
import torch
import wandb
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset, Dataset

wandb.init(project="blip-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# %%
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

# %%
dataset = load_dataset("nlphuji/flickr30k")
# %%
s_ds = dataset["test"].select(range(1000))

# %%
id_to_caption = {example["img_id"]: example["caption"] for example in s_ds}
# %%
train_ds = s_ds.filter(lambda example: example["split"] == "train")
test_ds = s_ds.filter(lambda example: example["split"] == "test")
val_ds = s_ds.filter(lambda example: example["split"] == "val")

# %%
train_ds[0]


# %%
def flatten_dataset(examples):
    new_images = []
    new_captions = []
    new_sentids = []
    new_splits = []
    new_img_ids = []
    new_filenames = []

    for i in range(len(examples["image"])):
        image = examples["image"][i]
        split = examples["split"][i]
        img_id = examples["img_id"][i]
        filename = examples["filename"][i]

        for caption, sentid in zip(examples["caption"][i], examples["sentids"][i]):
            new_images.append(image)
            new_captions.append(caption)
            new_sentids.append(sentid)
            new_splits.append(split)
            new_img_ids.append(img_id)
            new_filenames.append(filename)

    return {
        "image": new_images,
        "caption": new_captions,
        "sentid": new_sentids,
        "split": new_splits,
        "img_id": new_img_ids,
        "filename": new_filenames,
    }


# %%
train_ds = train_ds.map(
    flatten_dataset, batched=True, remove_columns=train_ds.column_names
)
val_ds = val_ds.map(flatten_dataset, batched=True, remove_columns=val_ds.column_names)
test_ds = test_ds.map(
    flatten_dataset, batched=True, remove_columns=test_ds.column_names
)
# %%
train_ds[0]

# %%
# get type of first column
type(train_ds[0]["image"])


# %%
def preprocess_function(examples):
    image = examples["image"]
    text = examples["caption"]
    inputs = processor(
        images=image,
        text=text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
    )
    inputs = {key: val.squeeze(0).to(device) for key, val in inputs.items()}

    return inputs

# %%
# # save train_ds and val_ds to local notebook/data/
# train_ds.save_to_disk("./notebook/data/train_ds.json")
# val_ds.save_to_disk("./notebook/data/val_ds.json")
# test_ds.save_to_disk("./notebook/data/test_ds.json")

# import train_ds and val_ds from local notebook/data/
# train_ds = Dataset.load_from_disk("./notebook/data/train_ds.json")
# val_ds = Dataset.load_from_disk("./notebook/data/val_ds.json")
# test_ds = Dataset.load_from_disk("./notebook/data/test_ds.json")

# %%
# need this step for blip preprocessing
train_ds = train_ds.map(preprocess_function, remove_columns=["image", "caption"])
val_ds = val_ds.map(preprocess_function, remove_columns=["image", "caption"])
test_ds = test_ds.map(preprocess_function, remove_columns=["image", "caption"])
# %%

training_args = TrainingArguments(
    output_dir="./notebook/results/",
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=4,
    num_train_epochs=3,
    save_strategy="epoch",
    save_total_limit=2,
    remove_unused_columns=False,
    logging_dir="./logs",
    logging_steps=10,
    report_to="wandb",
)
# %%
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
)

# %%
trainer.train()

# %%
import random
import torch
import evaluate
from datasets import Dataset
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from pycocoevalcap.cider.cider import Cider

# %%
# test_ds = Dataset.load_from_disk("./notebook/data/test_ds.json")


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
        plt.show()
    except Exception as e:
        print(f"Failed to display image: {e}")


# %%
def calculate_scores(generated_captions, reference_captions):
    bleu_scores = []
    for gen, refs in zip(generated_captions, reference_captions):
        gen_tokens = gen.split()
        ref_tokens = [ref.split() for ref in refs]
        score = sentence_bleu(
            ref_tokens,
            gen_tokens,
            weights=(0.5, 0.5, 0, 0),  # Adjust weights for n-grams
            smoothing_function=SmoothingFunction().method1,
        )
        bleu_scores.append(score)
    average_bleu = sum(bleu_scores) / len(bleu_scores)

    # cider_scorer = Cider()
    # cider_score, _ = cider_scorer.compute_score(
    #     {i: [gen] for i, gen in enumerate(generated_captions)},  # Wrap each generated caption in a list
    #     {i: refs for i, refs in enumerate(reference_captions)}
    # )

    return average_bleu


# %%
def evaluate_model(test_dataset, model, processor, id_to_caption):
    generated_captions = []
    reference_captions = []

    for example in random.sample(list(test_dataset), 2):
        pixel_values = example["pixel_values"]

        display_image_with_captions(np.array(pixel_values), "", "")

        pixel_values_tensor = torch.tensor(pixel_values).unsqueeze(0).to(device)
        generated_caption = generate_caption(model, processor, pixel_values_tensor)

        references = id_to_caption.get(example["img_id"], ["No reference available"])
        generated_captions.append(generated_caption)
        reference_captions.append(references)

        print(f"Image ID: {example['img_id']}")
        print(f"Generated Caption: {generated_caption}")

        for i, ref in enumerate(references, 1):
            print(f"Ref {i}: {ref}")

        print("-" * 50)

        average_bleu = calculate_scores(generated_caption, references)
        print(f"Average BLEU Score: {average_bleu}")
    # print(f"CIDEr Score: {cider_score}")


# %%
evaluate_model(test_ds, model, processor, id_to_caption)


# %%
