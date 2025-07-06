from fastapi import FastAPI
from pydantic import BaseModel
from utils.utils import is_topic_available, update_topic_status, enqueue_background_fetch, extract_topic
from patent_ai.main import run_flow

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/chat")
def chat(query: Query):
    topic = extract_topic(query.question)  # Can add real NER or keyword extract logic

    if not is_topic_available(topic):
        update_topic_status(topic, "queued")
        enqueue_background_fetch(topic)
        return {"response": f"We're fetching patent data for '{topic}'. Try again in a few hours."}

    answer = run_flow(query.question)
    return {"response": answer}