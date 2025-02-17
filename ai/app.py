from datasets import load_dataset, Dataset
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
import logging
import numpy as np
import os
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


#
# sequence
#


#
# token classification
#


# labels from passing xml of dataset (C00035) into NLP
# https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C00035/xml
# label2id = {
#     "O": 0,
#     "B-REPORT_TYPE": 1,
#     "I-REPORT_TYPE": 2,
#     "B-DATA_ELEMENT": 3,
#     "I-DATA_ELEMENT": 4,
#     "B-ORGANIZATION": 5,
#     "I-ORGANIZATION": 6,
#     "B-DATE": 7,
#     "I-DATE": 8,
#     "B-TIME": 9,
#     "I-TIME": 10,
#     "B-LOCATION": 11,
#     "I-LOCATION": 12
# }
label2id = {
  "O": 0,
  "B-REPORT_TYPE": 1,
  "I-REPORT_TYPE": 2,
  "B-DATA_ELEMENT": 3,
  "I-DATA_ELEMENT": 4,
  "B-ORGANIZATION": 5,
  "I-ORGANIZATION": 6,
  "B-DATE": 7,
  "I-DATE": 8,
  "B-TIME": 9,
  "I-TIME": 10,
  "B-LOCATION": 11,
  "I-LOCATION": 12,
  "B-FORECAST_TYPE": 13,
  "I-FORECAST_TYPE": 14,
  "B-WEATHER_EVENT": 15,
  "I-WEATHER_EVENT": 16,
  "B-OBSERVATION_TYPE": 17,
  "I-OBSERVATION_TYPE": 18
}
id2label = {v: k for k, v in label2id.items()}

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model_path = "./trained-model-label"

if os.path.exists(model_path):
    model_label = AutoModelForTokenClassification.from_pretrained(model_path,
        label2id=label2id,
        id2label=id2label)
else:
    model_label = AutoModelForTokenClassification.from_pretrained("bert-base-uncased", num_labels=len(label2id),
                    label2id=label2id,
                    id2label=id2label)

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
    # if len(training_buffer) < THRESHOLD:
    #     return {"status": f"Not enough messages to train. Current count: {len(training_buffer)}"}
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
        model=model_label,
        args=training_args,
        train_dataset=tokenized_datasets,
    )

    trainer.train()
    trainer.save_model(model_path)
    training_buffer.clear()
    return {"status": "Training complete and model saved."}


# Load model and tokenizer at startup
label_pipeline = pipeline("ner", model=model_label, tokenizer=tokenizer)

@app.post("/infer_label")
async def infer_label(request: Request):
    logger.info("inferring label")
    data = await request.json()
    message = data.get("message")

    result = label_pipeline(message)
    logger.info("done inferring")

    return jsonable_encoder(result, custom_encoder={np.float32: float})

