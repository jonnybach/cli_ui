#! /usr/bin/env python

import argparse
import re
from acescliui.utils.file_utils import jinjafy_var_name


def jinjafy_template_file(in_file, out_file):
    """
    :param in_file:
    :param out_file:
    :return:
    """

    re_hrm_nom = re.compile(r'(\{[\w\d-]+\.{1}[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\})')
    re_parm = re.compile(r'\{([\w\d-]+\.{1}[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*\.?[\w\d-]*)\}')

    num_kws = 0
    new_lines = []
    with open(in_file, 'rt') as f:
        #text = f.read()
        for line in f.readlines():
            line_parts = re_hrm_nom.split(line)
            new_line = ''
            for prt in line_parts:
                m = re.search(re_parm, prt)
                if m:
                    prt = '{{{{ {0:s} }}}}'.format(jinjafy_var_name(m.group(1)))
                    num_kws += 1
                new_line += prt
            new_lines.append(new_line)

    print('Replaced {0} keywords.'.format(num_kws))

    with open(out_file, 'wt') as f:
        f.writelines(new_lines)


def main():

    parser = argparse.ArgumentParser(
        description='Parses a user provided XML file from 2ndFlow that has been formatted '
                    'for use in the shell tool to include keyword substitutions using '
                    'the harmonized nomenclature, and renames the keywords so that they'
                    'follow jinja naming conventions.'
    )

    parser.add_argument(dest='in_file', help='Template file formatted for use in the Shell Tool.')
    parser.add_argument(dest='out_file', help='Template file to be output with the jinja naming conventions.')
    args = parser.parse_args()
    jinjafy_template_file(args.in_file, args.out_file)


if __name__ == '__main__':
    main()
