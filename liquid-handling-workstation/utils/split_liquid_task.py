import pandas as pd
from datetime import datetime
import os


def split_task(file_path: str, task_path: str, nums_per_subtask: int) -> list:
    # Excel
    df = pd.read_excel(file_path)

    df = df.dropna(how="all")
    df_cleaned = df[~df.applymap(lambda x: isinstance(x, str) and x.isspace()).all(1)]

    num_subtasks = (df_cleaned.shape[0] + nums_per_subtask - 1) // nums_per_subtask
    dt = datetime.now()
    date_str = dt.strftime("%Y-%m-%d")
    os.makedirs(f"{task_path}/{date_str}/", exist_ok=True)
    task_list = []
    for i in range(num_subtasks):
        start_row = i * nums_per_subtask
        end_row = min((i + 1) * nums_per_subtask, df_cleaned.shape[0])

        subtask_data = df_cleaned.iloc[start_row:end_row]
        subtask_data.loc[:, "NO"] = subtask_data.loc[:, "NO"] - (10 * i)

        # Excel
        subtask_name = f"{task_path}/{date_str}/subtask_{i + 1}.xlsx"
        subtask_data.to_excel(subtask_name, index=False)
        task_list.append(subtask_name)
    return task_list


def generate_task_df(task_df, reagent_df, bottle_volume):
    result = process_all_chemicals(task_df, reagent_df, bottle_volume)
    max_no = int(
        max(
            max(batch, key=lambda x: x[0])[0]
            for info in result.values()
            for batch in info["batches"]
        )
    )

    # DataFrame
    task_data = {"NO": list(range(1, max_no + 1))}
    for chemical, info in result.items():
        for i, batch in enumerate(info["batches"]):
            column_name = f"{chemical}-{i+1}"
            task_data[column_name] = [""] * max_no
            for no, volume in batch:
                task_data[column_name][int(no) - 1] = volume

    task_file_df = pd.DataFrame(task_data)

    # Excel
    return task_file_df


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
    df = df.dropna(subset=["Chemicals"])  # "Chemicals" NA / NaN
    positions = (
        df[df["Chemicals"].str.startswith(chemical_prefix)]
        .head(num_batches)[["X", "Y", "Z", "H"]]
        .values.tolist()
    )
    return positions


def process_chemical_batches(task_df, reagent_df, chemical, bottle_volume):
    batches = split_into_batches(task_df, chemical, bottle_volume)
    positions = find_chemical_positions(reagent_df, chemical, len(batches))
    if len(positions) < len(batches):
        raise ValueError(f"Not enough bottles for chemical {chemical}")
    return batches, positions


def process_all_chemicals(task_df, reagent_df, bottle_volume):
    chemicals = task_df.columns[1:]  # "NO"
    result = {}

    for chemical in chemicals:
        if task_df[chemical].notna().any():
            if not any(reagent_df["Chemicals"].str.startswith(chemical)):
                raise ValueError(f"Chemical {chemical} not found in reagent_df")
            batches, positions = process_chemical_batches(
                task_df, reagent_df, chemical, bottle_volume
            )
            result[chemical] = {"batches": batches, "positions": positions}

    return result
