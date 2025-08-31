import requests
import json
import sys

sys.path.insert(1, "algorithmic_trading_utilities")
# Try different import approaches for data modules
try:
    from common.prompts import FINANCIAL_ANALYSIS_PROMPT
except ImportError:
    from algorithmic_trading_utilities.common.prompts import FINANCIAL_ANALYSIS_PROMPT

# TODO implement this: https://community.crewai.com/t/connecting-ollama-with-crewai/2222/2
# The URL for the API endpoint #TODO move to config
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

model="gemma3:1b"
prompt=FINANCIAL_ANALYSIS_PROMPT.format(article=article)

def get_basic_llm_response(model, prompt):
    """
    Sends a prompt to the LLM API and returns the full text response.
    Args:
        model (str): The model name to use.
        prompt (str): The prompt to send.
    Returns:
        str: The concatenated full text response from the LLM.
    """
    # The payload for the POST request
    payload = {
        "model": model,
        "prompt": prompt,
    }

    try:
        # Make the POST request with stream=True to process the response in chunks. To get a stream of data change stream to True.
        response = requests.post(url, json=payload, stream=False)

        # Raise an exception for HTTP errors (4xx or 5xx)
        response.raise_for_status()

        # Initialize an empty list to store all parsed JSON objects
        all_response_data = []
        full_text_response = ""

        # Iterate over the response content line by line
        print("LLM Request successful!")
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

        return full_text_response

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
    return None

print(get_basic_llm_response(model, prompt))
print("\n")
print(get_basic_llm_response(model, "What is the capital of Paris? Respond in French"))
