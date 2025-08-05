import json
import time
import random

# In a real system, this would be a vector database or a searchable document store.
LINEAR_ALGEBRA_BOOK_CONTENT = {
    "introduction_to_vectors": "Vectors are fundamental objects in linear algebra. They can represent points in space or quantities with both magnitude and direction. A vector in 2D space is often written as (x, y) and in 3D as (x, y, z). Vector addition involves adding corresponding components. Scalar multiplication scales the vector's magnitude.",
    "matrix_basics": "A matrix is a rectangular array of numbers, symbols, or expressions, arranged in rows and columns. Matrices are used to represent linear transformations, systems of linear equations, and to store data. The dimensions of a matrix are given by rows x columns (e.g., a 2x3 matrix has 2 rows and 3 columns).",
    "matrix_inversion": "Matrix inversion is the process of finding a matrix (the inverse) that, when multiplied by the original matrix, yields the identity matrix. Only square matrices can have inverses, and not all square matrices are invertible (they must be non-singular, meaning their determinant is non-zero). The inverse of a matrix A is denoted A^-1. For a 2x2 matrix [[a,b],[c,d]], the inverse is (1/(ad-bc)) * [[d,-b],[-c,a]].",
    "eigenvalues_eigenvectors": "Eigenvalues and eigenvectors are special numbers and vectors associated with a linear transformation. An eigenvector of a linear transformation is a non-zero vector that changes at most by a scalar factor when that linear transformation is applied to it. The corresponding eigenvalue is the scalar factor by which the eigenvector is scaled. They are crucial for understanding the behavior of linear systems.",
    "rank_nullity_theorem": "The Rank-Nullity Theorem states that for a linear transformation T: V -> W, the dimension of the domain V is equal to the sum of the dimension of the kernel (nullity) and the dimension of the image (rank). Dim(V) = Nullity(T) + Rank(T). It provides a fundamental relationship between the dimensions of the kernel and image of a linear map.",
    "affine_geometry": "Affine geometry is a branch of geometry that studies properties of geometric figures that are preserved under affine transformations (transformations that preserve collinearity and ratios of distances along parallel lines). It's a generalization of Euclidean geometry where concepts like distance and angles are not necessarily preserved, but parallelism is."
}

def analyze_video(video_dat):
    print("Tool: Analyzing video feed for mood and concentration...")
    time.sleep(0.5)
    moods = ["confused", "focused", "frustrated", "bored", "engaged"]
    concentration_level = random.randint(10, 100) # Percentage
    return {
        "modality": "video",
        "mood": random.choice(moods),
        "concentration_level": concentration_level
    }
    
    
def analyse_audio(audio_dat):
    
    print("Tool: Analyzing audio stream for speech and knowledge...")
    time.sleep(0.5)
    knowledge_score_linear_algebra = random.randint(0, 100)
    hesitation_score = round(random.uniform(0, 1), 2) # 0 to 1
    return {
        "modality": "audio",
        "speech_hesitation": hesitation_score,
        "knowledge_score_linear_algebra": knowledge_score_linear_algebra
    }
    
    
def analyze_screen(sreen_dat):
    
    print("Tool: Analyzing screen data for performance and memory...")
    time.sleep(0.5)
    task_statuses = ["incorrect matrix syntax", "failed to solve equation", "correct", "incomplete", "stuck on definition"]
    memory_retention_rate = random.randint(50, 100)
    current_task_status = random.choice(task_statuses)
    
    return {
        "modality": "screen",
        "current_task_status": current_task_status,
        "memory_retention_rate": memory_retention_rate
    }
    
    

def update_short_term(action_input):
    
    print(f"Tool: Modifying short-term plan: {action_input}")
    time.sleep(1)
    return f"Observation: Short-term plan adjusted: '{action_input}'."

def update_long_term(action_input):
    print(f"Tool: Modifying long-term plan: {action_input}")
    time.sleep(1)
    return f"Observation: Long-term plan adjusted: '{action_input}'."

