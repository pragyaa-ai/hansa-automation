import os
import requests
import re
import json

def get_transcription_files(subscription_key, transcription_id, region):
    url = f"https://{region}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions/{transcription_id}/files"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json"
    }
    
    all_files = [] 
    while url:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}") 
        if response.status_code == 200:
            data = response.json()
            all_files.extend(data.get('values', [])) 
            url = data.get('@nextLink') 
        else:
            print(f"Failed to retrieve files. Status Code: {response.status_code}")
            print(response.json())
            return None

    return all_files  

def extract_content_urls_and_save_to_file(files, language):
    target_folders = {'2024-12-06', '2024-12-07'}
    
    for idx, file in enumerate(files):
        if idx == 0: 
            print("Skipping the first file.")
            continue
        
        if 'links' in file and 'contentUrl' in file['links']:
            audio_url = file['links']['contentUrl']
            print(f"Audio URL: {audio_url}") 

            res = requests.get(audio_url).json()  
            audio_url = res.get('source') 
            print(f"Extracted Audio URL: {audio_url}")  

            if audio_url is None:
                print("No audio URL extracted. Skipping this file.")
                continue

            channel_transcripts = {}
            for phrase in res.get('combinedRecognizedPhrases', []):
                channel = phrase.get('channel', 0)  
                transcript = phrase.get('display', '').strip()

                if channel not in channel_transcripts:
                    channel_transcripts[channel] = []
                if transcript:
                    channel_transcripts[channel].append(transcript)

            combined_transcripts = []
            for channel, phrases in channel_transcripts.items():
                combined_transcripts.append(f"Channel {channel}: " + " ".join(phrases))

            url_path = audio_url.split('/')[-1].split('?')[0] 
            print(f"Extracted File Name: {url_path}") 
            
            folder_structure = '/'.join(audio_url.split('/')[3:-1])
            print(f"Folder Structure: {folder_structure}")  

            folder_name = folder_structure.split('/')[-1] 
            if folder_name not in target_folders:
                print(f"Skipping folder: {folder_name} (not in target folders)")
                continue  

            folder_path = os.path.join("vlaudios", folder_structure)
            print(f"Creating directory: {folder_path}")
            
            try:
                os.makedirs(folder_path, exist_ok=True)
                print(f"Directory {folder_path} created successfully.")
            except Exception as e:
                print(f"Failed to create directory {folder_path}: {e}")

            audio_filename = re.sub(r'\.(wav|mp3|WAV)$', '.txt', url_path)
            print(f"Final filename for transcription: {audio_filename}")  

            file_path = os.path.join(folder_path, audio_filename)
            print(f"File will be saved at: {file_path}") 
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Audio URL: {audio_url}\n\n")  
                    for transcript in combined_transcripts:
                        f.write(f"{transcript}\n")
                print(f"File saved successfully at {file_path}")
            except Exception as e:
                print(f"Failed to save transcription file: {e}")

def check_transcription_status(subscription_key, transcription_id, region):
    url = f"https://{region}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions/{transcription_id}"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json" 
        }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('status') == 'Succeeded'
    else:
        print(f"Failed to check transcription status. Status Code: {response.status_code}")
        return False

def execute_post_transcription_command(subscription_key, transcription_id, region):
    url = "https://centralindia.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "displayName": "My Transcription",
        "description": "Speech Studio Batch speech to text",
        "locale": "en-in",
        "contentContainerUrl": "https://hansavartaaudiofiles.blob.core.windows.net/vlaudios?sp=racwdlmeo&st=2024-12-09T05:28:41Z&se=2025-02-27T13:28:41Z&spr=https&sv=2022-11-02&sr=c&sig=3U2bQ1KG8pj1ldQrpd77tZUTKIqP7OSFM2oq5iOQ3zc%3D",
        "model": {
            "self": "https://centralindia.api.cognitive.microsoft.com/speechtotext/v3.2/models/base/a971704d-e480-4687-b92b-2373f60da0db"
        },
        "properties": {
            "wordLevelTimestampsEnabled": False,
            "displayFormWordLevelTimestampsEnabled": True,
            "diarizationEnabled": False,
            "punctuationMode": "DictatedAndAutomatic",
            "profanityFilterMode": "Masked"
        },
        "customProperties": {}
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("Post transcription command response status:", response.status_code)
    if response.status_code == 201:
        print("Transcription command executed successfully.")
    else:
        print("Failed to execute transcription command:", response.json())

def main():
    transcriptions = {
        "english_transcription": {
            "subscription_key": "e5a4265391664fe084ee3d165bda383d", 
            "transcription_id": "11620ea0-5743-4e56-b504-3726e259447f", 
            "region": "centralindia"
        },
    }

    for lang, data in transcriptions.items():
        print(f"Processing {lang} transcription...")
        if check_transcription_status(data["subscription_key"], data["transcription_id"], data["region"]):
            files = get_transcription_files(
                transcription_id=data["transcription_id"],
                subscription_key=data["subscription_key"],
                region=data["region"]
            )
            if files is not None:
                extract_content_urls_and_save_to_file(files, lang)
                execute_post_transcription_command(data["subscription_key"], data["transcription_id"], data["region"])
            else:
                print(f"Failed to retrieve files for {lang} transcription.")
        else:
            print(f"Transcription for {lang} is not completed yet.")

if __name__ == "__main__":
    main()