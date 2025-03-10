import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import groq
import torch
from pydantic import BaseModel, Field
import random
import langchain
from typing import Any
from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import score_result

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

class AccuracyMetric:
    def __init__(self, name: str = "Accuracy"):
        self.name = name

    def score(self, output: str, reference: str, **ignored_kwargs: Any):
        score = int(output.strip().lower() == reference.strip().lower())
        reason = f"Output matches reference: {score}"
        return score_result.ScoreResult(name=self.name, value=score, reason=reason)

opik_client = Opik()
dataset = opik_client.get_or_create_dataset(name="Misspelled Inputs")
for i, item in enumerate(misspelled_test_data):
    dataset.insert([{"input": item["input"], "output": item["output"]}])

def evaluation_task(dataset_item):
    # your LLM application is called here

    input = dataset_item["input"]
    output = get_openai_response(input)  # Replace with your actual model response

    result = {
        "input": input,
        "output": output,
        "reference": dataset_item["output"]  # Add the reference key
    }

    return result

metrics = [AccuracyMetric()]
eval_results = evaluate(
    experiment_name="Misspelled Inputs Evaluation",
    dataset=dataset,
    task=evaluation_task,
    scoring_metrics=metrics
)
print(eval_results)
