# 🚀 Patent Chat Assistant

A smart assistant that answers user questions about future technology trends (like innovations in lithium batteries) by checking and analyzing patent data. Built with a step-by-step decision flow using a Retrieval-Augmented Generation (RAG) pipeline and modular agent workflow.

---

## 💡 How It Works

### 1. User Asks a Question
The assistant receives a user query such as:
> _"Give me future innovations or emerging technologies related to lithium batteries"_

### 2. Understanding the Topic
- The system extracts the main topic from the user’s query.
- Example: "lithium battery"

### 3. Check if Data is Ready
- If the topic data **is already available**, the assistant proceeds to answer.
- If the topic is **being processed**, the assistant notifies the user.
- If the topic is **unseen**, the assistant starts data ingestion in the background.

### 4. Three Possible Responses
- ⚡ **Processing**: _"We’re working on it. Please wait."_
- ❌ **Not Available**: _"We’re fetching patent data. Try again in a few hours."_
- ✅ **Available**: The assistant uses the RAG system to give a smart, informative answer.

### 5. When Data is Ready
- A Retrieval-Augmented Generation (RAG) pipeline is used to generate detailed answers using collected patent data.

---

## 📂 Patent Data Sources Used (and Limitations)

| Source | Description | Access Method | Status |
|--------|-------------|----------------|--------|
| **BigQuery (Google Cloud)** | Public patent datasets including USPTO, WIPO, etc. | SQL querying (paid) | - |
| **WIPO PATENTSCOPE** | Global patents via WIPO | Manual UI only | ❌ Web scraping not allowed, awaiting API access |
| **Espacenet (EPO)** | European patents and data | Manual interface only | ❌ Scraping disallowed, API access pending |
| **The Lens** | Patent and scholarly data platform | API after registration | ⏳ Access requested |
| **EPO Developer Portal** | European Patent Office API | Requires approval | ⏳ Waiting for API key |
| **USPTO PatentsView** | U.S. Patent API | Public REST API | ⏳ Waiting for access key |

---


## Architecture
![image](data/Data_Ingestion_Pipeline.png)

## 🌐 Future Enhancements
- Connect to real-time patent APIs once API keys are available
- Add summarization agents for deeper responses
- Build user dashboard 



