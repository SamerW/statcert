import argparse
import os
import warnings
from collections.abc import Mapping
from dataclasses import dataclass

from . import __doc__ as PROG_DESC


PROG_NAME = "statcert"

LOG_PRESETS = {  # (progress, summary, results)
    "specific":  (False, 0, 2),
    "broad":     (True, 1, 1),
    "file":     (True, 1, 0),
    "quiet":    (False, 0, 0),
    "verbose":  (True, 2, 2),
}

KNOWN_EXTENSIONS = {
    ".json": "json",
    ".csv": "csv",
    ".txt": "plain",
}


@dataclass
class Options(Mapping):
    inp_list:       list    # list[filename | str]
    inp_type:       str     # (domain | file | tranco)
    inp_range:      tuple   # (start: int = 0, end: int | None = None)
    inp_random:     bool
    inp_ocsp:       bool
    out_file:       str     # filename
    out_format:     str     # (json | csv | plain)
    log_progress:   bool
    log_summary:    int     # (none=0 | short=1 | long=2)
    log_results:    int     # (none=0 | short=1 | long=2)
    log_debug:      bool

    def __getitem__(self, key):
        return vars(self)[key]

    def __len__(self):
        return len(vars(self))

    def __iter__(self):
        return iter(vars(self))


def parse_options(raw_args):
    parser = _create_argument_parser(PROG_NAME, PROG_DESC)
    args = parser.parse_args(raw_args[1:])

    inp_type = args.type or _deduce_arg_type(args.input)
    inp_range = _parse_range(args.range)
    out_format = args.format or _deduce_file_format(args.output)

    default_preset = (
        "file" if args.output else
        "specific" if inp_type == "domain" else
        "broad"
    )
    log_preset = LOG_PRESETS[args.preset or default_preset]
    log_opts = {}
    for opt, inp, preset in [
        ("log_progress", args.progress, log_preset[0]),
        ("log_summary", args.summary, log_preset[1]),
        ("log_results", args.results, log_preset[2]),
    ]:
        log_opts[opt] = preset if inp is None else inp

    return Options(
        inp_list=args.input,
        inp_type=inp_type,
        inp_range=inp_range,
        inp_random=args.random,
        inp_ocsp=args.ocsp,
        out_file=args.output,
        out_format=out_format,
        **log_opts,
        log_debug=args.debug,
    )


def _create_argument_parser(name, desc):
    parser = argparse.ArgumentParser(
        prog=name,
        description=desc,
    )

    _add_log_args(parser)
    _add_input_args(parser)
    _add_output_args(parser)

    return parser


def _add_log_args(parser):
    log_pre = parser.add_argument_group("Logging presets")
    log_pre.add_argument(
        "-q", "--quiet",
        action="store_const",
        const="quiet",
        dest="preset",
        help="Don't show any output"
    )
    log_pre.add_argument(
        "-v", "--verbose",
        action="store_const",
        const="verbose",
        dest="preset",
        help="Show as much output as"
    )

    log_opts = parser.add_argument_group("Logging options")
    log_opts.add_argument(
        "-p", "--progress",
        action="store_const",
        const=True,
        dest="progress",
        help="Show progress bar"
    )
    log_opts.add_argument(
        "-P", "--no-progress",
        action="store_const",
        const=False,
        dest="progress",
        help="Don't show progress bar"
    )

    log_opts.add_argument(
        "-S", "--no-summary",
        action="store_const",
        const=0,
        dest="summary",
        help="Don't show operation summary",
    )
    log_opts.add_argument(
        "-s", "--short-summary",
        action="store_const",
        const=1,
        dest="summary",
        help="Show short operation summary",
    )
    log_opts.add_argument(
        "-ss", "--detailed-summary",
        action="store_const",
        const=2,
        dest="summary",
        help="Show detailed operation summary",
    )

    log_opts.add_argument(
        "-R", "--no-results",
        action="store_const",
        const=0,
        dest="results",
        help="Print resulting certificates (default is to"
        " show only when no output file is specified)"
    )
    log_opts.add_argument(
        "-r", "--short-results",
        action="store_const",
        const=1,
        dest="results",
        help="Print resulting certificates (default is to"
        " show only when no output file is specified)"
    )
    log_opts.add_argument(
        "-rr", "--detailed-results",
        action="store_const",
        const=2,
        dest="results",
        help="Print resulting certificates (default is to"
        " show only when no output file is specified)"
    )

    log_opts.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Show debugging info"
    )

    return parser


def _add_input_args(parser):
    parser.add_argument(
        "input",
        action="store",
        nargs="*",
        type=str,
        help="either domains to be fetched, or a file "
        "containing a list of domains (get Tranco Top "
        "Sites Ranking by default)",
        metavar="FILE | DOMAIN",
    )

    # Input options (-n, --type, --random)
    input_opts = parser.add_argument_group("Input options")
    input_opts.add_argument(
        "-n", "--range",
        action="store",
        default=None,
        help="fetch only first [N] entries, or fetch from"
        " [START]th entry to [END]th entry; underlines are"
        " ignored",
        metavar="NUM | RANGE",
    )
    input_opts.add_argument(
        "-t", "--type",
        action="store",
        default=None,
        choices=["file", "domain", "tranco"],
        help="explicitly declare input type instead of"
        " guessing",
    )
    input_opts.add_argument(
        "--random",
        action="store_true",
        help="shuffle domains before fetching",
    )
    input_opts.add_argument(
        "--ocsp",
        action="store_true",
        help="also fetch OCSP status",
    )
    return parser


def _add_output_args(parser):
    output_opts = parser.add_argument_group("Output options")
    output_opts.add_argument(
        "-o", "--output",
        help="save output to specified file (format "
        "can be infered from filename extension or "
        "specified with --format)",
        metavar="FILE",
    )
    output_opts.add_argument(
        "-f", "--format",
        action="store",
        choices=KNOWN_EXTENSIONS.values(),
        help="format results as plain text ('plain'/.txt),"
        " Comma-Separated Values ('csv') or using"
        " Javascript Object Notation ('json') (requires"
        " --output)",
    )


def _deduce_arg_type(input_list):
    if len(input_list) == 0:
        return "tranco"
    elif all(os.path.isfile(inp) for inp in input_list):
        return "file"
    else:
        return "domain"


def _parse_range(raw_range_str):
    if not raw_range_str:
        return (0, None)

    range_str = raw_range_str.replace("_", "")
    if "-" in range_str:
        range_ls = range_str.split("-")

        if len(range_ls) != 2 or not all(s.isnumeric() for s in range_ls):
            raise ValueError(f"Invalid range: {range_str}")

        [start, end] = [int(n) for n in range_ls]

        return (start-1, end)

    elif range_str.isnumeric():
        return (0, int(range_str))

    else:
        raise ValueError(f"Invalid range: {range_str}")


def _deduce_file_format(file_name):
    if not file_name:
        return None

    for (ext, fmt) in KNOWN_EXTENSIONS.items():
        if file_name.lower().endswith(ext):
            return fmt

    raise ValueError("Unknown or unespecified file format for"
                     f" output file {file_name}")
