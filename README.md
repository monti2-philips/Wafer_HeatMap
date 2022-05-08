# Wafer_HeatMap

Wafer_HeatMap provides tools to create Wafer Level HeatMaps based on the Tx and Rx Peak-Peak results for a wafer.

## Installation
Download Repository either from GitHub through a zipped folder or by cloning this repository.
Next use pip to install the requirements needed.

```
pip install -r requirements.txt
```

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

## Usage
Currently, the Tx and Rx scripts are set to run only one SFC. A for loop can be added to loop through a list of wafers.

Change input value of sfc varaible to run for different wafers. A window will appear after running to determine the output folder for plots to be saved.

Example of "create_wafer_heatmap_Tx_Comparison.py"
``` python
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
df_amb, df_hot = parse_data.Parser_Tx(location, asic_list, sfc).process_data()
plot_wafers.Plotter_Tx(df_amb, df_hot, output_path, asic_list, sfc).plot_wafers()

print(f'Plots saved at {output_path}')
```

## Output
Scripts will output plots similiar to those shown below.

### Example Tx
![Example Tx](./output_examples/R0EQLE%20-%20Tx%20Element%20Peak-Peak___Pk-Pk.png)

### Example Rx
![Example Rx](./output_examples/R0EQLE%20-%20Rx%20Element%20Peak-Peak___Pk-Pk.png)
