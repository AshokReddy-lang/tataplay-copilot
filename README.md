# Tata Play Subscriber Retention & Support Copilot

## Overview

This project is an internal tool for the Tata Play retention and support teams. It is built in four parts that feed into each other. Part A cleans the raw exports and stores them in a SQLite database. Part B predicts which subscribers will cancel next month. Part C groups subscribers into segments and ranks them by revenue at risk. Part D adds language-model tools for support tickets, policy questions and retention briefs.

All data is synthetic and is created by `generate_data.py`. Every language-model call goes through the offline `mock_llm.py`, so no API key or paid service is needed.

## Reproduce

1. `py -3.11 -m venv .venv`
2. `.venv\Scripts\activate` (on Mac/Linux: `source .venv/bin/activate`)
3. `pip install -r requirements.txt`
4. `python generate_data.py`
5. `python src/a1_audit.py`
6. `python src/a2_clean_subscribers.py`
7. `python src/a3_recharges.py`
8. `python src/a4_database_queries.py`

## Part A

The four scripts in `src/` (a1 to a4) audit the raw files, clean them, save the clean tables and build the database. The SQL lives in `sql/queries.sql` and is run from `a4_database_queries.py`.

Files produced: `data/clean/subscribers.csv`, `data/clean/recharges.csv`, `data/clean/plans.csv` and `data/tataplay.db`.

I used Python 3.11 with pandas 3.1.1 and numpy 2.4.6. The full list of versions is in `requirements.txt`.

### Audit of the raw files

**subscribers.csv** has 2,415 rows and 17 columns. Data type and missing values for each column:

- subscriber_id: str, 0 missing (0.00%)
- city: str, 0 missing (0.00%)
- plan_id: str, 0 missing (0.00%)
- tenure_months: int64, 0 missing (0.00%)
- age: float64, 99 missing (4.10%)
- payment_mode: str, 116 missing (4.80%)
- auto_renew: str, 0 missing (0.00%)
- add_on_count: int64, 0 missing (0.00%)
- monthly_recharge_inr: int64, 0 missing (0.00%)
- hours_watched_per_week: float64, 0 missing (0.00%)
- hd_hours_per_week: float64, 0 missing (0.00%)
- sports_hours_per_week: float64, 0 missing (0.00%)
- channels_watched: int64, 0 missing (0.00%)
- support_calls_90d: int64, 0 missing (0.00%)
- closure_request_logged: str, 0 missing (0.00%)
- next_cycle_recharge_inr: float64, 516 missing (21.37%)
- churned: int64, 0 missing (0.00%)

Problems found in subscribers.csv:

- 15 rows are exact duplicates, so there are only 2,400 distinct subscriber IDs.
- 99 ages are blank and 6 more are impossible (outside 10 to 100).
- 116 payment modes are blank.
- City is written in 22 different ways for only 7 real cities.
- auto_renew is written in 6 different ways (Yes, yes, Y, No, no, N).
- next_cycle_recharge_inr is blank for 516 rows. This is expected, because these are the subscribers who left.

**recharges.csv** has 13,055 rows and 6 columns. All six columns (recharge_id, subscriber_id, recharge_date, amount_inr, status, channel) are read as str and none has missing values (0.00%).

Problems found in recharges.csv:

- 60 rows are exact duplicates, leaving 12,995 distinct recharge IDs.
- 366 amounts are not plain numbers (they look like "INR 498").
- status is written in 6 different ways (success, Success, SUCCESS, failed, FAILED, pending).
- 10 rows belong to subscriber IDs that do not exist in subscribers.csv.

### Cleaning rules

Subscribers (`a2_clean_subscribers.py`):

1. Removed exact duplicate rows. 15 rows were removed and 2,400 remain.
2. Standardised city. I trimmed spaces, ignored case and mapped the old names (Bangalore to Bengaluru, Bombay to Mumbai, Madras to Chennai, Calcutta to Kolkata, New Delhi to Delhi, Hyd to Hyderabad). This changed 892 values and left exactly 7 cities.
3. Mapped auto_renew to Yes or No. This changed 695 values.
4. Turned every age outside 10 to 100 into a missing value. This affected 6 values.