def gen_content(action_input):
    
    print(f"Tool: Generating new content on: {action_input}")
    time.sleep(2)
    return f"Observation: New content generated: 'A simplified example for {action_input} was created and presented.'"

def update_content(action_input):
    print(f"Tool: Modifying existing content: {action_input}")
    time.sleep(1)
    return f"Observation: Existing content modified: '{action_input}'."

def encourage_user():
    print("Tool: Providing encouragement...")
    time.sleep(1)
    return "Observation: The tutor said, 'You're making great progress!'"

def rag_book(query):
    """
    Simulates retrieving relevant knowledge from the Linear Algebra book (KAG/RAG).
    """
    print(f"Tool: Retrieving knowledge from book for query: '{query}'...")
    time.sleep(1.5)
    # Simple keyword matching for POC
    for key, content in LINEAR_ALGEBRA_BOOK_CONTENT.items():
        if query.lower() in key.lower() or query.lower() in content.lower():
            return f"Observation: Retrieved relevant passage: '{content[:100]}...'" # Return snippet
    return "Observation: No highly relevant passage found in the book for that query."


TOOLS = {
    "analyze_video": analyze_video,
    "analyse_audio": analyse_audio,
    "analyze_screen": analyze_screen,
    "update_short_term": update_short_term,
    "update_long_term": update_long_term,
    "gen_content": gen_content,
    "update_content": update_content,
    "encourage_user": encourage_user,
    "rag_book":rag_book
}

def mock_lmm_resp(prompt):

    if "'frustrated'" in prompt and "knowledge score on 'Linear Algebra' is" in prompt and "incorrect matrix syntax" in prompt:
        # Extract knowledge score (mock parsing)
        try:
            knowledge_score_str = prompt.split("knowledge score on 'Linear Algebra' is ")[1].split("/")[0]
            knowledge_score = int(knowledge_score_str)
            if knowledge_score < 50: # Low knowledge
                return """
Thought: Student is frustrated, has low knowledge, and is making syntax errors. This is a critical state. I should immediately modify the current content to highlight the syntax error and provide a targeted hint to alleviate frustration and guide them.
Action: modify_existing_content
Action Input: 'highlight the specific incorrect matrix syntax and provide a hint for matrix inversion'
"""
        except (ValueError, IndexError):
            pass 

    if "Concentration level is 10%" in prompt and "knowledge score on 'Linear Algebra' is 20/100" in prompt:
        return """
Thought: Student has very low concentration and poor knowledge. The current approach isn't working. I need to generate a completely new, simpler piece of content to re-engage and re-teach.
Action: generate_new_content
Action Input: 'a very simplified, visual example for matrix basics'
"""
    elif "Memory retention rate is 50%" in prompt and "failed to solve equation" in prompt:
        return """
Thought: Student has low memory retention and is failing tasks. This indicates a need for foundational review. I should adjust the long-term plan to incorporate a dedicated review session.
Action: modify_long_term_plan
Action Input: 'schedule a review session for foundational vector and matrix operations'
"""
    elif "Concentration level is 30%" in prompt:
        return """
Thought: Student's concentration is dropping. A timely encouragement might help re-focus them without interrupting the learning flow too much.
Action: encourage_user
Action Input: None
"""
    elif "stuck on definition" in prompt:
        return """
Thought: The student is stuck on a definition. I should retrieve the exact definition from the Linear Algebra book to provide precise information.
Action: retrieve_knowledge_from_book
Action Input: 'matrix inversion definition'
"""
    else:
        return """
Thought: The current state is stable or no clear critical pattern detected. I will continue to analyze incoming multimodal observations.
Final Answer: The tutor is observing and ready for the next interaction or to provide a general response.
"""
    
def parse_llm_output(output):
    parsed_output = {}
    lines = output.strip().split('\n')
    for line in lines:
        if line.startswith("Thought"):
            parsed_output["thought"] = line.replace("Thought:", "").strip()
        elif line.startswith("Action:"):
            parsed_output["action"] = line.replace("Action:", "").strip()
        elif line.startswith("Action Input:"):
            action_input = line.replace("Action Input:", "").strip()
            parsed_output["action_input"] = action_input if action_input != "None" else None
        elif line.startswith("Final Answer:"):
            parsed_output["final_answer"] = line.replace("Final Answer:", "").strip()
    return parsed_output

