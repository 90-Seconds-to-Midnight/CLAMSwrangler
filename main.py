import tkinter as tk
from tkinter import filedialog, font
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from clams_processing import clean_all_clams_data, trim_all_clams_data, process_directory, recombine_columns


class StdoutRedirect:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self._stdout = sys.stdout

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Scroll to the end
        self._stdout.write(message)

    def flush(self):
        self._stdout.flush()


def browse_directory():
    """Opens dialog window to select file path.
    """
    folder_selected = filedialog.askdirectory()
    directory_path_entry.delete(0, tk.END)
    directory_path_entry.insert(0, folder_selected)

    # Initialize the experiment configuration file for the selected directory
    initialize_experiment_config_file(folder_selected)


def initialize_experiment_config_file(directory_path):
    # Create a folder for the config file
    config_file_path = os.path.join(directory_path, 'config')
    os.makedirs(config_file_path, exist_ok=True)

    # Path to the experiment configuration file
    config_file = os.path.join(config_file_path, 'experiment_config.csv')

    with open(config_file, 'w') as file:
        file.write("ID,GROUP LABEL\n")


def save_configuration(id_value, group_label_value, directory_path):
    # Path to the experiment configuration file
    config_file = os.path.join(directory_path, 'config', 'experiment_config.csv')

    # Write the ID and GROUP LABEL to the config file
    with open(config_file, 'a') as file:
        file.write(f"{id_value},{group_label_value}\n")

    # Display confirmation message in output_text
    confirmation_message = f"Configuration saved: ID = {id_value}, Group Label = {group_label_value}"
    output_text.insert(tk.END, confirmation_message + "\n")
    output_text.see(tk.END)  # Scroll to the end

    # Clear the entry boxes
    entry_id.delete(0, tk.END)
    entry_group_label.delete(0, tk.END)


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
    directory_path = directory_path_entry.get()
    trim_hours = int(trim_hours_entry.get())
    keep_hours = int(keep_hours_entry.get())
    bin_hours = int(bin_hours_entry.get())

    # Get ID and GROUP LABEL input values
    id_value = entry_id.get()
    group_label_value = entry_group_label.get()

    # Save ID and GROUP LABEL to the experiment configuration file
    save_configuration(id_value, group_label_value, directory_path)

    # Redirect stdout to the output_text widget
    original_stdout = sys.stdout
    sys.stdout = StdoutRedirect(output_text)

    output_text.insert("end", "Cleaning all CLAMS data...\n")
    clean_all_clams_data(directory_path)

    output_text.insert("end", "\nTrimming all cleaned CLAMS data...\n")
    trim_all_clams_data(directory_path, trim_hours, keep_hours)

    output_text.insert("end", "\nBinning all trimmed CLAMS data...\n")
    process_directory(directory_path, bin_hours)

    # Path to experiment config file
    experiment_config_file = os.path.join(directory_path, 'config/experiment_config.csv')

    output_text.insert("end", "\nCombining all binned CLAMS data...\n")
    recombine_columns(directory_path, experiment_config_file)

    output_text.insert("end", "\nAll CLAMS files processed successfully!")

    # Restore the original stdout
    sys.stdout = original_stdout


# Create the main window
root = ttk.Window(themename="superhero")
root.title("CLAMSwrangler")

# Get the default font
default_font = font.nametofont("TkDefaultFont")

# Configure the default font
default_font.configure(size=12, family="Arial")

# Create a header frame for the logo
header_frame = ttk.Frame(root)
header_frame.pack(fill=tk.X)

# Add a logo (replace 'logo.png' with the path to your logo image)
logo_image = tk.PhotoImage(file='./assets/logo.png')
logo_label = ttk.Label(header_frame, image=logo_image)
logo_label.pack(side=tk.TOP, pady=10)

# Set the column weights for the header frame
header_frame.grid_columnconfigure(0, weight=4)
header_frame.grid_columnconfigure(1, weight=1)

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

instructions_frame = ttk.Frame(main_frame)
instructions_frame.grid(row=0, column=0, padx=10, pady=10)

