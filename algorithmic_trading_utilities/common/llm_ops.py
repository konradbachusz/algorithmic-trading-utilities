import requests
import json
import sys
import os

sys.path.insert(1, "algorithmic_trading_utilities")
# Try different import approaches for data modules
try:
    from common.prompts import FINANCIAL_ANALYSIS_PROMPT, FINANCIAL_ANALYSIS_PROMPT_RAW_WEBSITE_CONTENT
    from common.config import model, ollama_url
except ImportError:
    from algorithmic_trading_utilities.common.prompts import FINANCIAL_ANALYSIS_PROMPT, FINANCIAL_ANALYSIS_PROMPT_RAW_WEBSITE_CONTENT
    from algorithmic_trading_utilities.common.config import model, ollama_url
import time
import re
from typing import List, Dict, Any
# TODO implement this: https://community.crewai.com/t/connecting-ollama-with-crewai/2222/2
# TODO try: https://huggingface.co/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis?text=Lilly+Biotechnology+Center+is+shown+in+San+Diego+after+cutting+price+of+insulin%0ALilly+Biotechnology+Center+is+shown+in+San+Diego%2C+California%2C+U.S.+March+1%2C+2023+after+Eli+Lilly+and+Co+on+Wednesday+said+it+will+cut+list+prices+by+70%25+for+its+most+commonly+prescribed+insulin+products%2C+Humalog+and+Humulin%2C+beginning+from+the+fourth+quarter+of+this+year.+REUTERS%2FMike+Blake%2FFile+Photo+Purchase+Licensing+Rights%2C+opens+new+tab%0A%0AListen+to+This+Page%C2%B72+min%0AJune+21+%28Reuters%29+-+Eli+Lilly+%28LLY.N%29%2C+opens+new+tab+said+on+Saturday+its+experimental+pill+orforglipron+helped+diabetics+lose+weight+and+lower+their+blood+sugar%2C+and+the+company+aims+to+announce+in+the+third+quarter+trial+results+for+the+drug+in+overweight+and+obese+people+without+diabetes.%0ALilly+expects+to+submit+the+non-diabetes+Phase+3+data+to+global+regulatory+agencies+by+the+end+of+the+year%2C+said+Ken+Custer%2C+head+of+cardiometabolic+health+at+the+company.+The+U.S.+Food+and+Drug+Administration+typically+makes+new+drug+approval+decisions+10+months+after+a+manufacturer%27s+submission.%0AKeep+up+with+the+latest+medical+breakthroughs+and+healthcare+trends+with+the+Reuters+Health+Rounds+newsletter.+Sign+up+here.%0AAdvertisement+%C2%B7+Scroll+to+continue%0ALilly+said+it+plans+to+file+for+regulatory+approvals+for+orforglipron+as+a+diabetes+treatment+in+2026.%0AFull+results+of+the+diabetes+trial+were+presented+at+the+annual+meeting+of+the+American+Diabetes+Association+in+Chicago.%0AThe+Phase+3+study+showed+that+type+2+diabetes+patients+taking+the+highest+dose+of+daily+orforglipron+lost+nearly+8%25+of+their+body+weight+over+40+weeks.+That+compares+favorably+with+Novo+Nordisk%27s+%28NOVOb.CO%29%2C+opens+new+tab+injected+drug+Ozempic%2C+for+which+trials+showed+that+diabetic+patients+on+the+highest+dose+lost+roughly+6%25+of+their+body+weight.%0ALilly%27s+pill%2C+which+can+be+taken+without+food+or+water%2C+lowered+blood+sugar+levels+by+an+average+of+1.3%25+to+1.6%25+across+doses.%0AAdvertisement+%C2%B7+Scroll+to+continue%0AThe+company+said+the+most+frequently+reported+side+effects+were+gastrointestinal+and+similar+to+other+GLP-1+drugs%2C+including+diarrhea+and+vomiting.%0ACuster+said+Lilly%27s+goal+in+its+non-diabetes+trials+is+to+achieve+weight+loss+consistent+with+GLP-1+drugs+that+are+currently+available.+Ozempic+was+shown+in+trials+to+lead+to+weight+loss+of+15%25+for+people+without+diabetes+over+68+weeks.%0AHe+said+orforglipron%2C+which+has+a+simpler+production+process+than+injected+GLP-1+drugs+such+as+Ozempic+or+Lilly%27s+Zepbound+and+does+not+require+cold+storage%2C+could+mean+wider+global+access+to+weight-loss+drugs.%0A%22This+is+the+type+of+molecule+that+is+going+to+allow+us+to+reach+the+broader+globe%2C%22+Custer+said.%0AThe+executive+declined+to+comment+on+pricing+plans+for+orforglipron.
#https://colab.research.google.com/#scrollTo=MKTdFkoN_SJU&fileId=https%3A//huggingface.co/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis.ipynb
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


# prompt = FINANCIAL_ANALYSIS_PROMPT.format(article=article) #todo FIX
prompt = FINANCIAL_ANALYSIS_PROMPT_RAW_WEBSITE_CONTENT.format(article=article)


