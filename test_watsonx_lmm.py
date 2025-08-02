import requests
import os
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

ibm_cloud_api_key = "" # API KEY
iam_token_url = "https://iam.cloud.ibm.com/identity/token"

iam_body = {
	"grant_type" : "urn:ibm:params:oauth:grant-type:apikey",
	"apikey" : ibm_cloud_api_key
}
iam_headers = {
	"Content-Type" : "application/x-www-form-urlencoded",
	"Accept" : "application/json"
}

try:
    iam_response = requests.post(iam_token_url , data=iam_body , headers=iam_headers)
    iam_response.raise_for_status()
    
    iam_data = iam_response.json()
    access_token = iam_data.get("access_token")
    
    if not access_token:
        raise ValueError("not found 'access_token' in payload ")
    
    print("generated token")
    
except requests.exceptions.RequestException as re:
    print(f"Token request error: {re}")
    exit(1)
except ValueError as e:
    print(f"Error parsing payload: {e}")
    exit(1)
    


# Use 'service' to invoke operations.
url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

message_list = {
	"What are polynomial functions", # Simple Maths
	"Are linear equations a subset of Polynomials",
	"How can a multi-variable linear equation be described in terms of dimensional represenations",
	"What are calibi-yau manifolds , how do they describe the behaviour of complex linear equations",
	"What are the limitations of Newton's method, define the function boundaries if any here",
	"How would you describe ",
	"What is a field in Number theory.",
	"Define the rank plus nihility theorem",
	"Explain the complexification of a real vector space",
	"What are linear functionals",
	"What are cyclic Modules",
	"Explain the hilbert basis theorem",
}

body = {
	"messages": [{"role":"system","content":"You always answer the questions with markdown formatting using GitHub syntax. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.\n\nAny HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.\n\nWhen returning code blocks, specify language.\n\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. \nYour answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don'\''t know the answer to a question, please don'\''t share false information."}],
	"project_id": "e869834c-a4d3-4d17-8d16-cb6db32b3354",
	"model_id": "meta-llama/llama-3-3-70b-instruct",
	"frequency_penalty": 0,
	"max_tokens": 2000,
	"presence_penalty": 0,
	"temperature": 0,
	"top_p": 1
}

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": f"Bearer {access_token}"
}

try:
	response = requests.post(
		url,
		headers=headers,
		json=body
	)
	
	response.raise_for_status()
 
	data = response.json()

	print("\nAPI response: ")
	print(json.dumps(data,indent=2))

except requests.exceptions.RequestException as re:
    print(f"\nError making api call : {e}")
    print(F"\nPayload: {response.text}")
    exit(1)
# if response.status_code != 200:
# 	raise Exception("Non-200 response: " + str(response.text))

# data = response.json()