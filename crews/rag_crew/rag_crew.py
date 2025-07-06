# background_pipeline/rag_crew_pipeline.py
import os
import yaml
from crewai import Agent, Task, Crew, Process
# from crewai.project import CrewBase, agent, task, crew
# from crewai.agent import Agent, BaseAgent
# from crewai.task import Task
from crewai import LLM
from tools.retrieval_tool import qdrant_retrieval_tool
from typing import List
from dotenv import load_dotenv

load_dotenv()

with open('crews/rag_crew/config/agents.yaml', 'r') as f:
    agents_config = yaml.safe_load(f)

with open('crews/rag_crew/config/tasks.yaml', 'r') as f:
    tasks_config = yaml.safe_load(f)


llm = LLM(model="gpt-4o-mini")


query_optimizer_agent = Agent(config=agents_config['query_optimizer'],
                       llm=llm)

query_optimizer_task = Task(config=tasks_config['query_optimizer'],
                     agent=query_optimizer_agent
                     )

rag_agent = Agent(config=agents_config['rag'],
                        tools = [qdrant_retrieval_tool],
                       llm=llm)

rag_task = Task(config=tasks_config['retrieve_and_answer'],
                     agent=rag_agent
                     )

hallucination_checker_agent = Agent(config=agents_config['hallucination_checker'],
                       llm=llm)

hallucination_checker_task = Task(config=tasks_config['hallucination_checker'],
                     agent=hallucination_checker_agent
                     )

RAGPipelineCrew = Crew(
    agents = [query_optimizer_agent, rag_agent, hallucination_checker_agent],
    tasks = [query_optimizer_task, rag_task, hallucination_checker_task],
    process = Process.sequential,
    verbose = True
)

# @CrewBase
# class RAGPipelineCrew:
    
#     llm = LLM(model="gpt-4o-mini")

#     with open("crews/rag_crew/config/agents.yaml", "r") as af:
#         agent_configs = yaml.safe_load(af)

#     with open("crews/rag_crew/config/tasks.yaml", "r") as tf:
#         task_configs = yaml.safe_load(tf)
    
#     agents: List[BaseAgent]
#     tasks: List[Task]

#     agents_config = agent_configs
#     tasks_config = task_configs

#     @agent
#     def query_optimizer(self) -> Agent:
#         return Agent(config=self.agents_config["query_optimizer"])

#     @agent
#     def rag(self) -> Agent:
#         return Agent(config=self.agents_config["rag"],
#                      tools=[qdrant_retrieval_tool],
#                      llm = self.llm)
    

#     @agent
#     def hallucination_checker(self) -> Agent:
#         return Agent(config=self.agents_config["hallucination_checker"],
#                      llm = self.llm)

#     @task
#     def optimize_query(self) -> Task:
#         print(self.task_configs)
#         return Task(config = self.tasks_config["query_optimizer"],
#                     llm = self.llm)

#     @task
#     def retrieve_and_answer(self) -> Task:
#         return Task(config = self.tasks_config["rag"])

#     @task
#     def check_hallucination(self) -> Task:
#         return Task(config = self.tasks_config["hallucination_checker"])

#     @crew
#     def run(self) -> Crew:
#         return Crew(
#             agents=[self.query_optimizer(), self.rag(), self.hallucination_checker()],
#             tasks=[
#                 self.optimize_query(),
#                 self.retrieve_and_answer(),
#                 self.check_hallucination()
#             ],
#             verbose=True
#         )
    
