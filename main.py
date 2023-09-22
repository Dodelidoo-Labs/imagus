import os
from dotenv import load_dotenv
import json
import openai
import sys

load_dotenv(".env")

assistant = "You are a comic writer. You follow up to the previous comic panel scene with a new comic panel scene. Your response includes only visual descriptions of the comic panel scene itself. You use about 120 characters for the description. Your next comic panel scene is a direct continuation of this scene: "
prompt = input("Enter prompt:" )
artstyle = input("Enter Artstyle (Example: \"illustrated by Juan Giménez\", or \"in black and white pencil drawing style\"):")
panel_nu = int( input("Enter amount of Panels to generate:") )

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
		prompt= f"An intrinsic detailed single comic panel scene {artstyle} showing " + result,
		n=1,
		size="512x512"
	)
    image_url = image['data'][0]['url']
    data = {
		"content": result,
		"url": image_url
	}
    appendto(jsonpath, data)

def get_legacy_response(prompt, n, panel_n, panel_nu):
    if panel_n == panel_nu:
        end_message = 'All panels have been generated. Run imgs.py and then comic.py to finish your Comic!'
        print( end_message )
        sys.exit()
    if n == 0:
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

        make_image(result)

        n += 1
        prompt = assistant + result
        panel_n += 1

        get_legacy_response(prompt, n, panel_n, panel_nu)

        return result
    except Exception as e:
        result = f'Request failed with exception {e}'
        print( result )
        return False

def recur(panel_n, panel_nu):
    get_legacy_response(prompt, 0, panel_n, panel_nu)

recur(panel_n, panel_nu)