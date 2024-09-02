import os 
import google.generativeai as genai 
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import json

load_dotenv(override=True)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Create the model


class LLM:
    def __init__(self):
        self.model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config={
            "temperature": 0,
            "top_p": 1,
            "max_output_tokens": 8096,
            "response_mime_type": "text/plain",
        },
        safety_settings="BLOCK_NONE"
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
            print(response)
            print(f"retrying for the {times} time")
            await asyncio.sleep(10 ** times)
            return await self.main(prompt, time_zone, times=times+1)


if __name__ == "__main__":
    prompt = "holiday this week from wed to sat"
    llm = LLM()
    res = asyncio.run(llm.main(prompt, time_zone="Europe/London"))
    print(res)


    import gcal

    for _ in res: 
        print(_) 
        gcal.write2gcal(_)