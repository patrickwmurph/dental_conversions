import pandas as pd
import numpy as np
import re
from io import StringIO
import csv


def xml_clean():
    
    ## Planned Treatments
    with open("data\DXE_Extract_PlannedTreatment.csv", "r", encoding="utf-8", newline="") as f:
        text = f.read()

    text = re.sub(r",,?\r?\n,,\r?\n(?!\|)", ";", text)
    text = re.sub(r",,?\r?\n,,\r?\n(?=\|,,)", "", text)
    
    with open("planned_treatments.csv", "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print("planned_treatments.csv written.")

