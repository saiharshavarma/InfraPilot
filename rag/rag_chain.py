from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA


def create_rag_chain(k: int = 3) -> RetrievalQA:
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(persist_directory=".chromadb", embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)