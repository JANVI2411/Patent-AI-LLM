# tools/qdrant_retrieval_tool.py
import os 
from typing import List, Optional

from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_community.document_compressors.rankllm_rerank import RankLLMRerank

from crewai.tools import tool

from rank_llm.data import Request, Query, Candidate
import langchain_community.document_compressors.rankllm_rerank as rllm

from qdrant_client import QdrantClient

from dotenv import load_dotenv

load_dotenv()

# Inject missing imports into the module
rllm.Request = Request
rllm.Query = Query
rllm.Candidate = Candidate

embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

qdrant_api_key = os.environ.get("QDRANT_CLOUD_KEY")
qdrant = QdrantClient(
    url="https://01f14d7a-9e05-4804-bfd3-a69b4c3a97da.us-west-1-0.aws.cloud.qdrant.io:6333",
    api_key=qdrant_api_key,
)

collection_name = "meta_report_tables_docling_v1"
ind_vector_index = Qdrant(
    client=qdrant,
    collection_name=collection_name,
    embeddings=embed_model,
    content_payload_key="text"
)

def retrieve_documents(query,filter= None,top_k= 5,reranker_top_n= 3,use_reranker=False):
    
    retriever = ind_vector_index.as_retriever(
        search_kwargs={"k": top_k, "filter": filter} if filter else {"k": top_k}
    )

    if use_reranker:
        compressor = RankLLMRerank(top_n=reranker_top_n, model="gpt", gpt_model="gpt-4o-mini")
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=retriever
        )

    results = retriever.invoke(query)
    return [doc.page_content for doc in results]

@tool("qdrant_retrieval_tool")
def qdrant_retrieval_tool(query: str):
    """Retrieves relevant documents from Qdrant using OpenAI embeddings and reranking."""
    docs = retrieve_documents(query, use_reranker=True),
    return docs

