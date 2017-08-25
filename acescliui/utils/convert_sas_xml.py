#! /usr/bin/env python

import argparse
import re
from xml.etree.ElementTree import parse
from acescliui.utils.file_utils import jinjafy_var_name


def create_xml_jinja_template(xml_tmpl, templ_file):
    """
    Jinjafys the three SAS model XML files required for 2ndFlow:  FlowNetwork.xml, AdditionalSettings.xml,
    SolverSettings.xml.  Typically these files are exported from the Shell Tool, but these files could also be provided
    from the excel interface sheet.
    :param xml_tmpl:
    :param templ_file:
    :return:
    """

    pfx_sas = "DISCIP\.SAS\.2NDFLOW"
    pfx_perf = "DISCIP\.PERF\.KREISPR"
    pfx_comp = "DISCIP\.COMP\.GENERIC"
    pfx_turb = "DISCIP\.TURB\.GENERIC"

    re_bc_00 = re.compile(r'(BC\.00\.\w+)')
    re_sas_comp = re.compile(pfx_sas + r'\.(20\..+)\}')
    re_sas_turb = re.compile(pfx_sas + r'\.(40\..+)\}')
    re_sas_perf = re.compile(pfx_sas + r'\.([035]0\..+)\}')

    re_fc_pr = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC\.PR\})')
    re_fc_xml = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC[._\w\d]+\w{2}_XML)\}')

    num_kws = 0

    with open(xml_tmpl, 'rt') as f:
        et = parse(f)

    for e in et.getroot().iter():
        txt = e.text
        if txt:

            # Jinjafy ambient conditions keyword placeholders
            m = re_bc_00.search(txt)
            if m:
                new_txt = '{{{{ {0:s} }}}}'.format( jinjafy_var_name(m.group(1)) )
                e.text = new_txt
                num_kws += 1
                continue

            # Jinjafy compressor keyword placeholders
            m = re_sas_comp.search(txt)
            if m:
                new_txt = '{{{{ {0:s} }}}}'.format( jinjafy_var_name(m.group(1)) )
                e.text = new_txt
                num_kws += 1
                continue

            # Jinjafy turbine keyword placeholders
            m = re_sas_turb.search(txt)
            if m:
                new_txt = '{{{{ {0:s} }}}}'.format( jinjafy_var_name(m.group(1)) )
                e.text = new_txt
                num_kws += 1
                continue

            # Jinjafy other engine parameter keyword placeholders
            m = re_sas_perf.search(txt)
            if m:
                new_txt = '{{{{ {0:s} }}}}'.format( jinjafy_var_name(m.group(1)) )
                e.text = new_txt
                num_kws += 1
                continue

            # Jinjafy flow curve pressure ratio keyword placeholders
            m = re_fc_pr.search(txt)
            if m:
                new_txt = '{{{{ {0:s} }}}}'.format( jinjafy_var_name(m.group(1)) )
                e.text = new_txt
                num_kws += 1
                continue

            # Jinjafy flow curve massflow xml keyword placeholders
            m = re_fc_xml.search(txt)
            if m:
                new_txt = '{{{{ {0:s} }}}}'.format( jinjafy_var_name(m.group(1)) )
                e.text = new_txt
                num_kws += 1
                continue

    print('Replaced {0} keywords.'.format(num_kws))

    et.write(templ_file)


def main():

    parser = argparse.ArgumentParser(
        description='Parses a user provided XML file from 2ndFlow that has been formatted '
                    'for use in the shell tool to include keyword substitutions using '
                    'the harmonized nomenclature, and renames the keywords so that they'
                    'follow jinja naming conventions.'
    )

    parser.add_argument(dest='in_file', help='XML file formatted for use in the Shell Tool.')
    parser.add_argument(dest='out_file', help='XML file to be output with the jinja naming conventions.')
    args = parser.parse_args()
    create_xml_jinja_template(args.in_file, args.out_file)

    # xml_file = '/home/bachm03j/ProjectsSoftware/aces/2ndFlow_test/LC185_model/2ndFlow_ModelData/FlowNetwork.xml'
    # templ_file = '/home/bachm03j/ProjectsSoftware/aces/aces/tools/2ndflow/test/config_sas_model/sample_models/LC185_model/2ndFlow_ModelData/FlowNetwork.xml'
    # xml_file = './LC185/submodels/Submodel437-1_2017-01-19_MODEL.SAS.2NDFLOW.SOLVER.GAS_PROP.dat'
    # templ_file = 'AdditionalData.xml'
    # create_xml_jinja_template(xml_file, templ_file)
    #
    # xml_file = './LC185/submodels/Submodel437-1_2017-01-19_MODEL.SAS.2NDFLOW.SOLVER.SETTINGS.dat'
    # templ_file = 'SolverSettings.xml'
    # create_xml_jinja_template(xml_file, templ_file)


if __name__ == '__main__':
    main()
