import tkinter as tk
from tkinter import filedialog, font
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


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


from clams_processing import clean_all_clams_data, trim_all_clams_data, process_directory, split_csv_files


def browse_directory():
    """Opens dialog window to select file path.
    """
    folder_selected = filedialog.askdirectory()
    directory_path_entry.delete(0, tk.END)
    directory_path_entry.insert(0, folder_selected)


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

    # Redirect stdout to the output_text widget
    original_stdout = sys.stdout
    sys.stdout = StdoutRedirect(output_text)

    output_text.insert("end", "Cleaning all CLAMS data...\n")
    clean_all_clams_data(directory_path)

    output_text.insert("end", "\nTrimming all cleaned CLAMS data...\n")
    trim_all_clams_data(directory_path, trim_hours, keep_hours)

    output_text.insert("end", "\nBinning all trimmed CLAMS data...\n")
    process_directory(directory_path, bin_hours)

    output_text.insert("end", "\nCombining all binned CLAMS data...\n")
    split_csv_files(directory_path)

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

input_frame = ttk.Frame(main_frame)
input_frame.grid(row=0, column=1, padx=10, pady=10)

path_frame = ttk.Frame(input_frame)
path_frame.pack(pady=5)
directory_path_label = ttk.Label(path_frame, text="Directory Path:")
directory_path_label.grid(row=0, column=0, sticky=tk.W, padx=2)
directory_path_entry = ttk.Entry(path_frame, width=50)
directory_path_entry.grid(row=0, column=1, padx=2)
browse_button = ttk.Button(path_frame, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, padx=2)

trim_hours_frame = ttk.Frame(input_frame)
trim_hours_frame.pack(pady=5)
trim_hours_label = ttk.Label(trim_hours_frame, text="Trim Hours:")
trim_hours_label.grid(row=0, column=0, sticky=tk.W, padx=2)
trim_hours_entry = ttk.Entry(trim_hours_frame, width=50)
trim_hours_entry.grid(row=0, column=1, padx=2)

keep_hours_frame = ttk.Frame(input_frame)
keep_hours_frame.pack(pady=5)
keep_hours_label = ttk.Label(keep_hours_frame, text="Keep Hours:")
keep_hours_label.grid(row=0, column=0, sticky=tk.W, padx=2)
keep_hours_entry = ttk.Entry(keep_hours_frame, width=50)
keep_hours_entry.grid(row=0, column=1, padx=2)

bin_hours_frame = ttk.Frame(input_frame)
bin_hours_frame.pack(pady=5)
bin_hours_label = ttk.Label(bin_hours_frame, text="Bin Hours:")
bin_hours_label.grid(row=0, column=0, sticky=tk.W, padx=2)
bin_hours_entry = ttk.Entry(bin_hours_frame, width=50)
bin_hours_entry.grid(row=0, column=1, padx=2)

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

path_frame.grid_rowconfigure(0, weight=1)
path_frame.grid_columnconfigure(0, weight=1)
path_frame.grid_columnconfigure(1, weight=3)
path_frame.grid_columnconfigure(2, weight=1)

trim_hours_frame.grid_rowconfigure(0, weight=1)
trim_hours_frame.grid_columnconfigure(0, weight=1)
trim_hours_frame.grid_columnconfigure(1, weight=3)

keep_hours_frame.grid_rowconfigure(0, weight=1)
keep_hours_frame.grid_columnconfigure(0, weight=1)
keep_hours_frame.grid_columnconfigure(1, weight=3)

bin_hours_frame.grid_rowconfigure(0, weight=1)
bin_hours_frame.grid_columnconfigure(0, weight=1)
bin_hours_frame.grid_columnconfigure(1, weight=3)

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

output_text = ttk.Text(input_frame, wrap=tk.WORD, width=80, height=20)
output_text.pack(padx=10, pady=10)

start_button = ttk.Button(input_frame, text="Start Processing", command=main_process_clams_data)
start_button.pack(padx=10, pady=10)

root.mainloop()
