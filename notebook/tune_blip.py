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

# Initialize wandb
wandb.init(project="blip-image-captioning")

# Check if GPU is available
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
train_ds = train_ds.map(preprocess_function, remove_columns=["image", "caption"])
val_ds = val_ds.map(preprocess_function, remove_columns=["image", "caption"])
test_ds = test_ds.map(preprocess_function, remove_columns=["image", "caption"])
# %%
# save train_ds and val_ds to local notebook/data/
train_ds.save_to_disk("./notebook/data/train_ds.json")
val_ds.save_to_disk("./notebook/data/val_ds.json")
test_ds.save_to_disk("./notebook/data/test_ds.json")
# import train_ds and val_ds from local notebook/data/
# train_ds = Dataset.load_from_disk("./notebook/data/train_ds.json")
# val_ds = Dataset.load_from_disk("./notebook/data/val_ds.json")
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
    report_to="wandb",  # Enable wandb logging
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
