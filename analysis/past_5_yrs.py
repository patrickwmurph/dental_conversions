import pandas as pd

def filter_after_2020_instant(df, instant_col):
    df = df.copy()

    # Epic instant for 2020-01-01 00:00:00
    cutoff_instant = 5648745600

    filtered_df = df[
        pd.to_numeric(df[instant_col], errors="coerce")
        >= cutoff_instant
    ]

    return filtered_df


# periodontal
periodontal_past_5 = pd.read_csv("periodontal_formatted.csv", delimiter="|")
periodontal_past_5 = filter_after_2020_instant(
    periodontal_past_5,
    "Update Inst (UTC)"
)
periodontal_past_5.to_csv("test_files/periodontal_past_5.csv", sep="|", index=False)

# existing treatments
existing_treatments_past_5 = pd.concat(
    [
        pd.read_csv("existing_treatments_formatted_part1.csv", delimiter="|"),
        pd.read_csv("existing_treatments_formatted_part2.csv", delimiter="|"),
        pd.read_csv("existing_treatments_formatted_part3.csv", delimiter="|"),
    ],
    ignore_index=True
)

existing_treatments_past_5 = filter_after_2020_instant(
    existing_treatments_past_5,
    "Update Inst (UTC)"
)

existing_treatments_past_5_dfs = np.array_split(existing_treatments_past_5, 3)

# Export each chunk
for i, df_chunk in enumerate(existing_treatments_past_5_dfs, start=1):
    df_chunk.to_csv(f"test_files/existing_treatments_past_5_part{i}.csv", sep="|", index=False)

# findings
findings_past_5 = pd.read_csv("findings_formatted.csv", delimiter="|")
findings_past_5 = filter_after_2020_instant(
    findings_past_5,
    "Update Inst (UTC)"
)
findings_past_5.to_csv("test_files/findings_past_5.csv", sep="|", index=False)


# dentition
dentition_past_5 = pd.read_csv("dentition_formatted.csv", delimiter="|")
dentition_past_5 = filter_after_2020_instant(
    dentition_past_5,
    "Update Inst (UTC)"
)
dentition_past_5.to_csv("test_files/dentition_past_5.csv", sep="|", index=False)