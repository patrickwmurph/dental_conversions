import pandas as pd
import numpy as np
from datetime import datetime
from func.func import (
    set_resid, 
    format_pid, 
    map_teeth, 
    map_provider, 
    map_perio_loc, 
    instant_calc, 
    quad_category_column,
    consolidate_periodontal_rows,
    map_chart_number
)

from func.tables import (
    teeth_map, 
    provider_emp_map, 
    provider_ser_map, 
    right_perio_map,
    left_perio_map,
    pid_to_chartnumber,
    chartnumber_to_soarian,
    pid_to_chartnumber_final
)

# Load df
periodontal = pd.read_csv("data\DXE_Extract_PerioCharting.csv", delimiter="|", dtype={"PatientID": "string"})

# Map Chart Number and create chartnumber column
periodontal["ChartNumber"] = periodontal["PatientID"].astype(str)
periodontal[periodontal["ChartNumber"].astype(str).isin(IDs)].value_counts("ChartNumber")

## Map ChartNumber based on PatientID
periodontal = map_chart_number(
    periodontal,
    pid_to_chartnumber_final,
    patient_id_col="PatientID",
    chart_number_col="ChartNumber"
)

periodontal = map_chart_number(
    periodontal,
    chartnumber_to_soarian,
    patient_id_col="ChartNumber",
    chart_number_col="ChartNumber"
)

# Initial Filtering
periodontal = periodontal[
    # periodontal["ChartNumber"].notna() &
    ~periodontal["ChartNumber"].astype(str).str.strip().str.contains("_", na=False)
    & (periodontal["UpdateUser"] != "TEST")
    & (periodontal["EncProvider"] != "TEST")
]

# RESID Populating
periodontal = set_resid(
    periodontal,
    "ChartNumber"
)

# Patient ID renaming
periodontal = format_pid(periodontal, "ChartNumber")

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
# periodontal = map_perio_loc(periodontal, perio_map)

# Add Quad Category to Perio
periodontal = quad_category_column(
    periodontal, 
    "AnatomyVEL",
    target_column="Quad_Category" 
)

# Map perio location based on quadrant
periodontal = map_perio_loc(periodontal, right_perio_map, quadrants=["UR","LR"] )
periodontal = map_perio_loc(periodontal, left_perio_map, quadrants=["UL","LL"])

# Update Instant
periodontal = instant_calc(
    periodontal,
    "UpdateInstant(UTC)",
    "Update Inst (UTC)"
)

# Set DentalGingivalMargin and DentalClinicalAttachmentLevel 0s to null
periodontal["DentalProbingDepth"] = periodontal["DentalProbingDepth"].astype(str)
#TODO If probing depth is 0 then remove the row

# periodontal["DentalGingivalMargin"] = periodontal["DentalGingivalMargin"].astype(str)
# periodontal["DentalClinicalAttachmentLevel"] = periodontal["DentalClinicalAttachmentLevel"].astype(str)

# periodontal.loc[
#     periodontal["DentalGingivalMargin"] == "0",
#     "DentalGingivalMargin"
# ] = pd.NA

# periodontal.loc[
#     periodontal["DentalClinicalAttachmentLevel"] == "0",
#     "DentalClinicalAttachmentLevel"
# ] = pd.NA

periodontal.loc[
    periodontal["DentalProbingDepth"] == "0",
    "DentalProbingDepth"
] = pd.NA

periodontal[periodontal["ChartNumber"] == "10014531"]

periodontal = periodontal[periodontal["DentalProbingDepth"].notna()]

periodontal.to_csv("periodontal_unformatted.csv", sep="|", index=False)

reformatted_periodontal = periodontal.assign(
    **{
        "ID": periodontal["RESID"],
        "Patient ID": periodontal["ChartNumber"],
        "Tooth VEL": periodontal["ToothVEL"],
        "Perio CSN Identifier": "G^1",
        "Dental:Probing Depth": periodontal["DentalProbingDepth"],
        "Dental:Gingival Margin": "",
        "Dental:Perio Location": periodontal["Dental:Perio Location"],
        "Dental:Clinical Attachment Level": "",
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

reformatted_periodontal = consolidate_periodontal_rows(
    reformatted_periodontal
)

reformatted_periodontal[
    reformatted_periodontal["Dental:Probing Depth"]
        .astype(str)
        .str.count("\n")
    !=
    reformatted_periodontal["Dental:Perio Location"]
        .astype(str)
        .str.count("\n")
]


reformatted_periodontal[reformatted_periodontal["Patient ID"].isin(IDs)]


reformatted_periodontal.to_csv("periodontal_formatted.csv", sep = "|", index=False)
# periodontal_dfs = np.array_split(reformatted_periodontal, 3)

# # Export each chunk
# for i, df_chunk in enumerate(periodontal_dfs, start=1):
#     df_chunk.to_csv(f"periodontal_formatted_part{i}.csv", sep="|", index=False)