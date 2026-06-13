import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
from datetime import datetime

# ----------------------------
# FILES
# ----------------------------
TRACT_FILE = "CensusTractList2026.xlsx"
FLAT_FILE = "CensusFlatFile2025.csv"
DISTRESSED_FILE = "2025DistressedorUnderservedTracts.xls"

LOG_FILE = "lookup_log.csv"

# ----------------------------
# ADDRESS CLEANING
# ----------------------------
def clean_address(addr):
    addr = addr.upper().strip()
    addr = addr.replace(",", "")
    addr = re.sub(r"\s+", " ", addr)
    return addr


# ----------------------------
# LOAD DATA
# ----------------------------
def load_all_data():
    global tract_df, flat_df, distressed_set

    tract_df = pd.ExcelFile(TRACT_FILE).parse(sheet_name=1, dtype=str)
    tract_df.columns = [c.upper().strip() for c in tract_df.columns]

    tract_df["TRACT_ID"] = (
        tract_df["STATE CODE"].str.zfill(2) +
        tract_df["COUNTY CODE"].str.zfill(3) +
        tract_df["TRACT"].str.replace(".", "", regex=False).str.zfill(6)
    )

    flat_raw = pd.read_csv(FLAT_FILE, header=None, low_memory=False)

    flat_df = pd.DataFrame({
        "TRACT_ID":
            flat_raw[2].astype(str).str.zfill(2) +
            flat_raw[3].astype(str).str.zfill(3) +
            flat_raw[4].astype(str).str.zfill(6),
        "MFI_PCT": flat_raw[12],
        "INCOME_LEVEL": flat_raw[14]
    })

    try:
        df = pd.read_excel(DISTRESSED_FILE, dtype=str)
        df = df[df.iloc[:, -3].astype(str).str.isnumeric()]

        distressed_set = set(
            df.iloc[:, -3].str.zfill(2) +
            df.iloc[:, -2].str.zfill(3) +
            df.iloc[:, -1].str.replace(".", "", regex=False).str.zfill(6)
        )
    except:
        distressed_set = set()


# ----------------------------
# LOGGING
# ----------------------------
def log_lookup(address, tract, method):
    row = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "address": address,
        "tract": tract,
        "method": method
    }])

    row.to_csv(LOG_FILE, mode="a",
               header=not pd.io.common.file_exists(LOG_FILE),
               index=False)


# ----------------------------
# GEOCODING ENGINE
# ----------------------------
def get_tract(address):

    def census(addr):
        try:
            r = requests.get(
                "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress",
                params={
                    "address": addr,
                    "benchmark": "Public_AR_Current",
                    "vintage": "Current_Current",
                    "format": "json"
                },
                timeout=5
            )
            matches = r.json()["result"]["addressMatches"]
            if matches:
                geo = matches[0]["geographies"]["Census Tracts"][0]
                return geo["STATE"] + geo["COUNTY"] + geo["TRACT"], "Exact", 100
        except:
            pass
        return None, None, 0

    # 1️⃣ exact
    tract, method, score = census(address)
    if tract:
        return tract, method, score

    # 2️⃣ simple
    simple = address.split(",")[0]
    tract, method, score = census(simple)
    if tract:
        return tract, "Adjusted Address", 90

    # 3️⃣ nearby numbers
    parts = simple.split()
    for i, p in enumerate(parts):
        if p.isdigit():
            base = int(p)
            for offset in [-10, -5, -2, 2, 5, 10]:
                parts[i] = str(base + offset)
                t, _, _ = census(" ".join(parts))
                if t:
                    return t, "Nearby Address Match", 80
            break

    # 4️⃣ ZIP fallback
    zip_match = re.search(r"\b\d{5}\b", address)
    if zip_match:
        zip_code = zip_match.group()
        try:
            r = requests.get(f"https://api.zippopotam.us/us/{zip_code}")
            place = r.json()["places"][0]
            fallback = f"{place['place name']} {place['state abbreviation']}"
            t, _, _ = census(fallback)
            if t:
                return t, "ZIP Approximation", 60
        except:
            pass

    # 5️⃣ County fallback (Big Lake)
    if "BIG LAKE" in address or "55309" in address:
        match = tract_df[tract_df["TRACT_ID"].str.startswith("27141")]
        if not match.empty:
            return match.iloc[0]["TRACT_ID"], "County Approximation", 40

    return None, None, 0


