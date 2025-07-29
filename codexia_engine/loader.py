# codexia_engine/loader.py

import os
import shutil
import tempfile
from langchain_community.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

def load_and_split_repo(repo_url: str):
    # Create a temporary directory to clone the Git repo into
    repo_path = tempfile.mkdtemp()
    print(f"Created temporary directory: {repo_path}")

    try:
        # Clone the Git repository to the temp directory using LangChain's GitLoader
        print(f"Cloning repository from {repo_url} to {repo_path}...")
        loader = GitLoader(clone_url=repo_url, repo_path=repo_path)
        documents = loader.load()

        # If no documents were extracted (repo is empty or unsupported format), abort early
        if not documents:
            print("No documents were loaded from the repository.")
            return [], []

        # Extract and sort unique source file paths from the document metadata
        file_paths = sorted(list(set([doc.metadata['source'] for doc in documents])))

        # --- FIX IS HERE: Handle OS path normalization and robust relative path calculation ---
        cleaned_file_names = []
        normalized_repo_path = os.path.normpath(repo_path)  # Normalize to handle OS-specific slashes

        for path in file_paths:
            normalized_path = os.path.normpath(path)
            if normalized_path.startswith(normalized_repo_path):
                # Remove the absolute temp path prefix to get clean relative path for display
                relative_path = normalized_path[len(normalized_repo_path) + 1:]
                cleaned_file_names.append(relative_path.replace('\\', '/'))  # Standardize to forward slashes
            else:
                # Fallback: just use the filename (likely shouldn't happen, but covers edge case)
                cleaned_file_names.append(os.path.basename(normalized_path))
        # --- END OF FIX ---

        # Filter out README.md files (not useful for code understanding)
        documents = [doc for doc in documents if os.path.basename(doc.metadata['source']).lower() != 'readme.md']

        # If all loaded files were README.md, abort and return just file names
        if not documents:
            print("No documents were loaded (only READMEs were found).")
            return [], cleaned_file_names

        print(f"Loaded {len(documents)} documents (READMEs excluded).")

        # Mapping file extensions to supported languages for syntax-aware splitting
        extension_to_language = {
            ".py": Language.PYTHON, ".cpp": Language.CPP, ".c": Language.C,
            ".java": Language.JAVA, ".js": Language.JS, ".ts": Language.TS,
            ".html": Language.HTML,
        }

        all_chunks = []
        # Default splitter if no language-specific strategy is available
        default_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

        print("Splitting documents...")

        # Iterate through each document and split it into manageable chunks
        for doc in documents:
            file_extension = os.path.splitext(doc.metadata['source'])[-1]
            language = extension_to_language.get(file_extension)

            if language:
                # Use language-aware splitting (e.g., aware of functions, classes, etc.)
                language_splitter = RecursiveCharacterTextSplitter.from_language(
                    language=language, chunk_size=2000, chunk_overlap=200
                )
                chunks = language_splitter.split_documents([doc])
            else:
                # Fallback to default text-based splitting
                chunks = default_splitter.split_documents([doc])

            all_chunks.extend(chunks)

        print(f"Created {len(all_chunks)} chunks from {len(documents)} files.")
        return all_chunks, cleaned_file_names

    finally:
        # Always delete the temp directory no matter what happens
        print(f"Cleaning up temporary directory: {repo_path}")
        shutil.rmtree(repo_path, ignore_errors=True)
