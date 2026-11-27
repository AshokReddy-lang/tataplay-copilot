import os 
import sqlite3
import pandas as pd 

DB="data/tataplay.db"
subs=pd.read_csv("data/clean/subscribers.csv")
rech=pd.read_csv("data/clean/recharges.csv")
plans=pd.read_csv("data/clean/plans.csv")


#three tables
if os.path.exists(DB):
    os.remove(DB)
con=sqlite3.connect(DB)
subs.to_sql("subscribers",con,index=False)
rech.to_sql("recharges",con,index=False)
plans.to_sql("plans",con,index=False)
print(f"Wrote {DB}: tables subscribers, recharges, plans")

#reading the queries from sql/queries.sql
with open("sql/queries.sql") as f:
    queries=[q.strip() for q in f.read().split(";") if "SELECT" in q.upper() ]
#returning the four queries in dataframe format
q1,q2,q3,q4=[pd.read_sql_query(q,con) for q in queries]
con.close()


print("\n*** Revenue by Plan ***")
print(q1.to_string(index=False))

# checking the wheather the sql queries are correct or not using pandas
ok=rech[rech["status"]=="success"].merge(subs[["subscriber_id","plan_id"]],on="subscriber_id")
ok=ok.merge(plans[["plan_id","plan_name"]],on="plan_id")
prem=ok[ok["plan_name"]=="premium"]
print(f"pandas check (Premium): revenue {prem['amount_inr'].sum():,}, "
      f"avg {prem['amount_inr'].mean():.2f}, subscribers {prem['subscriber_id'].nunique()}")

print("\n*** Q2: subscribers who never successfully recharged ***")
print(f"{len(q2)} subscribers, of whom {(q2['tenure_months'] == 0).sum()} have tenure_months = 0")

print("\n*** Q3: ranking within a city ***")
summary = pd.DataFrame({
    "RANK()=1": q3[q3["rnk"] == 1].groupby("city").size(),
    "ROW_NUMBER()=1": q3[q3["row_num"] == 1].groupby("city").size(),
})
print(summary.to_string())
print("\nKolkata, first four rows:")
print(q3[q3["city"] == "Kolkata"].head(4).to_string(index=False))

print("\n*** Q4: running total for TP00010 ***")
print(q4.to_string(index=False))
