import tkinter as tk

import customtkinter
import customtkinter as ctk
from clams_processing import clean_all_clams_data, trim_all_clams_data, process_directory


def main_process_clams_data():
    """Main function to process all CLAMS data files in the provided directory.

    Parameters:
    directory_path (string): directory containing .csv files to process
    trim_hours (int): number of hours to trim from the beginning of the cleaned data
    keep_hours (int): number of hours to keep in the trimmed data
    bin_hours (int): number of hours to bin the data

    Returns:
    Nothing. Prints progress and saves processed files to respective directories.
    """
    # directory_path, trim_hours, keep_hours, bin_hours
    directory_path = directory_path_entry.get()
    trim_hours = int(trim_hours_entry.get())
    keep_hours = int(keep_hours_entry.get())
    bin_hours = int(bin_hours_entry.get())

    output_text.insert(tk.END, "Cleaning all CLAMS data...\n")
    clean_all_clams_data(directory_path)

    output_text.insert(tk.END, "\nTrimming all cleaned CLAMS data...\n")
    trim_all_clams_data(directory_path, trim_hours, keep_hours)

    output_text.insert(tk.END, "\nBinning all trimmed CLAMS data...\n")
    process_directory(directory_path, bin_hours)


# customtkinter global settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
customtkinter.deactivate_automatic_dpi_awareness()

# Create the main window
root = ctk.CTk()
root.title("CLAMSwrangler")
root.geometry("800x600")

# Create input fields
directory_path_label = ctk.CTkLabel(root, text="Directory Path:")
directory_path_label.pack()
directory_path_entry = ctk.CTkEntry(root, width=500)
directory_path_entry.pack()

trim_hours_label = ctk.CTkLabel(root, text="Trim Hours:")
trim_hours_label.pack()
trim_hours_entry = ctk.CTkEntry(root, width=50)
trim_hours_entry.pack()

keep_hours_label = ctk.CTkLabel(root, text="Keep Hours:")
keep_hours_label.pack()
keep_hours_entry = ctk.CTkEntry(root, width=50)
keep_hours_entry.pack()

bin_hours_label = ctk.CTkLabel(root, text="Bin Hours:")
bin_hours_label.pack()
bin_hours_entry = ctk.CTkEntry(root, width=50)
bin_hours_entry.pack()

# Create a button to start processing
# main_process_clams_data retrieves values from entry widgets when called
start_button = ctk.CTkButton(root, text="Process CLAMS data", command=main_process_clams_data)
start_button.place(relx=0.5, rely=0.5)
start_button.pack(padx=20, pady=20)

# Create a text widget to display the output
output_text = tk.Text(root, wrap=tk.WORD, width=600, height=20)
output_text.pack()

# Start the main loop
root.mainloop()

# Example usage
# directory_path = "/path/to/All_CSVs"
# main_process_clams_data(directory_path, trim_hours=24, keep_hours=72, bin_hours=4)
