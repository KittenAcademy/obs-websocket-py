#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from six.moves.urllib.request import urlopen
from collections import OrderedDict

import_url = "https://raw.githubusercontent.com/Palakis/obs-websocket/4.x-current/docs/generated/comments.json"  # noqa: E501


def clean_var(string):
    """
    Converts a string to a suitable variable name by removing not allowed
    characters.
    """
    string = string.replace('-', '_').replace('[]', '')
    return string


def generate_classes():
    """Generates the necessary classes."""
    print("Downloading {} for last API version.".format(import_url))
    data = json.loads(urlopen(import_url).read().decode('utf-8'), object_pairs_hook=OrderedDict)
    print("Download OK. Generating python files...")

    for event in ['requests', 'events']:
        if event not in data:
            raise Exception("Missing {} in data.".format(event))
        with open('obswebsocket/{}.py'.format(event), 'w') as f:

            f.write("#!/usr/bin/env python\n")
            f.write("# -*- coding: utf-8 -*-\n")
            f.write("\n")
            f.write("# THIS FILE WAS GENERATED BY generate_classes.py - DO NOT EDIT #\n")
            f.write("# (Generated on {}) #\n".format(datetime.now().isoformat(" ")))
            f.write("\n")
            f.write("from .base_classes import Base{}\n".format(event))
            f.write("\n\n")
            for sec in data[event]:
                for i in data[event][sec]:
                    f.write("class {}(Base{}):\n".format(i['name'], event))
                    f.write("    \"\"\"{}\n\n".format(i['description']))

                    arguments_default = []
                    arguments = []
                    try:
                        if len(i['params']) > 0:
                            f.write("    :Arguments:\n")
                            for a in i['params']:
                                a['name'] = a['name'].replace("[]", ".*")
                                f.write("       *{}*\n".format(clean_var(a['name'])))
                                f.write("            type: {}\n".format(a['type']))
                                f.write("            {}\n".format(a['description']))
                                if 'optional' in a['type']:
                                    arguments_default.append(a['name'])
                                else:
                                    arguments.append(a['name'])
                    except KeyError:
                        pass

                    returns = []
                    try:
                        if len(i['returns']) > 0:
                            f.write("    :Returns:\n")
                            for r in i['returns']:
                                r['name'] = r['name'].replace("[]", ".*")
                                f.write("       *{}*\n".format(clean_var(r['name'])))
                                f.write("            type: {}\n".format(r['type']))
                                f.write("            {}\n".format(r['description']))
                                returns.append(r['name'])
                    except KeyError:
                        pass

                    arguments = set([x.split(".")[0] for x in arguments])
                    arguments_default = set([x.split(".")[0] for x in arguments_default])
                    arguments_default = set([x for x in arguments_default if x not in arguments])
                    returns = set([x.split(".")[0] for x in returns])

                    f.write("    \"\"\"\n\n")
                    f.write("    def __init__({}):\n".format(
                        ", ".join(
                            ["self"]
                            + [clean_var(a) for a in arguments]
                            + [clean_var(a) + "=None" for a in arguments_default]
                        )
                    ))
                    f.write("        Base{}.__init__(self)\n".format(event))
                    f.write("        self.name = '{}'\n".format(i['name']))
                    for r in returns:
                        f.write("        self.datain['{}'] = None\n".format(r))
                    for a in arguments:
                        f.write("        self.dataout['{}'] = {}\n".format(a, clean_var(a)))
                    for a in arguments_default:
                        f.write("        self.dataout['{}'] = {}\n".format(a, clean_var(a)))
                    f.write("\n")
                    for r in returns:
                        cc = "".join(x[0].upper() + x[1:] for x in r.split('-'))
                        f.write("    def get{}(self):\n".format(clean_var(cc)))
                        f.write("        return self.datain['{}']\n".format(r))
                        f.write("\n")
                    f.write("\n")

    print("API classes have been generated.")


if __name__ == '__main__':
    generate_classes()
