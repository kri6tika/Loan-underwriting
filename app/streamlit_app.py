# Streamlit application
import pandas as pd
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features.feature_engineering import calculate_features
from src.models.customer_segmentation import predict_segment
from src.models.predict import prediction
from src.features.document_validation import (extract_text,validate_customer_name,validate_land,validate_income,validate_quotation)

# Custom red warning box
st.markdown("""
    <style>
    div[data-testid="stNotification"] > div {
    background-color: #ffcccc !important;
    border-left: 6px solid #b30000 !important;}
    </style>
    """, unsafe_allow_html=True)


# Global CSS styling
st.markdown("""
    <style>
    .stButton > button {
    background-color: #1565C0;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 12px 30px;}
    .stButton > button:hover {
    background-color: #0D47A1;}
    </style>
    """, unsafe_allow_html=True)


df = pd.read_csv("data/raw/Customer_Data.csv")

st.set_page_config(
    page_title="AI Loan Underwriter",
    page_icon="💰",
    layout="wide"
)

st.sidebar.info("Automated credit risk assessment powered by machine learning.")
st.sidebar.markdown("Developed by Kritika • Version 1.0")



if "manufacturer" not in st.session_state:
    st.session_state["manufacturer"] = "Select..."
if "vehicle_model" not in st.session_state:
    st.session_state["vehicle_model"] = "Select..."
if "mobile_verified" not in st.session_state:
    st.session_state["mobile_verified"] = False
if "otp_sent" not in st.session_state:
    st.session_state["otp_sent"] = False
if "demo_otp" not in st.session_state:
    st.session_state["demo_otp"] = None
for key in ["land_acres_str", "other_income_str", "obligation_str"]:
      if key not in st.session_state:
         st.session_state[key] = ""

def safe_float(value):
    try:
         return float(value.strip()) if value and value.strip() != "" else None
    except ValueError:
         return None

# Initialize session state
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "Customer Info"

tab_names = ["Customer Info", "Loan Details","Document Upload","Result"]

# Custom Tab Navigation

current_tab = st.session_state["current_tab"]

tab_html = """<style>

.custom-tabs {
    display: flex;
    width: 100%;
    border-bottom: 2px solid #c7dff5;
    margin-bottom: 30px;
}

.custom-tab {
    padding: 10px 18px;
    color: #0757a6;
    font-size: 16px;
    font-weight: 500;
    text-align: center;
    white-space: nowrap;
}

.custom-tab.active {
    border-bottom: 3px solid #1976d2;
    font-weight: 600;
}

</style>

<div class="custom-tabs">
"""

for tab in tab_names:

    active_class = "active" if tab == current_tab else ""

    tab_html += f"""<div class="custom-tab {active_class}">{tab}</div>"""

tab_html += "</div>"

st.markdown(tab_html, unsafe_allow_html=True)

