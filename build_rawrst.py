#!/usr/bin/env python
# -*- coding:UTF-8 -*-
"""Build RST files to display raw files in Sphinx"""

import os
import os.path
import sys


# Templates
RAWRST_HEADER = """``{dirpath}/{filename}``
{underline}
:download:`Download file<{filename}>`

"""


def build_rawrst_file(dirpath, filename):
    """Build the corresponding raw RST file for filename in dirpath"""
    if '/' in filename or '\\' in filename:
        raise ValueError("Invalid filename: {}".format(filename))

    content = RAWRST_HEADER
    if filename.endswith(('.ico', '.jpg', '.png')):
        content += '.. image:: {filename}\n   :alt: {dirpath}/{filename}\n'
    else:
        content += '.. literalinclude:: {filename}\n'
        if filename.endswith(('.htm', '.html')):
            content += '   :language: html\n'
        elif filename.endswith(('.ini', '.inf')):
            content += '   :language: ini\n'
        elif 'apache' in filename:
            content += '   :language: apache\n'
        elif 'lighttpd' in filename:
            content += '   :language: lighttpd\n'
        elif 'nginx' in filename:
            content += '   :language: nginx\n'
        else:
            content += '   :language: sh\n'

    content = content.format(
        dirpath=dirpath,
        filename=filename,
        underline='=' * (len(dirpath) + len(filename) + 5))

    with open(os.path.join(dirpath, filename + '.raw.rst'), 'w') as rstfd:
        rstfd.write(content)


def build_rawrst_dir(dirpath):
    """Build all needed raw RST files under dirpath"""
    for root, _, files in os.walk(dirpath):
        for filename in files:
            if filename.lower().endswith(('~', '.bak', '.rst')):
                continue
            build_rawrst_file(root, filename)


if __name__ == '__main__':
    for directory in sys.argv:
        build_rawrst_dir(directory)
