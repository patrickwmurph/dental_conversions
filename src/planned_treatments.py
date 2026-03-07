import pandas as pd
from func.tables import procedure_map, teeth_map, surface_anterior_map, surface_posterior_map, posterior_anatomy_vel, anterior_anatomy_vel, provider_emp_map, max_arch_proc, man_arch_proc, quad_proc
from func.func import xml_clean, format_pid, set_resid, map_teeth, map_surfaces, map_provider, map_procedure, format_procedure, quad_category_column, consolidate_partial_dentures

# Format XML
# xml_clean("data\DXE_Extract_PlannedTreatment.csv", "working_data/planned_treatments.csv")

planned_treatments = pd.read_csv("working_data/planned_treatments.csv", delimiter="|")
planned_treatments = planned_treatments.shift(axis=1).reset_index()

# Initial Filtering
planned_treatments = planned_treatments[
    planned_treatments["PatientID"].notna()
    & ~planned_treatments["PatientID"].astype(str).str.strip().str.contains("_", na=False)
    & (planned_treatments["PlanOwner"] != "TEST")
    & (planned_treatments["UpdateUser"] != "TEST")
]

# RESID Populating
planned_treatments = set_resid(
    planned_treatments,
    "PatientID"
)

# Patient ID renaming
planned_treatments = format_pid(planned_treatments, "PatientID")

# Teeth Mapping
planned_treatments = map_teeth(
    planned_treatments,
    teeth_map,
    "AnatomyVEL",
    "ToothVEL"
)

# Quad Mapping Column
planned_treatments = quad_category_column(
    planned_treatments,
    "AnatomyVEL",
    "Quad_Category"
)

# Surface Map
planned_treatments = map_surfaces(
    planned_treatments,
    "AnatomyVEL",
    "Surfaces",
    surface_anterior_map,
    surface_posterior_map,
    anterior_anatomy_vel,
    posterior_anatomy_vel
)

# Provider Map (EMP)
planned_treatments = map_provider(
    planned_treatments,
    provider_emp_map,
    "PlanOwner",
    "Update User",
    "49783"
)

# Procedure Map
planned_treatments = map_procedure(
    planned_treatments, 
    procedure_map, 
    fallback_value="WIS81",
    comments_column="Comments",
    filter_fallback=True
)

planned_treatments = format_procedure(planned_treatments, "Procedure_Mapped")

# Partial Denture

## Maxillary Arch
planned_treatments = consolidate_partial_dentures(
    planned_treatments,
    patient_column="PatientID",
    procedure_column = "Procedure",
    teeth_column = "ToothVEL",
    area_column="AreaofOralCavity",
    procedure_filter=max_arch_proc,
    quad_category_column="Quad_Category",
    group_on_quad=False
)

## Mandibular Arch
planned_treatments = consolidate_partial_dentures(
    planned_treatments,
    patient_column="PatientID",
    procedure_column = "Procedure",
    teeth_column = "ToothVEL",
    area_column="AreaofOralCavity",
    procedure_filter=man_arch_proc,
    quad_category_column="Quad_Category",
    group_on_quad=False
)

## Quad 
planned_treatments = consolidate_partial_dentures(
    planned_treatments,
    patient_column="PatientID",
    procedure_column = "Procedure",
    teeth_column = "ToothVEL",
    area_column="AreaofOralCavity",
    procedure_filter=quad_proc,
    quad_category_column="Quad_Category",
    group_on_quad=True
)

planned_treatments.to_csv("planned_treatments_unformatted.csv", sep="|", index=False)


# Reformat Columns
planned_treatment_reformatted = planned_treatments.assign(
    **{
        "ID": planned_treatments["RESID"],
        "Patient ID": planned_treatments["PatientID"],
        "Tooth VEL": planned_treatments["ToothVEL"],
        "Additional Tooth VEL": "",
        "Surfaces": planned_treatments["Surfaces_Mapped"],
        "Procedure": planned_treatments["Procedure_Mapped"],
        "Comment": planned_treatments["Comments"],
        "Area of Oral Cavity": planned_treatments["AreaofOralCavity"],
        "Substatus": "",
        "Update User (EMP)": planned_treatments["Update User"],
        "Updated Inst (UTC)": ""
    }
)

# Reorder and keep only required columns
planned_treatment_reformatted = planned_treatment_reformatted[
    [
        "ID",
        "Patient ID",
        "Tooth VEL",
        "Additional Tooth VEL",
        "Surfaces",
        "Procedure",
        "Comment",
        "Area of Oral Cavity",
        "Substatus",
        "Update User (EMP)",
        "Updated Inst (UTC)"
    ]
]

planned_treatment_reformatted.to_csv("planned_treatments_formatted.csv", sep = "|", index=False)