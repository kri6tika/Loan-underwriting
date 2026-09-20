import pandas as pd
import joblib

scaler2 = joblib.load("src/models/segmentation_scaler.pkl")
kmeans = joblib.load("src/models/kmeans_model.pkl")

def predict_segment(NFCF, land_acres, Loan_amount_requested, LTV, existing_customer):

    segment_input = pd.DataFrame({
        "NFCF": [NFCF],
        "Land acres": [land_acres],
        "Loan amount requested": [Loan_amount_requested],
        "LTV": [LTV],
        "Existing Customer": [existing_customer]
    })

  
    X_scaled = scaler2.transform(segment_input)

    # Use existing trained KMeans
    segment = kmeans.predict(X_scaled)[0]

    return segment
