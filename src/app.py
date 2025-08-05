import os;
from flask import Flask , request , jsonify
from flask_cors import CORS
import requests
from generate_token import orch_gen_token

app = Flask(__name__)
CORS(app)

keys = orch_gen_token()
WATSON_API_KEY = keys['bearer_token']
WATSON_PROJECT_ID = keys['project_id']
WATSON_API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
WATSON_MODEL_ID = "meta-llama/llama-3-2-11b-vision-instruct"

print(WATSON_API_KEY)

@app.route('/analyze-image' , methods =['POST'])
def analyze_image():
    try:
        data = request.json
        prompt = data.get('prompt')
        img_url = data.get('imageUrl')
        
        if not prompt or not img_url:
            return jsonify({"error": "Prompt and image data are required"}), 400
        
        payload = {
            "model_id": WATSON_MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url
                            }
                        }
                    ]
                }
            ],
            "project_id": WATSON_PROJECT_ID,
            "model_id" : "meta-llama/llama-3-2-11b-vision-instruct",
            "frequency_penalty": 0,
            "max_tokens": 2000,
            "presence_penalty": 0,
            "temperature": 0,
            "top_p": 1
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {WATSON_API_KEY}"
        }
        try:
            response = requests.post(WATSON_API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            result = response.json()
        except requests.exceptions.RequestException as req_err:
            print(f"Watsonx API request failed: {req_err}")
            # This ensures that a proper JSON response is always returned on API failure.
            return jsonify({"error": f"Failed to connect to Watsonx API: {req_err}"}), 502
        
        result_text = "Could not get a valid response from the API."
        if result.get('choices') and result['choices'][0].get('message'):
            cont_pts = result['choices'][0]['message']['content']
            if isinstance(cont_pts, list):
                result_text = "\n\n".join(part.get('text', '') for part in cont_pts)
            else:
                result_text = cont_pts
                
        return jsonify({"result": result_text})
    except requests.exceptions.RequestException as e:
        print(f"request failed: {e}")
        return jsonify({"error": "Failed to connect to watsonx endpoint"}), 500
    except Exception as e:
        print(f"An unexpected error occurred in the analyze-image function: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