student_long_term_performance = {
    "knowledge_scores_history": [], 
    "concentration_history": [],    
    "memory_retention_history": []   
}

def update_long_term_performance(new_observations):
    print("Tool: Updating long-term performance records...")
    if new_observations.get("knowledge_score_linear_algebra") is not None:
        student_long_term_performance["knowledge_scores_history"].append(
            new_observations["knowledge_score_linear_algebra"]
        )
    if new_observations.get("concentration_level") is not None:
        student_long_term_performance["concentration_history"].append(
            new_observations["concentration_level"]
        )
    if new_observations.get("memory_retention_rate") is not None:
        student_long_term_performance["memory_retention_history"].append(
            new_observations["memory_retention_rate"]
        )
    print(f"Long-term performance updated: {student_long_term_performance}")
    return "Observation: Long-term performance records updated."

def retrieve_long_term_performance():
    print("Tool: Retrieving long-term performance records...")
    return f"Observation: Historical performance data: {student_long_term_performance}"

TOOLS["update_long_term_performance"] = update_long_term_performance
TOOLS["retrieve_long_term_performance"] = retrieve_long_term_performance

def react_loop(init_state , max_it = 50 , time_constr=10):
    conv_hist = init_state
    start_time = time.time()
    print(f"Initial State: {init_state}\n")
    print(f"Session Time Constraint: {time_constr} minutes\n")
    for i in range(max_it):
        print(f"--- Iteration {i+1} ---")
        
        elapsed_time = (time.time() - start_time) / 60 # in minutes
        time_remaining = max(0, time_constr - elapsed_time)
        video_obs = analyze_video("mock_data")
        audio_obs = analyse_audio("mock_data")
        screen_obs = analyze_screen("mock_data")
    
    
        prompt_with_obs = (
            f"{conv_hist}\n"
            f"Current Time Remaining: {time_remaining:.1f} minutes.\n"
            f"Video Observation: {json.dumps(video_obs)}\n"
            f"Audio Observation: {json.dumps(audio_obs)}\n"
            f"Screen Observation: {json.dumps(screen_obs)}\n"
            f"Historical Performance (Summary): {json.dumps(student_long_term_performance)}" # Provide historical context
        )
    
        lmm_out = mock_lmm_resp(prompt_with_obs)
        parsed_out = parse_llm_output(lmm_out)
        thought = parsed_out.get("thought")
        action = parsed_out.get("action")
        action_input = parsed_out.get("action_input")
        final_answer = parsed_out.get("final_answer")
    
    
        if thought:
            print(f"Thought: {thought}")
        
        if final_answer:
            print(f"final answer: {final_answer}")
        
        if action:
            print(f"Action: {action}")
            
            if action in TOOLS:
                tool_function = TOOLS[action]
                
                obs = tool_function(action_input)
                
                print(f"Observation: {obs}")
                
                conv_hist += f"\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {obs}"
            else:
                print(f"Error: Unknown tool '{action}'")
                return "I'm sorry, I don't know how to perform that action."
        else:
            print("Error: LLM output did not contain a valid action or final answer.")
            return "An unexpected error occurred in the ReAct loop."

    return "Maximum number of iterations reached without a final answer."

if __name__ == "__main__":
    print("--- Running Example 1: Advanced Adaptive Tutoring Loop for Linear Algebra ---")
    react_loop(
        initial_state="The student is currently learning about matrix inversion and is working on a 2x2 matrix problem.",
        max_iterations=5,
        time_constraint_minutes=5
    )    
    
    print("\n" + "="*80 + "\n")
    print("--- Running Example 2: Demonstrating KAG ---")
    react_loop(
        initial_state="The student just asked: 'What is affine geometry?'",
        max_iterations=1,
        time_constraint_minutes=1
    )