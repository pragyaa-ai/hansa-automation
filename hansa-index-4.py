import os
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta
import urllib3
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
from pydub import AudioSegment
from requests.auth import HTTPBasicAuth
from mutagen.mp3 import MP3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INDEX = "hansa-varta-index-4"
URL = "98.70.12.66"
index_url = f'https://{URL}:9200/{INDEX}/_doc/'
search_url = f'https://{URL}:9200/{INDEX}/_search'
delete_index_url = f'https://{URL}:9200/{INDEX}'
update_url = f'https://{URL}:9200/{INDEX}/_update/'

import requests
from requests.auth import HTTPBasicAuth

def create_index():
    index_creation_url = f'https://{URL}:9200/{INDEX}'
    index_mapping = {
        "mappings": {
            "properties": {
                "audio_url": { 
                    "type": "keyword", 
                    "ignore_above": 512 
                },
                "audio_duration": {
                    "type": "integer"
                },
                "date": { 
                    "type": "date",  
                    "format": "yyyy-MM-dd"
                },
                "filename": { 
                    "type": "keyword" 
                },
                "timestamp": { 
                    "type": "date" 
                },
                "total_score": { 
                    "type": "integer" 
                },
                "transcription": { 
                    "type": "text", 
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "transcript_summary": { 
                    "type": "text", 
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "lead_metrics_lead_source": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "lead_metrics_inquiry_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "lead_metrics_test_drive_status": {
                    "type": "boolean"
                },
                "lead_metrics_vehicle_model": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_profile_state": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_profile_profession": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_profile_age_group": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_profile_previous_vehicle_brand": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_profile_previous_vehicle_model": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "preferences_variant": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "preferences_transmission": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "preferences_fuel_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "preferences_exchange_required": {
                    "type": "boolean"
                },
                "preferences_finance_preference": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_queries_top_questions": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "customer_queries_primary_concerns": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "sentiment_analysis_overall_sentiment": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "sentiment_analysis_key_positive_points": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                },
                "sentiment_analysis_key_negative_points": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 51200
                        }
                    }
                }
            }
        }
    }

    response = requests.put(index_creation_url, json=index_mapping, auth=HTTPBasicAuth('admin', 'Threeguys01!'), verify=False)

    if response.status_code == 200:
        print("Index created successfully.")
    else:
        print(f"Error creating index: {response.status_code}, Response: {response.text}")

def check_and_create_index():
    response = requests.get(f'https://{URL}:9200/{INDEX}', auth=HTTPBasicAuth('admin', 'Threeguys01!'), verify=False)
    
    if response.status_code == 404:  
        create_index()
    else:
        print(f"Index '{INDEX}' already exists.")

def get_upload_date_and_timestamp(podcast_id, base_dir='vlaudios'):
    expected_file = f'{podcast_id}.txt'
    print("Expected File Path : ", expected_file)

    upload_date = datetime.now()  
    timestamp = upload_date 

    if upload_date < datetime(2024, 12, 1):
        upload_date = datetime(2024, 12, 2)
        timestamp = upload_date 

    sample_dir = os.path.join(base_dir, 'sample')
    if os.path.isdir(sample_dir):
        file_path = os.path.join(sample_dir, expected_file)
        if os.path.isfile(file_path):
            upload_date = datetime(2024, 10, 9)
            timestamp = upload_date.replace(hour=5, minute=30, second=0) 

    if upload_date < datetime(2024, 12, 1):
        upload_date = datetime(2024, 12, 2)

    return upload_date.strftime('%Y-%m-%d'), timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    for subfolder in os.listdir(base_dir):
        subfolder_path = os.path.join(base_dir, subfolder)
        if os.path.isdir(subfolder_path) and subfolder != 'sample' and subfolder != '2024-12-03':
            print(f"Checking subfolder: {subfolder}") 
            try:
                subfolder_date = datetime.strptime(subfolder, '%Y-%m-%d')
                print(f"Parsed date from folder: {subfolder_date}") 
                subfolder_file_path = os.path.join(subfolder_path, expected_file)
                if os.path.isfile(subfolder_file_path):
                    upload_date = subfolder_date
                    timestamp = upload_date 
                    print(f"File found: {subfolder_file_path}") 
                    break 
            except ValueError:
                print(f"Could not parse date from folder name: {subfolder}") 
                continue  

    formatted_upload_date = upload_date.strftime('%Y-%m-%d')
    formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f"Final Upload Date: {formatted_upload_date}")  
    print(f"Final Timestamp: {formatted_timestamp}") 
    return formatted_upload_date, formatted_timestamp


