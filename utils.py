import os
import json
import requests
from PyPDF2 import PdfReader
from langchain.chains.question_answering import load_qa_chain
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from flask import Flask, request, jsonify
from openai import OpenAI as OpenAI2

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


def continue_conversation(input_message, conversation_stage, conversation_history):
    next_stage = ""
    response = "error"
    match conversation_stage:
        case "t1":
            response_and_stage = track_order(input_message)
            response = response_and_stage[0]
            next_stage = response_and_stage[1]
            return response, next_stage
        case "r1":
            next_stage = "r2"
            response = "Thank you " + input_message + " next can you tell me which product you want to review?"
        case "r2":
            next_stage = "r3"
            response = "Fantastic, what star rating out of 5 would you give " + input_message + "?"
        case "r3":
            next_stage = "r4"
            response = "Excellent, finally could you please write a sentence " \
                       "or two about your experience with the product?"
        case "r4":
            post_review(conversation_history, input_message)
            next_stage = ""
            response = "Thank you for taking the time to review our product, " \
                       "we appreciate your feedback and have a great day!"
        case "c1":
            if input_message == "question":
                next_stage = ""
                response = "Of course, ask away and I'll answer to the best of my abilities"
            else:
                next_stage = "c2"
                response = "Sorry that I couldn't help you resolve your issue, lets raise a support ticket. Firstly, " \
                           "can I please have a contact email that we can reach you through?"
        case "c2":
            next_stage = "c3"
            response = "Thank you, next can you write a short description of the issue you've had with our service?"
        case "c3":
            raise_ticket(conversation_history, input_message)
            next_stage = ""
            response = "I've raised a support ticket with your complaint, we will reach out to you as soon as " \
                       "possible to help resolve your problem. Have a nice day!"
    return response, next_stage


def post_review(conversation_history, input_message):
    review_data = (conversation_history.split("|"))
    review_data.append(input_message)
    review_json = {
        'name': review_data[-4],
        'product': review_data[-3],
        'starRating': review_data[-2],
        'reviewContent': review_data[-1]
    }
    requests.post("http://127.0.0.1:5000/reviewStubEndpoint",
                  data=review_json,
                  headers={"Content-Type": "application/json"})


def raise_ticket(conversation_history, input_message):
    ticket_data = (conversation_history.split("|"))
    ticket_data.append(input_message)
    ticket_json = {
        "email": ticket_data[-2],
        "complaint": ticket_data[-1]
    }
    requests.post(url="http://127.0.0.1:5000/supportStubEndpoint",
                  data=ticket_json,
                  headers={"Content-Type": "application/json"})


def track_order(input_message):
    endpoint = "http://127.0.0.1:5000/trackingStubEndpoint/" + input_message
    tracking_information = requests.get(endpoint)

    if tracking_information.status_code == 200:
        all_order_data = tracking_information.json()
        client = OpenAI2(api_key=constants.APIKEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful ecommerce chatbot who will receive a json object "
                                              "containing data about a users order. your job is to summarise the "
                                              "details of their order in normal human speech, ensuring that they are "
                                              "told the order status, what date it was shipped on, whether they will "
                                              "receive a SMS or Email notification and whether they will have to "
                                              "provide a signature upon delivery"},
                {"role": "user", "content": str(all_order_data)}
            ]
        )
        openai_answer = response.choices[0].message.content
        return openai_answer, ""

    elif tracking_information.status_code == 404:
        return ("Im afraid we couldn't find an order with tracking code: "
                + input_message
                + ". Please try another code or type '"'cancel'"' to do something else"), "t1"
