import pandas as pd
import re
from io import StringIO
import csv

# Existing Treatments Cleaning

# XML Cleaning
def xml_clean2(data, working_data):
     rows = []
     buffer = ""

     with open(data, "r", encoding="cp1252", errors="ignore") as f:
         for line in f:
             line = line.replace("\x07", "")  # remove bad char
             line = line.rstrip("\r\n")       # NEW

             # ✅ updated row detection
             if re.match(r"^\|[^|]+\|", line) and buffer:
                 rows.append(buffer.strip())
                 buffer = line
             else:
                 buffer += line

         if buffer:
             rows.append(buffer.strip())

     # flatten multi-line comments
     cleaned_rows = [
         re.sub(r"\r?\n+", ";", r) for r in rows
     ]

     with open(working_data, "w", encoding="utf-8", newline="") as f:
         for r in cleaned_rows:
             f.write(r + "\n")

     print(f"{working_data} written.")

def pip_count_cleaning(data, working_data, expected_pipes=17):

    with open(data, "r", encoding="cp1252") as f:
        raw = f.read()

    # Normalize line endings
    raw = raw.replace("\r\n", "\n")

    # Split physical lines
    lines = raw.split("\n")

    # Preserve header row exactly
    header = lines[0]

    # Remaining rows only
    data_lines = lines[1:]

    rebuilt_rows = []
    current = ""

    for line in data_lines:

        # Skip fully empty lines
        if not line.strip():
            continue

        # Add separator for continued multiline text
        if current:
            current += ";"

        # Append current fragment
        current += line.strip()

        # Row complete once expected pipe count reached
        if current.count("|") >= expected_pipes:

            rebuilt_rows.append(current)
            current = ""

    # Catch dangling partial row
    if current:
        rebuilt_rows.append(current)

    # Rebuild final text
    text = header + "\n" + "\n".join(rebuilt_rows)

    # Cleanup duplicate semicolons
    text = re.sub(r";{2,}", ";", text)

    with open(working_data, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print(f"{working_data} written.")


def xml_clean(data, working_data):
    with open(data, "r", encoding="cp1252") as f:
        text = f.read()
    
    # 1) Turn paragraph breaks (blank lines) into a single semicolon
    text = re.sub(r"\r?\n\r?\n+", ";", text)

    # 2) Turn any remaining newline NOT followed by '|' into a semicolon
    text = re.sub(r"\r?\n(?!\|)", ";", text)

    # 3) Clean up any accidental repeats
    text = re.sub(r";{2,}", ";", text)

    with open(working_data, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print(f"{working_data} written.")
    
# def xml_clean(data, working_data):
    
#     with open(data, "r", encoding="utf-8", newline="") as f:
#         text = f.read()
    
#     LB = r"(?:\r\n|\r|\n)"  # match all newline styles

#     ## Handle ,,\n instances or \n,,
#     # text = re.sub(r",,?\r?\n,,\r?\n(?!\|)", ";", text)
#     # text = re.sub(r",,?\r?\n,,\r?\n(?=\|,,)", "", text)
    
#     ## Handle stand alone new lines
#     text = re.sub(LB + r"(?!\|)", ";", text)
    
#     ## Replace ;; with ; for double newline scenarios
#     text = re.sub(r";{2,}", ";", text)
    
#     ## Fix accidental row-break semicolon
#     text = re.sub(r";" + LB + r"(?=\|)", "", text)

#     with open(working_data, "w", encoding="utf-8", newline="") as f:
#         f.write(text)

#     print(f"{working_data} written.")


# Reformat PID
def format_pid(df, column_name):
    mask = df[column_name].notna() 
    # Index new column on nonNA; nan remains intact
    df.loc[mask, column_name] = (
        "{{MPI}}" 
        + df.loc[mask, column_name].astype(str) 
        + ",-1,158"
    )
    
    return df

def set_resid(df, patient_column, resid_column="RESID"):
    df.loc[df[patient_column].notna(), resid_column] = "*" #sort on PID notna, and set to *
    
    return df

def set_csn(df, patient_column, resid_column="CSN"):
    df.loc[df[patient_column].notna(), resid_column] = "G^1" #sort on PID notna, and set to G^1
    
    return df

def instant_calc(df, col_name, new_col_name=None):
    
    if new_col_name is None:
        new_col_name = f"{col_name}_INSTANT" # give new column name if none provided

    # Ensure datetime
    dt_series = pd.to_datetime(df[col_name], errors='coerce') # convert column to DT list

    # Epic epoch
    epic_epoch = pd.Timestamp("1840-12-31 00:00:00") # set 12/31/1840

    # Calculate seconds
    df[new_col_name] = (
        (dt_series - epic_epoch) # subtract epoch from all in list
        .dt.total_seconds() # convert DT to seconds
        .round() 
        .astype("Int64") 
    )
    
    return df

def map_teeth(df, teeth_map, source_column, target_column):
        source = df[source_column].astype('string').str.strip() # save off source column
        mapped = source.map(teeth_map) # apply map teeth based on table
        df[target_column] = mapped #.fillna(source) # fill na w/ previous values
         
        return df

#TODO Set 0 AOC for procedures where it is the only allowed AOC
#TODO Check procedures that require teeth

def create_area_of_oral_cavity(
    df,
    arch_map,
    quad_map,
    whole_mouth_codes,
    procedure_column="Procedure",
    arch_column="Arch",
    quadrant_column="Quadrant",
    target_column="AreaOfOralCavity"
):
    df = df.copy()

    arch = df[arch_column].astype("string").str.strip()
    quad = df[quadrant_column].astype("string").str.strip()
    proc = df[procedure_column].astype("string").str.strip()

    # start blank
    df[target_column] = pd.NA

    # Arch takes priority if populated
    mask_arch = arch.notna() & (arch != "")
    df.loc[mask_arch, target_column] = arch.loc[mask_arch].map(arch_map)

    # If no Arch, use Quadrant if populated
    mask_quad = ~mask_arch & quad.notna() & (quad != "")
    df.loc[mask_quad, target_column] = quad.loc[mask_quad].map(quad_map)

    # If neither Arch nor Quadrant is populated:
    # mask_neither = ~mask_arch & ~mask_quad
    # mask_whole_mouth = mask_neither & proc.isin(whole_mouth_codes)

    # df.loc[mask_whole_mouth, target_column] = 0
    # df.loc[mask_neither & ~proc.isin(whole_mouth_codes), target_column] = pd.NA

    return df

def filter_full_mouth_codes(df, source_column, procedure_column, whole_mouth_codes):
    df = df.copy()

    mask_source_zero = df[source_column] == 0
    mask_valid_proc = df[procedure_column].isin(whole_mouth_codes)

    # Where source = 0 AND procedure NOT in list → set NA
    df.loc[(mask_source_zero & mask_valid_proc), source_column] = pd.NA

    return df

def quad_category_column(df, teeth_column, target_column="Quad_Category"):
    df = df.copy()

    anatomy = df[teeth_column].astype(str).str.strip()

    quad_map = (
        {str(t): "UR" for t in list(range(1, 9)) + ["A", "B", "C", "D", "E"]} |
        {str(t): "UL" for t in list(range(9, 17)) + ["F", "G", "H", "I", "J"]} |
        {str(t): "LL" for t in list(range(17, 25)) + ["K", "L", "M", "N", "O"]} |
        {str(t): "LR" for t in list(range(25, 33)) + ["P", "Q", "R", "S", "T"]}
    )

    df[target_column] = anatomy.map(quad_map)

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
    anatomy = df[anatomy_column].astype("string").str.strip()
    surfaces = df[surfaces_column].astype("string").str.strip()

    def map_surface_string(surface_string, surface_map):
        if pd.isna(surface_string) or str(surface_string).strip() == "":
            return pd.NA

        surface_string = str(surface_string).strip().upper()
        mapped = []
        i = 0

        # valid sets
        valid_keys = set(surface_map.keys())
        valid_values = set(str(v) for v in surface_map.values())

        while i < len(surface_string):
            two_char = surface_string[i:i+2]

            # Try 2-character match
            if two_char in surface_map:
                mapped.append(str(surface_map[two_char]))
                i += 2

            # Try 1-character match
            elif surface_string[i] in surface_map:
                mapped.append(str(surface_map[surface_string[i]]))
                i += 1

            else:
                return pd.NA

        # Final safety check (probably redundant but safe)
        if not all(val in valid_values for val in mapped):
            return pd.NA

        return "\n".join(mapped)

    df = df.copy()
    df["Surfaces_Mapped"] = pd.NA

    # Anterior
    mask_anterior = anatomy.isin(anterior_anatomy_vel)
    df.loc[mask_anterior, "Surfaces_Mapped"] = surfaces.loc[mask_anterior].apply(
        lambda x: map_surface_string(x, surface_anterior_map)
    )

    # Posterior
    mask_posterior = anatomy.isin(posterior_anatomy_vel)
    df.loc[mask_posterior, "Surfaces_Mapped"] = surfaces.loc[mask_posterior].apply(
        lambda x: map_surface_string(x, surface_posterior_map)
    )

    return df


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

def map_procedure(df, mapping_table, fallback_value, comments_column, filter_fallback=False):
    df = df.copy()

    # Normalize mapping table keys to uppercase
    mapping_upper = {str(k).strip().upper(): v for k, v in mapping_table.items()}

    proc = df["Procedure"].astype("string").str.strip()
    proc_upper = proc.str.upper()

    # CDT/CPT patterns
    cdt_re = r"^D\d{4}$"
    cdt_re_d = r"^D\d{4}[A-Za-z]$"
    cpt_re = r"^\d{5}$"
    cpt_re_t = r"^\d{4}[A-Za-z]$"

    is_cdt = proc_upper.str.match(cdt_re, na=False)
    is_cdt_d = proc_upper.str.match(cdt_re_d, na=False)
    is_cpt = proc.str.match(cpt_re, na=False)
    is_cpt_t = proc_upper.str.match(cpt_re_t, na=False)

    mapped = proc_upper.map(mapping_upper)

    preserve_original = is_cdt | is_cdt_d | is_cpt | is_cpt_t

    result = mapped.fillna(proc)

    needs_fallback = mapped.isna() & ~preserve_original
    result = result.mask(needs_fallback, fallback_value)

    df["Procedure_Mapped"] = result

    comment_mask = mapped.notna() | needs_fallback

    df[comments_column] = df.get(comments_column, "").astype("string").fillna("")

    comment_text = "Dentrix Pre-Conversion Procedure: " + proc

    df.loc[comment_mask, comments_column] = (
        comment_text[comment_mask]
        + ";"
        + df.loc[comment_mask, comments_column].str.rstrip(";")
    )

    if filter_fallback:
        df = df[df["Procedure_Mapped"] != fallback_value].copy()

    return df

def format_procedure(df, column_name):
    mask = df[column_name].notna() 
    # Index new column on nonNA; nan remains intact
    df.loc[mask, column_name] = (
        "{{EXTID}}" 
        + df.loc[mask, column_name].astype(str) 
    )
    
    return df


# Partial Denture Code
def consolidate_partial_dentures(
    df,
    patient_column="PatientID",
    procedure_column="Procedure",
    teeth_column="ToothVEL",
    area_column="AreaOfOralCavity",
    procedure_filter=None,
    quad_category_column="Quad_Category",
    group_on_quad=False
):
    df = df.copy()

    if procedure_filter is None:
        procedure_filter = []

    # Split rows into those to consolidate and those to leave alone
    mask_max_arch = df[procedure_column].isin(procedure_filter)

    df_max_arch = df.loc[mask_max_arch].copy()
    df_other = df.loc[~mask_max_arch].copy()

    if df_max_arch.empty:
        return df

    has_compinstant = "CompInstant" in df_max_arch.columns
    has_planowner = "PlanOwner" in df_max_arch.columns
    has_provider = "Provider" in df_max_arch.columns

    if has_compinstant:
        df_max_arch["_compinstant_dt"] = pd.to_datetime(
            df_max_arch["CompInstant"],
            errors="coerce"
        )

    # Flag rows where AreaOfOralCavity should be prioritized
    area = df_max_arch[area_column].astype("string").str.strip()
    has_valid_area = area.notna() & (area != "") & (area != "0")
    df_max_arch["_area_priority"] = has_valid_area.astype(int)

    # Sort so rows with valid area come first within each group
    df_max_arch = df_max_arch.sort_values(
        by=[patient_column, procedure_column, "_area_priority"],
        ascending=[True, True, False]
    )

    def combine_teeth(series):
        vals = series.astype("string").dropna().str.strip()
        vals = vals[vals != ""]

        if vals.empty:
            return pd.NA

        teeth_list = []
        seen = set()

        for val in vals:
            for tooth in str(val).split(","):
                tooth = tooth.strip()
                if tooth and tooth not in seen:
                    seen.add(tooth)
                    teeth_list.append(tooth)

        return "\n".join(teeth_list) if teeth_list else pd.NA #update commas

    def consolidate_group(group):
        # Base preserved row comes from AOC-priority logic
        row = group.iloc[0].copy()
        row[teeth_column] = combine_teeth(group[teeth_column])

        # If CompInstant exists, set PlanOwner/Provider from most recent CompInstant row
        if has_compinstant:
            group_valid_comp = group[group["_compinstant_dt"].notna()]

            if not group_valid_comp.empty:
                latest_idx = group_valid_comp["_compinstant_dt"].idxmax()
                latest_row = group.loc[latest_idx]

                if has_planowner:
                    row["PlanOwner"] = latest_row["PlanOwner"]
                if has_provider:
                    row["Provider"] = latest_row["Provider"]

        return row

    group_cols = [patient_column, procedure_column]

    if group_on_quad:
        group_cols.append(quad_category_column)

    df_consolidated = (
        df_max_arch
        .groupby(group_cols, dropna=False, group_keys=False)
        .apply(consolidate_group)
        .reset_index(drop=True)
        .drop(columns=["_area_priority", "_compinstant_dt"], errors="ignore")
    )

    # Convert AreaOfOralCavity values of 0 to NA before recombining
    df_consolidated[area_column] = (
        df_consolidated[area_column]
        .replace("0", pd.NA)
        .replace(0, pd.NA)
    )

    # Recombine with untouched rows
    result = pd.concat([df_other, df_consolidated], ignore_index=True)

    return result

# Finding Type+Comment Mapping
def map_findings(df, finding_type_map, finding_comment_map):
    df["FindingType"] = df["FindingType"].astype("string").str.strip()
    df["Finding_Type"] = df["FindingType"].map(finding_type_map)
    df["Finding_Comment"] = df["FindingType"].map(finding_comment_map)
    return df

def map_dentition_tooth_status(df, finding_type_dentition_map):
    df["FindingType"] = df["FindingType"].astype("string").str.strip()
    df["Tooth Status"] = df["FindingType"].map(finding_type_dentition_map)
    return df


# Perio Location Mapping
def map_perio_loc(df, perio_map):
    df["Dental:Perio Location"] = df["DentalLocation"].map(perio_map)
    return df