def extract_filename_from_url(audio_url):
    path = urlparse(audio_url).path
    
    filename = os.path.basename(path)
    
    return filename

def process_audio_and_filename(transcript_folder, podcast_id):
    file_path = os.path.join(transcript_folder, f"{podcast_id}.txt")
    audio_url = extract_audio_url(file_path)  
    
    print(f"Processing Podcast ID: {podcast_id}")
    print("Audio URL:", audio_url)
    
    filename = extract_filename_from_url(audio_url)
    print(f"Final Audio File Name: {filename}")
    
    audio_file_path_mp3 = os.path.join(transcript_folder, f"{podcast_id}.mp3")
    audio_file_path_wav = os.path.join(transcript_folder, f"{podcast_id}.wav")
    
    if os.path.exists(audio_file_path_mp3):
        filename = f"{podcast_id}.mp3"
    elif os.path.exists(audio_file_path_wav):
        filename = f"{podcast_id}.wav"
    else:
        print(f"Audio file not found for Podcast ID {podcast_id}. Skipping...")
        return 
def extract_audio_url(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('Audio URL:'):
                    return line.split('Audio URL:')[1].strip()
        return None
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while extracting audio URL: {e}")
        return None

def extract_summary(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            summary = file.read().strip() 
        return summary if summary else None
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def extract_eval_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            eval_data = json.loads(content)
        return eval_data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def extract_transcription(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            transcription = ''.join(lines[1:]).strip() 
        return transcription if transcription else None
    except FileNotFoundError:
        return None

def get_audio_duration(file_path):
    try:
        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path)
            duration_seconds = audio.info.length 
        else:
            audio = AudioSegment.from_file(file_path)
            duration_seconds = len(audio) / 1000 

        duration_minutes = duration_seconds / 60         
        return round(duration_minutes, 2)

    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return 0

import os

def find_audio_file_in_subdirectories(podcast_id, duration_folder):
    print(f"Searching for audio files for podcast ID: '{podcast_id}' in '{duration_folder}'")
    
    podcast_id = podcast_id.strip().lower()
    
    for root, dirs, files in os.walk(duration_folder):
        for file in files:
            if (file.lower().endswith('.mp3') or file.lower().endswith('.wav')) and podcast_id in file.lower():
                return os.path.join(root, file)
    
    print("No matching audio file found.")
    return None


def check_if_document_exists(filename):
    search_query = {
        "query": {
            "match": {
                "filename": filename
            }
        }
    }
    response = requests.get(search_url, json=search_query, auth=HTTPBasicAuth('admin', 'Threeguys01!'), verify=False)
    if response.status_code == 200:
        hits = response.json().get('hits', {}).get('hits', [])
        return len(hits) > 0, hits[0]['_id'] if hits else None
    else:
        print(f"Error checking document existence: {response.status_code}, Response: {response.text}")
        return False, None

def process_and_index_document(podcast_id, eval_data, audio_duration, transcription, audio_url, filename, summary):
    upload_date, timestamp = get_upload_date_and_timestamp(podcast_id)

    exists, doc_id = check_if_document_exists(filename)

    document = {
        "audio_url": audio_url,
        "filename": filename,
        "audio_duration": audio_duration,
        "date": upload_date,
        "transcription": transcription,
        "transcript_summary": summary,
        "timestamp": timestamp,
        "lead_metrics_lead_source": eval_data.get("lead_metrics", {}).get("lead_source"),
        "lead_metrics_inquiry_type": eval_data.get("lead_metrics", {}).get("inquiry_type"),
        "lead_metrics_test_drive_status": eval_data.get("lead_metrics", {}).get("test_drive_status"),
        "lead_metrics_vehicle_model": eval_data.get("lead_metrics", {}).get("vehicle_model"),
        "customer_profile_state": eval_data.get("customer_profile", {}).get("state"),
        "customer_profile_profession": eval_data.get("customer_profile", {}).get("profession"),
        "customer_profile_age_group": eval_data.get("customer_profile", {}).get("age_group"),
        "customer_profile_previous_vehicle_brand": eval_data.get("customer_profile", {}).get("previous_vehicle", {}).get("brand"),
        "customer_profile_previous_vehicle_model": eval_data.get("customer_profile", {}).get("previous_vehicle", {}).get("model"),
        "preferences_variant": eval_data.get("preferences", {}).get("variant"),
        "preferences_transmission": eval_data.get("preferences", {}).get("transmission"),
        "preferences_fuel_type": eval_data.get("preferences", {}).get("fuel_type"),
        "preferences_exchange_required": eval_data.get("preferences", {}).get("exchange_required"),
        "preferences_finance_preference": eval_data.get("preferences", {}).get("finance_preference"),
        "customer_queries_top_questions": eval_data.get("customer_queries", {}).get("top_questions"),
        "customer_queries_primary_concerns": eval_data.get("customer_queries", {}).get("primary_concerns"),
        "sentiment_analysis_overall_sentiment": eval_data.get("sentiment_analysis", {}).get("overall_sentiment"),
        "sentiment_analysis_key_positive_points": eval_data.get("sentiment_analysis", {}).get("key_positive_points"),
        "sentiment_analysis_key_negative_points": eval_data.get("sentiment_analysis", {}).get("key_negative_points"),
    }

    if exists:
        response = requests.post(update_url + doc_id, json={"doc": document}, auth=HTTPBasicAuth('admin', 'Threeguys01!'), verify=False)
        if response.status_code == 200:
            print(f"Document updated successfully: {filename}")
        else:
            print(f"Failed to update document: {filename}. Status code: {response.status_code}")
    else:
        response = requests.post(index_url, json=document, auth=HTTPBasicAuth('admin', 'Threeguys01!'), verify=False)
        if response.status_code == 201:
            print(f"Document indexed successfully: {filename}")
        else:
            print(f"Failed to index document: {filename}. Status code: {response.status_code}")

def index_transcripts_from_folder(transcript_folder, eval_folder_path, duration_folder, summary_folder):
    if not os.path.exists(transcript_folder):
        print(f"Transcript folder does not exist: {transcript_folder}")
        return

    for filename in os.listdir(transcript_folder):
        print(filename)
        if filename.endswith('.txt'):
            file_path = os.path.join(transcript_folder, filename)
            podcast_id = os.path.splitext(filename)[0]
            print(f"Processing file: {file_path}")

            transcription = extract_transcription(file_path)
            eval_data = None
            
            eval_file_path = os.path.join(eval_folder_path, f"{podcast_id}.json")
            print(f"Looking for eval file at: {eval_file_path}")
            
            if os.path.exists(eval_file_path):
                eval_data = extract_eval_from_file(eval_file_path)
                print(f"Loaded evaluation data from {eval_file_path}")
            else:
                print(f"Evaluation data not found for Podcast ID {podcast_id}. Skipping...")
                continue  
            
            if transcription is None:
                print(f"Missing transcription data for Podcast ID {podcast_id}. Skipping...")
                continue  
            
            summary_file_path = os.path.join(summary_folder, f"{podcast_id}.txt")
            summary = extract_summary(summary_file_path)
            if summary is None:
                print(f"Summary not found for Podcast ID {podcast_id}. Skipping...")
                continue  
            
            audio_url = extract_audio_url(file_path)
            if not audio_url:
                print(f"Audio URL not found for Podcast ID {podcast_id}. Skipping...")
                continue  

            filename_from_url = extract_filename_from_url(audio_url)
            print(f"Final Audio File Name from URL: {filename_from_url}")

            audio_file_path = os.path.join(duration_folder, f"downloaded_audio_{podcast_id}.mp3")  # Assuming audio files are in duration_folder
            if not os.path.exists(audio_file_path):
                print(f"Audio file not found for Podcast ID {podcast_id}. Skipping...")
                continue
            
            audio_duration = get_audio_duration(audio_file_path)
            if audio_duration is None:
                print(f"Could not get duration for audio file: {audio_file_path}. Skipping...")
                continue
            
            print(f"Processing Podcast ID: {podcast_id}")
            process_and_index_document(podcast_id, eval_data, audio_duration, transcription, audio_url, filename_from_url, summary)

def delete_index():
    response = requests.delete(delete_index_url, auth=HTTPBasicAuth('admin', 'Threeguys01!'), verify=False)
    if response.status_code == 200:
        print("Index deleted successfully.")
    else:
        print(f"Error deleting index: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    for folders in ['2024-12-06'] : 
        transcript_folder = f"vlaudios/{folders}"
        eval_1 = f"new_prompt_eval_1/{folders}"
        summary_folder = f"transcript_summary/{folders}"
        duration_folder = f"duration/{folders}"
        # # check_and_create_index()    
        # # for folder in os.listdir("vlaudios"):
        # #         index_transcripts_from_folder(os.path.join(transcript_folder, folder), eval_1,duration_folder, summary_folder)
        index_transcripts_from_folder(transcript_folder, eval_1,duration_folder, summary_folder)
    # delete_index()
#     # delete_last_inserted_record()


