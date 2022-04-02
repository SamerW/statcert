import asyncio
import platform
import pytest


def pytest_addoption(parser):
    # register command line option
    parser.addoption(
        "--slow", action="store_true", help="run slow tests"
    )


def pytest_configure(config):
    # run all async tests with pytest-asyncio
    config._inicache["asyncio_mode"] = "auto"
    # register an additional marker
    config.addinivalue_line(
        "markers", "web: marks slow and unreliable tests"
    )
    # fix annoying Windows issues
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )


def pytest_collection_modifyitems(config, items):
    # add "skip" mark to slow tests
    if not any(config.getoption(opt) for opt in ["-k", "--slow"]):
        [
            item.add_marker(
                pytest.mark.skip(
                    reason="need --slow option to run"
                )
            )
            for item in items
            if "web" in item.keywords
        ]
