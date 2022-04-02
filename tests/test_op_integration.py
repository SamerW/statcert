import async_timeout
import pytest

from statcert import Certificate, get_server_certificate, get_site_certificate
from statcert.operation.api import get_certificates


"""XXX:
These tests assume things about the external world,
such as
    - that Google and Twitter certificates will
      be available and valid;
    - that google.com will redirect to www.google.com
      and www.twitter.com will redirect to twitter.com;
    - that there's a working internet connection;
    - etc.
Their failure is not considered critical.
"""


@pytest.mark.web
@pytest.mark.parametrize(
    ["domain",              "xsite"],
    [
        ("google.com",      "https://google.com",),
        ("www.google.com",  "https://www.google.com",),
        ("twitter.com",     "https://twitter.com",),
        ("www.twitter.com", "https://www.twitter.com", ),
    ]
)
async def test_get_server_cert(domain, xsite):

    info = await get_server_certificate(domain)

    assert info["site"] == xsite
    assert isinstance(info["cert"], Certificate)


@pytest.mark.web
@pytest.mark.parametrize(
    ["domain",              "xsite",                   "xredir"],
    [
        ("google.com",      "https://www.google.com/", True),
        ("www.google.com",  "https://www.google.com",  False),
        ("twitter.com",     "https://twitter.com",     False),
        ("www.twitter.com", "https://twitter.com/",    True),
    ]
)
async def test_get_site_cert(domain, xsite, xredir):

    info = await get_site_certificate(domain)

    assert info["site"] == xsite
    assert info["redirected"] == xredir
    assert isinstance(info["cert"], Certificate)


@pytest.mark.web
async def test_get_site_cert_fake_browser():

    info = await get_site_certificate("usnews.com")

    assert isinstance(info["cert"], Certificate)

@pytest.mark.web
async def test_get_certificates():
    res = await get_certificates(["google.com", "twitter.com"])
    assert isinstance(res, list)
    assert len(res) == 2
    assert all(r.get("domain") for r in res)
    assert all(isinstance(r.get("cert"), Certificate) for r in res)
    assert all(r.get("site") for r in res)
    assert all(r.get("redirected") != None for r in res)
