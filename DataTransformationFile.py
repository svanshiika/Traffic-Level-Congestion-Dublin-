import pandas as pd
from pathlib import Path

# list of all months traffic files in csv format
files = [r"/Users/vanshikasharma/Downloads/SCATSJanuary2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSFebruary2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSMarch2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSApril2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSMay2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSJune2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSJuly2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSAugust2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSSeptember2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSOctober2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSNovember2023.csv",
         r"/Users/vanshikasharma/Downloads/SCATSDecember2023.csv"]

# columns we care about
columns_to_keep = [
    "End_Time",
    "Region",
    "Site",
    "Detector",
    "Sum_Volume",
    "Avg_Volume"
]

# Load the DCC file so we know which sites have names
dcc_path = r"/Users/vanshikasharma/Desktop/Advanced ML/dcc_traffic_signals_20221130.csv"
dcc = pd.read_csv(dcc_path, dtype=str)
dcc_sites = dcc["SiteID"].astype(str).str.strip().unique()

selected = []

for f in files:
    df = pd.read_csv(f)
    
    # keep only the relevant columns that exist
    available_cols = [c for c in columns_to_keep if c in df.columns]
    df = df[available_cols].copy()

    # Keep only NCITY + SCITY (normalize for safety)
    if "Region" in df.columns:
        df["Region"] = df["Region"].astype(str).str.strip().str.upper()
        df = df[df["Region"].isin(["NCITY", "SCITY"])]
        if df.empty:
            print(f"Skipping {Path(f).name}: no rows left after Region filter (NCITY/SCITY).")
            continue
    else:
        print(f"Skipping {Path(f).name}: no 'Region' column after column selection.")
        continue

    # standardize Site to string and trim, then keep only Sites that exist in the DCC file
    if "Site" in df.columns:
        df["Site"] = df["Site"].astype(str).str.strip()
        df = df[df["Site"].isin(dcc_sites)]
        if df.empty:
            print(f"Skipping {Path(f).name}: no rows left after DCC site filter.")
            continue
    else:
        # If there's no Site column, the filter can’t be applied; skip this file.
        print(f"Skipping {Path(f).name}: no 'Site' column after column selection.")
        continue

    #  No volume-based filtering. Just take the last 5000 rows as they appear.
    take = 5000 if len(df) >= 5000 else len(df)
    tail_df = df.tail(take).copy()

    print(f"{Path(f).name}: took last {take} rows after Region + DCC filters (from {len(df)} eligible).")
    selected.append(tail_df)

# Combine all months
if not selected:
    raise ValueError("No data selected. Check Region filter or DCC file and input CSVs.")

combined = pd.concat(selected, ignore_index=True)

# Save consolidated file
combined.to_csv("new_file.csv", index=False)
print(f"new_file.csv created with {len(combined)} rows.")

# --- Time enrichment ---
# Read back to ensure consistent types
df = pd.read_csv("new_file.csv", dtype={"End_Time": str})  

# Convert End_Time to datetime 
df['End_Time'] = pd.to_datetime(df['End_Time'], errors='coerce')

# Create useful time columns
df['Year'] = df['End_Time'].dt.year
df['Month'] = df['End_Time'].dt.month
df['Day'] = df['End_Time'].dt.day
df['Hour'] = df['End_Time'].dt.hour
df['Minute'] = df['End_Time'].dt.minute
df['Second'] = df['End_Time'].dt.second
df['DayOfWeek'] = df['End_Time'].dt.day_name()
df['ISO_Week'] = df['End_Time'].dt.isocalendar().week
df['Date'] = df['End_Time'].dt.date

# Ship time-enriched artifact
df.to_csv("file_one.csv", index=False)

print("New file created: file_one.csv")
print(df.head())

import pandas as pd

orignal_file = r'/Users/vanshikasharma/Desktop/Advanced ML/dcc_traffic_signals_20221130.csv'
working_file = r'/Users/vanshikasharma/Desktop/Advanced ML/file_one.csv'
new_file = r'working_file_with_street_names.csv'


#load datasets
dcc = pd.read_csv(orignal_file, dtype=str)
working = pd.read_csv(working_file, dtype=str)

# removing whitespaces
dcc["SiteID"] = dcc["SiteID"].str.strip()
working["Site"] = working["Site"].str.strip()

# renaming the columns in orignal street names files 
dcc = dcc.rename(columns={
        "SiteID": "Site",
        "Site_Description_Lower": "Description",
        "Lat": "Latitude",
        "Long": "Longitude"})

# merging files 
merged = working.merge(dcc[["Site", "Description", "Latitude", "Longitude"]], on="Site", how="left")


# Save new_file
merged.to_csv(new_file, index=False)

#confirming
print(f" File saved as {new_file}")
