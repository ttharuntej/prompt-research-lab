import os
import json
import pydantic
from dotenv import load_dotenv
from openai import OpenAI
import groq
import random
from opik.evaluation.metrics import base_metric, score_result
from opik.evaluation.metrics import (LevenshteinRatio, IsJson)
from opik import Opik
from typing import Any
from opik.evaluation import evaluate
import time
from pydantic import BaseModel
from litellm import completion
from litellm.exceptions import RateLimitError

# Load Environment Variables
load_dotenv()
my_eval_model = "groq/Llama-3.3-70b-Versatile"

class LLMJudgeScoreFormat(pydantic.BaseModel):
    score: int
    reason: str

# Define a function to introduce misspellings
def introduce_misspellings(text, num_misspellings):
    misspelled_text = ""
    for char in text:
        if random.random() < num_misspellings / len(text):
            misspelled_text += chr(random.randint(ord('a'), ord('z')))
        else:
            misspelled_text += char
    return misspelled_text

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
    break

class LLMJudgeMetric(base_metric.BaseMetric):
    def __init__(self, name: str = "Accurate Response"):
        self.name = name
        self.prompt_template = '''
        TASK :
        You are a judge who evaluates the stability of a model to understand a misspelled input prompt and effectively respond with an accurate response.
        It must be JSON formatted and consistently formatted.
        Do not penalize , if the model responds with the correct answer but also includes some additional information.
        The model must be able to understand the misspelled input prompt and respond with an accurate response.
        IF the answer from the model includes the expected output, then give a score of 1.
        If the answer from the model does not include the expected output at all, then give a score of 0.

        The format of the your response should be a JSON object with no additional text or backticks that follows the format:
        {{
            "score": <score between 0 and 1>
            "reason": "<reason for the score>"
        }}
        OUTPUT :{output}
        Response:
        '''

    def score(self, output: str, reference: str, **ignored_kwargs: Any):
        """
        Score the output a of an LLM.

        Args:
            output: The output of an LLM to score.
            reference: Text that the output should be compared against.
            **ignored_kwargs: Any additional keyword arguments. This is important so that the metric can be used in the `evaluate` function.
        """
        # Construct the prompt based on the output of the LLM
        prompt = self.prompt_template.format(output=output, reference=reference)
        #client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        #Generate and parse the response from the LLM
        response = completion(
            model=my_eval_model,
            messages=[{"role": "user", "content": prompt}],
            response_format=LLMJudgeScoreFormat,
            max_tokens=1000
        )
        '''
        # Parse the JSON response to extract the score and reason
        try:
            response_content = response_llama.choices[0].message.content
            score_data = json.loads(response_content)
            final_score = float(score_data.get("score", 0))  # Default to 0 if score is not found
            reason = score_data.get("reason", "No reason provided")
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error parsing score: {e}")
            final_score = 0.0  # Default to 0 in case of error
            reason = "Error parsing response"
        # Return the score and the reason
        return score_result.ScoreResult(
            name=self.name, value=final_score, reason=reason
        )
        '''
        final_score = float(json.loads(response.choices[0].message.content)["score"])
        reason = json.loads(response.choices[0].message.content)["reason"]
            # Return the score and the reason
        return score_result.ScoreResult(
            name=self.name, value=final_score, reason=reason
        )
class LLMOutputSchema(BaseModel):
    input: str
    output: str

def get_model_answer(input_text, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            prompt = f"Give me the answer to the question:'{input_text}'"
            response = completion(
                model=my_model,
                messages=[
                    {"role": "system", "content": "You are just getting answers from llm. return answers in JSON only"},
                    {"role": "user", "content": prompt}
                ],
                response_format=LLMOutputSchema,
                temperature=0
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            # Parse the error message to extract the retry-after time
            error_message = str(e)
            try:
                error_data = json.loads(error_message.split("GroqException - ")[1])
                retry_after_ms = error_data["error"]["message"].split("Please try again in ")[1].split("ms")[0]
                retry_after = int(retry_after_ms) / 1000.0  # Convert milliseconds to seconds
            except (IndexError, KeyError, ValueError):
                retry_after = 2 ** retries + random.uniform(0, 1)  # Fallback to exponential backoff with jitter
            print(f"Rate limit exceeded. Retrying in {retry_after:.2f} seconds...(Attempt {retries + 1}/{max_retries})")
            time.sleep(retry_after)
            retries += 1
    raise Exception("Max retries exceeded. Please try again later.")


def evaluation_task(dataset_item, max_retries=5):
    input_text = dataset_item["input"]
    reference = dataset_item["output"]
    answer = get_model_answer(input_text, max_retries=max_retries)

    result = {
        "input": input_text,
        "output": answer,
        "reference": reference
    }

    return result
'''
def print_evaluation_results(results):
    print("Evaluation Results")
    print("=" * 18)
    print(f"Experiment Name: {results.experiment_name}")
    print(f"Experiment ID: {results.experiment_id}\n")

    for test_result in results.test_results:
        print("Test Case")
        print("-" * 9)
        print(f"Trace ID: {test_result.test_case.trace_id}")
        print(f"Dataset Item ID: {test_result.test_case.dataset_item_id}\n")

        # Accessing the input, expected output, and model output from task_output
        print(f"Input: {test_result.task_output['input']}")
        print(f"Expected Output: {test_result.task_output['reference']}")
        print(f"Model Output: {test_result.task_output['output']}\n")

        print("Scores")
        print("-" * 6)
        for score in test_result.score_results:
            print(f"{score.name}: {score.value}")
            print(f"  - Reason: {score.reason}\n")
        print("-" * 40)
    '''

def main():
    # Create dataset with misspelled test data
    opik_client = Opik()
    dataset = opik_client.get_or_create_dataset(name="Misspelled Inputs")
    print("misspelled test data before for loop in main method:", misspelled_test_data)

    metrics = [LLMJudgeMetric(), IsJson()]
    global my_model
    for model_name in [
        "groq/Llama-3.3-70b-Versatile",
        "gpt-4o",
        # "gpt-4o-mini"
    ]:
        my_model = model_name

        # Define a lambda function to pass max_retries to evaluation_task
        task_with_retries = lambda item: evaluation_task(item, max_retries=5)

        eval_results = evaluate(
            experiment_name="Misspelled Inputs Evaluation: " + model_name,
            dataset=dataset,
            task=task_with_retries,
            scoring_metrics=metrics,
        )
        # Print the formatted results
        print(eval_results)

if __name__ == "__main__":
    main()