# Display content based on active tab
if st.session_state["current_tab"] == "Customer Info":
    st.subheader("Customer Information 🧑‍💼")
    col1, col2 = st.columns(2)
    with col1:
          customer_name = st.text_input("Customer Name",placeholder="Enter Full Name")
    
          state = st.selectbox("State",["Select..."] +sorted(df["State"].dropna().unique()))
    
          cibil_score_str = st.text_input("CIBIL Score",value="")
          
    
    with col2:
         age_str = st.text_input("Age", placeholder="Enter age as per Aadhaar")
         age = int(age_str) if age_str else None 
         if age and (age < 18 or age > 70): 
            st.warning("Age must be between 18 and 70.")
            st.stop()
    
         district = st.selectbox( "District",["Select..."] + sorted(df[df["State"] == state]["District"].dropna().unique()))
        
         existing_customer = st.selectbox("Existing Customer", ["Select..."] +["Yes", "No"])

         if existing_customer == "Select...":
            st.info("If customer has availed term loan or FD from XYZ bank, select existing customer as Yes.")


    mobile_number = st.text_input("Mobile Number",placeholder="Enter 10-digit mobile number",max_chars=10,key="mobile_number")

    col_mobile1, col_mobile2 = st.columns(2)

    with col_mobile1:
        if st.button("Send OTP", key="send_otp"):
             if not mobile_number.isdigit() or len(mobile_number) != 10:
                     st.error( "Please enter a valid 10-digit mobile number.")

             else:
                     st.session_state["demo_otp"] = "123456"
                     st.session_state["otp_sent"] = True
                     st.success( "OTP sent successfully.")

    with col_mobile2:
         if st.session_state["otp_sent"]:
                 otp = st.text_input( "Enter OTP",max_chars=6,key="otp")
                 if st.button( "Verify OTP", key="verify_mobile_otp"):
                        if otp == st.session_state["demo_otp"]:
                                 st.session_state["mobile_verified"] = True
                                 st.success( "✅ Mobile number verified successfully.")

                        else:
                                 st.session_state["mobile_verified"] = False
                                 st.error( "❌ Invalid OTP. Please try again.")
         
    
    # Income Details
    if st.session_state["mobile_verified"]:
         st.subheader("Income Details 🌾")
         col3, col4 = st.columns(2)
         with col3:
          land_acres_str = st.text_input("Land (Acres)",value="")
          other_income_str = st.text_input("Other Documented Income",value="") 
    
         with col4:
          crop = st.selectbox(
            "Crop",["Select..."] + sorted(df["Crop"].dropna().unique()))
          
          obligation_str = st.text_input( "Obligation",value="")
    
    else:
          st.info(
        "🔒 Please verify your mobile number to continue "
        "to Income Details."
    )
    
    # Navigation buttons
    col_back, col_next = st.columns([1, 1])
    with col_next:
        if st.button("Next ➡️", key="customer_next"):
           st.session_state["customer_name"] = customer_name
           st.session_state["district"] = district
           st.session_state["state"] = state
           st.session_state["age_str"] = age_str
           st.session_state["existing_customer"] = existing_customer
           st.session_state["cibil_score_str"] = cibil_score_str
           st.session_state["land_acres_str"] = land_acres_str
           st.session_state["other_income_str"] = other_income_str
           st.session_state["obligation_str"] = obligation_str
           st.session_state["crop"] = crop
           st.session_state["current_tab"] = "Loan Details"
           st.rerun()

elif st.session_state["current_tab"] == "Loan Details":
    st.subheader("Loan Requirement 💰")
    col1, col2 = st.columns(2)
    with col1:
        manufacturer = st.selectbox("Manufacturer",["Select..."] + sorted(df["Manufacturer"].dropna().unique()),placeholder="Mention Vehicle Manufacturer")

        vehicle_model = st.selectbox("Vehicle Model",["Select..."] + sorted(df[df["Manufacturer"] == manufacturer]["Vehicle_Model"].dropna().unique()))
    
    with col2: 
        loan_amount_str = st.text_input("Loan Amount Requested",value="")
        loan_tenure_str = st.text_input( "Loan Tenure (Years)",value="") 

# Navigation buttons
    col_back, col_next = st.columns([1, 1])
    with col_back:
         if st.button("⬅️ Back", key="loan_back"):
             st.session_state["current_tab"] = "Customer Info"
             st.rerun()

    with col_next:
         if st.button("Next ➡️", key="loan_next"):
             if manufacturer == "Select..." or vehicle_model == "Select...":
                 st.warning("Please select both Manufacturer and Vehicle Model before proceeding.")
             else:
                 st.session_state["current_tab"] = "Document Upload"
                 st.session_state["manufacturer"] = manufacturer
                 st.session_state["vehicle_model"] = vehicle_model
                 st.session_state["loan_amount_str"] = loan_amount_str
                 st.session_state["loan_tenure_str"] = loan_tenure_str
                 st.rerun()

