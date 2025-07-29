# Codexia: Your AI GitHub Analyst 💻

Codexia is an AI-powered tool designed to make understanding complex software projects easier. By leveraging Large Language Models (LLMs) and a Retrieval-Augmented Generation (RAG) framework, this application allows you to "chat" with any public GitHub repository. Simply provide a repository URL, and Codexia will ingest the entire codebase, enabling you to ask questions in plain English—from "How is user authentication handled?" to "What is the purpose of the `utils` folder?"—and receive intelligent, context-aware answers.

## ✨ Features

* **Interactive Chat Interface:** Ask questions about a codebase in a natural, conversational way.
* **Dynamic Repository Analysis:** Provide any public GitHub repository URL to start an analysis on the fly.
* **Multi-Language Code Understanding:** Intelligently processes various programming languages by using language-specific text splitters.
* **Context-Aware Answers:** Utilizes a RAG pipeline to ensure answers are grounded in the actual code and documentation of the repository, reducing hallucinations.
* **Conversational Memory:** Remembers the context of your conversation to allow for follow-up questions.

---

## 🛠️ Tech Stack

* **Backend Framework:** Python
* **LLM Orchestration:** LangChain
* **AI Model Provider:** Hugging Face
    * **Core LLM:** `meta-llama/Llama-3.1-8B-Instruct`
    * **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
* **Vector Database:** FAISS (for local similarity search)
* **Web Framework:** Streamlit
* **Core Libraries:** `huggingface_hub`, `transformers`, `torch`, `python-dotenv`, `GitPython`

---

## 🧠 Core Concept: Retrieval-Augmented Generation (RAG)

This project is powered by RAG, a technique that enhances the capabilities of LLMs by connecting them to external, dynamic data—in this case, the code from a GitHub repository. The process works in two main phases:

### Phase 1: Indexing (Building the Knowledge Base)

This is a one-time process that happens when you click "Analyze Repository."

1.  **Load:** The application uses LangChain's `GitLoader` to clone the entire target repository into a temporary local folder.
2.  **Split:** The code and documentation files are broken down into small, meaningful chunks. The application is smart about this, using language-specific splitters (e.g., for Python, Java, C++) to keep related code like functions and classes intact.
3.  **Embed:** Each chunk is converted into a numerical vector using the `SentenceTransformer` embedding model. This vector represents the semantic meaning of the code or text.
4.  **Store:** All these vectors are loaded into a FAISS vector store, which acts as a high-speed, searchable index of the entire codebase.

### Phase 2: Retrieval & Generation (Answering a Question)

This happens in real-time every time you ask a question.

1.  **Retrieve:** Your question is converted into a vector using the same embedding model. The FAISS index is then queried to find the most relevant code chunks from the repository that are semantically similar to your question.
2.  **Augment:** A detailed prompt is constructed. This prompt includes your original question, the conversation history, and the relevant code chunks retrieved from the repository.
3.  **Generate:** This complete prompt is sent to the powerful `Llama-3.1` model. Because the model has the exact context it needs, it can generate a highly relevant and accurate answer instead of relying on its general knowledge.

---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

* Python 3.9+
* Git

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd codexia
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your API Token:**
    * Create a file named `.env` in the root of the project folder.
    * Go to your [Hugging Face Access Tokens settings](https://huggingface.co/settings/tokens) and generate a **new token** with the **"write"** role.
    * Add the token to your `.env` file:
        ```env
        HUGGINGFACE_API_TOKEN="hf_YourTokenGoesHere"
        ```
    * **Important:** You must also accept the license agreement for the Llama 3.1 model on the Hugging Face website to get access. [Visit the model page here](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct).

### Running the Application

Once the setup is complete, run the following command in your terminal:

```bash
streamlit run app.py


🪲 Troubleshooting Journey: From Errors to Success
This project went through a significant debugging process to achieve a stable and high-quality result. Here’s a summary of the key challenges and their solutions:

Challenge: Dependency & Environment Errors

Issue: Initial ModuleNotFoundError errors occurred frequently.

Solution: The root cause was either forgetting to activate the virtual environment (venv\Scripts\activate) or a missing package. We fixed this by ensuring the venv was always active and by installing missing dependencies like langchain-community and langchain-huggingface and updating requirements.txt.

Challenge: Unreliable Hugging Face Free Tier API

Issue: We repeatedly encountered a ValueError stating that a model was not supported for the text-generation task by various backend providers (like cerebras, nebius, featherless-ai). This was the most persistent issue.

Troubleshooting: We tried several powerful models (Mixtral, Gemma, Llama 3.1, Zephyr), but the API backend would often route them to a provider that only supported the conversational task, causing a crash.

Solution: We abandoned the standard LangChain LLM wrappers and built a custom class that calls the Hugging Face InferenceClient directly using the .chat_completion() method. This ensured our requests were always sent in the correct format, finally resolving the API incompatibility.

Challenge: The 403 Forbidden Permissions Error

Issue: Even with the correct code, the API returned a 403 Forbidden error.

Solution: This was not a code issue but a permissions problem with the Hugging Face account. The fix involved two steps on the HF website:

Accepting the license agreement for the gated model (Llama 3.1).

Generating a new API token with "write" permissions.

Challenge: Poor Quality & Hallucinated AI Responses

Issue: The AI's answers were often repetitive, poorly formatted, or completely wrong (e.g., hallucinating file names).

Troubleshooting: This required several rounds of prompt engineering.

Solution: We implemented a final, robust "Few-Shot" prompt. By showing the AI a perfect example of a question and a well-structured answer, we gave it a clear template to follow. This, combined with switching to the more capable meta-llama/Llama-3.1-8B-Instruct model, eliminated the repetition and hallucinations, resulting in high-quality, professional answers.

Challenge: Windows-Specific Errors

Issue: We encountered a WinError 32 (file in use) and a path error when the project was on a different drive than the temporary folder.

Solution: We fixed the WinError 32 by refactoring the loader.py script to manually manage the temporary directory with a try...finally block and shutil. We fixed the cross-drive path error by replacing os.path.relpath with a more robust string manipulation method.
