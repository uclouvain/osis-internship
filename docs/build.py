##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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


def generate_pdf():
    print("Generating PDF...")
    subprocess.check_output(['asciidoctor-pdf', '-a', 'pdf-stylesdir=resources/themes', '-a', 'pdf-styles=osis',
                             DOCUMENTATION_FILE.format("adoc")])
    print("PDF file generated.")


def generate_html():
    print("Generating HTML...")
    subprocess.check_output(['asciidoctor', DOCUMENTATION_FILE.format("adoc")])
    print("HTML file generated.")


def generate_homepage():
    message = """
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
        </html>""".format(DOCUMENTATION_FILE.format("html"), DOCUMENTATION_FILE.format("pdf"))

    with open('index.html', 'w') as html_file:
        html_file.write(message)


def initialize_content():
    length_args = len(sys.argv)
    if length_args > 2 and sys.argv[1] == 'html' and sys.argv[2] == 'index':
        subprocess.check_output(['xdg-open', 'index.html'])
    elif len(sys.argv) > 1:
        subprocess.check_output(['xdg-open', DOCUMENTATION_FILE.format(sys.argv[1])])


def show_help():
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print("Examples of use:")
        print("  $ python3 build.py             Generates all artifacts.")
        print("  $ python3 build.py html        Generates all artifacts and opens the html artifact.")
        print("  $ python3 build.py pdf         Generates all artifacts and opens the pdf artifact.")
        print("  $ python3 build.py html index  Generates all artifacts and opens the index page artifact.")
        return True
    return False


def build():
    if not show_help():
        generate_pdf()
        generate_html()
        generate_homepage()
        initialize_content()


build()
