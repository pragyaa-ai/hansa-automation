import os
import requests
from pydub import AudioSegment
import datetime
today = datetime.date.today()
folder_name = today.strftime("%Y-%m-%d")

def download_audio(url, output_filename):
    print(f"Attempting to download audio from URL: {url}")
    try:
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            print(f"Successfully downloaded audio to {output_filename}")
            with open(output_filename, 'wb') as audio_file:
                audio_file.write(response.content)
            return output_filename
        else:
            print(f"Failed to download audio. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while downloading audio: {e}")
        return None

def get_audio_duration(file_path):
    print(f"Getting duration for audio file: {file_path}")
    try:
        audio = AudioSegment.from_file(file_path)
        duration_seconds = len(audio) / 1000
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration = f"{minutes:02}:{seconds:02}"
        print(f"Duration for {file_path}: {duration}")
        return duration
    except Exception as e:
        print(f"Exception occurred while getting duration: {e}")
        return None

def extract_audio_url(file_path):
    print(f"Extracting audio URL from transcript file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('Audio URL:'):
                    audio_url = line.split('Audio URL:')[1].strip()
                    print(f"Found audio URL: {audio_url}")
                    return audio_url
        print("No audio URL found in the transcript.")
        return None
    except FileNotFoundError:
        print("Transcript file not found.")
        return None
    except Exception as e:
        print(f"Exception occurred while extracting audio URL: {e}")
        return None

def get_audio_extension(url):
    url_lower = url.lower()
    if '.mp3' in url_lower:
        print("Detected audio format: mp3")
        return 'mp3'
    elif '.wav' in url_lower:
        print("Detected audio format: wav")
        return 'wav'
    print("Defaulting audio format to mp3")
    return 'mp3'

def process_transcripts(base_dir, output_dir):
    print(f"Processing transcripts in directory: {base_dir}")

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.txt'):
                transcript_file = os.path.join(root, file)
                print("Transcript file :", transcript_file)
                
                duration_file_path = os.path.join(root, os.path.splitext(file)[0] + '_duration.txt')
                print("Duration file path : ", duration_file_path)
                if os.path.isfile(duration_file_path):
                    print(f"Duration file '{duration_file_path}' already exists. Skipping '{transcript_file}'.")
                    continue
                
                audio_url = extract_audio_url(transcript_file)
                print("Audio URL : ", audio_url)
                if audio_url:
                    audio_extension = get_audio_extension(audio_url)
                    relative_path = os.path.relpath(root, base_dir)
                    output_folder = os.path.join(output_dir, relative_path)

                    os.makedirs(output_folder, exist_ok=True)
                    print(f"Output folder created: {output_folder}")

                    audio_file_path = os.path.join(output_folder, f'downloaded_audio_{file[:-4]}.{audio_extension}')
                    print(audio_file_path)
                    if os.path.isfile(audio_file_path):
                        print(f"Audio file '{audio_file_path}' already exists. Skipping download.")
                    else:
                        downloaded_file = download_audio(audio_url, audio_file_path)

                        if downloaded_file:
                            duration = get_audio_duration(audio_file_path)
                            if duration:
                                with open(duration_file_path, 'w') as duration_file:
                                    duration_file.write(f"Audio URL: {audio_url}\n")
                                    duration_file.write(f"Duration: {duration}\n")
                                print(f"Duration information written to: {duration_file_path}")
base_directory = f"vlaudios/{folder_name}"
output_directory = f"duration/{folder_name}"

process_transcripts(base_directory, output_directory)