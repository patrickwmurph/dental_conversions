import pandas as pd

# Reformat PID
def format_pid(df, column_name):
    mask = df[column_name].notna()

    df.loc[mask, column_name] = (
        "{{MPI}}" 
        + df.loc[mask, column_name].astype(str) 
        + ",-1,158"
    )
    
    return df

def set_resid(df, patient_column, resid_column="RESID"):
    df.loc[df[patient_column].notna(), resid_column] = "*"
    
    return df