import pandas as pd
from func.func import set_resid, format_pid, map_teeth, map_provider, map_perio_loc
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
    provider_emp_map,
    "EncProvider",
    "Enc Provider",
    "E1012"
)

# Perio Location Mapping
periodontal = map_perio_loc(periodontal, perio_map)

periodontal.to_csv("periodontal_unformatted.csv", sep="|", index=False)