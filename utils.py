import os

from PyPDF2 import PdfReader
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

import constants


def get_response(msg):
    os.environ["OPENAI_API_KEY"] = constants.APIKEY

    company_information = digest_and_format_company_data('ecommerceBusinesses.pdf')
    vector_structure = OpenAIEmbeddings()

    searchable_document = FAISS.from_texts(company_information, vector_structure)

    docs = searchable_document.similarity_search(msg)

    chain = load_qa_chain(OpenAI(), chain_type="stuff")
    return chain.run(input_documents=docs, question=msg)


def digest_and_format_company_data(name):
    pdf_reader = PdfReader(name)

    digested_text_from_pdf = ''

    for p, page in enumerate(pdf_reader.pages):
        page_content = page.extract_text()
        if page_content:
            digested_text_from_pdf += page_content

    text_formatter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    formatted_document_data = text_formatter.split_text(digested_text_from_pdf)
    return formatted_document_data

