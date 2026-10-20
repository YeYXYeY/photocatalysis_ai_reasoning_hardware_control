import pandas as pd


def split_task(file_path):
    """Split the supplied workbook into solid and liquid task tables."""

    # NO	A1	B1	C0	C1	C2	C3	C4	C5	C6	D1	E0	E1	E2	E3	E4	F0	F1	F2	F3	G1	H0	H1	H2	H3	I0	I1	I2	I3	J0	J1	J2	J3	J4	J5	J6	J7	J8
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
    # ["NO", "F1", "F2", "F3", "I1", "I2", "I3"]
    solid_task_columns = ["NO", "F1", "F2", "F3", "I1", "I2", "I3"]

    df = pd.read_excel(file_path)

    missing_columns_1 = [col for col in liquid_task_columns if col not in df.columns]
    missing_columns_2 = [col for col in solid_task_columns if col not in df.columns]
    if missing_columns_1:
        print(f"Missing liquid-task columns: {missing_columns_1}")
        return
    elif missing_columns_2:
        print(f"Missing solid-task columns: {missing_columns_1}")
        return

    solid_task_df = df[solid_task_columns]
    liquid_task_df = df[liquid_task_columns]

    return solid_task_df, liquid_task_df
