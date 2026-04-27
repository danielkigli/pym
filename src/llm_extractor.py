import os
import json
from google import genai
from pydantic import BaseModel, Field


class TransactionInsight(BaseModel):
    company: str = Field(description="The name of the company.")
    person_name: str = Field(
        description="The name of the person making the transaction."
    )
    job_title: str = Field(
        description="The job title or role of the person (e.g., Director, CEO)."
    )
    action: str = Field(description="The action taken, usually 'BUY' or 'SELL'.")
    amount_shares: float = Field(
        description="The number of shares transacted.", default=0.0
    )
    price_per_share: float = Field(
        description="The price per share in the transaction.", default=0.0
    )


class ExtractedReport(BaseModel):
    transactions: list[TransactionInsight] = Field(
        description="List of transactions found in the report."
    )


def extract_insights_from_report(report_text: str) -> dict:
    """
    Uses Gemini to analyze a Maya stock market report (usually in Hebrew)
    and extract structured information about director/insider transactions.

    Args:
        report_text (str): The raw text extracted from the Maya report.

    Returns:
        dict: A dictionary containing the structured data.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. Please set it to your Google AI Studio API key."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are a financial analyst expert in reading Israeli stock market (TASE) reports.
    Read the following report text (which may be in Hebrew or English) and extract information about any insider or director transactions (buying or selling of shares).

    If the report does not contain information about someone buying or selling shares, return an empty list for transactions.

    Report Text:
    {report_text}
    """

    try:
        # We use gemini-2.5-flash as it is fast, free tier friendly, and supports Structured Outputs (JSON Schema)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedReport,
            },
        )

        # The response.text is guaranteed to be a JSON string matching the ExtractedReport schema
        result = json.loads(response.text)
        return result

    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return {"transactions": []}


if __name__ == "__main__":
    # Mock text for testing
    mock_text = "ביום 20 באפריל, משה כהן, מנכ״ל חברת טבע, רכש 1000 מניות במחיר של 50 שקלים למניה."
    print("Testing LLM Extraction (requires GEMINI_API_KEY to be set)...")
    if os.environ.get("GEMINI_API_KEY"):
        res = extract_insights_from_report(mock_text)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Skipped. Set GEMINI_API_KEY to run the test.")