def read_json_articles(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads a JSON file containing a list of articles and returns it.

    This function is designed to be robust, handling common file-related
    errors gracefully.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        List[Dict[str, Any]]: A list of articles loaded from the JSON file.
                              Returns an empty list if the file is not found,
                              is empty, or contains invalid JSON.
    """
    try:
        # Check if the file exists and is not empty before trying to load it
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"Warning: File is missing or empty at '{file_path}'.")
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Check file format.")
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
    return []


# TODO unit test this function
def get_basic_ollama_llm_response(model, prompt):
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
        response = requests.post(ollama_url, json=payload, stream=False)

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
                    print(
                        f"\nAn unexpected error occurred while processing a line: {e}"
                    )
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


def get_article_sentiment_json(article: str) -> dict:
    """
    Analyzes the sentiment of a financial article using an LLM.

    Args:
        article (str): The financial article text.

    Returns:
        dict: The sentiment analysis JSON from the LLM, or None if failed.
    """
    # Create the prompt with the article
    # prompt = FINANCIAL_ANALYSIS_PROMPT.format(article=article) #todo FIX
    prompt = FINANCIAL_ANALYSIS_PROMPT_RAW_WEBSITE_CONTENT.format(article=article)

    # Define the keys we expect in a valid response
    required_keys = [
        "primary_entity",
        "key_information_summary",
        "sentiment",
        "sentiment_justification",
        "recommendation",
        "recommendation_justification",
    ]

    # Valid recommendation values
    valid_recommendations = ["BUY", "SELL", "HOLD"]

    # Try up to 3 times to get a valid response
    for attempt in range(3):
        # Get response from LLM
        response = get_basic_ollama_llm_response(model, prompt)
        if not response:
            continue

        try:
            # Try to parse as JSON directly
            result_json = json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from within the response text
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    result_json = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    print(f"Attempt {attempt+1}: Could not parse JSON. Retrying...")
                    continue
            else:
                print(f"Attempt {attempt+1}: No JSON found in response. Retrying...")
                continue

        # Check if all required keys are present (including Symbol/symbol)
        has_symbol = "Symbol" in result_json or "symbol" in result_json
        has_all_keys = all(key in result_json for key in required_keys)

        # Validate recommendation value
        recommendation_valid = (
            "recommendation" in result_json and
            result_json["recommendation"] in valid_recommendations
        )

        if has_all_keys and has_symbol and recommendation_valid:
            return result_json
        else:
            # Log what's missing for debugging
            missing = [key for key in required_keys if key not in result_json]
            if not has_symbol:
                missing.append("Symbol/symbol")
            if not recommendation_valid:
                rec_value = result_json.get("recommendation", "missing")
                missing.append(f"Invalid recommendation: '{rec_value}' (must be BUY, SELL, or HOLD)")
            print(f"Attempt {attempt+1}: Missing/invalid: {missing}. Retrying...")

        # Wait before retrying
        time.sleep(1)

    # All attempts failed
    print("Failed to get valid response after 3 attempts.")
    return None


def process_articles_folder():
    """Process all articles in the articles folder and save sentiment analysis results."""
    articles_dir = "articles"
    results = []
    
    # Process each file in the articles directory
    for filename in os.listdir(articles_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(articles_dir, filename)
            print(f"\nProcessing {filename}...")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    article_content = f.read()
                
                sentiment_result = get_article_sentiment_json(article_content)
                if sentiment_result:
                    # Add filename to result for reference
                    sentiment_result['source_file'] = filename
                    results.append(sentiment_result)
                    print(f"Successfully analyzed {filename}")
                else:
                    print(f"Failed to analyze {filename}")
            
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Save combined results
    if results:
        output_file = "articles_analysis.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved combined analysis to {output_file}")
    else:
        print("\nNo successful analyses to save")

# Replace the existing file processing code with this
# process_articles_folder()

def process_articles(articles):
    """Process a list of articles and save sentiment analysis results."""
    results = []

    for article in articles:
        url = article.get("url")
        content = article.get("content")
        source = article.get("source")

        # Concatenate URL and content for sentiment analysis
        combined_input = f"URL: {url}\nContent: {content}\nSource: {source}"
        sentiment_result = get_article_sentiment_json(combined_input)

        if sentiment_result:
            sentiment_result['url'] = url
            results.append(sentiment_result)
            print(f"Successfully analyzed article from {source}")
        else:
            print(f"Failed to analyze article from {source}")

    # Save combined results
    if results:
        output_file = "articles_analysis2.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved combined analysis to {output_file}")
    else:
        print("\nNo successful analyses to save")

#TODO remove
if __name__ == "__main__":
    input_filename = "articles/scraped_articles_soup2.json"
    # Load articles from the specified JSON file
    scraped_articles = read_json_articles(input_filename)

    if scraped_articles:
        print(f"Loaded {len(scraped_articles)} articles from {input_filename}")
        process_articles(scraped_articles)
    else:
        print("No articles were loaded. Exiting.")
