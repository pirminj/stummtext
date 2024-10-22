from jinja2 import Template
from functools import partial
from subprocess import run, PIPE, CalledProcessError
from pathlib import Path
from typing import Dict, Callable, NamedTuple
import tempfile


class PaperSize(NamedTuple):
    width: str
    height: str
    name: str


PAPER_SIZES = {
    'a3': PaperSize('297mm', '420mm', 'A3'),
    'a4': PaperSize('210mm', '297mm', 'A4'),
    'a5': PaperSize('148mm', '210mm', 'A5'),
    'b5': PaperSize('176mm', '250mm', 'B5'),
    'letter': PaperSize('8.5in', '11in', 'US Letter'),
    'legal': PaperSize('8.5in', '14in', 'US Legal'),
    'remarkable2': PaperSize('180mm', '250mm', 'reMarkable2'),
    'phone': PaperSize('70mm', '150mm', 'phone')
}


def render_template(template: Template, data: Dict[str, str]) -> str:
    return template.render(**data)


def run_latex(input_tex: str, output_path: str) -> None:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "input.tex"
            tex_path.write_text(input_tex)

            latex_cmd = partial(run, cwd=tmpdir, check=True, stdout=PIPE,
                                stderr=PIPE)
            latex_cmd(["pdflatex", "-interaction=nonstopmode", str(tex_path)])

            output_pdf = Path(tmpdir) / "input.pdf"
            if output_pdf.exists():
                output_pdf.rename(output_path)
    except CalledProcessError as e:
        breakpoint()
        raise


def render_latex(tex: str, filename: str) -> None:
    output_path = Path(filename).with_suffix('.pdf')
    run_latex(tex, str(output_path))


def compose(f: Callable, g: Callable) -> Callable:
    return lambda x: g(f(x))


def process_document(template: Template,
                     data: Dict[str, str],
                     output_file: str) -> None:
    pipeline = compose(
        partial(render_template, template),
        partial(render_latex, filename=output_file)
    )
    pipeline(data)


long_text = r""" Antarctica is the coldest, windiest, and most remote
continent on Earth. Located at the South Pole, it's covered almost
entirely by ice and snow. This massive land is bigger than Europe and
is surrounded by the Southern Ocean.

Almost all of Antarctica (about 98\%) is covered by an ice sheet that's
very thick - in some places, it's more than 4 kilometers deep. This
ice sheet contains about 90% of all the world's ice. If it were to
melt completely, sea levels worldwide would rise by about 60 meters.

The weather in Antarctica is extreme. The average winter temperature
near the South Pole is about -60°C (-76°F), while coastal areas are
slightly warmer. In summer, coastal regions might reach just above
freezing point. Strong winds, sometimes reaching over 300 kilometers
per hour, blow across the continent, making it even colder.

"""

template_figure = Template(r'''
\begin{figure}[h]
\begin{tikzpicture}
\begin{axis}[
    width=\textwidth,
    xlabel=X axis,
    ylabel=Y axis,
    scatter/classes={
        a={mark=o,draw=black}
    }
]
\addplot[scatter,only marks,scatter src=explicit symbolic]
    coordinates {
        (1,2)[a]
        (2,4)[a]
        (3,5)[a]
        (4,4)[a]
        (5,7)[a]
    };
\addplot[red,domain=0:6] {1.2*x + 1};
\end{axis}
\end{tikzpicture}
\caption{Scatter plot with linear regression}
\label{fig:scatter}
\end{figure}
''')

template = Template(r'''
\documentclass{article}
\usepackage[paperwidth={ {{ pagesize.width }} },
            paperheight={ {{ pagesize.height}} },
            margin={ {{margin}} }]{geometry}

\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18} % or whatever recent version you have
\usepackage{float} % for the [h] placement specifier

\begin{document}
\section{ {{ title }} }
{{ content }}
\end{document}
''')


testdata = {"title": "A nice document",
            "content": long_text * 10,
            "pagesize": PAPER_SIZES['phone'],
            "margin": "3mm"}


testdata2 = {"title": "A nice document",
             "content": long_text + template_figure.render() + 3 * long_text,
             "pagesize": PAPER_SIZES['remarkable2'],
             "margin": "3mm"}


process_document(template,
                 data=testdata2,
                 output_file="test-phone.pdf")


process_document(template,
                 data=testdata2,
                 output_file="test-remarkable.pdf")
