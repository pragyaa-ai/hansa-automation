from azure.storage.blob import BlobServiceClient
import requests
import json
import os
import re
from datetime import datetime
import time

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=hansavartaaudiofiles;AccountKey=PVYcw9JPqy4Yr5BK4NcP72TXOj+k8ZWuv8MYYPHOBttGpyVnlhdfArKGKkH/iIMNmDHj8Vmm7sn9+AStx3PMMg==;EndpointSuffix=core.windows.net")

def get_today_folder_name():
    today_folder = datetime.now().strftime("%Y-%m-%d")
    print(f"Today's folder name: {today_folder}")
    return today_folder

def list_audio_files(container_name, folder_name):
    print(f"Listing audio files in container '{container_name}' with folder prefix '{folder_name}'")
    container_client = blob_service_client.get_container_client(container_name)
    audio_urls = []
    for blob in container_client.list_blobs(name_starts_with=folder_name):
        audio_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob.name}"
        audio_urls.append(audio_url)
        print(f"Found audio file: {audio_url}")
    return audio_urls

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

def create_transcription(subscription_key, region, content_urls):
    print(f"Creating transcription for {len(content_urls)} audio files.")
    url = f"https://{region}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json"
    }
    data = {
        "displayName": "Batch Transcription",
        "contentUrls": content_urls,
        "locale": "en-US",
        "properties": {
            "wordLevelTimestampsEnabled": True
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Transcription response: {response.status_code}, {response.text}")
    return response.json()

def check_transcription_status(transcription_url, subscription_key):
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    while True:
        response = requests.get(transcription_url, headers=headers)
        status_info = response.json()
        status = status_info.get('status')
        print(f"Current transcription status: {status}")
        if status == 'Succeeded':
            return status_info
        elif status in ['Failed', 'NotStarted']:
            print("Transcription has not started or failed. Retrying...")
            time.sleep(5)  # Wait before checking again
        else:
            print("Transcription is still in progress. Waiting...")
            time.sleep(10)  # Wait before checking again

def extract_content_urls_and_save_to_file(files):
    print(f"Extracting content URLs and saving to files. Total files: {len(files)}")
    for idx, file in enumerate(files):
        if idx == 0: 
            continue
        if 'links' in file and 'contentUrl' in file['links']:
            audio_url = file['links']['contentUrl']
            print(f"Processing audio URL: {audio_url}")
            res = requests.get(audio_url).json()  
            audio_url = res.get('source') 
            if audio_url is None:
                print("No source URL found for audio.")
                continue
            channel_transcripts = {}
            for phrase in res.get('combinedRecognizedPhrases', []):
                channel = phrase.get('channel',  0)  
                transcript = phrase.get('display', '').strip()
                if channel not in channel_transcripts:
                    channel_transcripts[channel] = []
                if transcript:
                    channel_transcripts[channel].append(transcript)
            combined_transcripts = []
            for channel, phrases in channel_transcripts.items():
                combined_transcripts.append(f"Channel {channel}: " + " ".join(phrases))
            url_path = audio_url.split('/')[-1].split('?')[0] 
            folder_structure = '/'.join(audio_url.split('/')[3:-1])
            folder_path = os.path.join("vlaudios", folder_structure)
            os.makedirs(folder_path, exist_ok=True)
            audio_filename = re.sub(r'\.(wav|mp3|WAV)$', '.txt', url_path)
            file_path = os.path.join(folder_path, audio_filename)
            print(f"Saving transcription to: {file_path}")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Audio URL: {audio_url}\n\n") 
                    for transcript in combined_transcripts:
                        f.write(f"{transcript}\n")
                print(f"Successfully saved transcription for {audio_url}")
            except Exception as e:
                print(f"Failed to save transcription file: {e}")

def main():
    print("Starting main function...")
    container_name = "vlaudios"
    today_folder_name = get_today_folder_name() + "/"
    subscription_key = "e5a4265391664fe084ee3d165bda383d"
    region = "centralindia"
    content_urls = list_audio_files(container_name, today_folder_name)
    if content_urls:
        transcription_response = create_transcription(subscription_key, region, content_urls)
        print("Transcription Response:", transcription_response)
        
        transcription_url = transcription_response['self']
        final_status_info = check_transcription_status(transcription_url, subscription_key)
        
        if final_status_info['status'] == 'Succeeded':
            transcription_url = transcription_response['self']
            transcription_id = transcription_url.split('/')[-1]
            files = get_transcription_files(subscription_key, transcription_id, region)
            if files:
                extract_content_urls_and_save_to_file(files)
            else:
                print("No transcription files found.")
        else:
            print("Transcription did not succeed.")
    else:
        print("No audio files found in the specified folder.")

if __name__ == "__main__":
    main()