elif st.session_state["current_tab"] == "Document Upload":
    st.subheader("📄 Document Upload")
    st.info("Please upload the following documents before proceeding to underwriting assessment")

    customer_name = st.session_state.get("customer_name", "")

    land_acres = safe_float(st.session_state.get("land_acres_str", ""))

    other_income = safe_float(st.session_state.get("other_income_str", ""))

    loan_amount = safe_float(st.session_state.get("loan_amount_str", ""))

    identity_document = st.file_uploader("1. Identity Proof",type=["pdf", "jpg", "jpeg", "png"])

    land_document = st.file_uploader("2. Land Ownership Document",type=["pdf", "jpg", "jpeg", "png"])

    income_document = st.file_uploader( "3. Income Proof",type=["pdf", "jpg", "jpeg", "png"])

    vehicle_quotation = st.file_uploader("4. Vehicle Quotation",type=["pdf", "jpg", "jpeg", "png"])

    if (
        identity_document is None
        or land_document is None
        or income_document is None
        or vehicle_quotation is None):

        st.error( "Please upload all four documents.")

    else:
        st.info("Document Upload Complete ✅")

    col_back, col_next = st.columns(2)

    with col_back:
        if st.button("⬅️ Back", key="document_back"):
            st.session_state["current_tab"] = "Loan Details"
            st.rerun()

    with col_next:
        if st.button( "Next ➡️",key="validate_documents"):
            st.session_state["identity_document"] = identity_document
            st.session_state["land_document"] = land_document
            st.session_state["income_document"] = income_document
            st.session_state["vehicle_quotation"] = vehicle_quotation
            st.session_state["current_tab"] = "Result"
            st.rerun()

                
