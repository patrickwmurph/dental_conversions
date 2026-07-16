import pandas as pd
from datetime import datetime
import numpy as np
from func.tables import (
    # procedure mappings
    procedure_map,
    max_arch_proc,
    man_arch_proc,
    quad_proc,

    # anatomy mappings
    teeth_map,
    surface_anterior_map,
    surface_posterior_map,
    anterior_anatomy_vel,
    posterior_anatomy_vel,

    # provider mappings
    provider_emp_map,
    provider_ser_map,

    # oral cavity mappings
    arch_map,
    quad_map,
    whole_mouth_codes,
    
    pid_to_chartnumber,
    chartnumber_to_soarian,
    pid_to_chartnumber_final
)


from func.func import (
    xml_clean2, 
    format_pid, 
    set_resid, 
    map_teeth, 
    map_surfaces, 
    map_provider, 
    map_procedure, 
    format_procedure, 
    consolidate_partial_dentures, 
    consolidate_partial_dentures2,
    create_area_of_oral_cavity, 
    quad_category_column, 
    instant_calc, 
    filter_full_mouth_codes,
    pip_count_cleaning,
    map_chart_number
)

# pip_count_cleaning("data\DXE_Extract_ExistingTreatment.csv", "working_data/existing_treatments.csv")

# OLD xml_clean2("data\DXE_Extract_ExistingTreatment.csv", "working_data/existing_treatments.csv")

# Clean XML
existing_treatments = pd.read_csv("working_data/existing_treatments.csv", delimiter="|")
existing_treatments = existing_treatments.shift(axis=1).reset_index()

existing_treatments[existing_treatments["ChartNumber"].astype(str).isin(IDs)].value_counts("ChartNumber")

# Map Chart Number
## Map ChartNumber baed on PatientID
existing_treatments = map_chart_number(
    existing_treatments,
    pid_to_chartnumber_final,
    patient_id_col="PatientID",
    chart_number_col="ChartNumber"
)

## Map ChartNumber to Soarian Chart Number
# existing_treatments = map_chart_number(
#     existing_treatments,
#     chartnumber_to_soarian,
#     patient_id_col="ChartNumber",
#     chart_number_col="ChartNumber"
# )


# Initial Filtering
existing_treatments = existing_treatments[
    # existing_treatments["ChartNumber"].notna() &
    ~existing_treatments["ChartNumber"].astype(str).str.strip().str.contains("_", na=False)
    & (existing_treatments["Provider"] != "TEST")
    & (existing_treatments["UpdateUser"] != "TEST")
]

# RESID Populating
existing_treatments = set_resid(
    existing_treatments,
    "ChartNumber"
)

# Patient ID renaming
existing_treatments = format_pid(existing_treatments, "ChartNumber")

# Teeth Mapping
existing_treatments = map_teeth(
    existing_treatments,
    teeth_map,
    "AnatomyVEL",
    "ToothVEL"
)

# Area of Oral Cavity Column Creation
existing_treatments = create_area_of_oral_cavity(
    existing_treatments,
    arch_map,
    quad_map,
    whole_mouth_codes,
    procedure_column="Procedure",
    arch_column = "Arch",
    quadrant_column="Quadrant",
    target_column="AreaofOralCavity"
)

# Area of Oral Cavity 0s
existing_treatments = filter_full_mouth_codes(
    existing_treatments,
    "AreaofOralCavity",
    "Procedure",
    whole_mouth_codes
)

# Quad Mapping Column
existing_treatments = quad_category_column(
    existing_treatments,
    "AnatomyVEL",
    "Quad_Category"
)

# Surface Map
existing_treatments = map_surfaces(
    existing_treatments,
    "AnatomyVEL",
    "Surfaces",
    surface_anterior_map,
    surface_posterior_map,
    anterior_anatomy_vel,
    posterior_anatomy_vel
)

surfaces_test = existing_treatments[existing_treatments["Surfaces"].notna()][["Surfaces","Surfaces_Mapped"]]


# Provider Map (EMP)
existing_treatments = map_provider(
    existing_treatments,
    provider_emp_map,
    "UpdateUser",
    "Update User",
    "49783"
)

# Provider Map (SER)
existing_treatments = map_provider(
    existing_treatments,
    provider_ser_map,
    "Provider",
    "Provider_Mapped",
    "E1012"
)

