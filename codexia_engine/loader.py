# codexia_engine/loader.py

import os
import shutil
import tempfile
from langchain_community.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

def load_and_split_repo(repo_url: str):
    repo_path = tempfile.mkdtemp()
    print(f"Created temporary directory: {repo_path}")

    try:
        print(f"Cloning repository from {repo_url} to {repo_path}...")
        loader = GitLoader(clone_url=repo_url, repo_path=repo_path)
        documents = loader.load()

        if not documents:
            print("No documents were loaded from the repository.")
            return [], []

        file_paths = sorted(list(set([doc.metadata['source'] for doc in documents])))
        
        # --- FIX IS HERE: More robust way to get relative paths ---
        cleaned_file_names = []
        # Normalize the base path to handle different OS separators
        normalized_repo_path = os.path.normpath(repo_path)
        for path in file_paths:
            normalized_path = os.path.normpath(path)
            # Remove the base repo path prefix to get the relative path
            if normalized_path.startswith(normalized_repo_path):
                relative_path = normalized_path[len(normalized_repo_path) + 1:]
                cleaned_file_names.append(relative_path.replace('\\', '/'))
            else:
                cleaned_file_names.append(os.path.basename(normalized_path))
        # --- END OF FIX ---

        documents = [doc for doc in documents if os.path.basename(doc.metadata['source']).lower() != 'readme.md']

        if not documents:
            print("No documents were loaded (only READMEs were found).")
            return [], cleaned_file_names

        print(f"Loaded {len(documents)} documents (READMEs excluded).")

        extension_to_language = {
            ".py": Language.PYTHON, ".cpp": Language.CPP, ".c": Language.C,
            ".java": Language.JAVA, ".js": Language.JS, ".ts": Language.TS,
            ".html": Language.HTML,
        }
        all_chunks = []
        default_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

        print("Splitting documents...")
        for doc in documents:
            file_extension = os.path.splitext(doc.metadata['source'])[-1]
            language = extension_to_language.get(file_extension)
            if language:
                language_splitter = RecursiveCharacterTextSplitter.from_language(
                    language=language, chunk_size=2000, chunk_overlap=200
                )
                chunks = language_splitter.split_documents([doc])
            else:
                chunks = default_splitter.split_documents([doc])
            all_chunks.extend(chunks)

        print(f"Created {len(all_chunks)} chunks from {len(documents)} files.")
        return all_chunks, cleaned_file_names

    finally:
        print(f"Cleaning up temporary directory: {repo_path}")
        shutil.rmtree(repo_path, ignore_errors=True)