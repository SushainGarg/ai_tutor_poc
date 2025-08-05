import json
import os;
from flask import Flask , request , jsonify
from flask_cors import CORS
import requests
from generate_token import orch_gen_token
from simple_react_agent import react_loop

app = Flask(__name__)
CORS(app)

keys = orch_gen_token()
WATSON_API_KEY = keys['bearer_token']
WATSON_PROJECT_ID = keys['project_id']
WATSON_API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
WATSON_MODEL_ID = "meta-llama/llama-3-2-11b-vision-instruct"
WATSONX_MODEL_ID_TEXT = "meta-llama/llama-3-3-70b-instruct"
WATSONX_MODEL_ID_VISION = "meta-llama/llama-3-2-11b-vision-instruct"
WATSONX_MODEL_ID_PARSING = "meta-llama/llama-3-8b-instruct"

print(WATSON_API_KEY)

current_multimodal_observations = {
    "video": {},
    "audio": {},
    "screen": {}
}

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

@app('/process-video-frame', methods=['POST'])
def process_video_frame():
    try:
        data = request.json()
        img_url = data.get('imageUrl')
        
        if not img_url:
            return jsonify({"Error": "No image data"}) , 400
        
        vision_prompt_desc =  "Describe the person's facial expression and body language, focusing on signs of mood, engagement, and concentration."
        
        vision_payload = {
            "model_id": WATSON_MODEL_ID,
            "messages": [
                {
                    "role" : "user",
                    "content" : [
                        {
                            "type": "text",
                            "text": vision_prompt_desc
                        },
                        {
                            "type" : "image_url",
                            "image_url" : {
                            "url" : img_url
                            }
                        }
                    ]                    
                }
            ],
            "project_id" : WATSON_PROJECT_ID,
            "frequency_penalty": 0,
            "max_tokens": 2000,
            "presence_penalty": 0,
            "temperature": 0,
            "top_p": 1
        }
        
        headers = {
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {WATSON_API_KEY}"
        }
        
        vision_desc_text = ""
        try:
            response_vision = requests.post(WATSON_API_URL, headers=headers, json=vision_payload)
            response_vision.raise_for_status()
            watsonx_vision_result = response_vision.json()
            
            if watsonx_vision_result.get('choices') and watsonx_vision_result['choices'][0].get('message'):
                vision_desc_text = watsonx_vision_result['choices'][0]['message']['content']
            else:
                vision_desc_text = "Vision model did not return valid content."
                print("Warning: Vision model response structure unexpected.")
                print(json.dumps(watsonx_vision_result, indent=2))

        except requests.exceptions.RequestException as req_err:
            print(f"Watsonx Vision API (description) request failed: {req_err}")
            return jsonify({"error": f"Failed to get vision description: {req_err}"}), 502
        
        parsing_prompt = f"""
        Analyze the following description of a person's mood, engagement, and concentration.
        Extract the primary mood (e.g., focused, confused, frustrated, bored, engaged, neutral) and estimate their concentration level as an integer from 0 to 100.
        Return the output as a JSON object with two keys: "mood" (string) and "concentration_level" (integer).
        If a value cannot be confidently extracted, use "unknown" for mood and 0 for concentration_level.

        Description: "{vision_desc_text}"
        """
        
        parsing_payload = {
            "model_id": WATSONX_MODEL_ID_PARSING, # Using the smaller LLM for parsing
            "messages": [
                {
                    "role": "user",
                    "content": parsing_prompt
                }
            ],
            "project_id": WATSON_PROJECT_ID,
            "decoding_method": "greedy",
            "max_new_tokens": 100, 
            "temperature": 0.1
        }
        
        parsed_mood = "unknown"
        parsed_concentration = 0
        
        try:
            response_parsing = requests.post(WATSON_API_URL, headers=headers, json=parsing_payload)
            response_parsing.raise_for_status()
            watsonx_parsing_result = response_parsing.json()

            if watsonx_parsing_result.get('choices') and watsonx_parsing_result['choices'][0].get('message'):
                parsed_content_str = watsonx_parsing_result['choices'][0]['message']['content']
                # Attempt to parse the string content as JSON
                try:
                    parsed_data = json.loads(parsed_content_str)
                    parsed_mood = parsed_data.get("mood", "unknown")
                    parsed_concentration = parsed_data.get("concentration_level", 0)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to JSON parse LLM response: {parsed_content_str}")
                    if "Mood:" in parsed_content_str and "Concentration:" in parsed_content_str:
                        try:
                            mood_part = parsed_content_str.split("Mood:")[1].split(",")[0].strip()
                            concentration_part = parsed_content_str.split("Concentration:")[1].split(".")[0].strip()
                            parsed_mood = mood_part.lower()
                            parsed_concentration = int(concentration_part)
                        except (ValueError, IndexError):
                            print(f"Warning: Simple parsing also failed for: {parsed_content_str}")
            else:
                print("Warning: Parsing LLM did not return valid content.")
                print(json.dumps(watsonx_parsing_result, indent=2))

        except requests.exceptions.RequestException as req_err:
            print(f"Watsonx LLM (parsing) API request failed: {req_err}")
        except Exception as e:
            print(f"An unexpected error occurred during parsing LLM call: {e}")
        
        current_multimodal_observations["video"] = {
            "modality": "video",
            "mood": parsed_mood,
            "concentration_level": parsed_concentration
        }
        print(f"Updated video observations: {current_multimodal_observations['video']}")

        return jsonify({"status": "success", "observations": current_multimodal_observations["video"]})

    except Exception as e:
        print(f"An unexpected error occurred in /process-video-frame: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500


@app.route('/run-tutor-react', methods=['POST'])
def run_tutor_react():
    try:
        data = request.json
        initial_state = data.get('initial_state', "The student is starting a new session on Linear Algebra.")
        max_iterations = data.get('max_iterations', 5)
        time_constraint_minutes = data.get('time_constraint_minutes', 10)

        final_response = react_loop(
            initial_state=initial_state,
            max_iterations=max_iterations,
            time_constraint_minutes=time_constraint_minutes,
            
            video_obs=current_multimodal_observations["video"],
            audio_obs=current_multimodal_observations["audio"],
            screen_obs=current_multimodal_observations["screen"]
        )
        
        return jsonify({"tutor_response": final_response, "latest_observations": current_multimodal_observations})

    except Exception as e:
        print(f"Error running ReAct agent: {e}")
        return jsonify({"error": f"Failed to run tutor agent: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

