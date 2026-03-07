import pandas as pd
from func.func import xml_clean, set_resid, format_pid, map_teeth, map_surfaces, map_provider, map_findings
from func.tables import teeth_map, surface_anterior_map, surface_posterior_map, anterior_anatomy_vel, posterior_anatomy_vel, provider_emp_map, finding_type_map, finding_comment_map

# xml_clean("data\DXE_Extract_Findings.csv","working_data/findings.csv")

findings = pd.read_csv("working_data/findings.csv", delimiter="|")

# Initial Filtering
findings = findings[
    findings["ChartNumber"].notna()
    & ~findings["ChartNumber"].astype(str).str.strip().str.contains("_", na=False)
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

findings.to_csv("findings_unformatted.csv", sep="|", index=False)