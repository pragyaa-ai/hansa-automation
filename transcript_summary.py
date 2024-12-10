import os
import requests
import time
import json

endpoint = "https://swedencentral.api.cognitive.microsoft.com/openai/deployments/pragyaaGPT4o/chat/completions?api-version=2024-02-15-preview"
key = "6424c639f54c46b88f7e8dcc512dcd70"

prompt = f"""
You are given Transcription of an audio. 
Summarize this transcription based on it, and try to include important points in it. 
The summary should be in 1 paragraph. 
"""

headers = {
    "Content-Type": "application/json",
    "api-key": key
}

def summarize_transcript(english_transcript, prompt):
    full_prompt = f"{prompt}\n Transcription: {english_transcript}\n\n Summary : "

    payload = {
        "messages": [
            {"role": "system", "content": "You are a Summarization assistant. You need to Summarize the Transcript into a single paragraph."},
            {"role": "user", "content": full_prompt}
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        if content:
            return content
        else:
            return json.dumps(content, indent=4)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def check_if_already_processed(input_file, output_directory):
    relative_path = os.path.relpath(input_file, input_eng_dir)
    output_filename = relative_path.replace('.txt', '.txt')  
    output_file_path = os.path.join(output_directory, output_filename)
    return os.path.exists(output_file_path)

def process_files(input_eng_dir, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    request_count = 0
    
    for root, dirs, files in os.walk(input_eng_dir):
        for filename in files:
            if not filename.endswith('.txt'):
                continue
            
            file_path = os.path.join(root, filename)
            
            if check_if_already_processed(file_path, output_directory):  
                print(f"Skipping {filename}, already processed.")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as file:
                english_transcript = file.read()

            summary = summarize_transcript(english_transcript, prompt)

            if summary:
                relative_path = os.path.relpath(root, input_eng_dir)
                output_subdir = os.path.join(output_directory, relative_path)
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)

                output_filename = filename.replace('.txt', '.txt') 
                output_file_path = os.path.join(output_subdir, output_filename)

                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(summary)

                print(f"Processed {filename} and saved evaluation result to {output_file_path}")
            
            request_count += 1
            if request_count > 3:
                print("Waiting for 40 seconds to avoid hitting rate limits...")
                time.sleep(40)
                request_count = 0

input_eng_dir = "vlaudios/2024-12-10"
output_directory = "transcript_summary/2024-12-10"

process_files(input_eng_dir, output_directory)