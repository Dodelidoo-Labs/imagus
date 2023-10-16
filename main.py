import os
import sys
import json
import time
import requests
import openai
from dotenv import load_dotenv

load_dotenv(".env")

assistant = (
    "You are a comic writer. You follow up to the previous comic panel scene with a new comic panel scene. "
    "Your response includes only visual descriptions of the comic panel scene itself. "
    "You use about 120 characters for the description. Your next comic panel scene is a direct continuation of this scene: "
)
prompt = input("Enter prompt: ")
artstyle = input(
    "Enter Artstyle (Example: \"illustrated by Juan Giménez\", or \"in black and white pencil drawing style\"): "
)
panel_nu = int(input("Enter amount of Panels to generate: "))

print("Choose an Image Engine:")
print("1. Dalle-2")
print("2. Leonardo AI")
choice = input()

if choice == "1":
    engine = "d3"
elif choice == "2":
    engine = "leo"
    l_model_id = input("Model ID: ")
    
else:
    print("Invalid choice!")
    exit()

base_url = os.getenv("BASE_URL")
model = os.getenv("MODEL")
max_tokens = int(os.getenv("MAX_TOKENS"))
temp = float(os.getenv("TEMPERATURE"))
freq = float(os.getenv("FREQ_PENALTY"))
pres = float(os.getenv("PRES_PENALTY"))
openai.api_key = os.getenv("TOKEN")
jsonpath = "logs.json"
cpath = "comic.pdf"
panel_n = 1
leo_url = os.getenv("LEO_URL")
leo_token = os.getenv("LEO_TOKEN")


def appendto(file, data):
    if os.path.isfile(file) and os.path.getsize(file) > 0:
        with open(file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    existing_data.append(data)
    with open(file, 'w') as f:
        json.dump(existing_data, f)


def make_image(result):
    image = openai.Image.create(
        prompt=f"An intrinsic detailed single comic panel scene {artstyle} showing " + result,
        n=1,
        size="512x512"
    )
    image_url = image['data'][0]['url']
    data = {
        "content": result,
        "url": image_url
    }
    appendto(jsonpath, data)


def make_leo_image(result):
    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + leo_token,
        "content-type": "application/json"
    }
    data = {
        "height": 512,
        "modelId": l_model_id,
        "prompt": result + " " + artstyle,
        "width": 912,
		"alchemy": False,
		"controlNet": False,
		"guidance_scale": 7,
		"highContrast": True,
		"highResolution": True,
		"nsfw": False,
		"num_images": 1,
		"photoReal": False,
		"promptMagic": True,
		"public": False,
		"seed": 123456789,
		"tiling": False,
		"unzoom": False,
		"promptMagicVersion": "v2"
    }
    post_response = requests.post(leo_url, headers=headers, json=data)
    post_response_data = post_response.json()
    generation_id = post_response_data['sdGenerationJob']['generationId']
    time.sleep(5)
    max_retries = 10
    retry_interval = 10  # in seconds
    get_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
    for _ in range(max_retries):
        get_response = requests.get(get_url, headers=headers)
        get_response_data = get_response.json()
        status = get_response_data['generations_by_pk']['status']
        if status == "COMPLETE":
            image_url = get_response_data['generations_by_pk']['generated_images'][0]['url']
            break
        else:
            time.sleep(retry_interval)
    data = {
        "content": result,
        "url": image_url
    }
    appendto(jsonpath, data)


def get_legacy_response(prompt, n, panel_n, panel_nu):
    if panel_n == panel_nu:
        end_message = 'All panels have been generated. Run imgs.py and then comic.py to finish your Comic!'
        print(end_message)
        sys.exit()
    if n == 0:
        if engine == 'leo':
            make_leo_image(prompt)
        if engine == 'd3':
            make_image(prompt)
    prompt = assistant + prompt
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            frequency_penalty=freq,
            presence_penalty=pres
        )
        result = response['choices'][0]['text']
        completion_tokens = None
        if 'usage' in response and 'completion_tokens' in response['usage']:
            completion_tokens = response['usage']['completion_tokens']
        if not completion_tokens or completion_tokens == 0:
            get_legacy_response(prompt, n, panel_n, panel_nu)
        if engine == 'leo':
            make_leo_image(result)
        if engine == 'd3':
            make_image(result)
        n += 1
        panel_n += 1
        get_legacy_response(result, n, panel_n, panel_nu)
        return result
    except Exception as e:
        result = f'Request failed with exception {e}'
        print(result)
        return False


def recur(panel_n, panel_nu):
    print("Generating Comic Panels. Please wait..")
    get_legacy_response(prompt, 0, panel_n, panel_nu)


recur(panel_n, panel_nu)
