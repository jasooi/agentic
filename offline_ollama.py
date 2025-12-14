# This is a simple script to call ollama's API for a locally downloaded model

import requests
import json

api_url = "http://localhost:11434/api/generate"

def main():
    prompt = input("Please enter your question:\n")
    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt
    }

    try:
        response = requests.post(api_url, json=payload, stream=False)
        response_str = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    response_str += str(data["response"])
                    # print(data["response"], end="", flush=True)
        
        print(response_str)

    except (TypeError, ValueError):
        print("enter valid question")

if __name__ == "__main__":
    main()