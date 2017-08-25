#! /usr/bin/env python

import argparse
import json
import re
import os
from acescliui.utils.file_utils import jinjafy_var_name, get_units, create_new_param


def create_datasets(file):
    """
    Processes a json file that has been exported from the shell tool, which contains the required key-value pairs
    to describe the Compressor BCs, Turbine BCs, other engine BCs, and the Turbine flow curves.  Creates 4 seperate
    files for each of these datasets that can be used as input into the SAS Configure BCs activity block.

    NOTE: uses hard coded file names in the python script so refactoring is needed to make this more generic

    :return:
    """

    work_dir, _ = os.path.split(file)

    all_rslts = {}
    with open(file, 'r') as f:
        all_rslts = json.load(f)

    pfx_sas = "DISCIP\.SAS\.2NDFLOW"
    pfx_perf = "DISCIP\.PERF\.KREISPR"
    pfx_comp = "DISCIP\.COMP\.GENERIC"
    pfx_turb = "DISCIP\.TURB\.GENERIC"

    re_bc_00 = re.compile(r'(BC\.00\..+)')
    re_sas_comp = re.compile(pfx_sas + r'\.(20\..+)')
    re_sas_turb = re.compile(pfx_sas + r'\.(40\..+)')
    re_sas_perf = re.compile(pfx_sas + r'\.([035]0\..+)')

    re_fc_pr = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC\.PR$)')
    re_fc_csv = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC\.\w{2}_CSV)')
    re_fc_xml = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC[._\w\d]+\w{2}_XML)')

    d_perf = {}
    d_comp = {}
    d_turb = {}
    d_fc_pr = {}
    d_fc_csv = {}
    d_fc_xml = {}

    for k, v in all_rslts.items():

        # Add to compressor data set
        m = re_sas_comp.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_comp[new_k] = new_v
            continue

        # Add to perf data set
        m = re_sas_perf.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_perf[new_k] = new_v
            continue

        m = re_bc_00.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_perf[new_k] = new_v
            continue

        # Add to turb data set
        m = re_sas_turb.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_turb[new_k] = new_v
            continue

        # Add to fc PR data set
        m = re_fc_pr.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_fc_pr[new_k] = new_v
            continue

        # Add to fc CSV data set
        m = re_fc_csv.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_fc_csv[new_k] = new_v
            continue

        # Add to fc XML data set
        m = re_fc_xml.search(k)
        if m:
            new_k = m.group(1)
            new_u = get_units(new_k)
            new_v = create_new_param(v, units=new_u)
            d_fc_xml[new_k] = new_v
            continue

    with open(os.path.join(work_dir, 'comp_results.json'), 'wt') as f:
        json.dump(d_comp, f, indent=4)

    with open(os.path.join(work_dir, 'perf_results.json'), 'wt') as f:
        json.dump(d_perf, f, indent=4)

    with open(os.path.join(work_dir, 'turb_results.json'), 'wt') as f:
        json.dump(d_turb, f, indent=4)

    with open(os.path.join(work_dir, 'fc_results.json'), 'wt') as f:
        d_fc_pr.update(d_fc_xml)
        json.dump(d_fc_pr, f, indent=4)


def main():

    parser = argparse.ArgumentParser(
        description='Processes a json file that has been exported from the shell tool, which contains the required '
                    'key-value pairs to describe the Compressor BCs, Turbine BCs, other engine BCs, and the Turbine '
                    'flow curves.  Creates 4 separate files for each of these data sets that can be used as input '
                    'into the SAS Configure BCs activity block.'
    )

    parser.add_argument(dest='param_file', help='Parameter json file exported from the Shell Tool.')
    args = parser.parse_args()
    create_datasets(args.param_file)


if __name__ == '__main__':
    main()
