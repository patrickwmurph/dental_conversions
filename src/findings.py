import pandas as pd
from func.func import (
    xml_clean, 
    set_resid, 
    format_pid, 
    map_teeth, 
    map_surfaces, 
    map_provider, 
    map_findings, 
    instant_calc,
    map_dentition_tooth_status
)
from func.tables import (
    teeth_map, 
    surface_anterior_map, 
    surface_posterior_map, 
    anterior_anatomy_vel, 
    posterior_anatomy_vel, 
    provider_emp_map, 
    finding_type_map, 
    finding_comment_map, 
    finding_type_dentition_map,
    pid_to_chartnumber,
    chartnumber_to_soarian,
    pid_to_chartnumber_final
)

# xml_clean("data\DXE_Extract_Findings.csv","working_data/findings.csv")

findings = pd.read_csv("working_data/findings.csv", delimiter="|")

findings[findings["ChartNumber"].astype(str).isin(IDs)].value_counts("ChartNumber")


# Map Chart Number
## Map ChartNumber baed on PatientID
findings = map_chart_number(
    findings,
    pid_to_chartnumber_final,
    patient_id_col="PatientID",
    chart_number_col="ChartNumber"
)
## Map ChartNumber to Soarian Chart Number
# findings = map_chart_number(
#     findings,
#     chartnumber_to_soarian,
#     patient_id_col="ChartNumber",
#     chart_number_col="ChartNumber"
# )

# Initial Filtering
findings = findings[
    # findings["ChartNumber"].notna() &
    ~findings["ChartNumber"].astype(str).str.strip().str.contains("_", na=False)
    & (findings["UpdateUser"] != "TEST")
]

# RESID Populating
findings = set_resid(
    findings,
    "ChartNumber"
)

# Patient ID renaming
findings = format_pid(findings, "ChartNumber")

# Teeth Mapping
findings = map_teeth(
    findings,
    teeth_map,
    "AnatomyVEL",
    "ToothVEL"
)

# Surface Map
findings = map_surfaces(
    findings,
    "AnatomyVEL",
    "Surfaces",
    surface_anterior_map,
    surface_posterior_map,
    anterior_anatomy_vel,
    posterior_anatomy_vel
)

# Provider Map (EMP)
findings = map_provider(
    findings,
    provider_emp_map,
    "UpdateUser",
    "Update User",
    "49783"
)

# Map finding type and comment based on FindingType
findings = map_findings(
    findings,
    finding_type_map,
    finding_comment_map
)

# Calcuate Instant
findings = instant_calc(
    findings,
    "UpdateInstant",
    "Update Inst (UTC)"
)

## Pull NA findings into dentition and then filter NA Finding Types
dentition = findings[findings["Finding_Type"].isna()]
findings = findings[findings["Finding_Type"].notna()]

# Fix data types; #TODO if we ever keep NAs this conversion will not work
findings["Finding_Type"] = findings["Finding_Type"].astype(int)

# Clear Surfaces_Mapped if Finding_Type is 4,5,6,14
findings.loc[
    findings["Finding_Type"].isin([4, 5, 6, 14, 99]),
    "Surfaces_Mapped"
] = pd.NA


# Map Dentitions
dentition = map_dentition_tooth_status(
    dentition,
    finding_type_dentition_map
)

# Remove NAs
dentition = dentition[dentition["AnatomyVEL"].notna()]
# findings = findings[findings["AnatomyVEL"].notna()]

# CSV
findings.to_csv("findings_unformatted.csv", sep="|", index=False)
dentition.to_csv("dentition_unformatted.csv", sep="|", index=False)

#Findings File
findings_reformatted = findings.assign(
    **{
        "ID": findings["RESID"],
        "Patient ID": findings["ChartNumber"],
        "Tooth VEL": findings["ToothVEL"],
        "CSN for Perio": "",
        "Surfaces": findings["Surfaces_Mapped"],
        "PARL Override Name":"",
        "Finding Type": findings["Finding_Type"],
        "Associated Diagnosis": "",
        "Mblty Class": findings["MobilityClass"],
        "Caries Class": findings["CariesClass"],
        "Caries Depth": findings["CariesDepth"],
        "Caries Activity": "",
        "Caries Progression": "",
        "Status": "2",
        "Caries Incipiency": "",
        "BL/SUP Locations": findings["Bleeding/SuppurationLocation"],
        "Finding Cmt": findings["Finding_Comment"],
        "Furc Locations": "",
        "Furc Class": findings["FurcationClass"],
        "Update User": findings["Update User"],
        "Update Inst (UTC)": findings["Update Inst (UTC)"]
    }
)

findings_reformatted = findings_reformatted[
    [
        "ID",
        "Patient ID",
        "Tooth VEL",
        "CSN for Perio",
        "Surfaces",
        "PARL Override Name",
        "Finding Type",
        "Associated Diagnosis",
        "Mblty Class",
        "Caries Class",
        "Caries Depth",
        "Caries Activity",
        "Caries Progression",
        "Status",
        "Caries Incipiency",
        "BL/SUP Locations",
        "Finding Cmt",
        "Furc Locations",
        "Furc Class",
        "Update User",
        "Update Inst (UTC)"
    ]
]

# Dentition File
dentition_reformatted = dentition.assign(
    **{
        "ID": "*",
        "Patient ID": dentition["ChartNumber"],
        "Anatomy VEL": dentition["ToothVEL"],
        "Mouth Cmt": "",
        "Tooth Status": dentition["Tooth Status"],
        "Active Flag": "1", 
        "Update User": dentition["Update User"],
        "Update Inst (UTC)": dentition["Update Inst (UTC)"]
    }
)

dentition_reformatted = dentition_reformatted[
    [
        "ID",
        "Patient ID",
        "Anatomy VEL",
        "Mouth Cmt",
        "Tooth Status",
        "Active Flag",
        "Update User",
        "Update Inst (UTC)"
    ]
]

findings_reformatted.to_csv("findings_formatted.csv", sep="|", index=False)
dentition_reformatted.to_csv("dentition_formatted.csv", sep="|", index=False)