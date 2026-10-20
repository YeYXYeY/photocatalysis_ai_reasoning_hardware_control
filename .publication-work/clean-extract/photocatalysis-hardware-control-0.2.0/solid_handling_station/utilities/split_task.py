import pandas as pd


def extract_and_save_columns(file_path, column_names, output_file_path):
    """Validate and export selected columns from an Excel workbook."""

    df = pd.read_excel(file_path)

    missing_columns = [col for col in column_names if col not in df.columns]
    if missing_columns:
        print(f"Missing workbook columns: {missing_columns}")
        return

    selected_columns = df[column_names]

    selected_columns.to_excel(output_file_path, index=False)
    print(f"Saved data to {output_file_path}")
