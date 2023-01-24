# Wafer_HeatMap

Wafer_HeatMap provides tools to create Wafer Level Heat Maps based on the Tx and Rx Peak-Peak results for a wafer.
___
## Installation
Download Repository either from GitHub through a zipped folder or by cloning this repository. If using zipped folder, extract contents into a folder that will be used for following steps.

### Creating Virtual Environment
If you wish to create a virtual environment to use with this set of scripts, go to the extracted folder in your windows explorer and type "cmd" in the address bar and hit enter.

Once the command prompt is open with the current working directory at the desired folder, run the following command.

```
C:\PATH\TO\FOLDER> python -m venv env
```

This will create a virtual environment named "env" in the desired directory location. Once this virtual environment is created, you can activate it by running the following command.

```
C:\PATH\TO\FOLDER> .\env\Scripts\activate
```

Once activated, your command prompt line should look like this.

```
(env) C:\PATH\TO\FOLDER> 
```

### Installing Requirements
Use pip to install the requirements needed.

Installing to Global Python Installation
```
pip install -r requirements.txt
```

Installing to Virtual Environment
```
(env) C:\PATH\TO\FOLDER> pip install -r requirements.txt
```
___
## Configuration
The "configuration_app.json" file must be updated with correct input directory. "configuration_app_github.json" has representative path only.

``` json
{
  "input_directory": "/PATH/TO/DATA",
  "asic_list": [
                "001_006","001_007","001_008",
                "002_004","002_005","002_006","002_007","002_008","002_009","002_010",
                "003_002","003_003","003_004","003_005","003_006","003_007","003_008","003_009","003_010","003_011","003_012",
                "004_002","004_003","004_004","004_005","004_006","004_007","004_008","004_009","004_010","004_011","004_012",
                "005_001","005_002","005_003","005_004","005_005","005_006","005_007","005_008","005_009","005_010","005_011","005_012","005_013",
                "006_002","006_003","006_004","006_005","006_006","006_007","006_008","006_009","006_010","006_011","006_012",
                "007_002","007_003","007_004","007_005","007_006","007_007","007_008","007_009","007_010","007_011","007_012",
                "008_004","008_005","008_006","008_007","008_008","008_009","008_010",
                "009_006","009_007","009_008"
                ]
}
```
___
## Usage
Three scripts are currently available:
- create_wafer_heatmap_comparison.py - Plots Tx and Rx for SFC
- create_wafer_heatmap_Tx_comparison.py - Plots only Tx for SFC
- create_wafer_heatmap_Rx_comparison.py - Plots only Rx for SFC
  
Currently, the scripts are set to run only one SFC. A for loop can be implemented to loop through a list of wafers.
___
## Running

### Before Running
**Change input value of the "sfc" varaible to run for different wafers.**

Example of "create_wafer_heatmap_comparison.py"
``` python
# Import Libraries, Input Directory, ASIC List
import json
import os
from tkinter import *
from tkinter import filedialog

import parse_data
import plot_wafers

# Ask for directory to store HeatMap output
root = Tk()
root.withdraw()
output_path = filedialog.askdirectory(
    title="Select Save Location", mustexist=True)

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

# Run Parser_Tx then Plotter_Tx
df_amb, df_hot, df_rx = parse_data.Parser(
    location, asic_list, sfc).process_data()
plot_wafers.Plotter_Tx(df_amb, df_hot, output_path,
                       asic_list, sfc).plot_wafers()
plot_wafers.Plotter_Rx(df_rx, output_path,
                       asic_list, sfc).plot_wafers()

print(f'Plots saved at {output_path}')
```

### Running From Command Prompt
The script can be run from the command prompt or an IDE of choice (VSCode, PyCharm, Spyder, etc.)

To run from the command prompt (either in a virtual environment or global python) use the following commands.

Combined Script
```
(env) C:\PATH\TO\FOLDER> python create_wafer_heatmap_comparison.py
```

Tx Script
```
(env) C:\PATH\TO\FOLDER> python create_wafer_heatmap_Tx_comparison.py
```

Rx Script
```
(env) C:\PATH\TO\FOLDER> python create_wafer_heatmap_Rx_comparison.py
```

A window will appear after running to determine the output folder for plots to be saved.
___
## Output
Scripts will output plots similiar to those shown below.

### Example Tx
![Example Tx](./output_examples/R0EQLE%20-%20Tx%20Element%20Peak-Peak___Pk-Pk.png)

### Example Rx
![Example Rx](./output_examples/R0EQLE%20-%20Rx%20Element%20Peak-Peak___Pk-Pk.png)
