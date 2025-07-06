#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start, router

from crews.rag_crew.rag_crew import RAGPipelineCrew
from utils.data_ingestion import DataIngestion

class State(BaseModel):
    query: str = ""
    topic_status: str = ""
    topic: str = ""

class ChatAssistant(Flow[State]):
    data_ingestion_obj = DataIngestion()

    @start()
    def extract_topic(self):
        topic = self.data_ingestion_obj.extract_patent_topic(self.state.query)
        self.state.topic = topic

        topic_status = self.data_ingestion_obj.get_topic_status(topic)
        if topic_status in ["queued","processing"]:
            self.state.topic_status = "processing"
        elif topic_status == "available":
            self.state.topic_status = "available"
        else:
            self.state.topic_status = "not_available"
        return self.state

    @router(extract_topic)
    def next_step(self):
        if self.state.topic_status == "processing":
            return "start_processing"
        elif self.state.topic_status == "available":
            return "start_chat"
        else:
            return "start_data_ingestion"
    
    @listen("start_processing")
    def processing(self):
        return {"response": f"We're processing patent data for '{self.state.topic}'"}

    @listen("start_data_ingestion")
    def data_ingestion(self):
        self.data_ingestion_obj.insert_topic(self.state.topic)
        self.data_ingestion_obj.dummy_enqueue_background_fetch(self.state.topic)
        return {"response": f"We're fetching patent data for '{self.state.topic}'. Try again in a few hours."}

    @listen("start_chat")
    def chat(self):
        result = (
            RAGPipelineCrew.kickoff(inputs={"raw_query": self.state.query})
        )

        print("Answer: ", result.raw)
        return result


if __name__ == "__main__":
    query="Future innovation about Lithium battery?"
    result = ChatAssistant().kickoff(inputs={"query":query})
    print(result)

