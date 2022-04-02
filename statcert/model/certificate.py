import warnings

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.asymmetric import rsa, ec

from .constants import CERTIFICATE_TYPES, RDN_DESCRIPTIONS
from .info import Info


class Certificate(Info):
    op_name = "cert"

    def __init__(self, cert):
        if isinstance(cert, x509.Certificate):
            self.cert = cert
        elif isinstance(cert, bytes):
            self.cert = x509.load_der_x509_certificate(cert)
        elif isinstance(cert, str):
            cert_bytes = cert.encode("ascii")
            self.cert = x509.load_pem_x509_certificate(cert_bytes)
        else:
            raise ValueError(
                f"can't create certificate from type {type(cert)}"
            )

    def __hash__(self):
        return hash(self.cert.public_bytes(Encoding.DER))

    def __eq__(self, other):
        if not isinstance(other, Certificate):
            return False
        return hash(other) == hash(self)

    def __repr__(self):
        return f"Certificate({self.serial_number[-8:]})"

    def __bytes__(self):
        return self.as_bytes()

    def as_bytes(self, format="der"):
        format = format.lower()
        if format == "der":
            return self.cert.public_bytes(Encoding.DER)
        elif format == "pem":
            return self.cert.public_bytes(Encoding.PEM)
        else:
            raise ValueError(
                f"invalid format {format}, must be either PEM or DER"
            )

    @property
    def __dict__(self):
        return {
            "serial_number": self.serial_number,
            "subject_name": self.subject_name,
            "issuer_name": self.issuer_name,
            "subject": self.subject,
            "issuer": self.issuer,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "duration": self.duration,
            "key_alg": self.key_type[0],
            "key_length": self.key_type[1],
            "subject_alt_names": self.subject_alt_names,
            "policy_oids": self.policy_oids,
            "policy_type": self.policy_type,
            "bytes": bytes(self),
        }

    @property
    def serial_number(self):
        return f"{self.cert.serial_number:x}"

    @property
    def subject_name(self):
        return self.subject.get("organizationName") or self.subject["commonName"]

    @property
    def issuer_name(self):
        return self.issuer["organizationName"]

    @property
    def subject(self):
        return {
            RDN_DESCRIPTIONS[attr.oid.dotted_string]: attr.value
            for attr in self.cert.subject
        }

    @property
    def issuer(self):
        return {
            RDN_DESCRIPTIONS[attr.oid.dotted_string]: attr.value
            for attr in self.cert.issuer
        }

    @property
    def not_before(self):
        return self.cert.not_valid_before

    @property
    def not_after(self):
        return self.cert.not_valid_after

    @property
    def duration(self):
        return self.not_after - self.not_before

    @property
    def key_type(self):
        pk = self.cert.public_key()
        if isinstance(pk, rsa.RSAPublicKey):
            return "RSA", pk.key_size
        elif isinstance(pk, ec.EllipticCurvePublicKey):
            return "EC", pk.key_size
        else:
            warnings.warn(f"unknown key type {type(pk)}")
            try:
                return type(pk), pk.key_size
            except AttributeError:
                return type(pk), -1

    @property
    def subject_alt_names(self):
        return [
            san.value
            for san in self.cert.extensions.get_extension_for_class(
                x509.extensions.SubjectAlternativeName
            ).value
        ]

    @property
    def policy_oids(self):
        try:
            return [
                pol.policy_identifier.dotted_string
                for pol in self.cert.extensions.get_extension_for_class(
                    x509.extensions.CertificatePolicies
                ).value
            ]
        except x509.ExtensionNotFound:
            return []

    @property
    def policy_type(self):
        matching = [
            CERTIFICATE_TYPES[oid]
            for oid in self.policy_oids
            if oid in CERTIFICATE_TYPES
        ]

        if len(matching) > 1:
            warnings.warn(f"multiple certificate types: {matching}")
        elif len(matching) < 1:
            warnings.warn(
                f"unknown certificate type; oids: {self.policy_oids}")
            return "Unknown"
        else:
            return matching[0]
