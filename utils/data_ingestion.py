# core_modules/data_status.py
from datetime import datetime
import json
import os
import re
import threading
from utils.data_loader import fetch_patents_from_lens
from uuid import uuid4
import os
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import uuid
from qdrant_client.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams


load_dotenv()

class DataIngestion():

    def __init__(self):
        self.STATUS_FILE = os.getenv("PATENT_STATUS_FILE")
        
        self.LLM = ChatOpenAI(model='gpt-4o-mini',temperature=0)

        self.collection_name = "patent_data"

        self.embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

        self.qdrant_api_key = os.environ.get("QDRANT_CLOUD_KEY")
        self.qdrant_cloud_url = os.getenv("QDRANT_URL")
        self.qdrant = QdrantClient(
            url=self.qdrant_cloud_url,
            api_key=self.qdrant_api_key,
        )

        if not os.path.exists(self.STATUS_FILE):
            with open(self.STATUS_FILE, "w") as f:
                json.dump({}, f)

    def get_topic_status(self,topic):
        with open(self.STATUS_FILE, "r") as f:
            data = json.load(f)
        return data.get(topic,{"status":"not_available"})["status"]

    def insert_topic(self,topic):
        with open(self.STATUS_FILE, "r") as f:
            data = json.load(f)
        data[topic] = {"status": "queued","last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open(self.STATUS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def extract_patent_topic(self,user_input):
        patterns = ["lithium battery", "solar panel", "semiconductor"]
        for p in patterns:
            if p.lower() in user_input.lower():
                return p
        return "unknown"
    
    def update_topic_status(self,topic, status):
        with open(self.STATUS_FILE, "r") as f:
            data = json.load(f)
        data[topic] = {"status": status, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open(self.STATUS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def save_patents_to_json(self,results):
        pass 

    def background_fetch_and_store(self,topic):
        try:
            self.update_topic_status(topic, "processing")
            results = fetch_patents_from_lens(topic, years_back=3, max_results=100)
            file_path = os.path.join(self.DATA_DIR, f"{topic.replace(' ', '_')}_{uuid4().hex}.json")
            self.save_patents_to_json(results, filename=file_path)
            self.qdrant_data_ingestion(file_path)
            self.update_topic_status(topic, "available")
        except Exception as e:
            self.update_topic_status(topic, f"error: {str(e)}")

    def dummy_enqueue_background_fetch(self,topic):
        self.update_topic_status(topic, "available")
    
    def enqueue_background_fetch(self,topic):
        thread = threading.Thread(target=self.background_fetch_and_store, args=(topic,))
        thread.start()
    
    def qdrant_data_ingestion(self, filepath):

        docs = json.load(open(filepath,"r"))
        # List of dictionaries, each dictionary has keys: title, abstract, published_date etc

        vector_size = len(self.embed_model.embed_query("test"))
        if self.collection_name not in [col.name for col in self.qdrant.get_collections().collections]:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )

        points = []
        embeddings = self.embed_model.embed_documents(texts=[d["abstract"] for d in docs])

        for idx, document in enumerate(docs):
            vector = embeddings[idx]
            if vector is None:
                continue
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=document
            )
            points.append(point)


        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )