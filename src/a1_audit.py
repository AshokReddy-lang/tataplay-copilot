#  Part - A -->> Audit the data 
import pandas as pd
subs=pd.read_csv("data/raw/subscribers.csv")
rech=pd.read_csv("data/raw/recharges.csv")

def column_report(df):
    return pd.DataFrame({
        "dtype":df.dtypes.astype(str),
        "missing":df.isna().sum(),
        "missing_pct":(df.isna().mean() * 100).round(2),
    })

print("*** subscribers.csv ***")
print("shape:", subs.shape)
print(column_report(subs))
age=pd.to_numeric(subs["age"],errors="coerce") # it return NaN when values are invalid.
print("rows:", len(subs))
print("duplictaed Rows:", subs.duplicated().sum())
print("distinct subscriber_id:", subs["subscriber_id"].nunique())
print("blank age:", subs["age"].isna().sum())
print("age values outside 10-100", ((age<10) | (age>100)).sum())
print("blank payment mode", subs["payment_mode"].isna().sum())
print("distinct raw city spellings:", subs["city"].nunique())
print("distinct raw auto_renew spellings:", subs["auto_renew"].nunique())
print("blank next_cycle_recharge_inr:", subs["next_cycle_recharge_inr"].isna().sum())

print("\n*** rechages.csv ***")
print("shape:",rech.shape)
print(column_report(rech))
amount=pd.to_numeric(rech["amount_inr"],errors="coerce")
print("rows:", len(rech))
print("exact duplicate rows:", rech.duplicated().sum())
print("distinct recharge_id", rech["recharge_id"].nunique())
print("amount_inr not a plain number:", amount.isna().sum())
print("distinct raw status spellings:", rech["status"].nunique())
print("rows with unknown subscriber_id:", (~rech["subscriber_id"].isin(subs["subscriber_id"])).sum())