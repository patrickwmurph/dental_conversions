import pandas as pd
import numpy as np
import re
from io import StringIO
import csv


def xml_clean(data, working_data):
    
    ## Planned Treatments
    with open(data, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    text = re.sub(r",,?\r?\n,,\r?\n(?!\|)", ";", text)
    text = re.sub(r",,?\r?\n,,\r?\n(?=\|,,)", "", text)
    
    with open(working_data, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print(f"{working_data} written.")