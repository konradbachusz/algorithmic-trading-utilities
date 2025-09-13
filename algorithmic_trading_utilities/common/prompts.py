FINANCIAL_ANALYSIS_PROMPT = """You are an expert financial trader. Your task is to analyze the provided financial news article and determine a trading recommendation (BUY, HOLD, or SELL) for the primary publicly traded entity mentioned.

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

"""

FINANCIAL_ANALYSIS_PROMPT_RAW_WEBSITE_CONTENT = """You are an expert financial trader and content analyzer. Your task has two parts:

PART 1 - Content Filtering:
First, analyze the provided raw website content and extract only the main financial news article text. Ignore:
- Navigation menus and headers
- Advertisements
- Social media links
- Comment sections
- Sidebars with related articles
- Cookie notices or privacy warnings
- Any other non-article content

PART 2 - Financial Analysis:
Once you have isolated the article text, analyze it to determine a trading recommendation (BUY, HOLD, or SELL) for the primary publicly traded entity mentioned.

Follow these steps precisely:
1.  **Identify the Primary Entity:** Extract the full, official name of the main publicly traded company or financial instrument discussed. Mention only the company talked about in the article. If no specific publicly traded entity is the primary focus, state "N/A". If you're not sure about the stock symbol state "N/A".
2.  **Summarize Key Information:** Condense the article into 2-3 concise bullet points highlighting the most important financial news, events, or data points related to the primary entity that would impact its valuation.
3.  **Assess Sentiment:** Based *only* on the extracted article content, determine the overall sentiment towards the primary entity as POSITIVE, NEUTRAL, or NEGATIVE. Provide a very brief justification (1-2 sentences) for this sentiment.
4.  **Formulate Recommendation:** Based on your sentiment assessment and the summarized key information from the article, provide a clear trading recommendation: BUY, HOLD, or SELL.
    * **BUY:** Indicates strong positive news likely to lead to upward price movement.
    * **HOLD:** Indicates neutral news or mixed signals where significant price movement is unlikely or the impact is unclear.
    * **SELL:** Indicates strong negative news likely to lead to downward price movement.
5.  **Justify Recommendation:** Briefly explain *why* you made that specific BUY/HOLD/SELL recommendation, directly referencing the information and sentiment from the article.

Raw Website Content:

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

"""