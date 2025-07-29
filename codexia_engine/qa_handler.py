# codexia_engine/qa_handler.py

from huggingface_hub import InferenceClient
from langchain.memory import ConversationBufferMemory
from config import HUGGINGFACE_API_TOKEN



class ConversationalQASystem:
    def __init__(self, vector_store, file_list):
        self.client = InferenceClient(
            #model="HuggingFaceH4/zephyr-7b-beta",very bad response
            #model="meta-llama/Llama-3.1-8B-Instruct",
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=HUGGINGFACE_API_TOKEN
        )
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 2})
        self.memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )
        self.file_list = file_list

    def invoke(self, inputs):
        question = inputs["question"]
        retrieved_docs = self.retriever.invoke(question)
        context_str = "\n\n".join([doc.page_content for doc in retrieved_docs])
        context_str = context_str.replace("[/ASS]", "").replace("[/INST]", "")
        
        file_list_str = "\n".join([f"- {name}" for name in self.file_list])
        system_prompt = f"""
You are "Codexia," an expert AI code analyst. The user is asking questions about a GitHub repository with the following files:
---
{file_list_str}
---
Use the provided context to answer the user's question.

**CRITICAL INSTRUCTIONS:**
1.  **Answer ONLY the user's last question.** Stop after the answer.
2.  **Synthesize the information** into a clean, professional answer. Use bullet points for lists.DONT REPEAT THE CONTEXT
3.  **If asked to list the files, use the file list provided above.**
4.  **Stay Grounded:** If the context does not contain the answer, state that the information is not available.
### EXAMPLE ###
CONTEXT:
This project uses React for the frontend and Node.js with Express for the backend. Data is stored in a PostgreSQL database. The file `database.py` handles the connection.

QUESTION:
What is the tech stack?

ANSWER:
Based on the provided context, this project uses the following technologies:
- **Frontend:** React
- **Backend:** Node.js with Express
- **Database:** PostgreSQL
### END EXAMPLE ###
**Context from the Codebase:**
---
{context_str}
---
"""
        messages = [{"role": "system", "content": system_prompt}]
        chat_history = self.memory.load_memory_variables({})['chat_history']
        
        for msg in chat_history:
            role = "user" if msg.type == "human" else "assistant"
            messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": f"QUESTION:\n---\n{question}\n---\n\nANSWER:"})
        
        response = self.client.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.1,
            # --- FIX IS HERE: Renamed 'stop_sequences' to 'stop' ---
            stop=["<|user|>"]
        )
        
        if response.choices and response.choices[0].message:
            answer = response.choices[0].message.content
        else:
            answer = "Sorry, I encountered an issue and couldn't generate a response."

        self.memory.save_context({"question": question}, {"answer": answer})
        return {"answer": answer}

def create_qa_chain(vector_store, file_list):
    return ConversationalQASystem(vector_store, file_list)