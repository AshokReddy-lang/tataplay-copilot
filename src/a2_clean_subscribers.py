# cleaning the Subscribers.csv
import os 
import pandas as pd 

os.makedirs("data/clean",exist_ok=True)
subs=pd.read_csv("data/raw/subscribers.csv")

#removing the duplicates

#after removing the duplicates copy the updated dataframe to the subscribers.csv to itself.
subs=subs.drop_duplicates().copy()
print("After Removing duplicates:", len(subs))

#Stanadardizing the city column
CITY_MAP={
    "mumbai": "Mumbai", "bombay": "Mumbai",
    "delhi": "Delhi", "new delhi": "Delhi",
    "bengaluru": "Bengaluru", "bangalore": "Bengaluru",
    "chennai": "Chennai", "madras": "Chennai",
    "hyderabad": "Hyderabad", "hyd": "Hyderabad",
    "pune": "Pune",
    "kolkata": "Kolkata", "calcutta": "Kolkata",
}

new_city=subs['city'].str.strip().str.lower().map(CITY_MAP)
assert new_city.notna().all()
print(f"city values changed: {(subs['city'] != new_city).sum()}")
subs["city"]=new_city

# auto_renew Yes/no
AUTO_MAP= {"yes": "Yes", "y": "Yes", "no": "No", "n": "No"}

new_auto=subs["auto_renew"].str.strip().str.lower().map(AUTO_MAP)
assert new_auto.notna().all()
print(f"auto_renew_changed: {(subs['auto_renew']!=new_auto).sum()}")
subs["auto_renew"]=new_auto

#age outside 10-100
subs["age"]=pd.to_numeric(subs["age"],errors="coerce")
bad_age = (subs["age"] < 10) | (subs["age"] > 100)
subs.loc[bad_age,"age"]=pd.NA
subs["age"]=subs["age"].astype("Int64")

#results 
print("\nCity counts:")
print(subs["city"].value_counts().to_string())
print("\nauto_renew counts:")
print(subs["auto_renew"].value_counts().to_string())
print("\nmissing age:", subs["age"].isna().sum())
print("bad ages -> missing:", bad_age.sum())
print("missing payment mode:", subs["payment_mode"].isnull().sum())
churn=subs["churned"].sum()
print(f"churned : {churn} ({churn / len(subs) * 100:.2f}%)")

#save
subs.to_csv("data/clean/subscribers.csv",index=False)# it does not give index for the dataframe's rows
pd.read_csv("data/raw/plans.csv").to_csv("data/clean/plans.csv",index=False)
print("\nSaved data/clean/subscribers.csv and data/clean/plans.csv")










