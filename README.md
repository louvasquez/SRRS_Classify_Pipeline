# [WIP] SRRS Classify and NiFi Pipeline

Rudimentary attempts at
- Classify ANX messages (bulletins) in Jupyter notebook
- NiFi + FastAPI Infer NER from streaming messages

What works
- jupyter notebook can train a model
- nifi pipeline can stream messages into API for (BAD) label training (NER)

**AI Helped me**

# [WIP] Classifier (ipynb)
(see `jupyter/`)

Creates classifier model
- message labels provided
- ANX file required

Requires
- local downloaded ANX file (https://www.ncei.noaa.gov/data/service-records-retention-system/access/anx/2025/01/27/00/)

Current Stats

| Epoch  | Training Loss  | Validation Loss  |
|---|---|---|
| 1	| No log	| 0.214570 |
| 2	| 0.495600	| 0.177160 |
| 3	| 0.125400	| 0.130314 |

TODO
- improve classifier model loss
- add classifier infer to API for NiFi flow inference

# [WIP] NiFi Inferrer (bert NER)

2 parts
- *NiFi*: Streams anx messages into API train
- *API*: FastAPI for infer,train endpoint (message labels, NOT classify)

Notes
- API can train message labels (BADLY) (does NOT classify)
- API endpoints to train,infer (NER, NOT classify)
- Hardcoded user/pass in docker-compose for https

Plan
- implement infer_message_class endpoint using model built in 

## code

- `ai/` : FastAPI with endpoints for training AI
- `app-scripts/` : scripts used by NiFi flows
- `autoflows/` : NiFi flow
- `jupyter/` : Classifier model builder



## Running

```
docker-compose down
docker-compose up --build -d --remove-orphans
docker-compose logs nifi -f
```
