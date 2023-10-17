from pprint import pprint
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, JSONLoader
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import threading

"""
Sime steps of operation of the below class -

1. Read json / pdf file.
    a. Read json file
    b. Read PDF file
2. Break down and store document in vector DB
3. Run questions answer chains over the documents
4. Make them run parallelly
5. Return the json
"""


class AnsweringWizard():
    def __init__(self, doc_file_name, que_file_name, open_ai_key):
        self.doc_file_name = doc_file_name
        self.que_file_name = que_file_name
        self.open_ai_key = open_ai_key
        self.retriver = self.get_retriver(self.get_document())
        self.questions = self.get_questions()
        
    def get_document(self):
        if self.doc_file_name.endswith(".pdf"):
            return self.get_document_pdf()
        elif self.doc_file_name.endswith(".json"):
            return self.get_document_json()
        else:
            raise ValueError("File provided should be either a pdf or json")

    def get_questions(self):
        if self.que_file_name.endswith(".pdf"):
            return self.get_questions_pdf()
        elif self.que_file_name.endswith(".json"):
            return [x.page_content for x in self.get_questions_json()]
        else:
            raise ValueError("File provided should be either a pdf or json")

    def get_document_json(self):
        loader = JSONLoader(
            file_path=self.doc_file_name,
            jq_schema='.content',
            text_content=False
        )
        return loader.load()

    def get_questions_json(self):
        loader = JSONLoader(
            file_path=self.que_file_name,
            jq_schema='.questions[].content',
            text_content=False
        )
        return loader.load()

    def get_document_pdf(self):
        loader = PyPDFLoader(self.doc_file_name)
        return loader.load()

    def get_questions_pdf(self):
        # Building custom question loader in order to fetch questions from pdf as per example
        loader = PyPDFLoader(self.que_file_name)
        documents = loader.load()
        data = documents[0].page_content
        questions = []
        current_question_index = 0
        data = data.split("\n")
        current_question_str = ""
        for j in range(len(data)):
            if data[j].startswith(str(current_question_index+1)):
                current_question_index += 1
                if current_question_str!="":
                    questions.append(current_question_str.strip())
                    current_question_str = ""
                current_question_str = data[j][len(str(current_question_index))+1:]
            elif current_question_index!=0:
                current_question_str = current_question_str + data[j]

            if j==len(data)-1:
                questions.append(current_question_str.strip())
        return questions

    def get_retriver(self, contents):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        documents = text_splitter.split_documents(contents)
        embeddings_model = OpenAIEmbeddings(openai_api_key=self.open_ai_key)
        vector_db = FAISS.from_documents(documents, embeddings_model)
        return vector_db.as_retriever()

    def get_chain(self):
        llm =  ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=self.open_ai_key, temperature=0.1)
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer or add your own information. Keep the answers short.

        {context}

        Question: {question}
        Answer: """
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": PROMPT}
        # Using stuff as map_reduce does not take custom prompts
        return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=self.retriver, chain_type_kwargs=chain_type_kwargs)

    def get_answers(self):
        qa_chain = self.get_chain()
        results = []
        
        def run_qa_chain(question):
            answer = qa_chain.run(question)
            results.append({"questions": question, "answer": answer})
        
        threads = []

        for q in self.questions:
            current_thread = threading.Thread(target=run_qa_chain, args=(q, ))
            current_thread.start()
            threads.append(current_thread)

        for i in threads:
            i.join()

        return results