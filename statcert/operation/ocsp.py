import asyncio
import base64

import aiohttp
from cryptography import x509
from cryptography.x509.ocsp import OCSPResponseStatus, OCSPCertStatus
from cryptography.hazmat.primitives.hashes import SHA256, SHA1
from cryptography.hazmat.primitives.serialization import Encoding

from ..model import Operation, OCSPInfo


class CheckOCSP(Operation):
    def __init__(self) -> None:
        self.session = None

    async def __aenter__(self):
        self.session = await aiohttp.ClientSession().__aenter__()

        return self

    async def __aexit__(self, *args, **kwargs):
        return await self.session.__aexit__(*args, **kwargs)

    @staticmethod
    def prepare_entry(record):
        return {"cert": record.results["cert"].cert}

    async def execute(self, cert):
        if not self.session:
            raise ValueError(
                "Please call this function inside an async with block"
            )

        ocsp_url, issuer_url = _extract_aia_info(cert)
        if not (ocsp_url and issuer_url):
            return {"ocsp_status": "unavailable"}

        raw_issuer_cert = await _get(self.session, issuer_url)
        issuer_cert = x509.load_der_x509_certificate(
            raw_issuer_cert
        )

        for hash in [SHA1, SHA256]:
            ocsp_request = _build_ocsp_req(cert, issuer_cert, hash)
            ocsp_req_url = f"{ocsp_url}/{ocsp_request}"
            raw_ocsp_resp = await _get(self.session, ocsp_req_url)
            ocsp_resp = x509.ocsp.load_der_ocsp_response(raw_ocsp_resp)
            if ocsp_resp.response_status != OCSPResponseStatus.SUCCESSFUL:
                continue

            if ocsp_resp.certificate_status == OCSPCertStatus.GOOD:
                return [OCSPInfo("good")]
            if ocsp_resp.certificate_status == OCSPCertStatus.UNKNOWN:
                return [OCSPInfo("unknown")]
            if ocsp_resp.certificate_status == OCSPCertStatus.REVOKED:
                return [OCSPInfo("revoked")]

        return [OCSPInfo("req_failed")]


async def _get(client, url):
    async with client.get(url) as resp:
        raw = await resp.read()

    return raw


def _build_ocsp_req(cert, issuer_cert, hash):
    builder = x509.ocsp.OCSPRequestBuilder()
    builder = builder.add_certificate(cert, issuer_cert, hash())
    req = builder.build()
    req_path = base64.b64encode(req.public_bytes(Encoding.DER))
    return req_path.decode('ascii')


def _extract_aia_info(cert):
    aia_ext = cert.extensions.get_extension_for_class(
        x509.AuthorityInformationAccess
    )
    aia_info = {
        desc.access_method._name: desc.access_location.value
        for desc in aia_ext.value
    }
    return aia_info.get("OCSP"), aia_info.get("caIssuers")
