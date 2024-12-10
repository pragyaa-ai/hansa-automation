import os
import requests
import json
import re
import time

prompt1 = """evaluate the given call transcript in point 1 below, based on the following ten parameters only mentioned in point 2 below (soft skills to be evaluated and criteria specified for each soft skill) and not for any other parameter. Provide the response in the format specified in point 3 only. 
    Soft skills to be evaluated:
        Parameter: 1. Greet & Call Opening: Meeting any of below criteria means this criteria is met
        Criteria: a) Wishes the customer with  Good afternoon/ Morning/ Evening/ Namaskar/ Namaste or similar  b) Self introduction and Brand Personalisation
        
        Parameter: 2. Active Listening/ Interruption/ Acknowledgement/ Paraphrasing
        Criteria: a) Mandatory: Needs to acknowledge on each call/  Uses varied acknowledgments on the call like, ok, alright, sure, certainly etc. b) Associate listens to the customer actively and responds appropriately. b) Should not make him/ her repeat unnecessarily. c) Interruption or Parallel talks should be avoided. d) Allows the customer to vent, allows the customer to share his thoughts/views, allows the customer to talk.
        
        Parameter: 3. Empathy/Apology/ Power words or phrases
        Criteria: a) Uses empathetic statements. b) Uses power words or phrases, like "I understand your concern", "I’m really sorry for the inconvenience", "Absolutely", etc.
        
        Parameter: 4. Probing
        Criteria:a) Asking appropriate open and close ended questions. b) Failing to probe the customer appropriately and makes him/her repeat is a mark down
        
        Parameter: 5. Hold Procedure: Not Met if Fails to adhere to proper Hold Verbiage, Fails to mention the duration, Does not get back to the customer on promised time, does not thank the customer
        Criteria: a) Seeks permission before placing the call on hold. b) Informs the customer of the reason for the hold. c) Does not place the call on hold for more than two times.
        
        Parameter: 6. Dead Air/ Fillers and Foghorns/ Jargons: Failing to adhere any one of the parameter is a Not Met
        Criteria: a) Indulges the customer in 2 way conversation b) Does not fails to respond to the customer c) Avoids use of Jargon during the conversation.
        
        Parameter: 7. Appreciate Customers
        Criteria: a) Appreciate customer wherever applicable - on getting information or details/ for contacting us
        
        Parameter: 8. Confidence/ Fumbling - If more than 3 instance, then this parameter is a Not Met
        Criteria: a) Agent Fumbles / Hesitates during the conversation b)  Tends to repeat a statement either in same or similar verbiage
        
        Parameter: 9. Closing of the call
        Criteria: a) Call Summarisation b) Additional assistance c) Proper closing statement
        
        Parameter: 10. Agent Tone Of Voice (Polite / Courteous / Energetic)/ Speech clarity
        Criteria: a) Should be enthusiastic and displays appropriate levels of Energy b) The tone of voice used was business friendly c) Parameter is Not Met if Rude Tone, Abusive, Sarcastic, Laughing on the call, argues with the customer
        
        3.    Evaluation criteria: For each soft skill parameter mentioned in point 2, give a score between 0 – 10, with 0 being minimum if soft skill not met as per criteria mentioned and 10 being maximum with Soft skill criteria being fully met. Also provide reasoning for giving the specific score to this soft skill evaluation.Provide output as a numbered list as per below Soft Skills.Please provide the following information in key-value pairs:
        1. Greet & Call Opening# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        2. Active Listening/ Interruption/ Acknowledgement/ Paraphrasing# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        3. Empathy/Apology/ Power words or phrases# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        4. Probing# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        5. Hold Procedure# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        6. Dead Air/ Fillers and Foghorns/ Jargons# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        7. Appreciate Customers# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        8. Confidence/ Fumbling# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        9. Closing of the call# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        10. Agent Tone Of Voice (Polite / Courteous / Energetic)/ Speech clarity# a) Met: Yes/No; b) Score: [Between 0-10]; c) Reasons: [reasoning for the score given]
        
        Stop the response after parameter 10.
        
        Format:
        {
        "Greet_or_Call_Opening": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Active_Listening_Interruption_Acknowledgement_Paraphrasing": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Empathy_Apology_Power_words_or_phrases": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Probing": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Hold_Procedure": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Dead_Air_Fillers_and_Foghorns_Jargons": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Appreciate_Customers": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Confidence_Fumbling": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Closing_of_the_call": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" },
        "Tone_Of_Voice_Speech_clarity": { "Met":"[value]", "Score": "[value]", "Reasons": "[value]" }
        }            
    1.    Call transcript:
    """

