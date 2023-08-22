import os
import pandas as pd


# Function to reformat a single CSV file
def reformat_csv(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)

    # Extract the name of the last column
    last_column_name = df.columns[-1]

    # Pivot the table using "ID", "GROUP LABEL", "DAY", and "24 HOUR" as indices
    pivot_table = df.pivot_table(index=["ID", "GROUP LABEL", "DAY"],
                                 columns="24 HOUR", values=last_column_name,
                                 aggfunc="first").reset_index()

    # Flatten the column index and rename columns
    pivot_table.columns = ["ID", "GROUP LABEL", "DAY"] + [f"{last_column_name}_{hour}" for hour in
                                                          pivot_table.columns[3:]]

    # Save the pivot table to a new CSV file
    pivot_table.to_csv(output_csv_path, index=False)


# Function to process all CSV files in a directory
def reformat_csvs_in_directory(input_dir):
    output_dir = os.path.join(input_dir, "Reformatted_CSVs")
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            input_csv_path = os.path.join(input_dir, filename)
            output_csv_path = os.path.join(output_dir, f"reformatted_{filename}")
            reformat_csv(input_csv_path, output_csv_path)
            print(f"Reformatting '{filename}' to reformatted_'{filename}'")
