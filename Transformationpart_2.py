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