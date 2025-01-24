import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import groq
import torch
from pydantic import BaseModel, Field
import random
import langchain


# Load Environment Variables
load_dotenv()

# Define a function to introduce misspellings
def introduce_misspellings(text, num_misspellings):
    # Randomly replace characters in the text
    misspelled_text = ""
    for char in text:
        if random.random() < num_misspellings / len(text):
            misspelled_text += chr(random.randint(ord('a'), ord('z')))
        else:
            misspelled_text += char
    return misspelled_text

# Define the functions to get responses from OpenAI and LLaMA
def get_openai_response(prompt: str) -> str:
    """Get response from OpenAI's model"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content


def get_groq_response(prompt: str) -> str:
    """Get response from Groq"""
    client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

# Define the test data
test_data = [
    {"input": "How many stars are there on the flag of the united states of America", "output": "There are 50 stars on the flag of the United States of America"},
    # Add more test data here...
]

# Introduce misspellings into the test data
misspelled_test_data = []
for item in test_data:
    misspelled_input = introduce_misspellings(item["input"], 2)
    misspelled_test_data.append({"input": misspelled_input, "output": item["output"]})

# Get the responses from OpenAI and LLaMA
openai_responses = [get_openai_response(item["input"]) for item in misspelled_test_data]
llama_responses = [get_groq_response(item["input"]) for item in misspelled_test_data]

# Get the responses from OpenAI and LLaMA
openai_responses = [get_openai_response(item["input"]) for item in misspelled_test_data]
llama_responses = [get_groq_response(item["input"]) for item in misspelled_test_data]
# Calculate the accuracy
openai_accuracy = sum(1 for i, response in enumerate(openai_responses) if response.strip().lower() == misspelled_test_data[i]["output"].strip().lower()) / len(misspelled_test_data)
llama_accuracy = sum(1 for i, response in enumerate(llama_responses) if response.strip().lower() == misspelled_test_data[i]["output"].strip().lower()) / len(misspelled_test_data)
print("OpenAI Accuracy:", openai_accuracy)
print("LLaMA Accuracy:", llama_accuracy)

# Print out the input, output, and model responses for each test case
for i, item in enumerate(misspelled_test_data):
    print(f"Test Case {i+1}:")
    print(f"Input: {item['input']}")
    print(f"Expected Output: {item['output']}")
    print(f"OpenAI Response: {openai_responses[i]}")
    print(f"LLaMA Response: {llama_responses[i]}")
    print()
