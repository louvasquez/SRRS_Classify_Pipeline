import logging
import os
from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, pipeline
from datasets import load_dataset, Dataset
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


#
# sequence
#


#
# token classification
#




# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model_path = "./trained_model_label"

if os.path.exists(model_path):
    model = AutoModelForTokenClassification.from_pretrained(model_path)
else:
    model = AutoModelForTokenClassification.from_pretrained("bert-base-uncased", num_labels=5)

# Buffer for training data
training_buffer = []
THRESHOLD = 100  # Number of messages to trigger training

@app.post("/collect_message_label")
async def collect_message(request: Request):
    data = await request.json()
    message = data.get("message")
    training_buffer.append(message)

    if len(training_buffer) >= THRESHOLD:
        await train_label()
        return {"status": "Training triggered after reaching threshold."}
    return {"status": f"Message added. Total messages: {len(training_buffer)}"}

@app.post("/train_label")
async def train_label():
    if len(training_buffer) < THRESHOLD:
        return {"status": f"Not enough messages to train. Current count: {len(training_buffer)}"}
    logger.info("training label model")

    # Prepare dataset
    dataset = Dataset.from_dict({"text": training_buffer})
    tokenized_datasets = dataset.map(lambda x: tokenizer(x["text"], padding="max_length", truncation=True), batched=True)

    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        save_steps=1000,
        save_total_limit=2,
        logging_dir='./logs',
        logging_steps=500,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
    )

    trainer.train()
    trainer.save_model(model_path)
    training_buffer.clear()
    return {"status": "Training complete and model saved."}

@app.post("/infer_label")
async def infer_label(request: Request):
    data = await request.json()
    message = data.get("message")

    model = AutoModelForTokenClassification.from_pretrained(model_path)
    label_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

    result = label_pipeline(message)
    return {"labels": result}