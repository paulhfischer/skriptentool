import re
import subprocess


def get_pdf_page_count(path):
    output = subprocess.run(['pdfinfo', path], stdout=subprocess.PIPE).stdout.decode()
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return line.split(":")[1].strip()

    return "unbekannt"


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
    regex = re.compile("|".join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], string)


def xml_escape(string):
    conv = {
        "&": r"&amp;",
        "<": r"&lt;",
        ">": r"&gt;",
        '"': r"&quot;",
        "'": r"&#39;",
    }
    regex = re.compile("|".join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], string)
