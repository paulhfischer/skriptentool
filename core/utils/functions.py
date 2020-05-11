import re
import subprocess  # nosec

from django.apps import AppConfig
from django.apps import apps
from django.http import Http404
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


# return number of pages of pdf using pdfinfo
# on error return 'unknown'
def get_pdf_page_count(path):
    output = subprocess.run(  # nosec
        ["pdfinfo", path],
        stdout=subprocess.PIPE,
    ).stdout.decode()
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return line.split(":")[1].strip()

    return "unknown"


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


# get choices for all semesters in range
def get_semesters(start, end):
    year_start = int(start[1:])
    year_end = int(end[1:])

    choices = []

    # add summerterm
    if start.startswith("S"):
        choices.append(
            (
                f"S{int(start[1:])}",
                format_lazy("{} {}", _("summer term"), str(int(start[1:]))),
            ),
        )

    # add choices in range
    for year in range(year_start, year_end):
        choices.extend(
            [
                (
                    f"W{year}",
                    format_lazy("{} {} / {}", _("winter term"), str(year), str(year + 1)),
                ),
                (
                    f"S{year + 1}",
                    format_lazy("{} {}", _("summer term"), str(year + 1)),
                ),
            ],
        )

    # add winterterm
    if end.startswith("W"):
        choices.append(
            (
                f"W{int(end[1:])}",
                format_lazy(
                    "{} {} / {}",
                    _("winter term"),
                    str(int(end[1:])),
                    str(int(end[1:]) + 1),
                ),
            ),
        )

    choices.reverse()

    return choices
