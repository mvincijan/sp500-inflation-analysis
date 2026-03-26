import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("sp500_cpi.db")
merged = pd.read_sql("SELECT * FROM sp500_cpi", conn)
conn.close()

print("Broj zapisa:", len(merged))
print("Raspon:", merged["month"].min(), "->", merged["month"].max())

print(merged[["sp500_avg", "cpi"]].describe())
 
merged["month_dt"] = pd.to_datetime(merged["month"])

plt.figure()
plt.plot(merged["month_dt"], merged["sp500_avg"])
plt.xlabel("Vrijeme")
plt.ylabel("S&P 500 (mjesečni prosjek)")
plt.title("Kretanje S&P 500 indeksa")
plt.show()

plt.figure()
plt.plot(merged["month_dt"], merged["cpi"])
plt.xlabel("Vrijeme")
plt.ylabel("CPI")
plt.title("Kretanje indeksa potrošačkih cijena (CPI)")
plt.show()

plt.figure()
plt.scatter(merged["sp500_avg"], merged["cpi"])
plt.xlabel("S&P 500 (mjesečni prosjek)")
plt.ylabel("CPI")
plt.title("Odnos S&P 500 indeksa i inflacije (CPI)")
plt.show()
