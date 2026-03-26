import pandas as pd
import requests
import sqlite3
from flask import Flask, jsonify, request

# Dohvaćanje podataka
sp500 = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500")
cpi = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json={"seriesid": ["CUUR0000SA0"], "startyear": "2010", "endyear": "2019"}).json()
cpi_2 = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",json={"seriesid": ["CUUR0000SA0"], "startyear": "2020", "endyear": "2025"}).json()


# Pretvaranje CPI podataka iz JSON formata u tablicni oblik
records = []

for item in cpi["Results"]["series"][0]["data"]:
    if item["value"] != "-":
        records.append({
            "month": f"{item['year']}-{item['period'][1:]}",
            "cpi": float(item["value"])
    })

cpi_df = pd.DataFrame(records)

records_2 = []

for item in cpi_2["Results"]["series"][0]["data"]:
    if item["value"] != "-":
        records_2.append({
            "month": f"{item['year']}-{item['period'][1:]}",
            "cpi": float(item["value"])
        })

cpi_df_2 = pd.DataFrame(records_2)

cpi_df = pd.concat([cpi_df, cpi_df_2], ignore_index=True)
cpi_df = cpi_df.drop_duplicates("month").sort_values("month").reset_index(drop=True)


sp500["observation_date"] = pd.to_datetime(sp500["observation_date"])
sp500["SP500"] = pd.to_numeric(sp500["SP500"], errors="coerce")


sp500_monthly = (sp500.set_index("observation_date").resample("M").mean().reset_index())

sp500_monthly["month"] = sp500_monthly["observation_date"].dt.to_period("M").astype(str)
sp500_monthly = sp500_monthly[["month", "SP500"]]
sp500_monthly.rename(columns={"SP500": "sp500_avg"}, inplace=True)

merged = pd.merge(sp500_monthly, cpi_df, on="month", how="inner") # inner jer sadrzi samo mjesece koji postoje u oba skupa

# sort by time
merged = merged.sort_values("month").reset_index(drop=True)

# kreiranje konekcija sa sqlite bazom podataka
conn = sqlite3.connect("sp500_cpi.db")

# spremanje dataframe-a u bazu podataka
merged.to_sql(name = "sp500_cpi", con = conn, if_exists = "replace", index = False)

conn.close()

app = Flask(__name__)
DB_PATH = "sp500_cpi.db"

def query_db(query, args=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.route("/all_data", methods=["GET"])
def load_data():
    data = query_db("SELECT * FROM sp500_cpi")
    return jsonify(data)

@app.route("/all_data/<year>/<month>", methods=["GET"])
def load_data_month(year, month):
    month_request = f"{year}-{month.zfill(2)}"

    data = query_db(
        "SELECT * FROM sp500_cpi WHERE month = ?",
        (month_request,)
    )

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)


