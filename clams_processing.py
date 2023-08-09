import pandas as pd
import os
import glob
import numpy as np
import re
from datetime import datetime, timedelta


def clean_all_clams_data(directory_path):
    """Reformat all CLAMS data files (.csv) in the provided directory by dropping unnecessary rows.

    Parameters:
    directory_path (string): directory containing .csv files to clean

    Returns:
    Nothing. Prints new filenames saved to "Cleaned_CLAMS_data" directory.
    """

    def clean_file(file_path, output_directory):
        """Helper function to clean individual file."""
        # Read the file as plain text to extract metadata
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Extract the "Subject ID" value
        for line in lines:
            if 'Subject ID' in line:
                subject_id = line.split(',')[1].strip()
                break

        # Read the data chunk of the CSV file
        df = pd.read_csv(file_path, skiprows=range(0, 22))

        # Drop additional 2 formatting rows
        df.drop([0, 1], inplace=True)

        # Construct the new file name
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        ext = ext.lower()
        new_file_name = f"{base_name}_ID{subject_id}{ext}"

        # Save the cleaned data to the new directory
        output_path = os.path.join(output_directory, new_file_name)
        df.to_csv(output_path, index=False)
        print(f"Cleaning {file_name}")

    # Create the output directory if it doesn't exist
    output_directory = os.path.join(directory_path, "Cleaned_CLAMS_data")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

        # Process all CSV files in the directory, regardless of extension case
        csv_pattern = re.compile(r"\.csv$", re.IGNORECASE)
        all_files = glob.iglob(os.path.join(directory_path, "*"))
        csv_files = [file_path for file_path in all_files if csv_pattern.search(file_path)]

        for file_path in csv_files:
            clean_file(file_path, output_directory)


def trim_all_clams_data(directory_path, trim_hours, keep_hours):
    """Trims all cleaned CLAMS data files in the specified directory.

    Parameters:
    directory_path (string): path to the directory containing cleaned .csv files
    trim_hours (int): number of hours to trim from the beginning
    keep_hours (int): number of hours to keep in the resulting file

    Returns:
    Nothing. Saves the trimmed data to new CSV files in the "Trimmed_CLAMS_data" directory.
    """

    # Create a new directory for trimmed files if it doesn't exist
    trimmed_directory = os.path.join(directory_path, "Trimmed_CLAMS_data")
    if not os.path.exists(trimmed_directory):
        os.makedirs(trimmed_directory)

    # Get the path to the cleaned data files
    cleaned_directory = os.path.join(directory_path, "Cleaned_CLAMS_data")

    # List all files in the directory
    files = [f for f in os.listdir(cleaned_directory) if
             os.path.isfile(os.path.join(cleaned_directory, f)) and f.endswith('.csv')]

    for file in files:
        file_path = os.path.join(cleaned_directory, file)

        # Read the cleaned CSV file
        df = pd.read_csv(file_path)

        # Convert the 'DATE/TIME' column to datetime format
        df['DATE/TIME'] = pd.to_datetime(df['DATE/TIME'], errors='coerce')

        # Calculate the starting timestamp after trimming
        start_time = df['DATE/TIME'].iloc[0] + timedelta(hours=trim_hours)

        # Filter the dataframe to start from the trimmed timestamp
        df_trimmed = df[df['DATE/TIME'] >= start_time]

        # Note the value in the "LED LIGHTNESS" column after trimming
        initial_led_value = df_trimmed['LED LIGHTNESS'].iloc[0]

        # Find the index of the next change in the "LED LIGHTNESS" value
        led_lightness_change_index = df_trimmed[df_trimmed['LED LIGHTNESS'] != initial_led_value].index[0]

        # Calculate the ending timestamp
        end_time = df['DATE/TIME'].iloc[led_lightness_change_index] + timedelta(hours=keep_hours)

        # Filter the dataframe to start from the LED change and end at the specified timestamp
        df_result = df[
            (df['DATE/TIME'] >= df['DATE/TIME'].iloc[led_lightness_change_index]) & (df['DATE/TIME'] <= end_time)]

        # Save the resulting data to a new CSV file in the "Trimmed_CLAMS_data" directory
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file)
        ext = ext.lower()
        new_file_name = os.path.join(trimmed_directory, f"{base_name}_trimmed{ext}")
        df_result.to_csv(new_file_name, index=False)
        print(f"Trimming {file_name}")


