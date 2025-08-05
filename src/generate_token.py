import datetime
import requests
import os
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def get_api_key(key_file_path):
    try:
        with open(key_file_path, 'r') as dat:
            key = json.load(dat)
            ibm_cloud_api_key = key['api_key']
            ibm_project_id = key['project_id']
        # print(f"loaded API key from keys.json : {ibm_cloud_api_key}")
        # print(f"loaded project_id from keys.json : {ibm_project_id}")
        return key

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

def gen_token(ibm_cloud_api_key , iam_token_url):
    
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
        
        # print(f"generated token: {access_token}")
        return access_token
        
    except requests.exceptions.RequestException as re:
        print(f"Token request error: {re}")
        exit(1)
    except ValueError as e:
        print(f"Error parsing payload: {e}")
        exit(1)
        
def orch_gen_token():
    key_file_path = os.path.join(os.getcwd() , "keys" , "keys.json")
    iam_token_url = "https://iam.cloud.ibm.com/identity/token"
    keys = get_api_key(key_file_path)
    keys['bearer_token'] = gen_token(keys['api_key'] , iam_token_url)
    return keys

# if __name__ == '__main__':
#     print(orch_gen_token())