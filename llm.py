import os 
import google.generativeai as genai 
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import json
import requests
import magic
import uuid


load_dotenv(override=True)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Create the model


class LLM:
    def __init__(self):
        self.model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": 0,
            "top_p": 1,
            "max_output_tokens": 8096,
            "response_mime_type": "application/json",
        },
        safety_settings="BLOCK_NONE"
        )

        self.vision_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", 
            generation_config={
                "temperature": 0,
                "top_p": 1,
                "max_output_tokens": 8096,
                "response_mime_type": "text/plain",  
            },
            system_instruction="You convert image or documents to html. if any tables, make sure all the cells and formattings are accurately represented in the html",
        )


    def load_template(self): 
        with open("prompt.txt", "r") as f: 
            return f.read()
    
    def get_prompt(self, prompt, time_zone):
        date_time = datetime.now()
        # set datetime to format "YYYY-MM-DD HH:MM:SS"
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        date_time_prompt = f"For your reference, the current date and time is {date_time}."
        prompt = self.load_template() + prompt + date_time_prompt + "\n" + time_zone
        return prompt
    
    async def get_response(self, prompt):
        response = await self.model.generate_content_async(prompt)
        return response
    
    # remove ```json ... ``` or ``` ```from the response 
    def clean_response(self, response): 
        response = response.replace("```json", "")
        response = response.replace("```", "")
        return response
    
    async def img2text(self, img_url):
        img_bin = requests.get(img_url).content
        file_type = magic.from_buffer(img_bin, mime=True)
        if "image" not in file_type: 
            raise Exception("Not an image")
        file_extension = file_type.split("/")[1]

        # create tmp dir if not exists
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        file_name = f"tmp/{uuid.uuid4()}.{file_extension}"
        with open(file_name, "wb") as f:
            f.write(img_bin)
        file = genai.upload_file(file_name, mime_type=file_type)

        # delete the file
        os.remove(file_name)

        prompt = "You convert image to html. if any tables, make sure all the cells and formattings are accurately represented in the html, without any missing or extra cells or formattings."
        response = await self.vision_model.generate_content_async([file, "\n", prompt])
        print(response.text)
        return response.text
    


    async def main(self, prompt, time_zone="Europe/London", times = 1):
        if times > 10: 
            raise Exception("Too many retries")
        prompt = self.get_prompt(prompt, time_zone)
        response = await self.get_response(prompt)
        print(response)
        try:    
            response = response.text        
            response = self.clean_response(response)
            response = json.loads(response)
            print(response)
            return response
        
        except Exception as e:
            print("Error: ", e)
            if e == "Not an image":
                return "Not an image"
            print(response)
            print(f"retrying for the {times} time")
            await asyncio.sleep(10 ** times)
            return await self.main(prompt, time_zone, times=times+1)
    
    async def vision_main(self, text_input, img_url, time_zone="Europe/London"):
        text = await self.img2text(img_url)
        return await self.main(text_input + text, time_zone)
        


if __name__ == "__main__":
    prompt = "baskeball game 5-7pm this friday"
    img_link = "https://cdn.discordapp.com/attachments/977731448129855512/1283094527623823443/image.png?ex=66e1be66&is=66e06ce6&hm=b98608f475a0be248a99c52675a5612525932eddad8c6c7d8ddbab25efe03289&"
    model = LLM()
    response = asyncio.run(model.vision_main(img_link))
    print(response)