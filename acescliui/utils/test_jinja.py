# System imports
import sys
import json
import os
import shutil
import tempfile

# My imports
from model.readonly_model import TableModel
from core.constrained_text import ConstrainedText


def main():

    # Locate workspace created by ACES using tool core object
    oc_file = "./templates/OperatingConditionsDataset_EXAMPLE.json"
    
    # Load op conditions json file into dictionary
    d = {}
    with open(oc_file, 'r') as f:
        d["stuff"] = json.load(f)
        print(json.dumps(d, sort_keys=True, indent=4))
    
    ct = ConstrainedText()
    ct.get_mapped_data(d)
    ct.get_template("templates/kreispr.main")    
    raw_text = ct.render_textlines()
    for l in raw_text:
        print(l)

if __name__ == '__main__':
    main()