import pandas as pd
from func.tables import procedure_map, teeth_map, surface_anterior_map, surface_posterior_map, posterior_anatomy_vel, anterior_anatomy_vel, provider_ser_map
from func.func import format_pid, set_resid, map_teeth, map_surfaces, map_provider

planned_treatments = pd.read_csv("working_data/planned_treatments.csv", delimiter="|")
planned_treatments = planned_treatments.shift(axis=1)

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

# Provider Map (SER)
planned_treatments = map_provider(
    planned_treatments,
    provider_ser_map,
    "PlanOwner",
    "Update User",
    "E1012"
)

# Procedure Mapping
proc = planned_treatments["Procedure"].astype("string").str.strip()

## Define CDT/CPT patterns
cdt_re = r"^D\d{4}$"
cpt_re = r"^\d{5}$"

is_blank = proc.isna() | (proc == "")
is_cdt   = proc.str.upper().str.match(cdt_re, na=False)
is_cpt   = proc.str.match(cpt_re, na=False)

## Apply mapping table
mapped = proc.map(procedure_map)

## Preserve original when not mapped
result = mapped.fillna(proc)

## Any remaining non-empty, non-mappable, non-CDT/CPT -> WIS81
needs_wis81 = mapped.isna() & ~is_blank & ~(is_cdt | is_cpt)
result = result.mask(needs_wis81, "WIS81")

planned_treatments["Procedure_Mapped"] = result