# Procedure Map
existing_treatments = map_procedure(
    existing_treatments,
    procedure_map,
    fallback_value="WIS81",
    comments_column="Comments",
    filter_fallback=False
)

# Format Procedure
existing_treatments = format_procedure(existing_treatments, "Procedure_Mapped")

# Partial Denture
# # Maxillary Arch
existing_treatments = consolidate_partial_dentures2(
    existing_treatments,
    patient_column="ChartNumber",
    procedure_column="Procedure",
    teeth_column="ToothVEL",
    procedure_filter=max_arch_proc,
    quad_category_column="Quad_Category",
    group_on_quad=False
)

# Mandibular Arch
existing_treatments = consolidate_partial_dentures2(
    existing_treatments,
    patient_column="ChartNumber",
    procedure_column="Procedure",
    teeth_column="ToothVEL",
    procedure_filter=man_arch_proc,
    quad_category_column="Quad_Category",
    group_on_quad=False
)

# Quad
existing_treatments = consolidate_partial_dentures2(
    existing_treatments,
    patient_column="ChartNumber",
    procedure_column="Procedure",
    teeth_column="ToothVEL",
    procedure_filter=quad_proc,
    quad_category_column="Quad_Category",
    group_on_quad=True
)

# # Maxillary Arch
# existing_treatments = consolidate_partial_dentures(
#     existing_treatments,
#     patient_column="ChartNumber",
#     procedure_column = "Procedure",
#     teeth_column = "ToothVEL",
#     area_column="AreaofOralCavity",
#     procedure_filter=max_arch_proc,
#     quad_category_column="Quad_Category",
#     group_on_quad=False
# )

# ## Mandibular Arch
# existing_treatments = consolidate_partial_dentures(
#     existing_treatments,
#     patient_column="ChartNumber",
#     procedure_column = "Procedure",
#     teeth_column = "ToothVEL",
#     area_column="AreaofOralCavity",
#     procedure_filter=man_arch_proc,
#     quad_category_column="Quad_Category",
#     group_on_quad=False
# )

# ## Quad
# existing_treatments = consolidate_partial_dentures(
#     existing_treatments,
#     patient_column="ChartNumber",
#     procedure_column = "Procedure",
#     teeth_column = "ToothVEL",
#     area_column="AreaofOralCavity",
#     procedure_filter=quad_proc,
#     quad_category_column="Quad_Category",
#     group_on_quad=True
# )


## Calculate Update Instant
existing_treatments = instant_calc(
    existing_treatments,
    "UpdateInstant",
    "Update Inst (UTC)"
)

## Calculate Completed Instant
existing_treatments = instant_calc(
    existing_treatments,
    "CompInstant",
    "Comp Inst"
)

## Partial Denture Inact VEl Mapping
## If Patient/Procedure is the same. Look at CompInstant all but most recent CompInstant is moved to Inact VEL
mask = (
    existing_treatments["ToothVEL"]
    .astype(str)
    .str.contains("\n", na=False)
)

existing_treatments["Inact VEL"] = np.nan

filtered = existing_treatments.loc[mask].copy()

# Ensure proper datetime sorting
filtered["_CompInstant_dt"] = pd.to_datetime(
    filtered["CompInstant"],
    errors="coerce"
)

filtered = filtered.sort_values(
    ["ChartNumber", "Procedure", "_CompInstant_dt"],
    ascending=[True, True, False]
)

# Older rows within same patient + procedure
older_rows = (
    filtered
    .groupby(["ChartNumber", "Procedure"])
    .cumcount() > 0
)

older_idx = filtered.loc[older_rows].index

existing_treatments.loc[
    older_idx,
    "Inact VEL"
] = existing_treatments.loc[
    older_idx,
    "ToothVEL"
]

existing_treatments.loc[
    older_idx,
    "ToothVEL"
] = np.nan

existing_treatments = existing_treatments.drop(
    columns=["_CompInstant_dt"],
    errors="ignore"
)
# mask = existing_treatments["ToothVEL"].astype(str).str.contains("\n", na=False)

# existing_treatments["Inact VEL"] = np.nan

# filtered = existing_treatments.loc[mask].copy()

