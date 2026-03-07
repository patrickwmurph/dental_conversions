import pandas as pd
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
)
from func.func import xml_clean, format_pid, set_resid, map_teeth, map_surfaces, map_provider, map_procedure, format_procedure, consolidate_partial_dentures, create_area_of_oral_cavity, quad_category_column

# xml_clean("data\DXE_Extract_ExistingTreatment.csv", "working_data/existing_treatments.csv")

existing_treatments = pd.read_csv("working_data/existing_treatments.csv", delimiter="|")
existing_treatments = existing_treatments.shift(axis=1).reset_index()

# Initial Filtering
existing_treatments = existing_treatments[
    existing_treatments["ChartNumber"].notna()
    & ~existing_treatments["ChartNumber"].astype(str).str.strip().str.contains("_", na=False)
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
    provider_emp_map,
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

## Maxillary Arch
existing_treatments = consolidate_partial_dentures(
    existing_treatments,
    patient_column="ChartNumber",
    procedure_column = "Procedure",
    teeth_column = "ToothVEL",
    area_column="AreaofOralCavity",
    procedure_filter=max_arch_proc,
    quad_category_column="Quad_Category",
    group_on_quad=False
)

## Mandibular Arch
existing_treatments = consolidate_partial_dentures(
    existing_treatments,
    patient_column="ChartNumber",
    procedure_column = "Procedure",
    teeth_column = "ToothVEL",
    area_column="AreaofOralCavity",
    procedure_filter=man_arch_proc,
    quad_category_column="Quad_Category",
    group_on_quad=False
)

## Quad
existing_treatments = consolidate_partial_dentures(
    existing_treatments,
    patient_column="ChartNumber",
    procedure_column = "Procedure",
    teeth_column = "ToothVEL",
    area_column="AreaofOralCavity",
    procedure_filter=quad_proc,
    quad_category_column="Quad_Category",
    group_on_quad=True
)
#TODO calculate comp instant.
existing_treatments.to_csv("existing_treatments_unformatted.csv", sep = "|", index=False)

# Reformat Columns
existing_treatment_reformatted = existing_treatments.assign(
    **{
        "ID": existing_treatments["RESID"],
        "Patient ID": existing_treatments["ChartNumber"],
        "Tooth VEL": existing_treatments["ToothVEL"],
        "Encounter CSN":"G^1",
        "Additional Tooth VEL":"",
        "Surfaces": existing_treatments["Surfaces_Mapped"],
        "Procedure": existing_treatments["Procedure_Mapped"],
        "Comp Inst":existing_treatments["CompInstant"],
        # "Provider":existing_treatments["Provider"],
        "Assoc Diag": existing_treatments["AssociatedDiagnosis"],
        "Comment": existing_treatments["Comments"],
        "Area of Oral Cavity": existing_treatments["AreaofOralCavity"],
        "Inactive For Area":"",
        "Exist Proc":"",
        "Update User (EMP)": existing_treatments["Update User"],
        "Update Instant":existing_treatments["UpdateInstant"],
        "Enc Dep":"",
        "Enc Prov":existing_treatments["Provider"],
        "Enc Date":""
    }
)

# Reorder and keep only required columns
existing_treatment_reformatted = existing_treatment_reformatted[
    [
        "ID",
        "Patient ID",
        "Tooth VEL",
        "Encounter CSN",
        "Additional Tooth VEL",
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
        "Update Instant",
        "Enc Dep",
        "Enc Prov",
        "Enc Date"
    ]
]

existing_treatment_reformatted.to_csv("existing_treatments_formatted.csv", sep = "|", index=False)
