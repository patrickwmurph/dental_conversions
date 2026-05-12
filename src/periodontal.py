import pandas as pd
import numpy as np
from datetime import datetime
from func.func import set_resid, format_pid, map_teeth, map_provider, map_perio_loc, instant_calc
from func.tables import teeth_map, provider_emp_map, provider_ser_map, perio_map

# Load df
periodontal = pd.read_csv("data\DXE_Extract_PerioCharting.csv", delimiter="|")

# Initial Filtering
periodontal = periodontal[
    periodontal["PatientID"].notna()
    & ~periodontal["PatientID"].astype(str).str.strip().str.contains("_", na=False)
    & (periodontal["UpdateUser"] != "TEST")
    & (periodontal["EncProvider"] != "TEST")
]


# RESID Populating
periodontal = set_resid(
    periodontal,
    "PatientID"
)

# Patient ID renaming
periodontal = format_pid(periodontal, "PatientID")

# Teeth Mapping
periodontal = map_teeth(
    periodontal,
    teeth_map,
    "AnatomyVEL",
    "ToothVEL"
)

# Provider Map (EMP)
periodontal = map_provider(
    periodontal,
    provider_emp_map,
    "UpdateUser",
    "Update User",
    "49783"
)

# Provider Map (SER)
periodontal = map_provider(
    periodontal,
    provider_ser_map,
    "EncProvider",
    "Enc Provider",
    "E1012"
)

# Perio Location Mapping
periodontal = map_perio_loc(periodontal, perio_map)

# Update Instant
periodontal = instant_calc(
    periodontal,
    "UpdateInstant(UTC)",
    "Update Inst (UTC)"
)

# Set DentalGingivalMargin and DentalClinicalAttachmentLevel 0s to null
periodontal["DentalGingivalMargin"] = periodontal["DentalGingivalMargin"].astype(str)
periodontal["DentalClinicalAttachmentLevel"] = periodontal["DentalClinicalAttachmentLevel"].astype(str)
periodontal["DentalProbingDepth"] = periodontal["DentalProbingDepth"].astype(str)

periodontal.loc[
    periodontal["DentalGingivalMargin"] == "0",
    "DentalGingivalMargin"
] = pd.NA

periodontal.loc[
    periodontal["DentalClinicalAttachmentLevel"] == "0",
    "DentalClinicalAttachmentLevel"
] = pd.NA

periodontal.loc[
    periodontal["DentalProbingDepth"] == "0",
    "DentalProbingDepth"
] = pd.NA

periodontal.to_csv("periodontal_unformatted.csv", sep="|", index=False)

reformatted_periodontal = periodontal.assign(
    **{
        "ID": periodontal["RESID"],
        "Patient ID": periodontal["PatientID"],
        "Tooth VEL": periodontal["ToothVEL"],
        "Perio CSN Identifier": "G^1",
        "Dental:Probing Depth": periodontal["DentalProbingDepth"],
        "Dental:Gingival Margin": periodontal["DentalGingivalMargin"],
        "Dental:Perio Location": periodontal["Dental:Perio Location"],
        "Dental:Clinical Attachment Level": periodontal["DentalClinicalAttachmentLevel"],
        "Update User": periodontal["Update User"],
        "Update Inst (UTC)": periodontal["Update Inst (UTC)"],
        "Enc Dep": "490",
        "Enc Prov": periodontal["Enc Provider"],
        "Enc Date": datetime.today().strftime("%m/%d/%Y")
    }
)

reformatted_periodontal = reformatted_periodontal[
    [
        "ID",
        "Patient ID",
        "Tooth VEL",
        "Perio CSN Identifier", 
        "Dental:Probing Depth",
        "Dental:Gingival Margin", 
        "Dental:Perio Location",
        "Dental:Clinical Attachment Level", 
        "Update User",
        "Update Inst (UTC)",
        "Enc Dep",
        "Enc Prov",
        "Enc Date"
    ]
]

# reformatted_periodontal.to_csv("periodontal_formatted.csv", sep = "|", index=False)

periodontal_dfs = np.array_split(reformatted_periodontal, 3)

# Export each chunk
for i, df_chunk in enumerate(periodontal_dfs, start=1):
    df_chunk.to_csv(f"periodontal_formatted_part{i}.csv", sep="|", index=False)