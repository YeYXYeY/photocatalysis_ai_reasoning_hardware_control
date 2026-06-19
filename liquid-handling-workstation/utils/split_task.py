import pandas as pd


def split_task(file_path):
    """Split a combined task workbook into liquid and solid task tables."""
    liquid_task_columns = [
        "NO",
        "A1",
        "B1",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "D1",
        "E1",
        "E2",
        "E3",
        "E4",
        "G1",
        "H1",
        "H2",
        "H3",
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
        "J6",
        "J7",
        "J8",
    ]
    solid_task_columns = ["NO", "F2", "F3", "I1", "I2", "I3"]

    df = pd.read_excel(file_path)
    # Validate that all required columns exist before slicing the task file.
    missing_columns_1 = [col for col in liquid_task_columns if col not in df.columns]
    missing_columns_2 = [col for col in solid_task_columns if col not in df.columns]
    if missing_columns_1:
        print(
            f"These liquid-task columns are missing from the workbook: {missing_columns_1}"
        )
        return
    elif missing_columns_2:
        print(
            f"These solid-task columns are missing from the workbook: {missing_columns_2}"
        )
        return
    solid_task_df = df[solid_task_columns]
    liquid_task_df = df[liquid_task_columns]

    return solid_task_df, liquid_task_df


def generate_task_file(task_df, reactant_df, bottle_volume, filename):
    result = process_all_chemicals(task_df, reactant_df, bottle_volume)
    # Determine how many numbered tasks are required in the exported file.
    max_no = int(
        max(
            max(batch, key=lambda x: x[0])[0]
            for info in result.values()
            for batch in info["batches"]
        )
    )

    # Build the final task dataframe.
    task_data = {"NO": list(range(1, max_no + 1))}
    for chemical, info in result.items():
        for i, batch in enumerate(info["batches"]):
            column_name = f"{chemical}-{i+1}"
            task_data[column_name] = [""] * max_no
            for no, volume in batch:
                task_data[column_name][int(no) - 1] = volume

    task_file_df = pd.DataFrame(task_data)

    task_file_df.to_excel(filename, index=False)


def split_into_batches(df, column, bottle_volume):
    batches = []
    current_batch = []
    current_volume = 0

    for index, row in df.iterrows():
        if pd.notna(row[column]):
            if current_volume + row[column] > bottle_volume:
                batches.append(current_batch)
                current_batch = []
                current_volume = 0
            current_batch.append((row["NO"], row[column]))
            current_volume += row[column]

    if current_batch:
        batches.append(current_batch)

    return batches


def find_chemical_positions(df, chemical_prefix, num_batches):
    df = df.dropna(subset=["Chemicals"])  # Drop empty chemical names before matching.
    positions = (
        df[df["Chemicals"].str.startswith(chemical_prefix)]
        .head(num_batches)[["X", "Y", "Z", "H"]]
        .values.tolist()
    )
    return positions


def process_chemical_batches(task_df, reactant_df, chemical, bottle_volume):
    batches = split_into_batches(task_df, chemical, bottle_volume)
    positions = find_chemical_positions(reactant_df, chemical, len(batches))
    if len(positions) < len(batches):
        raise ValueError(f"Not enough bottles for chemical {chemical}")
    return batches, positions


def process_all_chemicals(task_df, reactant_df, bottle_volume):
    chemicals = task_df.columns[1:]  # Skip the numbering column.
    result = {}

    for chemical in chemicals:
        if task_df[chemical].notna().any():  # Only process chemicals that are used.
            if not any(reactant_df["Chemicals"].str.startswith(chemical)):
                raise ValueError(f"Chemical {chemical} not found in reactant_df")
            batches, positions = process_chemical_batches(
                task_df, reactant_df, chemical, bottle_volume
            )
            result[chemical] = {"batches": batches, "positions": positions}

    return result


if __name__ == "__main__":
    file_path = "./0417task.xlsx"

    s_df, l_df = split_task(file_path)

    print(s_df)
    print(l_df)
