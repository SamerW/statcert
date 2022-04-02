from collections import OrderedDict
from datetime import datetime

import pytest

from statcert import Certificate
from . import TEST_FILES


@pytest.fixture(
    params=[
        {
            "subject": OrderedDict(commonName="www.google.com"),
            "issuer": OrderedDict(
                commonName="GTS CA 1C3",
                organizationName="Google Trust Services LLC",
                countryName="US",
            ),
            "not_before": datetime(2022, 1, 10, 3, 35, 32),
            "not_after": datetime(2022, 4, 4, 3, 35, 31),
            "san": ["www.google.com"],
            "serial": "afff8ea23c08f71f0a000000012e077a",
            "key": ("EC", 256),
            "type": "DV",
            "cert": "google.der"
        },
        {
            "subject": OrderedDict(
                commonName="twitter.com",
                organizationName="Twitter, Inc.",
                localityName="San Francisco",
                stateOrProvinceName="California",
                countryName="US",
            ),
            "issuer": OrderedDict(
                commonName="DigiCert TLS RSA SHA256 2020 CA1",
                organizationName="DigiCert Inc",
                countryName="US",
            ),
            "not_before": datetime(2022, 1, 9, 0, 0, 0),
            "not_after": datetime(2023, 1, 8, 23, 59, 59),
            "san": ["twitter.com", "www.twitter.com"],
            "serial": "6788dcc8560c6793cb5921d644412a1",
            "key": ("RSA", 2048),
            "type": "OV",
            "cert": "twitter.der"
        },
        {
            "subject": OrderedDict(
                commonName="www.bb.com.br",
                organizationalUnit="DITEC",
                organizationName="Banco do Brasil S.A.",
                stateOrProvinceName="Distrito Federal",
                countryName="BR",
                businessCategory="Private Organization",
                jurisdictionOfIncorporationCountryName="BR",
                serialNumber="00.000.000/0001-91",
            ),
            "issuer": OrderedDict(
                commonName="Sectigo RSA Extended Validation Secure Server CA",
                organizationName="Sectigo Limited",
                localityName="Salford",
                stateOrProvinceName="Greater Manchester",
                countryName="GB",
            ),
            "not_before": datetime(2021, 12, 6, 0, 0, 0),
            "not_after": datetime(2022, 12, 6, 23, 59, 59),
            "san": [
                "www.bb.com.br",
                "bb.com.br",
                "www.bancobrasil.com.br",
                "www.bancodobrasil.com.br"
            ],
            "serial": "941ab95fcbcc437166569969fdf8cef2",
            "key": ("RSA", 2048),
            "type": "EV",
            "cert": "bb.der"
        },
    ],
    ids=["dv-google", "ov-twitter", "ev-bb"]
)
def cert_info(request):
    param = {**request.param}
    with open(TEST_FILES/"certs"/param["cert"], "rb") as f:
        param["cert"] = Certificate(f.read())
    return param


def test_model_attributes(cert_info):

    cert = cert_info["cert"]

    assert cert
    assert cert_info["subject"] == cert.subject
    assert cert_info["issuer"] == cert.issuer
    assert cert_info["not_before"] == cert.not_before
    assert cert_info["not_after"] == cert.not_after
    assert cert_info["san"] == cert.subject_alt_names
    assert cert_info["serial"] == cert.serial_number
    assert cert_info["key"] == cert.key_type
    assert cert_info["type"] == cert.policy_type
