from collections import Counter
import warnings


def create_summary(result_list):
    total = 0
    conn = 0
    https = 0
    no_cert = 0
    pol_t = Counter()
    errs = Counter()
    ocsp = Counter()

    for rec in result_list:
        total += 1

        if rec["probe_status"] != "unknown":
            conn += 1

        if rec["probe_status"] == "unknown":
            errs[rec["probe_reason"]] += 1
        elif rec["probe_status"] == "missing":
            no_cert += 1
        elif rec["probe_status"] == "valid":
            https += 1
            pol_t[rec["cert_policy_type"]] += 1
            if rec.get("ocsp_status"):
                ocsp[rec["ocsp_status"]] += 1
        else:
            warnings.warn(f"Unknown status {rec['probe_status']}")

    ret = {
        "total": total,
        "connected": conn,
        "https_support": https,
        "only_http": no_cert,
        "policy_types": pol_t,
        "errors": errs,
    }
    if sum(ocsp.values()) > 0:
        ret["ocsp"] = ocsp
    return ret
