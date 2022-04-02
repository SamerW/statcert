import pytest

from . import TEST_FILES
from statcert.cli.options import parse_options


class TestInputOptions:
    @pytest.fixture(params=[
        (  # Single domain
            "www.google.com",
            {
                "inp_list": ["www.google.com"],
                "inp_type": "domain",
            }
        ),
        (  # Multiple domains
            "www.google.com twitter.com apple.com",
            {
                "inp_list": [
                    "www.google.com",
                    "twitter.com",
                    "apple.com",
                ],
                "inp_type": "domain",
            },
        ),
        (  # Single file
            str(TEST_FILES/"inputs"/"test.txt"),
            {
                "inp_list": [str(TEST_FILES/"inputs"/"test.txt")],
                "inp_type": "file",
            },
        ),
        (  # Multiple files
            " ".join([
                str(TEST_FILES/"inputs"/"test.txt"),
                str(TEST_FILES/"inputs"/"test.csv"),
            ]),
            {
                "inp_list": [
                    str(TEST_FILES/"inputs"/"test.txt"),
                    str(TEST_FILES/"inputs"/"test.csv"),
                ],
                "inp_type": "file",
            },
        ),
        (  # Tranco list
            "--type tranco",
            {
                "inp_list": [],
                "inp_type": "tranco",
            },
        ),
    ], ids=[
        "Single domain",
        "Multiple domains",
        "Single file",
        "Multiple files",
        "Tranco list",
    ])
    def input_type(_, request):
        return request.param

    @pytest.fixture(params=[
        (  # All
            "",
            {"inp_range": (0, None)}
        ),
        (  # Number only
            "-n 4",
            {"inp_range": (0, 4)}
        ),
        (  # Full range
            "-n 3-5",
            {"inp_range": (2, 5)}
        ),
        (  # Ignore underlines
            "-n 3_000-5_000",
            {"inp_range": (2999, 5000)}
        ),
        (  # Invalid range
            "-n 100-",
            {"raises": ValueError}
        ),
        (  # Invalid number
            "-n abacate",
            {"raises": ValueError}
        ),
    ], ids=[
        "All",
        "Number only",
        "Full range",
        "Ignore underlines",
        "Invalid range",
        "Invalid number",
    ])
    def input_range(_, request):
        return request.param

    @pytest.fixture(params=[
        ("", {"inp_random": False}),
        ("--rand", {"inp_random": True}),
    ], ids=["ord", "rand"])
    def input_random(_, request):
        return request.param

    @pytest.fixture()
    def input_opts(_, input_type, input_range, input_random):
        (tstr, topt), (nstr, nopt), (rstr,
                                     ropt) = input_type, input_range, input_random
        return (
            "statcert "+" ".join([tstr, nstr, rstr]),
            {**topt, **nopt, **ropt}
        )

    def test_parse_opts_input(_, input_opts):
        inp_str, xopts = input_opts

        if "raises" in xopts:
            pytest.raises(xopts["raises"], parse_options, inp_str.split())
        else:
            options = parse_options(inp_str.split())
            for k, v in xopts.items():
                assert options.get(k) == v


class TestOutputOptions:
    @pytest.fixture(params=[
        (  # CSV
            "-o file.csv",
            {"out_file": "file.csv", "out_format": "csv"}
        ),
        (  # JSON
            "-o file.json",
            {"out_file": "file.json", "out_format": "json"}
        ),
        (  # text
            "-o file.txt",
            {"out_file": "file.txt", "out_format": "plain"}
        ),
    ], ids=[
        "file.csv",
        "file.json",
        "file.txt"
    ])
    def output_file(self, request):
        return request.param

    @pytest.fixture(params=[
        (  # infer
            "",
            {}
        ),
        (  # CSV
            "--format csv",
            {"out_format": "csv"}
        ),
        (  # JSON
            "--format json",
            {"out_format": "json"}
        ),
        (  # text
            "--format plain",
            {"out_format": "plain"}
        ),
    ], ids=[
        "infer",
        "CSV",
        "JSON",
        "plain",
    ])
    def output_format(self, request):
        return request.param

    @pytest.fixture
    def output_opts(self, output_file, output_format):
        (ostr, oopt), (fstr, fopt) = output_file, output_format
        return (
            "statcert "+" ".join([ostr, fstr]),
            {**oopt, **fopt}
        )

    def test_parse_opts_output(self, output_opts):
        inp_str, xopts = output_opts

        if "raises" in xopts:
            pytest.raises(xopts["raises"], parse_options, inp_str.split())
        else:
            options = parse_options(inp_str.split())
            for k, v in xopts.items():
                assert options.get(k) == v

    # @pytest.mark.parametrize(
    #     ["record"]
    # )
    def test_write_output(self):
        ...


class TestLoggingOptions:
    @pytest.fixture(params=[
        ("", {
            "log_progress": True,
            "log_summary": 1,
            "log_results": 2,
        }),
        ("--quiet", {
            "log_progress": False,
            "log_summary": 0,
            "log_results": 0,
        }),
        ("--verbose", {
            "log_progress": True,
            "log_summary": 2,
            "log_results": 2,
        }),
        ("-o somefile.txt", {
            "log_progress": True,
            "log_summary": 1,
            "log_results": 0,
        }),
    ], ids=[
        "default preset",
        "quiet preset",
        "verbose preset",
        "file preset",
    ])
    def logging_presets(self, request):
        return request.param

    @pytest.fixture(params=[
        ("", {}),
        ("--progress", {"log_progress": True}),
        ("--no-progress", {"log_progress": False}),
    ], ids=[
        "default",
        "progress",
        "no progress",
    ])
    def logging_progress(self, request):
        return request.param

    @pytest.fixture(params=[
        ("", {}),
        ("--no-summary", {"log_summary": 0}),
        ("--short-summary", {"log_summary": 1}),
        ("--detailed-summary", {"log_summary": 2}),
    ], ids=[
        "default",
        "no summary",
        "short summary",
        "long summary",
    ])
    def logging_summary(self, request):
        return request.param

    @pytest.fixture(params=[
        ("", {}),
        ("--no-results", {"log_results": 0}),
        ("--short-results", {"log_results": 1}),
        ("--detailed-results", {"log_results": 2}),
    ], ids=[
        "default",
        "short results",
        "long results",
        "long results",
    ])
    def logging_results(self, request):
        return request.param

    @pytest.fixture(params=[
        ("", {"log_debug": False}),
        ("--debug", {"log_debug": True}),
    ], ids=[
        "default",
        "debug",
    ])
    def logging_debug(self, request):
        return request.param

    @pytest.fixture
    def logging_opts(
        self,
        logging_presets,
        logging_progress,
        logging_summary,
        logging_results,
        logging_debug,
    ):
        (pstr, popt) = logging_presets
        (gstr, gopt) = logging_progress
        (sstr, sopt) = logging_summary
        (rstr, ropt) = logging_results
        (dstr, dopt) = logging_debug
        return (
            "statcert "+" ".join([
                pstr,
                gstr,
                sstr,
                rstr,
                dstr,
            ]),
            {
                **popt,
                **gopt,
                **sopt,
                **ropt,
                **dopt,
            },
        )

    def test_parse_opts_logging(self, logging_opts):
        inp_str, xopts = logging_opts

        options = parse_options(inp_str.split())

        for k, v in xopts.items():
            assert options.get(k) == v
