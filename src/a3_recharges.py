#cleaning the recharges.csv

import pandas as pd

rech=pd.read_csv("data/raw/recharges.csv")
subs = pd.read_csv("data/clean/subscribers.csv")



#removing the duplicates

#after removing the duplicates copy the updated dataframe to the subscribers.csv to itself.
rech=rech.drop_duplicates().copy()
print("After Removing duplicates:", len(rech))

#remove the rows whose subscriber doesn't exist
before=len(rech)
rech=rech[rech["subscriber_id"].isin(subs["subscriber_id"])].copy()
print(f"unknown subscribers:{before - len(rech)}  ->  {len(rech)} rows remain")


#change status to lower_case
new_status=rech["status"].str.strip().str.lower()
print(f"status values changed: {(rech['status']!=new_status).sum()}")
rech["status"]=new_status


#amount INR to  numbers like "INR 299" -->> 299
amount=pd.to_numeric(rech["amount_inr"],errors="coerce")
bad=amount.isna()
monthly = rech["subscriber_id"].map(subs.set_index("subscriber_id")["monthly_recharge_inr"])
rech["amount_inr"]=amount.where(~bad,monthly).astype(int)
print(f"amount rebuilt:  {bad.sum()}")

#recharge_data as date\
rech["recharge_date"]=pd.to_datetime(rech["recharge_date"],format="%Y-%m-%d")
print(f"dates parsed:  {len(rech)}"
      f"({rech['recharge_date'].min().date()} to {rech['recharge_date'].max().date()})")


print("\nStatus counts:")
print(rech["status"].value_counts().to_string())
total = rech.loc[rech["status"] == "success", "amount_inr"].sum()
print(f"\nTotal successful recharge amount: INR {total:,}")


#save
rech.to_csv("data/clean/recharges.csv", index=False, date_format="%Y-%m-%d")
print("\nSaved data/clean/recharges.csv")


