from clams_processing import clean_all_clams_data, trim_all_clams_data, process_directory


def main_process_clams_data(directory_path, trim_hours, keep_hours, bin_hours):
    """Main function to process all CLAMS data files in the provided directory.

    Parameters:
    directory_path (string): directory containing .csv files to process
    trim_hours (int): number of hours to trim from the beginning of the cleaned data
    keep_hours (int): number of hours to keep in the trimmed data
    bin_hours (int): number of hours to bin the data

    Returns:
    Nothing. Prints progress and saves processed files to respective directories.
    """

    print("Cleaning all CLAMS data...")
    clean_all_clams_data(directory_path)

    print("\nTrimming all cleaned CLAMS data...")
    trim_all_clams_data(directory_path, trim_hours, keep_hours)

    print("\nBinning all trimmed CLAMS data...")
    process_directory(directory_path, bin_hours)


# Example usage
directory_path = "/path/to/All_CSVs"
main_process_clams_data(directory_path, trim_hours=24, keep_hours=72, bin_hours=4)
