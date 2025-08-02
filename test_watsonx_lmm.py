import datetime
import requests
import os
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

iam_token_url = "https://iam.cloud.ibm.com/identity/token"
key_file_path = os.path.join(os.getcwd() , "keys" , "keys.json")

try:
    with open(key_file_path, 'r') as dat:
        key = json.load(dat)
        ibm_cloud_api_key = key['api_key']
    
    print(f"loaded API key from keys.json : {ibm_cloud_api_key}")

except FileNotFoundError:
    print(f"Error: {key_file_path} not found.")
    print("create 'keys' dir in cwd and keep 'keys.json' inside it.")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: {key_file_path} not valid JSON.")
    exit(1)
except KeyError:
    print(f"Error: {key_file_path} must have 'api_key' key-value pair.")
    exit(1)

iam_body = {
	"grant_type" : "urn:ibm:params:oauth:grant-type:apikey",
	"apikey" : ibm_cloud_api_key
}
iam_headers = {
	"Content-Type" : "application/x-www-form-urlencoded",
	"Accept" : "application/json"
}

try:
    iam_response = requests.post(iam_token_url , data=iam_body , headers=iam_headers , verify=False)
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
	"How would you describe affine Geometry",
	"What is a field in Number theory.",
	"Define the rank plus nihility theorem",
	"Explain the complexification of a real vector space",
	"What are linear functionals",
	"What are cyclic Modules",
	"Explain the hilbert basis theorem",
	"भारत की राजधानी क्या है?", 
    "Tell me a short story about a robot.", 
    "एक छोटे रोबोट के बारे में एक छोटी कहानी सुनाओ।",
    "Write a python function to find the factorial of a number." 
}

results_dir = os.path.join(os.getcwd() , 'results')
os.makedirs(results_dir, exist_ok=True)

of_name = f"api_resp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
of_path = os.path.join(results_dir , of_name)

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": f"Bearer {access_token}"
}


with open(of_path , 'w' , encoding='utf-8') as outfile:
    print(f'wWriting resp to {of_path}')
    for message in message_list:
        body = {
			"messages": [
				{
					"role":"system",
					"content":"You always answer the questions with markdown formatting using GitHub syntax. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.\n\nAny HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.\n\nWhen returning code blocks, specify language.\n\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. \nYour answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don'\''t know the answer to a question, please don'\''t share false information."
				},
				{
					"role" : "user",
					"content" : message
				}
			],
			"project_id": "e869834c-a4d3-4d17-8d16-cb6db32b3354",
			"model_id": "meta-llama/llama-3-3-70b-instruct",
			"frequency_penalty": 0,
			"max_tokens": 2000,
			"presence_penalty": 0,
			"temperature": 0,
			"top_p": 1
		}
        try:
            response = requests.post(
				url,
				headers=headers,
				json=body,
				verify=False
			)
            response.raise_for_status()
            data = response.json()
            
            print(f"\n--- Testing message: '{message}' ---")
            print("Response:")
            
            model_response = data['choices'][0]['message']['content']
            print(model_response)
            
            outfile.write(f"---Query: '{message}'----\n ")
            outfile.write(f"API Response: \n")
            outfile.write(model_response + "\n\n")
            
            
            
        except requests.exceptions.RequestException as re:
            print(f"\nError making api call for meassage {message} : {re}")
            outfile.write(re + '\n\n')
            if 'response' in locals() and response.text:
                er_text = f"Response text: {response.text}"
                outfile.write(er_text + "\n\n")
                print(er_text)
            continue
        except KeyError as ke:
            em = f"error parsing response for message {message} : Missing key {ke}"
            outfile.write(em + "\n\n")
            print(em)
            continue
		# if response.status_code != 200:
		# 	raise Exception("Non-200 response: " + str(response.text))

		# data = response.json()