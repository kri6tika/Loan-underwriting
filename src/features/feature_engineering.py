import pandas as pd

def calculate_features(
    State,
    District,
    Crop,
    Land_acres,
    Other_Documented_Income,
    Obligation,
    Loan_amount_requested,
    Loan_tenure,
    Manufacturer,
    Vehicle_Model,
    Existing_customer
):
   print("State:", State)
   print("District:", District)
   print("Crop:", Crop)
   df = pd.read_csv("/workspaces/Loan-underwriting/data/raw/Customer_Data.csv")

#Joining Customer data with Crop Income table 
   crop_income_df = pd.read_csv(
    "/workspaces/Loan-underwriting/data/raw/Crop_Income.csv"
)

   df = df.merge(
    crop_income_df,
    on=["State", "District", "Crop"],
    how="left"
)

   crop_concat = crop_income_df[
        (crop_income_df["State"] == State) &
        (crop_income_df["District"] == District) &
        (crop_income_df["Crop"] == Crop)
    ]

   if crop_concat.empty or Land_acres is None or crop_concat["Productivity(quintal/acre)"].iloc[0] is None or crop_concat["Rate(Rs/quintal)"].iloc[0] is None:
     crop_income = 0

   else:
     crop_income =  Land_acres*crop_concat["Productivity(quintal/acre)"].iloc[0]*crop_concat["Rate(Rs/quintal)"].iloc[0]*2
 

#Joining Customer data with Model cost table 
   assetcost_df = pd.read_csv(
    "/workspaces/Loan-underwriting/data/raw/Model_cost.csv"
)

   df = df.merge(
    assetcost_df,
    on=["Manufacturer", "Vehicle_Model"],
    how="left"
)

   Total_Income = (
    crop_income+
    Other_Documented_Income
   )

   NFCF = Total_Income-Obligation

   Manuf_model_concat = assetcost_df[
           (assetcost_df["Manufacturer"] == Manufacturer) &
           (assetcost_df["Vehicle_Model"] == Vehicle_Model)
       ]
   
   if Manuf_model_concat.empty:
           raise ValueError(
               f"No Dealer Price found for "
               f"{Manufacturer} - {Vehicle_Model}")    

   Net_Dealer_Price =  Manuf_model_concat["Net Dealer Price"].iloc[0]
   LTV= Loan_amount_requested/Net_Dealer_Price
   Existing_cust = {"Yes": 1, "No": 0}.get(Existing_customer, 0)

   return {
        "Crop_Income": crop_income,
        "Total_Income": Total_Income,
        "Net_Dealer_Price": Net_Dealer_Price,
        "LTV": LTV,
        "NFCF": NFCF,
        "Existing Customer": Existing_cust
    }