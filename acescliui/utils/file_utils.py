import re
import json
import logging
import os
import shutil
from xml.etree.ElementTree import parse

# Only export the following
__all__ = ['get_units', 'get_keywords_in_xml', 'jinjafy_var_name', 'copy_into']


def create_new_param(value, units="na"):
    p = {'value': value, 'units': units}
    return p


def get_units(key, press=None, temp=None):
    """
    
    :param key: 
    :param press: Override default pressure units of bar with something else like Pa. 
    :param temp: Override default temperature units of deg C with something else like K.
    :return: 
    """

    p_units = press if press else 'bar'
    t_units = temp if temp else 'deg C'

    new_u = ""
    if re.search(r"\.P_T|\.P_S", key):
        new_u = p_units
    elif re.search(r"\.DP_T|\.DP_S", key):
        new_u = "mbar"
    elif re.search(r"\.T_T|\.T_S|\.T_ISO", key):
        new_u = t_units
    elif re.search(r"\.V_", key):
        new_u = "m/s"
    elif re.search(r"\.M_*", key):
        new_u = "kg/s"
    elif re.search(r"\.RAD", key):
        new_u = "mm"
    elif re.search(r"\.RHO", key):
        new_u = "kg/m^3"
    elif re.search(r"\.RHO{0}", key):
        new_u = "%"
    elif re.search(r"\.N", key):
        new_u = "RPM"
    elif re.search(r"\.LHV", key):
        new_u = "kJ/kg"
    elif re.search(r"\.H_T", key):
        new_u = "kJ/kg"
    elif re.search(r"\.LSV", key):
        new_u = "%"
    elif re.search(r"\.[CHOSA]_W", key):
        new_u = "wt_%"
    elif re.search(r"GN\.ETA", key):
        new_u = "%"

    return new_u


def jinjafy_var_name(old_str):
    #new_str = "_{0:s}".format(old_str.replace('.', "_"))
    #new_str = "{0:s}".format(new_str.replace('-', "_"))
    new_str = 'kw["{0:s}"]'.format(old_str)
    return new_str


def get_keywords_in_textfile(text_file):
    with open(text_file, 'rt') as f:
        text = f.read()
    return get_keywords_in_text(text)


def get_keywords_in_text(text_tmpl):
    """
    Searches through a given string and looks for the presence of any keywords that follow the required specification
    for the shell tool (harmonized nomenclature keywords with surrounding curly braces, returning an array of these
    parameters.
    TODO: doesn't properly return a list of parameters that are optional
    :param text_tmpl: text string to search
    :return: dictionary of found keywords according to the category.
    """
    #re_jinj_kw = re.compile(r'\{\{\s+(\w+)\s+\}\}')  # If using the underscore based parameter syntax
    re_jinj_kw = re.compile(r'(?:format)*[\s(]kw\["([\w\d._-]+)"][\s)]')
    m = re_jinj_kw.findall(text_tmpl)
    logging.debug(' _get_keywords_in_text - Found {0} keywords'.format(len(m)))
    return m


def get_keywords_in_xml(xml_tmpl):
    """
    Searches through a given xml file and looks for the presence of any keywords that follow the required specification
    for the shell tool (harmonized nomenclature keywords with surrounding curly braces, returning an array of these
    parameters.
    :param xml_tmpl: XML file to search
    :return: dictionary of found keywords according to the category.
    """

    # # For original shell tool nomenclature
    # pfx_sas = r'DISCIP\.SAS\.2NDFLOW'
    # pfx_perf = r'DISCIP\.PERF\.KREISPR'
    # pfx_comp = r'DISCIP\.COMP\.GENERIC'
    # pfx_turb = r'DISCIP\.TURB\.GENERIC'
    #
    # re_bc_00 = re.compile(r'(BC\.00\.\w+)')
    # re_sas_comp = re.compile(pfx_sas + r'\.(20\.\w+)\}')
    # re_sas_turb = re.compile(pfx_sas + r'\.(40\.\w+)\}')
    # re_sas_perf = re.compile(pfx_sas + r'\.([035]0\.\w+)\}')
    #
    # re_fc_pr = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC\.PR\})')
    # re_fc_xml = re.compile(r'MODEL\.SAS\.2NDFLOW\.(\w+\..+\.FC[._\w\d]+\w{2}_XML)\}')

    # For jinja nomenclature
    pfx_sas = r'DISCIP_SAS_2NDFLOW'
    pfx_perf = r'DISCIP_PERF_KREISPR'
    pfx_comp = r'DISCIP_COMP_GENERIC'
    pfx_turb = r'DISCIP_TURB_GENERIC'

    re_bc_00 = re.compile(r'(_BC_00_\w+)\s*\}\}')
    re_sas_comp = re.compile(r'(_20_\w+)\s*\}\}')
    re_sas_turb = re.compile(r'(_40_\w+)\s*\}\}')  # TODO: Collides with the flow curve stuff down below!!!!  Hack is to search for flow curve stuff first
    re_sas_perf = re.compile(r'\s+(_[035]0_\w+)\s*\}\}')

    re_fc_pr = re.compile( r'(_\w+_.+_FC_PR)\s*\}\}')
    re_fc_xml = re.compile(r'(_\w+_.+_FC[._\w\d]+\w{2}_XML)\s*\}\}')

    with open(xml_tmpl, 'rt') as f:
        et = parse(f)

    kws = {
        'amb_bcs': [],
        'other_bcs': [],
        'comp_bcs': [],
        'turb_bcs': [],
        'turb_fcs': []
    }

    num_kws = 0
    for e in et.getroot().iter():
        txt = e.text
        if txt:

            # flow curve pressure ratio keyword placeholders
            m = re_fc_pr.search(txt)
            if m:
                kws['turb_fcs'].append(m.group(1))
                num_kws += 1
                continue

            # flow curve massflow xml keyword placeholders
            m = re_fc_xml.search(txt)
            if m:
                kws['turb_fcs'].append(m.group(1))
                num_kws += 1
                continue

            # ambient conditions keyword placeholders
            m = re_bc_00.search(txt)
            if m:
                kws['amb_bcs'].append(m.group(1))
                num_kws += 1
                continue

            # compressor keyword placeholders
            m = re_sas_comp.search(txt)
            if m:
                kws['comp_bcs'].append(m.group(1))
                num_kws += 1
                continue

            # turbine keyword placeholders
            m = re_sas_turb.search(txt)
            if m:
                kws['turb_bcs'].append(m.group(1))
                num_kws += 1
                continue

            # other engine parameter keyword placeholders
            m = re_sas_perf.search(txt)
            if m:
                kws['other_bcs'].append(m.group(1))
                num_kws += 1
                continue

    logging.debug(' get_keywords_in_xml - Found {0} keywords'.format(num_kws))
    return kws


def copy_into(src, dst, symlinks=False):
    """
    Source copied from https://docs.python.org/3.5/library/shutil.html#module-shutil
    :param src:
    :param dst:
    :param symlinks:
    :return:
    """
    names = os.listdir(src)
    # os.makedirs(dst) do not create new directory
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                shutil.copytree(srcname, dstname, symlinks)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # can't copy file access times on Windows
        if why.winerror is None:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
