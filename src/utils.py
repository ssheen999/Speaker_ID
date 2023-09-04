import os
import random
import json


def get_random_flac(folder_path):
    flac_files = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".flac"):
                flac_files.append(os.path.join(root, file))
    
    if flac_files:
        random_flac = random.choice(flac_files)
        return random_flac
    else:
        return "No .flac file"


def get_speaker_name(speaker_id):
    
    file_path = "data/speaker_name.json"  
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    # 查詢並取得值
    if speaker_id in data:
        speaker_name = data[speaker_id]
        return speaker_name
    else:
        print(f"Key {speaker_id} not found in the JSON data.")