def bin_clams_data(file_path, bin_hours):
    df = pd.read_csv(file_path)

    # Convert 'DATE/TIME' column to datetime format
    df['DATE/TIME'] = pd.to_datetime(df['DATE/TIME'])

    # Drop unnecessary columns
    columns_to_drop = ["STATUS1", "O2IN", "O2OUT", "DO2", "CO2IN", "CO2OUT", "DCO2", "XTOT", "YTOT", "LED HUE",
                       "LED SATURATION", "BIN"]
    df = df.drop(columns=columns_to_drop, errors='ignore')

    # Add TOT_AMB column to the original dataframe
    df['TOT_AMB'] = df['XAMB'] + df['YAMB']

    # Create a new column for bin labels
    df['BIN'] = np.nan

    # For each unique "LED LIGHTNESS" value, assign bin labels
    for led_value in df['LED LIGHTNESS'].unique():
        subset = df[df['LED LIGHTNESS'] == led_value].copy()
        start_time = subset['DATE/TIME'].iloc[0]
        bin_label = 0
        bin_labels = []

        for timestamp in subset['DATE/TIME']:
            if (timestamp - start_time) >= timedelta(hours=bin_hours):
                bin_label += 1
                start_time = timestamp
            bin_labels.append(bin_label)

        df.loc[subset.index, 'BIN'] = bin_labels

    # Columns to retain the last value in the bin
    last_val_columns = ["INTERVAL", "CHAN", "DATE/TIME", "ACCO2", "ACCCO2", "FEED1 ACC", "WHEEL ACC"]

    # Columns to sum within the bin
    sum_columns = ["WHEEL", "FEED1", "TOT_AMB"]

    # Columns to average (excluding the ones we're taking the last value or summing)
    avg_columns = df.columns.difference(last_val_columns + sum_columns + ['BIN', 'LED LIGHTNESS'])

    # Group by "LED LIGHTNESS" and "BIN" and calculate the mean, sum, or last value as appropriate
    df_binned = df.groupby(['LED LIGHTNESS', 'BIN']).agg({**{col: 'last' for col in last_val_columns},
                                                          **{col: 'mean' for col in avg_columns},
                                                          **{col: 'sum' for col in sum_columns}}).reset_index()

    # Add start and end time columns
    start_times = df.groupby(['LED LIGHTNESS', 'BIN'])['DATE/TIME'].first().reset_index(name='DATE/TIME_start')
    end_times = df.groupby(['LED LIGHTNESS', 'BIN'])['DATE/TIME'].last().reset_index(name='DATE/TIME_end')
    df_binned = pd.merge(df_binned, start_times, on=['LED LIGHTNESS', 'BIN'])
    df_binned = pd.merge(df_binned, end_times, on=['LED LIGHTNESS', 'BIN'])

    # Add start and end interval columns
    start_intervals = df.groupby(['LED LIGHTNESS', 'BIN'])['INTERVAL'].first().reset_index(name='INTERVAL_start')
    end_intervals = df.groupby(['LED LIGHTNESS', 'BIN'])['INTERVAL'].last().reset_index(name='INTERVAL_end')
    df_binned = pd.merge(df_binned, start_intervals, on=['LED LIGHTNESS', 'BIN'])
    df_binned = pd.merge(df_binned, end_intervals, on=['LED LIGHTNESS', 'BIN'])

    # Calculate the duration of each bin in hours
    df_binned['DURATION'] = (df_binned['DATE/TIME_end'] - df_binned['DATE/TIME_start']).dt.total_seconds() / 3600

    # Drop existing BIN column & sort based on INTERVAL_start
    df_binned = df_binned.sort_values(by='INTERVAL_start')

    # Add a DAY column
    df_binned['DAY'] = (df_binned['BIN'] // (12 / bin_hours) + 1).astype(int)

    # Reset index and add a new 'BIN' column starting from 1
    df_binned.reset_index(drop=True, inplace=True)
    df_binned['BIN'] = df_binned.index

    # Add DAILY_BIN column
    df_binned['DAILY_BIN'] = df_binned['BIN'] % ( 24 // bin_hours)

    # Reorder columns based on your request
    desired_order = ["CHAN", "INTERVAL_start", "INTERVAL_end", "DATE/TIME_start", "DATE/TIME_end", "DURATION",
                     "VO2", "ACCO2", "VCO2", "ACCCO2", "RER", "HEAT", "FLOW", "PRESSURE", "FEED1", "FEED1 ACC",
                     "TOT_AMB", "WHEEL", "WHEEL ACC", "ENCLOSURE TEMP", "ENCLOSURE SETPOINT", "LED LIGHTNESS", "DAY", "BIN", "DAILY_BIN"]
    df_binned = df_binned[desired_order]

    # Round all variables to 4 decimal places
    df_binned = df_binned.round(4)

    # Save the binned data to a new CSV file
    output_path = file_path.replace("Trimmed_CLAMS_data", "Binned_CLAMS_data").replace(".csv", "_binned.csv")

    # Check if the directory exists, if not, create it
    output_directory = os.path.dirname(output_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    df_binned.to_csv(output_path, index=False)


def process_directory(directory_path, bin_hours):
    # Get path to trimmed directory
    trimmed_directory = os.path.join(directory_path, "Trimmed_CLAMS_data")

    # Get a list of all .CSV files in the directory
    csv_files = [f for f in os.listdir(trimmed_directory) if
                 f.endswith('.csv') and os.path.isfile(os.path.join(trimmed_directory, f))]

    # Process each .CSV file
    for csv_file in csv_files:
        file_path = os.path.join(trimmed_directory, csv_file)
        bin_clams_data(file_path, bin_hours)
        print(f"Binning {csv_file}")


def extract_id_number(filename):
    # Extract the four digits following 'ID' in the filename
    match = re.search(r'ID(\d{4})', filename)
    if match:
        return match.group(1)
    else:
        return None


def split_csv_files(directory_path):
    # Define Combined CLAMS data directory
    combined_directory = os.path.join(directory_path, "Combined_CLAMS_data")
    if not os.path.exists(combined_directory):
        os.makedirs(combined_directory)

    # Define input directory
    input_directory = os.path.join(directory_path, "Binned_CLAMS_data")

    # Create a dictionary to store data for each selected column
    column_data = {}

    # Selected columns to combine
    selected_columns = ['VO2', 'ACCO2', 'VCO2', 'ACCCO2', 'RER', 'FEED1', 'FEED1 ACC', 'TOT_AMB', 'WHEEL', 'WHEEL ACC']

    # Loop through all files in the specified directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_directory, filename)
            # Get the 'ID' number from the file name
            file_id = extract_id_number(filename)

            # Read the current .csv file into a DataFrame
            df = pd.read_csv(file_path)

            # Process each selected column and store it in the dictionary
            for column in selected_columns:
                if column in df.columns:
                    if column not in column_data:
                        column_data[column] = pd.DataFrame()
                    # Rename the column with the 'ID' number
                    df.rename(columns={column: f'{column} (ID{file_id})'}, inplace=True)
                    column_data[column] = pd.concat([column_data[column], df[[f'{column} (ID{file_id})']]], axis=1)

        # Transpose the data before saving to separate .csv files
        for column, df in column_data.items():
            # Transpose the DataFrame using .T
            transposed_df = df.T

            # Format the index to include content within parentheses
            transposed_df.index = [idx[3:].split("(")[1].split(")")[0].strip() for idx in transposed_df.index]

            output_filename = os.path.join(combined_directory, f"{column}.csv")
            transposed_df.to_csv(output_filename, index=True, header=False)  # Index is used as header
