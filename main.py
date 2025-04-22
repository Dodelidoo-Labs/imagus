import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

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
    "You are writing comic book panel text for a published comic. "
    "The art is already drawn, and now you're adding the words.\n\n"
    "Write only what would appear as narration, dialogue, or sound effects in the panel — NOT a description of the art.\n"
    "Only include text that feels natural in a printed comic. It's okay if the panel has no words.\n\n"
    "Respond with just the comic panel narration. Do not explain anything. Do not add extra information like \"NARRATION: \" or similar. Respond _with_ the narration only."
)
# --- User Input ---
prompt = input("Enter prompt: ")
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
            presence_penalty=0.6
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating comic panel text: {e}")
        return ""

def generate_image_with_dalle3(prompt):
    print("Generating image with DALL·E 3...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Generate an image featuring {prompt}. {artstyle}.",
        n=1,
        quality="standard",
        size="1024x1024",
    )
    image_url = response.data[0].url
    revised_prompt = response.data[0].revised_prompt
    print(f"Image generated: {image_url} with prompt: {revised_prompt}")
    return image_url

def generate_panel_and_image(prompt, panel_index):
    try:
        print(f"Generating panel {panel_index + 1}...")

        # Generate image and get URL
        image_url = generate_image_with_dalle3(prompt)

        # Generate narration
        comic_text = generate_comic_text_from_image_description(prompt)

        # Append final clean JSON
        data = {
            "content": prompt,
            "url": image_url,
            "description": comic_text
        }
        appendto(jsonpath, data)

        if panel_index == 0:
            return prompt  # Reuse prompt for next panel

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

for panel in range(panel_nu):
    result = generate_panel_and_image(prompt, panel)
    if not result:
        print("Aborting.")
        break
    prompt = result

print("All panels have been generated. Run imgs.py and then comic.py to finish your Comic!")
