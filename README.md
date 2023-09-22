# iMagus

A Comic Generator based on GPT and Dall-E.

## Purpose

This set of Python scripts lets you generate a PDF Comic, complete with Images and description of each image, by starting off from one single initial "propt".

The Code uses GPT to generate follow up scenes, and Dall-E to generate an image for each scene described.

Finally, the scripts allow to download each Dall-E generated image, and assmeble them together with their scene descriptions in a PDF Comic, featuring 4 Panels each page, a title, a footnote and a page-number in the footer.

## Preparations

1. You need an OpenAI API Key
2. This program requires an `.env` file which is _not provided in the repository_. 
    - You have to add it on your own within the main folder.
	- You have to add these contents and swap `YOUR_OPENAI_API_KEY` with the actual OpenAI API KEY:
	```
	TOKEN=YOUR_OPENAI_API_KEY
	BASE_URL=https://api.openai.com/v1
	MODEL=text-davinci-003
	MAX_TOKENS=1000
	TEMPERATURE=0
	FREQ_PENALTY=2.0
	PRES_PENALTY=2.0
	```
	- You can, of course, alter the parameters where it makes sense. Please refer to the OpenAI DOCs for more details about what each of these settings do
3. You need the Python Libraries specified in the `requirements.txt` installed on your machine, and of course, Python (at least 3.11)

## Usage

1. Download this repository and add your `.env` file to the main folder.
2. `cd` into the repository in a Terminal.
3. Run `python3.11 main.py` (if you use another Python handle, make sure to use your specific handle).
4. Complete the prompts: 
    - When asked to `Enter prompt`, enter the first Comic Panel "description".
	    - This will be used both for Dall-E to generate the first image, and for the description of that image.
		- Example: `A gorilla eats breakfast with a snail.`
	- When asked to `Enter Artstyle`, enter an artstyle (if you want, you can also leave it empty). 
	    - Examples are provided in the input prompt.
	- When asked to `Enter amount of Panels to generate:`, enter a number that represents the amount of total panels in your comic.
	    - Averagely, about 50 panels (50 images and 50 descriptions) cost 1 USD of API usage.
		- The program will put maximally 4 panels on each PDF page.
5. Let the program generate all panels. This can take a while.
6. Once finished, the terminal will show the message `All panels have been generated. Run imgs.py and then comic.py to finish your Comic!`
7. Now run `python3.11 imgs.py` and let the program finish. Again, this can take a while.
8. Now run `python3.11 comic.py`
    - When asked to `Enter your Comic Title`, enter the Title you would like your finished comic to have.
9. Let the program finish and find your new Comic in the main folder, named `comic.pdf`. This should be pretty fast.
10. Cleanup for a new run:
    - Delete all contents in the `logs.json` file
	- Delete all images in the `imgs` folder
	- Delete the `comic.pdf` file

## Developer notes:
- You can alter several strings (prompts, credits) in the `main.py` file
- The program uses `text-davinci-003` for prompts and does _not_ support newer (chat) models, but, of course you can extend the code...

## Plans and future
- It is planned to add a GUI to the whole process, however this is not yet done. Contributions welcome!
- It is planned to make the images download asynchroneous, to speed it up a bit.
- It is planned to add support for newer GPT models, and once it is out, Dall-E 3