elif st.session_state["current_tab"] == "Result":
     st.subheader("Underwriting Result 📊")
     
     features = None
     customer_name = st.session_state.get("customer_name", "")
     age = safe_float(st.session_state.get("age_str", ""))
     state = st.session_state.get("state", "")
     district = st.session_state.get("district", "")
     cibil_score_str = st.session_state.get("cibil_score_str", "")
     cibil_score = int(cibil_score_str) if cibil_score_str else None
     existing_customer = st.session_state.get("existing_customer", "")
     land_acres = safe_float(st.session_state.get("land_acres_str", ""))
     crop = st.session_state.get("crop", "")
     other_income = safe_float(st.session_state.get("other_income_str", ""))
     obligation = safe_float(st.session_state.get("obligation_str", ""))
     
     manufacturer = st.session_state.get("manufacturer", "")
     vehicle_model = st.session_state.get("vehicle_model", "")
     loan_amount = safe_float(st.session_state.get("loan_amount_str", ""))
     loan_tenure = safe_float(st.session_state.get("loan_tenure_str", ""))

     identity_document = st.session_state.get("identity_document")
     land_document = st.session_state.get("land_document")
     income_document = st.session_state.get("income_document")
     vehicle_quotation = st.session_state.get("vehicle_quotation")
     
     if manufacturer in [None, "Select..."] or vehicle_model in [None, "Select..."]:
         st.warning("Please select both Manufacturer and Vehicle Model before proceeding.")
         st.stop()
     
     else:

         def compute_underwriting( age,cibil_score,state, district, crop, land_acres, other_income, obligation,
                loan_amount, loan_tenure, manufacturer, vehicle_model, existing_customer):
             
             features = calculate_features(
                     State=state,
                     District=district,
                     Crop=crop,
                     Land_acres=land_acres,
                     Other_Documented_Income=other_income,
                     Obligation=obligation,
                     Loan_amount_requested=loan_amount,
                     Loan_tenure= loan_tenure,
                     Manufacturer=manufacturer,
                     Vehicle_Model=vehicle_model,
                     Existing_customer=existing_customer)  

             with st.spinner("Reading and validating documents..."):
             
             # Identity document
             
                 identity_text = extract_text(identity_document)
                 name_result = validate_customer_name(customer_name,identity_text)
             
             # Land document
                 land_text = extract_text(land_document)
                 land_result = validate_land(land_acres,land_text)
             
              # Income document
                 income_text = extract_text(income_document)
                 income_result = validate_income(other_income,income_text)
             
              # Vehicle quotation
                 quotation_text = extract_text(vehicle_quotation)
                 quotation_result = validate_quotation(features['Net_Dealer_Price'],quotation_text)
             
                 st.subheader("Document Validation Results")

                 validation_data = [["Identity Proof", "Customer Name", name_result['status']],
                                    ["Land Ownership", "Land Area", land_result['status']],["Income Proof", "Income", income_result['status']],["Quotation", "Vehicle Price", quotation_result['status']]]

                 df_validation = pd.DataFrame(validation_data,columns=["Document", "Check", "Status"])
                 st.table(df_validation)

                 # Check whether ALL documents match
                 all_documents_match = (name_result["status"] == "✅ MATCH"and land_result["status"] == "✅ MATCH" and income_result["status"] == "✅ MATCH" and quotation_result["status"] == "✅ MATCH")

                 if not all_documents_match:
                         if name_result["status"] == "❌ MISMATCH":
                             st.error( "❌ Customer Name: MISMATCH")
             
                         if land_result["status"] == "❌ MISMATCH":
                             st.error(f"❌ Land mismatch: "
                             f"{land_result['entered']} acres entered vs "
                             f"{land_result['document']} acres in document")
             
                         if income_result["status"] == "❌ MISMATCH":
                          st.error(f"❌ Income mismatch: "
                                 f"₹{income_result['entered_income']:} entered vs "
                                 f"₹{income_result['document_income']:} in document")

                         if quotation_result["status"] == "❌ MISMATCH":
                           st.error(f"❌ MISMATCH: "
                                    f"₹{quotation_result['Net_Dealer_Price']:} as reported by Manufacturer vs "
                                    f"₹{quotation_result['quotation_amount']:}in quotation document")
                           
                         st.warning("Please correct the mismatched information/documents ""before proceeding with underwriting.")
                         st.session_state["documents_verified"] = False
                         return None

             st.session_state["documents_verified"] = True

             segment = predict_segment(
                     NFCF=features["NFCF"],
                     land_acres=land_acres,
                     Loan_amount_requested=loan_amount,
                     LTV=features["LTV"],
                     existing_customer=features["Existing Customer"])
             
             predicted_pd,risk_grade,decision,rate= prediction(
                     Age=age,
                     Cibil_Score=cibil_score,
                     NFCF=features["NFCF"],
                     Land_acres=land_acres,
                     Loan_amount_requested=loan_amount,
                     Loan_tenure= loan_tenure,
                     LTV=features["LTV"],
                     existing_customer=features["Existing Customer"],
                     Segment=segment)
                 
             return features, segment, predicted_pd, risk_grade, decision,rate
         
     result = compute_underwriting( age, cibil_score,state, district, crop, land_acres, 
     other_income, obligation,loan_amount, loan_tenure, manufacturer, vehicle_model, existing_customer)

     if result is None:st.stop()

     features, segment, predicted_pd, risk_grade, decision, rate = result
     
     segment_names = {
               0: "Existing customer- Low Exposure",
               1: "New customer- Low Exposure",
               2: "Existing customer - High Exposure",
               3: "Strong Financial Profile",
               4: "New customer- High Exposure"}
        
     segment_name = segment_names[segment]

     st.markdown("**__Application Summary__**")
     st.write( customer_name, "owns", land_acres, "acres land, grows", crop,"bi-annually, and makes annual crop income of Rs.",features["Crop_Income"])
     st.write("Total Income (including other documented income)",features["Total_Income"])
     st.write("The customer requested loan amount Rs.",loan_amount,"for a period of ",loan_tenure, "years", "against vehicle ", manufacturer,vehicle_model,".")
     st.write("The vehicle costs Rs.",features['Net_Dealer_Price'] , "which makes LTV:", f"{features['LTV']*100:.2f}", "%")
     st.write("Customer Segment:", segment_name)
     st.write("Probability of Default:", f"{predicted_pd:.2f}", "%"," and Risk grade:", risk_grade)
     st.write("Final Underwriting Decision:", decision)


