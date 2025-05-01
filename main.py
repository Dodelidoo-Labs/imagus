import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import base64

# Load environment variables
load_dotenv(".env")

# OpenAI client
client = OpenAI()

# Load OpenAI configuration
model = os.getenv("MODEL", "gpt-4")
max_tokens = int(os.getenv("MAX_TOKENS", "200"))
temp = float(os.getenv("TEMPERATURE", "0.7"))
freq = float(os.getenv("FREQ_PENALTY", "0.5"))
pres = float(os.getenv("PRES_PENALTY", "0.7"))
save_folder = "imgs"
n = 0
jsonpath = "logs.json"

# Prompt framework
assistant = (
    "You are a comic book scene writer. Each response you give should describe a single panel of a comic, "
    "continuing directly from the previous one.\n\n"
    "Do NOT describe the art style or framing — only describe the scene itself in vivid, imaginative detail. "
    "Stay grounded in physical elements: environment, characters, actions, objects, mood. Each panel should "
    "add something new or unexpected to the story, without explaining everything.\n\n"
    "Your goal is to build intrigue, atmosphere, and momentum — one panel at a time."
)
comic_text_prompt = (
    "You are writing comic book panel text for a published comic. The art is already drawn, and now you're adding the words.\n\n"
    "Write only what would appear as narration, dialogue, or sound effects in the panel — NOT a description of the art.\n"
    "Respond ONLY in valid JSON format with the following structure:\n\n"
    "{\n"
    "  \"narration\": [\"Optional narration text, if any.\"],\n"
    "  \"dialogue\": [\n"
    "    {\"character\": \"Name\", \"text\": \"Spoken words here.\"}\n"
    "  ],\n"
    "  \"sfx\": [\"SOUND EFFECT\"]\n"
    "}\n\n"
    "Omit fields that are empty. Do not explain. Do not add anything outside of the JSON. Use natural comic dialogue style."
)
# --- User Input ---
seed_idea = input("Enter comic idea or theme: ")
artstyle = input("Enter Artstyle (e.g., 'The image's style should follow the visual language of Japanese ukiyo-e prints with airy lines, delicate shading, and a gentle natural palette. This should be combined with the structured layout and muted tones characteristic of early 20th-century Eastern European propaganda lithographs. The background should be composed of watercolor-style rolling hills and trees meticulously crafted with precise ink linework. Overlay the entire image with a paper grain texture. Ensure the incorporation of cinematic lighting, balancing the scene elements, and capturing strong narrative posture.'): ")
panel_nu = int(input("Enter amount of Panels to generate: "))


# --- Utility ---
def appendto(file, data):
    if os.path.isfile(file) and os.path.getsize(file) > 0:
        with open(file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    existing_data.append(data)
    with open(file, 'w') as f:
        json.dump(existing_data, f, indent=2)

def seed_to_first_panel_prompt(seed_idea):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are starting a new comic book based on the following idea provided by a human.\n\n"
                        "Your job is to write the **first panel's visual scene description** — rich in detail and physical elements, "
                        "not abstract themes. Imagine what the camera sees. Be grounded, cinematic, and intriguing.\n\n"
                        "Do NOT explain or summarize the idea. Just write the first panel as if it's part of a real comic, "
                        "establishing the setting, mood, and character(s)."
                    )
                },
                {"role": "user", "content": f"Comic idea: {seed_idea}"}
            ],
            temperature=temp,
            max_tokens=max_tokens,
            frequency_penalty=freq,
            presence_penalty=pres
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating first panel from seed: {e}")
        return seed_idea  # fallback to user input
    
def generate_comic_text_from_image_description(image_prompt):
    try:
        chat_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": comic_text_prompt},
                {"role": "user", "content": image_prompt}
            ],
            temperature=temp,
            max_tokens=100,
            frequency_penalty=0.4,
            presence_penalty=0.6,
            response_format={"type": "json_object"}
        )
        return json.loads( chat_response.choices[0].message.content )
    except Exception as e:
        print(f"Error generating comic panel text: {e}")
        return ""

def generate_image_with_dalle3(prompt):
    global n
    print("Generating image with GPT Image 1...")
    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"Generate an image featuring {prompt}. {artstyle}.",
        n=1,
        quality="auto",
        size="auto",
    )
    image_b64 = response.data[0].b64_json
    #revised_prompt = response.data[0].revised_prompt
    image_data = base64.b64decode(image_b64)
    file_name = f"{n}-image.png"
    file_path = os.path.join(save_folder, file_name)
    with open(file_path, 'wb') as f:
        f.write(image_data)
        print(f"Image saved: {file_path} with prompt: {prompt}")
    n += 1
    return file_path

def generate_panel_and_image(prompt, panel_index):
    try:
        print(f"Generating panel {panel_index + 1}...")

        # Generate image and get URL
        file_path = generate_image_with_dalle3(prompt)

        # Generate narration
        comic_text = generate_comic_text_from_image_description(prompt)

        # Append final clean JSON
        data = {
            "content": prompt,
            "url": file_path,
            "description": comic_text
        }
        appendto(jsonpath, data)

        # Generate next scene prompt
        chat_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": assistant},
                {"role": "user", "content": prompt}
            ],
            temperature=temp,
            max_tokens=max_tokens,
            frequency_penalty=freq,
            presence_penalty=pres
        )
        next_prompt = chat_response.choices[0].message.content.strip()
        return next_prompt

    except Exception as e:
        print(f"Error during panel generation: {e}")
        return None


# --- Main Loop ---
print("Generating Comic Panels. Please wait...")

prompt = seed_to_first_panel_prompt(seed_idea)
for panel in range(panel_nu):
    result = generate_panel_and_image(prompt, panel)
    if not result:
        print("Aborting.")
        break
    prompt = result

print("All panels have been generated. Run imgs.py and then comic.py to finish your Comic!")