prompt2 = """
evaluate the given call transcript in point 1 below, evaluate for criteria specified in Point 2 and not for any other parameter. Provide output in json format specified in Point 3 only.
    Provide the response in the format specified in point 2 only. 
    2.    Evaluate criteria:
    1.      Sentiment: Evaluate Sentiment. If the customer is [Happy/ Unhappy/ Neutral].
 2. Did all the queries for the customer get answered or Not: [Yes/ No/ NA] 
3. What is customer's Interest Level: [High/ Low/ Neutral]
4. Is Customer looking for Exchange: [Yes/ No/ NA]
5. Which Variant is Customer Interested in : [Pertol/ Dielsel/ Electric/ NA]
6. What is customer's age: [Age/ Not Mentioned]
7. When is customer planning to buy : [Purchase within / Not mentioned]
8. What is key customer query : [Key customer query]
3.
        Format:
        {
        "Sentiment": {"value": "[Happy/ Unhappy/ Neutral]", "reasons": "[value]" },
        "customer_queries_answered": { "value": "[Yes/No/ NA]", "reasons": "[value]" },
        "customer_Interest_Level": {"value":"[High/Low/ NA]","reasons":"[value]"},
        "customer_looking_exchange": { "value":"[Yes/No/ NA]", "reasons": "[value]" },
        "variant Customer Interested in": {"value": "[Petrol/ Diesel/ Electric/NA]", "reasons": "[value]" },
        "customers_Age": "[value]",
        "customer_plan_to_buy": "[value]",
        "key_customer_query": "[value]",
        }            
    1.    Call transcript:

"""
new_prompt = """
You are a data extraction assistant specialized in analyzing automotive sales call transcripts. Your task is to extract specific data points in a structured JSON format that matches our dashboard requirements.
Analysis Instructions
Analyze the provided call transcript and extract the following data points in the specified format. If a data point is not explicitly mentioned in the transcript, mark it as null.
{
"lead_metrics": {
"lead_source": "string", // CRM, Website, Dealership, or Facebook
"inquiry_type": "string", // Hot or Regular
"test_drive_status": boolean,
"vehicle_model": "string"
},
"customer_profile": {
"state": "string",
"profession": "string", // Business or Salaried
"age_group": "string", // <30, 30-45, 45-60, >60
"previous_vehicle": {
"brand": "string",
"model": "string"
}
},
"preferences": {
"variant": "string",
"transmission": "string", // Manual or Automatic
"fuel_type": "string", // Petrol or Diesel
"exchange_required": boolean,
"finance_preference": "string" // Loan, Cash, or Undecided
},
"customer_queries": {
"top_questions": [
"string"
],
"primary_concerns": [
"string"
]
},
"sentiment_analysis": {
"overall_sentiment": "string", // Positive, Negative, or Neutral
"key_positive_points": [
"string"
],
"key_negative_points": [
"string"
]
}
}
# Example Query:
Given the following call transcript, extract the specified data points according to the format above:
[CALL TRANSCRIPT]
# Additional Rules:
1. Sentiment should be classified based on:
- Positive: Clear satisfaction with product/service
- Negative: Explicit dissatisfaction or concerns
- Neutral: Balanced or information-seeking tone
2. Hot inquiry criteria:
- Customer shows immediate purchase intent
- Discusses specific variants/pricing
- Requests test drive
- Discusses financing options
3. Extract location data when mentioned through:
- Direct mention of state
- Dealership location
- Area/city references
4. For vehicle preferences:
- Note specific models mentioned
- Include variant preferences if stated
- Capture any feature requirements

"""
endpoint = "https://swedencentral.api.cognitive.microsoft.com/openai/deployments/pragyaaGPT4o/chat/completions?api-version=2024-02-15-preview"
key = "6424c639f54c46b88f7e8dcc512dcd70"
headers = {
    "Content-Type": "application/json",
    "api-key": key
}
def evaluate_transcript(transcript, prompt):
    full_prompt = f"{prompt}\n{transcript}"
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful evaluation assistant. If there are Audio URL ignore that, and only focus on the transcription. Give only JSON output nothing else."},
            {"role": "user", "content": full_prompt}
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    
    if response.status_code == 200:
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        
        json_content = re.search(r'(\{.*\})', content, re.DOTALL)

        if json_content:
            return json_content.group(1).strip()  
        else:
            return json.dumps(content, indent=4) 
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def check_if_already_processed(input_file, output_directory):
    output_filename = input_file.replace('.txt', '.json')
    output_file_path = os.path.join(output_directory, output_filename)
    return os.path.exists(output_file_path)

def process_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    request_count = 0
    
    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if not filename.endswith('.txt'):
                continue
            
            file_path = os.path.join(root, filename)
            
            relative_path = os.path.relpath(root, input_directory)
            output_subdirectory = os.path.join(output_directory, relative_path)
            if not os.path.exists(output_subdirectory):
                os.makedirs(output_subdirectory)
            
            if check_if_already_processed(filename, output_subdirectory):
                print(f"Skipping {filename}, already processed.")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as file:
                transcript = file.read()

            result_prompt_1 = evaluate_transcript(transcript, new_prompt)
            # result_prompt_1 = evaluate_transcript(transcript, prompt2)
            
            if result_prompt_1:
                output_filename = filename.replace('.txt', '.json')
                output_file_path = os.path.join(output_subdirectory, output_filename)
                
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(result_prompt_1) 
                
                print(f"Processed {filename} and saved evaluation result to {output_file_path}")
            
            request_count += 1
            if request_count > 3:
                print("Waiting for 40 seconds to avoid hitting rate limits...")
                time.sleep(40) 
                request_count = 0

input_directories = [
    "vlaudios/2024-12-10", 
]
output_directory_1 = "new_prompt_eval_1/2024-12-10"
# output_directory_2 = "eval_transcript_2"

for input_directory in input_directories:
    process_files(input_directory, output_directory_1)
