import re
from jinja2 import Template


class ConstrainedText:
    """
    """

    # Text edit flag constants
    k_tag_rw = "{@ WRITEABLE @}"
    k_tag_ro = "{@ READONLY @}"
    k_tag_map = "{@ MAPPED @}"
    re_jin_exp = re.compile(r'{{\s[a-zA-Z_][a-zA-Z0-9_]*\s}}') 

    def __init__(self):
        self._jin_cntxt = {}
        self._template_text = ""
        self._has_data = False
        self._has_template = False

    #
    # def _jinjafy(self, dict_context, seperator="."):
    #     """
    #     Returns a dictionary whose keys have been processed such that each key follows the
    #     python naming convention pattern [a-zA-Z_][a-zA-Z0-9_]*.  It does this by:
    #        1) replacing each seperator by an underscore.
    #        2) appending an underscore to each key
    #
    #     This allows to generate dictionary contexts that contain dotted seperators such as that
    #     """

    def set_no_mapped_data(self):
        """
        Clears the mapped data context so that there is no mapped data
         and sets the flag that data has been provided to the constrained text instance
        :return: None
        """
        self._jin_cntxt.clear()
        self._has_data = True

    def get_mapped_data(self, mapped_data):
        """
        Extracts the numerical values form the mapped data dictionary which is of the form:
        "mapped_data": {
            "category_1": {
                "param_1": {
                    "value": xxx
                    "units": xxx
                },
                ...
                "param_n": {
                    "value": xxx
                    "units": xxx
                }
            },
            ...
            "category_n": {
                "param_1": {
                    "value": xxx
                    "units": xxx
                },
                ...
                "param_n": {
                    "value": xxx
                    "units": xxx
                }
            }
        }
        And generates a dictionary that is used as the database for rendering the final text file from the
        jinja formatted template and the mapped data provided to this method.

        :param mapped_data:
        :return: nothing
        """
        # Flatten context for jinja, also search through leaf value items, if any are strings
        # which contain line endings, append mapped keyword after each new line.
        self._jin_cntxt.clear()
        for d in mapped_data.values():
            for k, i in d.items():
                new_v = i["value"] 
                # if isinstance(new_v, str):
                #     new_v = re.sub(r'\n', self.k_tag_map+r'\n ', new_v)
                self._jin_cntxt[k] = new_v
        self._has_data = True

    def get_template_from_file(self, template_path):
        with open(template_path, "rt") as fin:
            template_lines = fin.readlines()
        self._process_template(template_lines)

    def get_template_from_string(self, template_string):
        template_lines = template_string.split("\n")
        for i in range(len(template_lines)):
            template_lines[i] += "\n"
        self._process_template(template_lines)

    def _process_template(self, template_lines):
        """
        Originally this method would find any lines containing Jinja variable namings and then add
        an identifier at the end to mark the line as mapped, but this is no longer used so this method
        is kind of no longer necessary (right now it really does nothing)
        :param template_lines: 
        :return: 
        """
        self._template_text = ""
        for line in template_lines:
            if self.re_jin_exp.search(line):
                self._template_text = "{0:s}{1:s} {2:s}\n".format(self._template_text, line.rstrip('\n'), '')
            else:
                self._template_text = "{0:s}{1:s}".format(self._template_text, line)
        self._has_template = True

    def can_render(self):
        """
        Returns true of the constrained text is ready to be rendered, otherwise returns false.
         Text can only be rendered if data has been mapped and a template file has been processed.
        """
        return self._has_data and self._has_template

    def template_text(self):
        return self._template_text

    def render_textlines(self):
        if not self.can_render():
            return None
        else:
            rendered_string = self.render_text()
            rendered_lines = rendered_string.split('\n')
            return rendered_lines

    def render_text(self):
        if not self.can_render():
            return None
        else:
            template = Template(self._template_text, trim_blocks=True, lstrip_blocks=True)
            rendered_string = str(template.render(self._jin_cntxt))
            return rendered_string
