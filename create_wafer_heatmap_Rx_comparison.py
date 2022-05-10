# Import Libraries, Input Directory, ASIC List
import json
import os
import parse_data
import plot_wafers
from tkinter import filedialog
from tkinter import *

# Ask for directory to store HeatMap output
root = Tk()
root.withdraw()
output_path = filedialog.askdirectory(mustexist=True)

# TODO Add section for input SFC, maybe CLI arguments for this
# Input SFC
sfc = 'R0EQLE'

# Confirm Config file exists
json_file = os.path.abspath('configuration_app.json')
if not os.path.exists(json_file):
    print(
        f'File "{os.path.basename(json_file)}" does not exist in source directory.')

# Opens JSON Configuration File
with open(json_file) as f:
    js = json.load(f)

# Unpack Location and ASIC List from JSON
location = os.path.abspath(js["input_directory"])
asic_list = js["asic_list"]

# Run Parser_Rx then Plotter_Rx
df_amb, df_hot, df_rx = parse_data.Parser(
    location, asic_list, sfc).process_data()
plot_wafers.Plotter_Rx(df_rx, output_path,
                       asic_list, sfc).plot_wafers()

print(f'Plots saved at {output_path}')
