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

def map_teeth(df, teeth_map, source_column, target_column):
        source = df[source_column].astype('string').str.strip()
        mapped = source.map(teeth_map)
        df[target_column] = mapped.fillna(source)
         
        return df

def map_surfaces(
    df,
    anatomy_column,
    surfaces_column,
    surface_anterior_map,
    surface_posterior_map,
    anterior_anatomy_vel,
    posterior_anatomy_vel
):
    anatomy = df[anatomy_column].astype(str).str.strip()
    surfaces = df[surfaces_column].astype(str).str.strip()

    df["Surfaces_Mapped"] = surfaces

    # Anterior
    mask_anterior = anatomy.isin(anterior_anatomy_vel)
    mapped_anterior = surfaces.map(surface_anterior_map).fillna(surfaces)
    df.loc[mask_anterior, "Surfaces_Mapped"] = mapped_anterior[mask_anterior]

    # Posterior
    mask_posterior = anatomy.isin(posterior_anatomy_vel)
    mapped_posterior = surfaces.map(surface_posterior_map).fillna(surfaces)
    df.loc[mask_posterior, "Surfaces_Mapped"] = mapped_posterior[mask_posterior]

    return df

import pandas as pd

def map_provider(
    df,
    mapping_table,
    source_column,
    target_column,
    default_value
):
    source = df[source_column].astype(str).str.strip()
    
    mapped = source.map(mapping_table)
    
    df[target_column] = (
        mapped
            .replace("", pd.NA)
            .fillna(default_value)
    )
    
    return df