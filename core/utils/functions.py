import re
import subprocess  # nosec

from django.apps import AppConfig
from django.apps import apps
from django.http import Http404


# return number of pages of pdf using pdfinfo
# on error return 'unbekannt'
def get_pdf_page_count(path):
    output = subprocess.run(  # nosec
        ["pdfinfo", path],
        stdout=subprocess.PIPE,
    ).stdout.decode()
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return line.split(":")[1].strip()

    return "unbekannt"


# escape characters to prevent tex-injection
def tex_escape(string):
    string = str(string)
    conv = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
        "\\": r"\textbackslash{}",
        "<": r"\textless{}",
        ">": r"\textgreater{}",
    }
    regex = re.compile(
        "|".join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: -len(item))),
    )

    return regex.sub(lambda match: conv[match.group()], string)


# escape characters to prevent xml-injection
def xml_escape(string):
    conv = {
        "&": r"&amp;",
        "<": r"&lt;",
        ">": r"&gt;",
        '"': r"&quot;",
        "'": r"&#39;",
    }
    regex = re.compile(
        "|".join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: -len(item))),
    )

    return regex.sub(lambda match: conv[match.group()], string)


# get model from name or raise 404
def get_model(model_name):
    try:
        return AppConfig.get_model(apps.get_app_config("core"), model_name)
    except LookupError:
        raise Http404
