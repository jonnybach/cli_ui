#! /usr/bin/env python

import argparse
import json
from acescliui.utils.file_utils import get_units, create_new_param


def transform_shelltool_file(in_file, out_file):
    all_rslts = {}
    with open(in_file, 'r') as f:
        all_rslts = json.load(f)

    d_params = {}
    for k, v in all_rslts.items():

        # Add to compressor data set
        new_k = k#jinjafy_var_name(k)
        new_u = get_units(new_k)
        new_v = create_new_param(v, units=new_u)
        d_params[new_k] = new_v

    with open(out_file, 'wt') as f:
        json.dump(d_params, f, indent=4)


def main():

    parser = argparse.ArgumentParser(
        description='Parses a parameter json file that has been exported from the shell tool, and that contains a '
                    'listing of harmonized nomenclature formatted parameters and creates a new file with the dictionary '
                    'keys converted to conform to the jinja naming convetions.'
    )

    parser.add_argument(dest='in_file', help='Parameter json file exported from the Shell Tool.')
    parser.add_argument(dest='out_file', help='Parameter json file to be output with the jinja naming conventions.')
    args = parser.parse_args()
    transform_shelltool_file(args.in_file, args.out_file)


if __name__ == '__main__':
    main()
