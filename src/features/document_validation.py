import re
import io
import pytesseract
import streamlit as st

from PIL import Image
from pypdf import PdfReader
from pdf2image import convert_from_bytes
from rapidfuzz import fuzz

# Extract text from uploaded document

def extract_text(uploaded_file):

    file_bytes = uploaded_file.getvalue()
    file_type = uploaded_file.type

    # Image document
    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text

    # PDF document
    elif file_type == "application/pdf":
        # First try normal PDF text extraction
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # If PDF has no selectable text, use OCR
        if len(text.strip()) < 20:
            pages = convert_from_bytes(file_bytes)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page)
                text += "\n"
        return text

    else:
        raise ValueError("Unsupported document format.")

def normalize_name(name):
    name = str(name).upper()
    name = re.sub(r"[^A-Z\s]", " ",name)
    name = re.sub( r"\s+"," ", name).strip()
    return name

def validate_customer_name(entered_name,document_text):
    entered_name = normalize_name(entered_name)
    document_text = normalize_name(document_text)
    similarity = fuzz.partial_ratio(entered_name,document_text)
    if similarity >= 80:
        return {"status": "✅ MATCH"}

    else:
        return {"status": "❌ MISMATCH"}

def extract_land_acres(text):
    patterns = [
        r"(?:land\s*area|area\s*of\s*land|land\s*holding)"
        r"\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*"
        r"(?:acres?|acre)",
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:acres?|acre)"
    ]

    text = text.lower()
    for pattern in patterns:
        match = re.search(pattern,text,re.IGNORECASE)
        if match:
            return float( match.group(1))

    return None

def validate_land(entered_land,document_text):

    document_land = extract_land_acres(document_text)

    if document_land is None:

        return {
            "status": "REVIEW",
            "entered": entered_land,
            "document": None,
            "message": "Could not extract land area."
        }


    if entered_land <= document_land:
         return {"status": "✅ MATCH"}

    else:     
         return {"status": "❌ MISMATCH",
                  "entered": entered_land,
                  "document": document_land,}
    
def extract_income(text):
    patterns = [
     
        r"(?:net\s+pay|gross\s+income|net\s+income)"
        r"\s*[:\-]?\s*(?:rs\.?|₹)?\s*"
        r"([\d,]+(?:\.\d+)?)",

        r"(?:annual\s+income|yearly\s+income)"
        r"\s*[:\-]?\s*(?:rs\.?|₹)?\s*"
        r"([\d,]+(?:\.\d+)?)",

        r"(?:income)"
        r"\s*[:\-]?\s*(?:rs\.?|₹)?\s*"
        r"([\d,]+(?:\.\d+)?)"

    ]

    text = text.lower()

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = match.group(1)
            value = value.replace(",","")
            return float(value)

    return None

def validate_income(entered_income,document_text):
    document_income = extract_income(document_text)
    if document_income is None:
        return {
            "status": "REVIEW",
            "entered": entered_income,
            "document": None,
            "message": "Could not extract income."}

    if entered_income <= document_income:
         return {"status": "✅ MATCH"}
    else:
         return {"status": "❌ MISMATCH",
                 "entered": entered_income,
                 "document": document_income}
        
def extract_vehicle_price(text):
    patterns = [
        r"(?:net\s*purchase\s*price)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
        
        r"(?:net\s*dealer\s*price)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
        
        r"(?:final\s*price)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
        
        r"(?:net\s*price)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
        
        r"(?:total\s*price)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            price = match.group(1)

            # Remove commas
            price = price.replace(",", "")

            return float(price)

    return None

def validate_quotation(Net_Dealer_Price,document_text, tolerance_percentage=5):
    quotation_amount = extract_vehicle_price(document_text)
    if quotation_amount is None:
        return {
            "status": "REVIEW",
            "entered": Net_Dealer_Price,
            "document": None,
            "message": "Could not extract quotation amount."
        }

    difference_percentage = (abs(Net_Dealer_Price-quotation_amount)/ max(quotation_amount, 1)) * 100

    if difference_percentage <= tolerance_percentage:
        return {"status": "✅ MATCH"}
    else:
        return {"status": "❌ MISMATCH",
                 "entered": Net_Dealer_Price,
                 "document": quotation_amount}
