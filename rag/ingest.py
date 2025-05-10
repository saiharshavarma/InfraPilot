from langchain.document_loaders import (
    UnstructuredURLLoader,
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredRSTLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from config import config

def ingest_documentation(source_dir: str = "docs"):
    config.init()
    documents = []

    # 1. Fetch remote docs if configured
    if config.infrapilot_CONFIG.REMOTE_DOC_URLS:
        url_loader = UnstructuredURLLoader(urls=config.infrapilot_CONFIG.REMOTE_DOC_URLS)
        web_docs = url_loader.load()
        documents.extend(web_docs)
        print(f"Fetched {len(web_docs)} docs from remote URLs")
    # ── Markdown (.md)
    md_loader = DirectoryLoader(
        source_dir,
        glob="**/*.md",
        loader_cls=TextLoader
    )
    md_docs = md_loader.load()

    # ── reStructuredText (.rst)
    rst_loader = DirectoryLoader(
        source_dir,
        glob="**/*.rst",
        loader_cls=TextLoader
    )
    rst_docs = rst_loader.load()

    # ── Plain text (.txt)
    txt_loader = DirectoryLoader(
        source_dir,
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    txt_docs = txt_loader.load()

    count_local = len(md_docs) + len(rst_docs) + len(txt_docs)
    print(
        f"Loaded {count_local} local docs from '{source_dir}' "
        f"({len(md_docs)} md, {len(rst_docs)} rst, {len(txt_docs)} txt)"
    )

    documents.extend(md_docs)
    documents.extend(rst_docs)
    documents.extend(txt_docs)

    # 2a️⃣ Short-circuit if nothing to index
    if not documents:
        print("⚠️  No documentation found—skipping ingestion.")
        return

    # 3️⃣ Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_chunks = splitter.split_documents(documents)

    # 3a️⃣ Also bail on empty chunks
    if not docs_chunks:
        print("⚠️  No document chunks—nothing to index.")
        return

    # 4️⃣ Embed & persist
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        docs_chunks,
        embeddings,
        persist_directory=".chromadb"
    )
    vectorstore.persist()
    print(f"Ingested {len(docs_chunks)} chunks into .chromadb")


if __name__ == "__main__":
    ingest_documentation()