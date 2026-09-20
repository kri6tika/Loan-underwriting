
import pandas as pd
import joblib
import streamlit as st

pd_model = joblib.load("src/models/underwriting_model.pkl")

def prediction(Age, Cibil_Score, NFCF, Land_acres,Loan_amount_requested,Loan_tenure, LTV, existing_customer,Segment):

  new_customer = pd.DataFrame({
    "Age": [Age],
    "Cibil Score": [Cibil_Score],
    "NFCF": [NFCF],
    "Land acres": [Land_acres],
    "Loan amount requested": [Loan_amount_requested],
    "LTV": [LTV],
    "Loan_tenure(years)": [Loan_tenure],
    "Existing Customer":[existing_customer],
    "Segment": [Segment]
  })

  
  def assign_risk_grade(pd):
    if pd < 0.05:
      return "Very Low Risk"
    elif pd < 0.10:
      return "Low Risk"
    elif pd < 0.20:
      return "Moderate Risk"
    elif pd < 0.30:
      return "High Risk"
    else:
      return "Very High Risk"

  def assign_rate(pd):
    if pd < 0.05:
      return 0.135
    elif pd < 0.10:
      return 0.140
    elif pd < 0.20:
      return 0.145
    elif pd < 0.30:
      return 0.15
    else:
      return 0.155

  new_pd = pd_model.predict_proba(new_customer)[:, 1][0]
  risk_grade = assign_risk_grade(new_pd)
  rate = assign_rate(new_pd)
  AI = (new_customer["Loan amount requested"]*rate*(1 + rate)**new_customer["Loan_tenure(years)"]) / ((1 + rate)**new_customer["Loan_tenure(years)"]- 1)
  NFCF_AI=((new_customer["NFCF"])/AI)

   #Underwriting Decision
  def underwriting_decision(new_pd,NFCF_AI):
      if new_pd < 0.05 and float(NFCF_AI.iloc[0]) >= 1.5:
        st.balloons()
        st.success("✅ Application Approved — Excellent Financial Profile!")
        st.write("Interest Rate:", round(rate*100,2),"%")
        st.write("Annual Installment:", round(AI.iloc[0],2))
        return "APPROVED"

      elif new_pd < 0.30 and float(NFCF_AI.iloc[0]) >= 1.1:
        st.error("⏳ Credit Review — In progress.")
        return "REFER TO CREDIT"

      else:
        st.error("❌ Application Rejected — High Risk Detected.")
        st.snow()
        return "REJECTED"

  decision = underwriting_decision(new_pd,NFCF_AI)
  predicted_pd=new_pd * 100
  return predicted_pd, risk_grade, decision,rate
