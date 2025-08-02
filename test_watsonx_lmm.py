import requests

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm-cloud-sdk-core.example_service_v1 import *

# Create the authenticator.
authenticator = IAMAuthenticator('myapikey')

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# Use 'service' to invoke operations.
url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

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
	"Authorization": "Bearer ApiKey-dd010e0f-973d-47af-a6df-c032c35df026"
}


response = requests.post(
	url,
	headers=headers,
	json=body
)

if response.status_code != 200:
	raise Exception("Non-200 response: " + str(response.text))

data = response.json()