import os
import requests
import json

n = 0
save_folder = "imgs"
os.makedirs(save_folder, exist_ok=True)

with open('logs.json', 'r') as file:
    json_array = json.load(file)

def download_image(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded: {file_path}")
    else:
        print(f"Failed to download image: {url}")

for item in json_array:
    image_url = item['url']
    file_name = str(n) + "-image.png"  # Extract file name from the URL
    file_path = os.path.join(save_folder, file_name)  # Create the file path
    download_image(image_url, file_path)
    n += 1
