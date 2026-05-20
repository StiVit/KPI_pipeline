import pandas as pd
import numpy as np

# The source of the data
master_df = pd.read_excel("data/KPI Navigator.xlsx", sheet_name="Export 22-25")
master_df["Sistema"] = master_df["Sistema"].str.strip()

df = pd.read_excel("data/Uso Navigator.xlsx", sheet_name="DB tot", header=2)
df.columns = df.columns.str.strip()

# Sort the df by date
df["Data"] = pd.to_datetime(df["Data"])

df = df.sort_values(by="Data").reset_index(drop=True).drop(columns = ["ID"])

source = master_df["RequestID"].to_list()

# Find the ITG that have been worked on using Navigator
present_ITGs = df[df["Numero ITG"].isin(source)]
present_ITGs["Numero ITG"] = present_ITGs["Numero ITG"].astype(int)
present_ITGs["Data"] = present_ITGs["Data"].dt.strftime("%Y-%m-%d")

# All the ITGs that are being worked on
master = master_df.groupby("Sistema")["RequestID"].nunique()
master.index.name = "Area"

# ITGs present
present = present_ITGs.groupby("Area")["Numero ITG"].unique()

# Starting to create the statistics
final_df = pd.DataFrame({
    "Master": master,
    "Present": present
}).fillna(0)

# Remove the Areas that are not being worked on using the Navigator
final_df = final_df[final_df['Present'].apply(lambda x: isinstance(x, (list, np.ndarray)))].copy()
final_df["Present"] = final_df["Present"].apply(len)

# Check the coverage of the ITGs based on all that are being worked on
final_df["Coverage"] = final_df["Present"] / final_df["Master"]

summary_metrics = []

# Do some measurements
for area, group in present_ITGs.groupby("Area"):
    summary_metrics.append({
        "Area": area,
        "Creatore": group["Creatore"].iloc[0],
        "total_time": group["Tempo (min)"].sum(),
        "avg_time_per_ITG": round(group["Tempo (min)"].mean(), 3),
        "avg_coverage": round(group["% copertura"].mean(), 3)
    })

metrics_df = pd.DataFrame(summary_metrics).set_index("Area")

# Combine all the data together
final_df = final_df.join(metrics_df)

final_df["Coverage"] = final_df["Coverage"].round(3)

# Create the other row
present_ITGs.index.name = "Area"

df_remaining = df.loc[~df.index.isin(present_ITGs.index)]

for col in ["Tempo (min)", "% copertura"]:
    df_remaining[col] = pd.to_numeric(df_remaining[col], errors="coerce")

other_row = {
    "Present": len(df_remaining),
    "total_time": df_remaining["Tempo (min)"].sum(),
    "avg_coverage": round(df_remaining["% copertura"].mean(), 3)
}

other_row["avg_time_per_ITG"] = round(other_row["total_time"] / other_row["Present"], 3)

areas_set = sorted(set(df_remaining["Area"]) - set(final_df.index))


other_row = pd.DataFrame([other_row])
other_row.index = [", ".join(areas_set)]
other_row.index.name = "Area"

final_df = pd.concat([final_df, other_row])

# Create the total row
total_row = {
    "Master": final_df["Master"].sum(),
    "Present": final_df["Present"].sum(),
    "Coverage": round(final_df["Coverage"].mean(), 3),
    "total_time": final_df["total_time"].sum(),
    "avg_time_per_ITG": round(final_df["avg_time_per_ITG"].mean(), 3),
    "avg_coverage": round(final_df["avg_coverage"].mean(), 3)
}

total_row = pd.DataFrame([total_row])
total_row.index = ["total"]
total_row.index.name = "Area"

final_df = pd.concat([final_df, total_row])

final_df = final_df.reset_index()
df.index.name = None

final_df.to_csv("res/area_summary.csv", index=False)