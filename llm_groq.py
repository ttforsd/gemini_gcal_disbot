import os 
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv
import json
from datetime import datetime
import re

load_dotenv(override=True)




class LLM:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_KEY"))
        self.model = "qwen/qwen3-32b" 
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"

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
        chat_completion = await self.client.chat.completions.create(
            model = self.model,
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.1, 
            max_tokens=6000
        )
        return chat_completion.choices[0].message.content
    
    def clean_response(self, response): 
        # remove <think> ... </think> 
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)

        response = response.replace("```json", "")
        response = response.replace("```", "")
        print("cleaned response: ", response)
        return response
    

    async def img2text(self, img_url):
        chat_completion = await self.client.chat.completions.create(
            model = self.vision_model,
            messages = [{
                "role": "user", 
                "content": [
                    {"type": "text", "text": "You convert image to html. if any tables, make sure all the cells and formattings are accurately represented in the html, without any missing or extra cells or formattings."},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }]
        )
        return chat_completion.choices[0].message.content
    async def main(self, prompt, time_zone="Europe/London", times = 1):
        if times > 10: 
            raise Exception("Too many retries")
        prompt = self.get_prompt(prompt, time_zone)
        response = await self.get_response(prompt)
        print(response)
        try:       
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
    llm = LLM()
    prompt = "https://media.discordapp.net/attachments/1142237153796030474/1499340272176201728/image0.jpg?ex=6a00f731&is=69ffa5b1&hm=ddac73c1579a40dba2c798ae2593b12f7bf7e49e748d0a2fbc31023b80091fe0&=&format=webp&width=2340&height=658"
    response = asyncio.run(llm.img2text(prompt))
    print(response)