# ----------------------------
# LOOKUP DATA
# ----------------------------
def lookup_data(tract):

    row = tract_df[tract_df["TRACT_ID"] == tract]
    if not row.empty:
        r = row.iloc[0]
        return {
            "income": r.get("TRACT INCOME LEVEL", "N/A"),
            "mfi": r.get("TRACT INCOME PERCENTAGE", "N/A")
        }

    row2 = flat_df[flat_df["TRACT_ID"] == tract]
    if not row2.empty:
        r = row2.iloc[0]
        return {
            "income": r.get("INCOME_LEVEL"),
            "mfi": r.get("MFI_PCT")
        }

    return None


# ----------------------------
# MASTER LOOKUP
# ----------------------------
def lookup(addr):

    addr = clean_address(addr)

    tract, method, score = get_tract(addr)

    if not tract:
        return {"error": "Unable to determine tract"}

    data = lookup_data(tract)

    if not data:
        return {"error": "Tract found but no data"}

    log_lookup(addr, tract, method)

    return {
        "tract": tract,
        "income": data["income"],
        "mfi": data["mfi"],
        "distressed": "Yes" if tract in distressed_set else "No",
        "method": method,
        "confidence": score
    }


# ----------------------------
# EXCEL FORMATTER (COLOR)
# ----------------------------
def style_excel(df):

    def color(val):
        if val in [1, "1"]:
            return "background-color: lightblue"
        elif val in [2, "2"]:
            return "background-color: lightgreen"
        elif val in [3, "3"]:
            return "background-color: orange"
        elif val in [4, "4"]:
            return "background-color: red"
        return ""

    return df.style.applymap(color, subset=["Income"])


# ----------------------------
# UI FUNCTIONS
# ----------------------------
def run_lookup():
    addr = entry.get()
    result = lookup(addr)

    output.delete(1.0, tk.END)

    if "error" in result:
        output.insert(tk.END, result["error"])
        return

    warn = ""
    if result["confidence"] < 100:
        warn = "\n⚠️ Approximate result — verify with FFIEC Geomap if needed.\n"

    output.insert(tk.END, f"""
Address: {addr}
Tract: {result['tract']}

Income Level: {result['income']}
MFI %: {result['mfi']}
Distressed: {result['distressed']}

Method: {result['method']}
Confidence: {result['confidence']}%
{warn}
""")


def run_batch():
    file = filedialog.askopenfilename()
    df = pd.read_excel(file)

    results = []

    for addr in df["Address"]:
        r = lookup(addr)

        results.append({
            "Address": addr,
            "Tract": r.get("tract"),
            "Income": r.get("income"),
            "MFI %": r.get("mfi"),
            "Confidence": r.get("confidence"),
            "Method": r.get("method")
        })

    out = file.replace(".xlsx", "_out.xlsx")
    styled = style_excel(pd.DataFrame(results))
    styled.to_excel(out, index=False)

    messagebox.showinfo("Done", f"Saved: {out}")


# ----------------------------
# GUI
# ----------------------------
root = tk.Tk()
root.title("FFIEC Tool V3 — Enhanced")
root.geometry("850x650")

entry = tk.Entry(root, width=70)
entry.pack()

tk.Button(root, text="Lookup", command=run_lookup).pack()
tk.Button(root, text="Batch Process Excel", command=run_batch).pack()

output = scrolledtext.ScrolledText(root, width=100, height=30)
output.pack()

# ----------------------------
# START
# ----------------------------
load_all_data()
root.mainloop()
