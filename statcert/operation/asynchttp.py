import asyncio
import ssl

import aiohttp

from ..model import Operation, Certificate, ProbeInfo


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "*",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

KNONW_ERRORS = [
    # [
    #     ErrorType,
    #     (should_retry, error_desc),
    # ],
    [
        aiohttp.ClientConnectorCertificateError,
        (False, "invalid certificate")
    ],
    [
        aiohttp.ClientResponseError,
        (True, "invalid HTTP response"),
    ],
    [
        aiohttp.ClientConnectionError,
        (True,  "connection error")
    ],
    [
        TimeoutError,
        (True,  "timeout")
    ],
    [
        asyncio.TimeoutError,
        (True,  "timeout")
    ],
    [
        aiohttp.TooManyRedirects,
        (False, "too many redirects")
    ],
    [
        ssl.SSLCertVerificationError,
        (False, "invalid certificate")
    ]
]


class _ResponseWithCert(aiohttp.ClientResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._peer_cert = None

    async def start(self, conn, **kwargs):
        if (
            (transp := conn.transport)
            and (ssl_obj := transp.get_extra_info("ssl_object"))
            and isinstance(ssl_obj, ssl.SSLObject)
        ):
            self._peer_cert = ssl_obj.getpeercert(binary_form=True)
        return await super().start(conn, **kwargs)

    @property
    def peer_cert(self):
        if self._peer_cert:
            return self._peer_cert
        else:
            return None


class CertAiohttp(Operation):
    def __init__(
        self,
        allow_redirects=True,
        max_attempts=6,
        default_timeout=2,
        lenient_timeout=60,
        fake_broser_headers=True,
    ):
        self.allow_redirects = allow_redirects
        self.max_attempts = max_attempts
        self.default_timeout = default_timeout
        self.lenient_timeout = lenient_timeout
        self.fake_broser_headers = fake_broser_headers
        self.session = None

    async def __aenter__(self):
        self.session = await aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(),
            response_class=_ResponseWithCert,
        ).__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.__aexit__(*args, **kwargs)

    @staticmethod
    def prepare_entry(record):
        return {"domain": record.domain}

    async def execute(self, domain):
        if not self.session:
            raise ValueError(
                "Please call this function inside an async with block"
            )

        status = "pending"
        site = None
        redirected = None
        errors = []
        attempts = 0
        cert = None
        for attempt in range(self.max_attempts):

            last_attempt = attempt == (self.max_attempts - 1)
            schema = "https" if not last_attempt else "http"
            url = f"{schema}://{domain}"
            timeout = self.default_timeout
            headers = BROWSER_HEADERS if self.fake_broser_headers else None

            try:
                async with await self.session.get(
                    url, headers=headers,
                    allow_redirects=self.allow_redirects,
                    timeout=aiohttp.ClientTimeout(timeout)
                ) as resp:

                    site = str(resp.url)
                    redirected = len(resp.history) > 0
                    https = (schema == "https")
                    cert = resp.peer_cert

                    if https and not cert:
                        status = "unknown"
                        errors.append("unable to extract certificate"
                                      " from response")
                        continue
                    elif not https and not cert:
                        status = "missing"
                        errors.append("no https support")
                    else:
                        status = "valid"
                        cert = cert
                        break

            except Exception as exc:
                status = "unknown"
                retry, error = _handle_errors(exc)
                errors.append({
                    "type": error,
                    "message": str(exc),
                    "class": str(type(exc)),
                })

                if error == "timeout":
                    if timeout != self.lenient_timeout:
                        timeout = self.lenient_timeout
                    else:
                        retry = False

                if retry:
                    continue
                else:
                    break

        if status == "valid":
            reason = None
        else:
            reason = errors[-1]["type"]

        return [
            ProbeInfo(
                status=status,
                home_page=site,
                redirected=redirected,
                attempts=attempts,
                errors=errors,
                reason=reason,
            ),
            Certificate(cert) if cert else None,
        ]


def _handle_errors(exception):
    for [error_type, return_value] in KNONW_ERRORS:
        if isinstance(exception, error_type):
            return return_value

    raise exception
