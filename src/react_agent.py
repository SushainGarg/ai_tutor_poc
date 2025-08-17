import json
import time
import requests
import re

class ReActAgent:
    """
    A class representing the ReAct agent for an adaptive tutoring system.
    This version is integrated to work with a live Flask server and Watsonx APIs.
    """

    def __init__(self, watsonx_api_key: str, watsonx_project_id: str,
                 watsonx_api_url: str, watsonx_model_id: str,
                 rag_db, multimodal_observations: dict):
        """
        Initializes the agent with its state, tools, and real-time data sources.
        
        Args:
            watsonx_api_key (str): API key for Watsonx.
            watsonx_project_id (str): Project ID for Watsonx.
            watsonx_api_url (str): API URL for text generation.
            watsonx_model_id (str): The model ID for the ReAct loop LLM.
            rag_db: An instance of the Chroma database for RAG.
            multimodal_observations (dict): A shared dictionary for real-time sensor data.
        """
        self.watsonx_api_key = watsonx_api_key
        self.watsonx_project_id = watsonx_project_id
        self.watsonx_api_url = watsonx_api_url
        self.watsonx_model_id = watsonx_model_id
        self.rag_db = rag_db
        self.multimodal_observations = multimodal_observations
        self.conversation_history = ""
        self.student_long_term_performance = {
            "knowledge_scores_history": [],
            "concentration_history": [],
            "memory_retention_history": []
        }
        self.tools = {
            "analyze_video": self.analyze_video,
            "analyze_audio": self.analyze_audio,
            "analyze_screen": self.analyze_screen,
            "update_short_term": self.update_short_term,
            "update_long_term": self.update_long_term,
            "gen_content": self.gen_content,
            "update_content": self.update_content,
            "encourage_user": self.encourage_user,
            "rag_book": self.rag_book,
            "update_long_term_performance": self.update_long_term_performance,
            "retrieve_long_term_performance": self.retrieve_long_term_performance,
        }

    def analyze_video(self, action_input=None):
        """Reads the latest video observations from the shared state."""
        print("Tool: Reading latest video observations...")
        return self.multimodal_observations.get("video", {})

    def analyze_audio(self, action_input=None):
        """Reads the latest audio observations from the shared state."""
        print("Tool: Reading latest audio observations...")
        return self.multimodal_observations.get("audio", {})
    
    def analyze_screen(self, action_input=None):
        """Reads the latest screen observations from the shared state."""
        print("Tool: Reading latest screen observations...")
        return self.multimodal_observations.get("screen", {})

    def update_short_term(self, action_input):
        """Modifies the short-term plan (mocked)."""
        print(f"Tool: Modifying short-term plan: {action_input}")
        time.sleep(1)
        return f"Observation: Short-term plan adjusted: '{action_input}'."

    def update_long_term(self, action_input):
        """Modifies the long-term plan (mocked)."""
        print(f"Tool: Modifying long-term plan: {action_input}")
        time.sleep(1)
        return f"Observation: Long-term plan adjusted: '{action_input}'."

    def gen_content(self, action_input):
        """Generates new content based on the input (mocked)."""
        print(f"Tool: Generating new content based on provided context and instruction...")
        
        try:
            # Parse the incoming JSON string from the ReAct loop
            parsed_input = json.loads(action_input)
            context = parsed_input.get("context", "")
            instruction = parsed_input.get("instruction", "provide a helpful explanation.")
            
            if not context:
                return "Observation: gen_content requires context. No content generated."

            # Construct the prompt using the context and the dynamic instruction
            synthesis_prompt = (
                f"You are a friendly and encouraging tutor. Your task is to explain a complex topic "
                f"in a simple, easy-to-understand way. Based on the student's needs, please {instruction}.\n\n"
                f"Here is some retrieved context about the topic:\n"
                f"---CONTEXT---\n"
                f"{context}\n"
                f"---CONTEXT---\n\n"
                f"Please synthesize this information into a helpful, one-paragraph explanation for the student."
            )

            # Call the LLM to synthesize the final content
            synthesized_content = self.call_llm_api(synthesis_prompt)
            print(f"Synthesized Content: {synthesized_content}")
            return f"Observation: New content generated: '{synthesized_content}'"
        except json.JSONDecodeError:
            return "Observation: Invalid JSON format for gen_content. Please provide a JSON string."
        except Exception as e:
            return f"Observation: Failed to generate content due to an error: {e}"

    def update_content(self, action_input):
        """Modifies existing content (mocked)."""
        print(f"Tool: Modifying existing content: {action_input}")
        time.sleep(1)
        return f"Observation: Existing content modified: '{action_input}'."

    def encourage_user(self, action_input=None):
        """Provides encouragement to the user (mocked)."""
        print("Tool: Providing encouragement...")
        time.sleep(1)
        return "Observation: The tutor said, 'You're making great progress!'"

    def rag_book(self, query):
        """Retrieves context from the real RAG database."""
        if not self.rag_db:
            return "Observation: RAG system not available."
        print(f"Tool: Retrieving knowledge from book for query: '{query}'...")
        docs = self.rag_db.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        return f"Observation: Retrieved relevant passages:\n{context}"

    def update_long_term_performance(self, new_observations):
        """Updates the agent's long-term performance records."""
        print("Tool: Updating long-term performance records...")
        if isinstance(new_observations, str):
            try:
                new_observations = json.loads(new_observations)
            except json.JSONDecodeError:
                return "Observation: Failed to parse long-term performance data."
        
        if new_observations.get("knowledge_score_linear_algebra") is not None:
            self.student_long_term_performance["knowledge_scores_history"].append(
                new_observations["knowledge_score_linear_algebra"]
            )
        if new_observations.get("concentration_level") is not None:
            self.student_long_term_performance["concentration_history"].append(
                new_observations["concentration_level"]
            )
        if new_observations.get("memory_retention_rate") is not None:
            self.student_long_term_performance["memory_retention_history"].append(
                new_observations["memory_retention_rate"]
            )
        print(f"Long-term performance updated: {self.student_long_term_performance}")
        return "Observation: Long-term performance records updated."

    def retrieve_long_term_performance(self, action_input=None):
        """Retrieves and returns the agent's long-term performance records."""
        print("Tool: Retrieving long-term performance records...")
        return f"Observation: Historical performance data: {self.student_long_term_performance}"

    def call_llm_api(self, prompt: str):
        """
        Calls the Watsonx LLM API with the ReAct prompt.
        """
        print("Calling Watsonx LLM API...")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.watsonx_api_key}"
        }
        payload = {
            "model_id": self.watsonx_model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "project_id": self.watsonx_project_id,
            "frequency_penalty": 0,
            "max_tokens": 2000,
            "presence_penalty": 0,
            "temperature": 0.4, # A slightly higher temp for more creative problem solving
            "top_p": 1,
        }
        
        try:
            response = requests.post(self.watsonx_api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            result_text = "Could not get a valid response from the API."
            if result.get('choices') and result['choices'][0].get('message'):
                result_text = result['choices'][0]['message']['content']
            return result_text
        except requests.exceptions.RequestException as req_err:
            print(f"Watsonx API request failed: {req_err}")
            return f"Error: Failed to connect to Watsonx API: {req_err}"
    
    def parse_llm_output(self, output: str):
        """Parses the output of the LLM into a structured dictionary."""
        parsed_output = {}
        output_lower = output.lower()

        thought_match = re.search(r"thought:([\s\S]*?)(?=action:|final answer:|$)", output_lower, re.IGNORECASE)
        action_match = re.search(r"action:([\s\S]*?)(?=action input:|final answer:|$)", output_lower, re.IGNORECASE)
        action_input_match = re.search(r"action input:([\s\S]*?)(?=final answer:|$)", output_lower, re.IGNORECASE)
        final_answer_match = re.search(r"final answer:([\s\S]*?)$", output_lower, re.IGNORECASE)

        if thought_match:
            parsed_output["thought"] = thought_match.group(1).strip()
        if action_match:
            parsed_output["action"] = action_match.group(1).strip()
        if action_input_match:
            action_input = action_input_match.group(1).strip()
            parsed_output["action_input"] = action_input if action_input.lower() != "none" else None
        if final_answer_match:
            parsed_output["final_answer"] = final_answer_match.group(1).strip()
            
        return parsed_output

    def run_react_loop(self, initial_state: str, max_it: int = 50, time_constr: int = 10):
        """Executes the main ReAct loop."""
        self.conversation_history = initial_state
        start_time = time.time()
        print(f"Initial State: {self.conversation_history}\n")
        
        for i in range(max_it):
            print(f"--- Iteration {i+1} ---")
            
            elapsed_time = (time.time() - start_time) / 60
            if elapsed_time > time_constr:
                print("Time constraint reached. Ending session.")
                return "Maximum time constraint reached."

            prompt_with_obs = (
                f"You are a ReAct agent for an adaptive tutoring system. Your task is to observe multimodal "
                f"data about a student and decide the best next action using the available tools.\n\n"
                f"Tools available: {json.dumps(list(self.tools.keys()))}\n\n"
                f"Current conversation history and context:\n{self.conversation_history}\n\n"
                f"Current Time Remaining: {time_constr - elapsed_time:.1f} minutes.\n"
                f"Latest Video Observation: {json.dumps(self.multimodal_observations.get('video'))}\n"
                f"Latest Audio Observation: {json.dumps(self.multimodal_observations.get('audio'))}\n"
                f"Latest Screen Observation: {json.dumps(self.multimodal_observations.get('screen'))}\n"
                f"Historical Performance (Summary): {json.dumps(self.student_long_term_performance)}\n\n"
                f"If the current conversation history does not contain relevant, retrieved knowledge, your primary goal is to use the 'rag_book' tool to get it.\n"
                f"Example: Thought: The user is asking about a new topic and I need to retrieve information. Action: rag_book. Action Input: What is a vector space?\n\n"
                f"If you have already retrieved the necessary information from the `rag_book` tool, you can then proceed to the next step.\n\n"
                f"Think about the best action to take. The thought should be concise and direct. The action must be a valid tool name.\n"
                f"If you choose 'gen_content', the 'Action Input' must be a JSON string with a 'context' key "
                f"(from the 'rag_book' tool) and a specific 'instruction' key (e.g., 'provide a simple analogy', "
                f"'explain with a step-by-step example', or 'give a concise summary').\n"
                f"Begin with 'Thought:', follow with 'Action: [tool_name]', and 'Action Input: [input]'.\n"
                f"If you have a final answer, use 'Final Answer: [response]'.\n"
            )

            lmm_out = self.call_llm_api(prompt_with_obs)
            print(f"LLM Output:\n{lmm_out}")
            parsed_out = self.parse_llm_output(lmm_out)

            thought = parsed_out.get("thought")
            action = parsed_out.get("action")
            action_input = parsed_out.get("action_input")
            final_answer = parsed_out.get("final_answer")

            if thought:
                print(f"Thought: {thought}")

            if final_answer:
                print(f"Final Answer: {final_answer}")
                return final_answer
            
            if action:
                print(f"Action: {action}")
                if action in self.tools:
                    tool_function = self.tools[action]
                    try:
                        obs_raw = tool_function(action_input)
                        
                        # Check for the structured final answer signal from gen_content
                        if isinstance(obs_raw, dict) and obs_raw.get("is_final_answer"):
                            final_answer = obs_raw.get("synthesized_content")
                            print(f"Final Answer (from gen_content tool): {final_answer}")
                            return final_answer

                        obs = obs_raw
                        print(f"Observation: {obs}")
                        # Update conversation history with the new observation
                        self.conversation_history += f"\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {obs}"
                    except Exception as e:
                        print(f"Error executing tool '{action}': {e}")
                        return f"An error occurred while executing a tool: {e}"
                else:
                    print(f"Error: Unknown tool '{action}'")
                    return "I'm sorry, I don't know how to perform that action."
            else:
                print("Error: LLM output did not contain a valid action or final answer.")
                return "An unexpected error occurred in the ReAct loop."

        return "Maximum number of iterations reached without a final answer."
