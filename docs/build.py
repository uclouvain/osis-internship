##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import sys
import subprocess


DOCUMENTATION_FILE = 'user-manual_fr.{}'
HOMEPAGE_CONTENT = """
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>OSIS - Internship - Documentation</title>
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css"
                      integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M"
                      crossorigin="anonymous">
            </head>
            <body>
                <div class="container">
                    <br><br>
                    <img src="resources/images/logo.png" width="250">
                    <h1>Documentation de l'application Stages de médecine</h1>
                    <br><br>
                    <h3><a href="{}">Documentation en ligne</a></h3>
                    <h3><a href="{}">Documentation en PDF</a></h3>
                </div>
            </body>
        </html>"""

def increment_version():
    """"""
    return

def generate_pdf():
    print("Generating PDF...")
    path = get_path()
    subprocess.check_output(['asciidoctor-pdf',
                             '-a', 'pdf-stylesdir={}resources/themes'.format(path),
                             '-a', 'pdf-styles=osis', "{}{}".format(path, DOCUMENTATION_FILE.format("adoc"))])
    print("PDF file generated.")


def generate_html():
    print("Generating HTML...")
    path = get_path()
    subprocess.check_output(['asciidoctor', "{}{}".format(path, DOCUMENTATION_FILE.format("adoc"))])
    print("HTML file generated.")


def generate_homepage():
    print("Generating Homepage...")
    path = get_path()
    with open('{}index.html'.format(path), 'w') as html_file:
        html_file.write(HOMEPAGE_CONTENT.format(DOCUMENTATION_FILE.format("html"),
                                                DOCUMENTATION_FILE.format("pdf")))
    print("Homepage generated.")


def initialize_content():
    if "-v" in sys.argv:
        v_idx = sys.argv.index("-v")
        if sys.argv[v_idx + 1] == "index":
            subprocess.check_output(['xdg-open', 'index.html'])
        else:
            subprocess.check_output(['xdg-open', DOCUMENTATION_FILE.format(sys.argv[v_idx + 1])])


def show_help():
    if "-h" in sys.argv:
        print("Examples of use:")
        print()
        print("  $ python3 build.py           Generates all artifacts.")
        print("  $ python3 build.py -v html   Generates all artifacts and opens the html artifact.")
        print("  $ python3 build.py -v index  Generates all artifacts and opens the index page artifact.")
        print("  $ python3 build.py -v pdf    Generates all artifacts and opens the pdf artifact.")
        print()
        print("If you are running the build outside of the folder internship/docs: ")
        print()
        print("  $ python3 build.py -p [path-to-docs]")
        return True
    return False


def get_path():
    if "-p" in sys.argv:
        return sys.argv[sys.argv.index("-p") + 1]
    else:
        return ""


def build():
    if not show_help():
        increment_version()
        generate_pdf()
        generate_html()
        generate_homepage()
        initialize_content()


if __name__ == '__main__':
    build()