# filtered = filtered.sort_values(
#     ["ChartNumber", "CompInstant"],
#     ascending=[True, False]
# )

# older_rows = filtered.groupby("ChartNumber").cumcount() > 0

# older_idx = filtered.loc[older_rows].index

# existing_treatments.loc[older_idx, "Inact VEL"] = existing_treatments.loc[older_idx, "ToothVEL"]

# existing_treatments.loc[older_idx, "ToothVEL"] = np.nan

# Filter out LOS from procedures
existing_treatments = existing_treatments[~existing_treatments["Procedure"].astype(str).str.contains(r"99\d{3}", na=False)]

# Remove ",,," from DX
existing_treatments["AssociatedDiagnosis"] = existing_treatments["AssociatedDiagnosis"].astype(str).str.replace(",,,", "", regex=False)

# Filter out NA Procedures
existing_treatments = existing_treatments[existing_treatments["Procedure"].notna()]

# Remove characters from end if Comments exceeds 254 characters
existing_treatments["Comments"] = existing_treatments["Comments"].astype("string").str.slice(0, 254)

# If patient has permanent teeth ToothVEL contains numeric, and patient has primary teeth ToothVEL contains alphabetic. 
## The ToothVEL column should remain the same for permanent, but the primary teeth should be moved to the Inact VEL column.
anatomy = (
    existing_treatments["AnatomyVEL"]
    .astype(str)
    .str.strip()
)

is_primary = anatomy.str.fullmatch(r"[A-Za-z]+", na=False)
is_permanent = anatomy.str.contains(r"\d", na=False)

patients_with_both = (
    set(existing_treatments.loc[is_primary, "ChartNumber"]) &
    set(existing_treatments.loc[is_permanent, "ChartNumber"])
)

mask = (
    is_primary &
    existing_treatments["ChartNumber"].isin(patients_with_both)
)

existing_treatments.loc[mask, "Inact VEL"] = (
    existing_treatments.loc[mask, "ToothVEL"]
)

existing_treatments.loc[mask, "ToothVEL"] = np.nan

existing_treatments.to_csv("existing_treatments_unformatted.csv", sep = "|", index=False)

# Reformat Columns
existing_treatment_reformatted = existing_treatments.assign(
    **{
        "ID": existing_treatments["RESID"],
        "Patient ID": existing_treatments["ChartNumber"],
        "Tooth VEL": existing_treatments["ToothVEL"],
        "Inact VEL": existing_treatments["Inact VEL"],
        "Additional Tooth VEL":"",
        "Encounter CSN":"G^1",
        "Surfaces": existing_treatments["Surfaces_Mapped"],
        "Procedure": existing_treatments["Procedure_Mapped"],
        "Comp Inst":existing_treatments["Comp Inst"],
        "Provider":existing_treatments["Provider_Mapped"],
        "Assoc Diag": "",
        "Comment": existing_treatments["Comments"],
        "Area of Oral Cavity": existing_treatments["AreaofOralCavity"],
        "Inactive For Area":"",
        "Exist Proc":"",
        "Update User (EMP)": existing_treatments["Update User"],
        "Update Inst (UTC)":existing_treatments["Update Inst (UTC)"],
        "Enc Dep":"490",
        "Enc Prov":existing_treatments["Provider_Mapped"],
        "Enc Date": datetime.today().strftime("%m/%d/%Y")
    }
)

# Reorder and keep only required columns
existing_treatment_reformatted = existing_treatment_reformatted[
    [
        "ID",
        "Patient ID",
        "Tooth VEL",
        "Inact VEL",
        "Additional Tooth VEL",
        "Encounter CSN",
        "Surfaces",
        "Procedure",
        "Comp Inst",
        "Provider",
        "Assoc Diag",
        "Comment",
        "Area of Oral Cavity",
        "Inactive For Area",
        "Exist Proc",
        "Update User (EMP)",
        "Update Inst (UTC)",
        "Enc Dep",
        "Enc Prov",
        "Enc Date"
    ]
]

existing_treatment_dfs = np.array_split(existing_treatment_reformatted, 3)

# Export each chunk
for i, df_chunk in enumerate(existing_treatment_dfs, start=1):
    df_chunk.to_csv(f"existing_treatments_formatted_part{i}.csv", sep="|", index=False)