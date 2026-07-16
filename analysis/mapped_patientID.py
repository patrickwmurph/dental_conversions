import pandas as pd
import numpy as np
from func.tables import pid_to_chartnumber_final
from func.func import format_pid


def strip_chart_number(df, patient_id_column):
    df[patient_id_column] = (
        df[patient_id_column]
        .astype(str)
        .str.extract(r"\{\{MPI\}\}(\d+),", expand=False)
    )
    
    return df

# Periodontal
periodontal_400_patients = pd.read_csv("periodontal_formatted.csv", delimiter="|", dtype=str)

periodontal_400_patients = strip_chart_number(
    periodontal_400_patients,
    "Patient ID"
)

periodontal_400_patients = periodontal_400_patients[
    periodontal_400_patients["Patient ID"].isin(pid_to_chartnumber_final.values())
]

periodontal_400_patients = format_pid(periodontal_400_patients, "Patient ID")

periodontal_400_patients.to_csv("test_files/periodontal_0607_patients.csv", sep="|", index=False)

# Existing treatments
existing_treatments_400_patients = pd.concat(
    [
        pd.read_csv("existing_treatments_formatted_part1.csv", delimiter="|", dtype=str),
        pd.read_csv("existing_treatments_formatted_part2.csv", delimiter="|", dtype=str),
        pd.read_csv("existing_treatments_formatted_part3.csv", delimiter="|", dtype=str),
    ],
    ignore_index=True
)

existing_treatments_400_patients = strip_chart_number(
    existing_treatments_400_patients,
    "Patient ID"
)

existing_treatments_400_patients = existing_treatments_400_patients[
    existing_treatments_400_patients["Patient ID"].isin(pid_to_chartnumber_final.values())
]
existing_treatments_400_patients = format_pid(existing_treatments_400_patients, "Patient ID")

existing_treatments_400_patients.to_csv("test_files/existing_treatments_0607_patients.csv", sep="|", index=False)

# Findings
findings_400_patients = pd.read_csv("findings_formatted.csv", delimiter="|", dtype=str)

findings_400_patients = strip_chart_number(
    findings_400_patients,
    "Patient ID"
)

findings_400_patients = findings_400_patients[
    findings_400_patients["Patient ID"].isin(pid_to_chartnumber_final.values())
]
findings_400_patients = format_pid(findings_400_patients, "Patient ID")

findings_400_patients.to_csv("test_files/findings_0607_patients.csv", sep="|", index=False)

# dentition
dentition_400_patients = pd.read_csv("dentition_formatted.csv", delimiter="|", dtype=str)

dentition_400_patients = strip_chart_number(
    dentition_400_patients,
    "Patient ID"
)

dentition_400_patients = dentition_400_patients[
    dentition_400_patients["Patient ID"].isin(pid_to_chartnumber_final.values())
]
dentition_400_patients = format_pid(dentition_400_patients, "Patient ID")

dentition_400_patients.to_csv("test_files/dentition_0607_patients.csv", sep="|", index=False)