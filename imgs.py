import os
import json
import aiohttp
import asyncio

n = 0
save_folder = "imgs"
os.makedirs(save_folder, exist_ok=True)

with open('logs.json', 'r') as file:
    json_array = json.load(file)

async def download_image(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as file:
                    file.write(await response.read())
                print(f"Image downloaded: {file_path}")
            else:
                print(f"Failed to download image: {url}")

async def main():
    global n
    tasks = []
    for item in json_array:
        image_url = item['url']
        file_name = str(n) + "-image.png"  # Extract file name from the URL
        file_path = os.path.join(save_folder, file_name)  # Create the file path
        tasks.append(download_image(image_url, file_path))
        n += 1
    await asyncio.gather(*tasks)

asyncio.run(main())