Recharges (`a3_recharges.py`):

5. Removed exact duplicate rows. 60 rows were removed and 12,995 remain.
6. Removed rows whose subscriber does not exist. 10 rows were removed and 12,985 remain.
7. Lower-cased status. This changed 5,099 values.
8. Converted amount_inr to numbers. Where it could not be converted, I rebuilt it from that subscriber's monthly_recharge_inr. 364 amounts were rebuilt. (The audit found 366, but 2 of them were in rows already removed by rules 5 and 6.)
9. Parsed recharge_date as a date. All 12,985 dates parsed, from 2025-10-01 to 2026-03-28.

Plans: copied unchanged.

**No missing values were filled in Part A.** After cleaning, 104 ages and 114 payment modes are still blank, and I left them that way on purpose. Filling them belongs inside the Part B pipeline, after the train/test split. If I filled them here using the whole dataset, information from the test rows would leak into training.

### Results after cleaning

Subscribers per city: Mumbai 524, Delhi 436, Chennai 391, Bengaluru 386, Hyderabad 262, Pune 245, Kolkata 156.

- auto_renew: 1,355 No and 1,045 Yes.
- Still missing: 104 ages and 114 payment modes.
- 514 subscribers churned, which is 21.42% of 2,400.
- Recharge status: 11,442 success, 1,422 failed, 121 pending.
- Total amount from successful recharges: INR 6,457,573.

### SQL queries

The four queries are in `sql/queries.sql`. They run on `data/tataplay.db` and use only successful recharges.

**Q1: Revenue by plan** (total revenue in INR / average recharge in INR / number of subscribers)

1. Premium: 1,471,199 / 860.35 / 339
2. Standard: 1,323,622 / 492.60 / 559
3. Standard HD: 1,283,471 / 645.61 / 407
4. Premium Plus: 1,262,398 / 1,075.30 / 228
5. Basic: 782,554 / 326.61 / 493
6. Basic Lite: 334,329 / 224.83 / 298

I checked the Premium row with a pandas groupby and got the same answer: revenue 1,471,199, average 860.35 and 339 subscribers.

**Q2: Subscribers who never had a successful recharge**

76 subscribers have no successful recharge, and 68 of them have tenure_months = 0 (they joined too recently to have paid yet).

An INNER JOIN only returns subscribers who have at least one matching successful recharge, so these 76 would simply disappear from the result without any error or warning. A LEFT JOIN keeps every subscriber and puts NULL where there is no recharge, which is how the query can find them with `IS NULL`.

**Q3: Ranking within each city**

Number of subscribers with RANK() = 1 in each city: Bengaluru 10, Chennai 10, Delhi 5, Hyderabad 5, Kolkata 2, Mumbai 6, Pune 4. ROW_NUMBER() = 1 always gives exactly one subscriber per city.

The first four rows for Kolkata (total INR; RANK / DENSE_RANK / ROW_NUMBER):

- TP00074: 6,876; 1 / 1 / 1
- TP00917: 6,876; 1 / 1 / 2
- TP00143: 6,582; 3 / 2 / 3
- TP01355: 6,582; 3 / 2 / 4

For "the top spender per city" I would use RANK() = 1. It keeps everyone who is tied for the highest total, and because it skips numbers after a tie, a "top N" list never has more than N places. ROW_NUMBER() would drop one of two tied top spenders (TP00917 in Kolkata, for example), and DENSE_RANK() does not skip numbers, so its "top N" lists would include extra people.

**Q4: Running total for TP00010**

TP00010 has 5 successful recharges of INR 498 each:

- R000053 on 2025-10-15: running total 498
- R000055 on 2025-12-15: running total 996
- R000056 on 2026-01-15: running total 1,494
- R000057 on 2026-02-15: running total 1,992
- R000058 on 2026-03-13: running total 2,490

The running total ends at INR 2,490.

## Part B

## Part C

## Part D

## Limitations and Next Steps
