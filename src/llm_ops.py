import requests
import json

# TODO implement this: https://community.crewai.com/t/connecting-ollama-with-crewai/2222/2
# TODO finish
# The URL for the API endpoint
url = "http://localhost:11434/api/generate"

article = """Lilly expects orforglipron obesity results in third quarter
By Deena Beasley
June 21, 20252:10 PM GMT+1Updated 3 hours ago



Lilly Biotechnology Center is shown in San Diego after cutting price of insulin
Lilly Biotechnology Center is shown in San Diego, California, U.S. March 1, 2023 after Eli Lilly and Co on Wednesday said it will cut list prices by 70% for its most commonly prescribed insulin products, Humalog and Humulin, beginning from the fourth quarter of this year. REUTERS/Mike Blake/File Photo Purchase Licensing Rights, opens new tab

Listen to This Page·2 min
June 21 (Reuters) - Eli Lilly (LLY.N), opens new tab said on Saturday its experimental pill orforglipron helped diabetics lose weight and lower their blood sugar, and the company aims to announce in the third quarter trial results for the drug in overweight and obese people without diabetes.
Lilly expects to submit the non-diabetes Phase 3 data to global regulatory agencies by the end of the year, said Ken Custer, head of cardiometabolic health at the company. The U.S. Food and Drug Administration typically makes new drug approval decisions 10 months after a manufacturer's submission.
Keep up with the latest medical breakthroughs and healthcare trends with the Reuters Health Rounds newsletter. Sign up here.
Advertisement · Scroll to continue
Lilly said it plans to file for regulatory approvals for orforglipron as a diabetes treatment in 2026.
Full results of the diabetes trial were presented at the annual meeting of the American Diabetes Association in Chicago.
The Phase 3 study showed that type 2 diabetes patients taking the highest dose of daily orforglipron lost nearly 8% of their body weight over 40 weeks. That compares favorably with Novo Nordisk's (NOVOb.CO), opens new tab injected drug Ozempic, for which trials showed that diabetic patients on the highest dose lost roughly 6% of their body weight.
Lilly's pill, which can be taken without food or water, lowered blood sugar levels by an average of 1.3% to 1.6% across doses.
Advertisement · Scroll to continue
The company said the most frequently reported side effects were gastrointestinal and similar to other GLP-1 drugs, including diarrhea and vomiting.
Custer said Lilly's goal in its non-diabetes trials is to achieve weight loss consistent with GLP-1 drugs that are currently available. Ozempic was shown in trials to lead to weight loss of 15% for people without diabetes over 68 weeks.
He said orforglipron, which has a simpler production process than injected GLP-1 drugs such as Ozempic or Lilly's Zepbound and does not require cold storage, could mean wider global access to weight-loss drugs.
"This is the type of molecule that is going to allow us to reach the broader globe," Custer said.
The executive declined to comment on pricing plans for orforglipron."""
# The data payload for the POST request
data = {
    "model": "gemma3:1b",
    "prompt": f"""You are an expert financial trader. Your task is to analyze the provided financial news article and determine a trading recommendation (BUY, HOLD, or SELL) for the primary publicly traded entity mentioned.

Follow these steps precisely:
1.  **Identify the Primary Entity:** Extract the full, official name of the main publicly traded company or financial instrument discussed. Mention only the company talked about in the article. If no specific publicly traded entity is the primary focus, state "N/A".
2.  **Summarize Key Information:** Condense the article into 2-3 concise bullet points highlighting the most important financial news, events, or data points related to the primary entity that would impact its valuation.
3.  **Assess Sentiment:** Based *only* on the provided article, determine the overall sentiment towards the primary entity as POSITIVE, NEUTRAL, or NEGATIVE. Provide a very brief justification (1-2 sentences) for this sentiment.
4.  **Formulate Recommendation:** Based on your sentiment assessment and the summarized key information from the article, provide a clear trading recommendation: BUY, HOLD, or SELL.
    * **BUY:** Indicates strong positive news likely to lead to upward price movement.
    * **HOLD:** Indicates neutral news or mixed signals where significant price movement is unlikely or the impact is unclear.
    * **SELL:** Indicates strong negative news likely to lead to downward price movement.
5.  **Justify Recommendation:** Briefly explain *why* you made that specific BUY/HOLD/SELL recommendation, directly referencing the information and sentiment from the article.

Financial News Article:

{article}

Your final response *must* be in **JSON format**, exactly as shown below:

{{
  "primary_entity": "[[Primary Entity Name or N/A]]",
  "Symbol": "[[Primary Entity stock symbol or N/A]]",
  "key_information_summary": [
    "[[Bullet Point 1]]",
    "[[Bullet Point 2]]",
    "[[Bullet Point 3 (optional)]]"
  ],
  "sentiment": "[[POSITIVE|NEUTRAL|NEGATIVE]]",
  "sentiment_justification": "[[Brief justification for sentiment]]",
  "recommendation": "[[BUY|HOLD|SELL]]",
  "recommendation_justification": "[[Brief justification for recommendation]]"
}}

RESPONSE:

""",
}

try:
    # Make the POST request with stream=True to process the response in chunks
    response = requests.post(url, json=data, stream=True)

    # Raise an exception for HTTP errors (4xx or 5xx)
    response.raise_for_status()

    # Initialize an empty list to store all parsed JSON objects
    all_response_data = []
    full_text_response = ""

    # Iterate over the response content line by line
    print("Request successful! Streaming response:")
    for line in response.iter_lines():
        if line:  # Ensure the line is not empty
            try:
                # Decode the bytes to a string (usually utf-8)
                decoded_line = line.decode("utf-8")

                # Parse each line as a JSON object
                json_data = json.loads(decoded_line)

                all_response_data.append(json_data)

                # Ollama often sends a 'response' field in each chunk
                if "response" in json_data:
                    print(
                        json_data["response"], end="", flush=True
                    )  # Print incrementally
                    full_text_response += json_data["response"]
                elif "error" in json_data:
                    print(f"\nError in streamed chunk: {json_data['error']}")
                    break  # Stop processing on error

                # Check for the 'done' flag, indicating the end of the stream
                if json_data.get("done"):
                    break

            except json.JSONDecodeError as e:
                print(f"\nError decoding JSON from line: {e}")
                print(f"Malformed line content: {decoded_line}")
                break  # Stop if a line is malformed
            except Exception as e:
                print(f"\nAn unexpected error occurred while processing a line: {e}")
                print(f"Line content: {line.decode('utf-8')}")
                break

    print("\n--- End of Stream ---")
    print("\nAll captured response data (as a list of JSON objects):")
    print(
        json.dumps(all_response_data, indent=2)
    )  # Pretty print the collected JSON objects

    print(f"\nFull text response (concatenated): {full_text_response}")


except requests.exceptions.ConnectionError as e:
    print(f"Error: Could not connect to the server at {url}.")
    print(f"Please ensure the server (e.g., Ollama) is running and accessible.")
    print(f"Details: {e}")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"An unexpected request error occurred: {e}")
except Exception as e:
    print(f"An unhandled error occurred: {e}")