instructions_text = tk.Text(instructions_frame, wrap=tk.WORD, width=60, height=40)
instructions_text.pack()
instructions_text.insert(tk.END,
                         "Instructions:\n\n1. Enter the path to the directory containing all of the .CSV CLAMS data files you wish to process.\n2. Enter the number of hours you wish to trim from the beginning of the data.\n\tRecommend at least 24 hours. \n3. Enter the number of hours of data you wish to keep of CLAMS data to be used downstream.\n4. Enter the size of the bin in hours.\n\tMust be a factor of 12.\n5. Click “Process CLAMS data”.\n\nCongratulations! You saved hours of menial labor! :D\n\n")  # Add your instructions here

# Defines frame for user input
input_frame = ttk.Frame(main_frame)
input_frame.grid(row=0, column=1, padx=10, pady=10)

directory_path_label = ttk.Label(input_frame, text="Directory Path:")
directory_path_label.grid(row=0, column=0, sticky=W, padx=2, pady=2)
browse_button = ttk.Button(input_frame, text="Browse", width=10, command=browse_directory)
browse_button.grid(row=0, column=2, sticky=E, padx=2, pady=2)
directory_path_entry = ttk.Entry(input_frame, width=50)
directory_path_entry.grid(row=0, column=1, sticky=E, padx=2, pady=2)

trim_hours_label = ttk.Label(input_frame, text="Trim Hours:")
trim_hours_label.grid(row=1, column=0, sticky=W, padx=2, pady=2)
trim_hours_entry = ttk.Entry(input_frame, width=50)
trim_hours_entry.grid(row=1, column=1, sticky=E, padx=2, pady=2)

keep_hours_label = ttk.Label(input_frame, text="Keep Hours:")
keep_hours_label.grid(row=2, column=0, sticky=W, padx=2, pady=2)
keep_hours_entry = ttk.Entry(input_frame, width=50)
keep_hours_entry.grid(row=2, column=1, sticky=E, padx=2, pady=2)

bin_hours_label = ttk.Label(input_frame, text="Bin Hours:")
bin_hours_label.grid(row=3, column=0, sticky=W, padx=2, pady=2)
bin_hours_entry = ttk.Entry(input_frame, width=50)
bin_hours_entry.grid(row=3, column=1, sticky=E, padx=2, pady=2)

label_id = ttk.Label(input_frame, text="ID:")
label_id.grid(row=4, column=0, sticky=W, padx=2, pady=2)
entry_id = ttk.Entry(input_frame, width=50)
entry_id.grid(row=4, column=1, sticky=E, padx=2, pady=2)

label_group_label = ttk.Label(input_frame, text="Group Label:")
label_group_label.grid(row=5, column=0, sticky=W, padx=2, pady=2)
entry_group_label = ttk.Entry(input_frame, width=50)
entry_group_label.grid(row=5, column=1, sticky=E, padx=2, pady=2)

# Add "Add Label" button
btn_add_config = ttk.Button(input_frame, text="Add Label",
                            command=lambda: save_configuration(entry_id.get(), entry_group_label.get(),
                                                               directory_path_entry.get()))
btn_add_config.grid(row=6, column=1, padx=2)

output_text = ttk.Text(input_frame, wrap=tk.WORD, width=100, height=20)
output_text.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

start_button = ttk.Button(input_frame, text="Start Processing", command=main_process_clams_data)
start_button.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

# Set weights for rescaling window
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=3)

instructions_frame.grid_rowconfigure(0, weight=1)
instructions_frame.grid_columnconfigure(0, weight=1)

input_frame.grid_rowconfigure(0, weight=1)
input_frame.grid_rowconfigure(1, weight=1)
input_frame.grid_rowconfigure(2, weight=1)
input_frame.grid_rowconfigure(3, weight=1)
input_frame.grid_rowconfigure(4, weight=1)
input_frame.grid_rowconfigure(5, weight=3)
input_frame.grid_columnconfigure(0, weight=1)

# Create a footer frame for the credits
footer_frame = ttk.Frame(root)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

# Add credits text
credits_text = "Developed by Pistilli Lab. Credits: Alan Mizener, Lauren Rentz, Stuart Clayton."
credits_label = ttk.Label(footer_frame, text=credits_text)
credits_label.pack(side=tk.LEFT, padx=10)

# Add Exit button
exit_button = ttk.Button(footer_frame, text="Exit", command=root.quit, bootstyle=DANGER)
exit_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()
