import csv
import json


FIELDS = [
    "index",
    "domain",
    "status",
    "site",
    "redirected",
    "serial_number",
    "subject_name",
    "issuer_name",
    "not_before",
    "not_after",
    "key_alg",
    "key_length",
    "sans",
    "policy_type",
    "ocsp_status",
    "errors",
]

IGNORE_FIELDS = [
    "cert_bytes",
]

IMPORTANT_FIELDS = [
    "probe_status",
    "probe_site",
    "probe_reason",
    "cert_subject_name",
    "cert_issuer_name",
    "cert_not_before",
    "cert_not_after",
    "cert_policy_type",
    "ocsp_status"
]

PRETTY_NAMES = {
    "probe_status": "Certificate Status",
    "probe_reason": "Reason",
    "probe_home_page": "Site",
    "cert_key_alg": "Key Algorithm",
    "cert_policy_type": "Certificate Type",
    "ocsp_status": "OCSP Status",
}

def write_output(records, file, format):
    data = [vars(rec) for rec in records]
    with open(file, "w") as fh:
        if format == "csv":
            fields = data[0].keys()
            writer = csv.DictWriter(fh, fields)
            writer.writeheader()
            writer.writerows(data)
        elif format == "json":
            json.dump(data, fh)
        elif format == "plain":
            fh.write(
                "\n\n".join(
                    [print_record(rec) for rec in records]
                )
            )


def print_record(rec, detailed=False):
    string = []

    title = f"#{rec.index} {rec.domain}"
    string.append(title)
    string.append("-" * len(title))

    rec_info = vars(rec)
    rec_info = _filter_fields(rec_info, detailed=detailed)

    string += [
        _stringify(_pretty_name(k), v)
        for k, v in rec_info.items()
        if not v is None
    ]

    return "\n".join(string)


def _filter_fields(info, detailed=False):
    return {
        k: v for k, v in info.items()
        if detailed or k in IMPORTANT_FIELDS
        if k not in IGNORE_FIELDS
    }


def _pretty_name(field: str):
    if PRETTY_NAMES.get(field):
        return PRETTY_NAMES[field]
    else:
        if field.startswith("cert_"):
            field = field[5:]
        return field.replace("_", " ").title()


def _stringify(k, v, indent=0):
    t = "\t" * indent
    if isinstance(v, str):
        return f"{t}{k}: {v}"
    elif isinstance(v, list):
        string = f"{t}{k}:\n"
        string += "\n".join(
            _stringify(i, s, indent=indent+1)
            for i, s in enumerate(v)
        )
        return string
    elif isinstance(v, dict):
        string = f"{t}{k}:\n"
        string += "\n".join(
            _stringify(k, v, indent=indent+1)
            for k, v in v.items()
        )
        return string
    else:
        return f"{t}{k}: {str(v)}"


#     if isinstance(val, dict):
    #         string.append(f"\t{field}:")
    #         string += [f"\t\t{k}: {v}" for k, v in val.items()]
    #     elif isinstance(val, list) and isinstance(val[0], str):
    #         string.append(f"\t{field}: {'; '.join(val)}")
    #     elif isinstance(val, list) and isinstance(val[0], dict):
    #         item_strings = "\n\n".join([
    #             "\n".join([f'\t\t{k}: {v}' for k, v in item.items()])
    #             for item in val
    #         ])
    #         string.append(f"\t{field}:\n{item_strings}")
    #     elif isinstance(val, list):
    #         string.append(f"\t{field}: {'; '.join(map(str, val))}")
    #     else:
    #         string.append(f"\t{field}: {val}")

    # rec = _serializable(record)
    # string = []
    # string.append(f"#{rec['index']} {rec['domain']}")
    # for field in FIELDS:
    #     val = rec.get(field)

    #     if not val:
    #         continue

    #     if isinstance(val, dict):
    #         string.append(f"\t{field}:")
    #         string += [f"\t\t{k}: {v}" for k, v in val.items()]
    #     elif isinstance(val, list) and isinstance(val[0], str):
    #         string.append(f"\t{field}: {'; '.join(val)}")
    #     elif isinstance(val, list) and isinstance(val[0], dict):
    #         item_strings = "\n\n".join([
    #             "\n".join([f'\t\t{k}: {v}' for k, v in item.items()])
    #             for item in val
    #         ])
    #         string.append(f"\t{field}:\n{item_strings}")
    #     elif isinstance(val, list):
    #         string.append(f"\t{field}: {'; '.join(map(str, val))}")
    #     else:
    #         string.append(f"\t{field}: {val}")
    # return "\n".join(string)


def _serializable(rec):
    common = {
        "index": rec["index"],
        "domain": rec["domain"],
        "status": rec["status"],
    }
    if rec["status"] == "success":
        ret = {
            **common,
            "site": rec["site"],
            "redirected": rec["redirected"],
            "serial_number": rec["cert"].serial_number,
            "subject_name": rec["cert"].subject,
            "issuer_name": rec["cert"].issuer,
            "not_before": rec["cert"].not_before.isoformat(),
            "not_after": rec["cert"].not_after.isoformat(),
            "key_alg": rec["cert"].key_type[0],
            "key_length": rec["cert"].key_type[1],
            "sans": rec["cert"].subject_alt_names,
            "policy_type": rec["cert"].policy_type,
        }
        if rec.get("ocsp_status"):
            ret["ocsp_status"] = rec["ocsp_status"]

        return ret
    elif rec["status"] == "no-https":
        return {
            **common,
            "site": rec["site"],
            "redirected": rec["redirected"],
        }
    else:
        return {
            **common,
            "errors": rec["errors"]
        }
