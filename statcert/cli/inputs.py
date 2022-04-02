import csv


def get_domains_from_file(file):
    content = file.readlines()

    def record(idx, dom): return {
        "index": int(idx),
        "domain": dom.strip(),
    }

    for line in content:
        first_line = line.strip().split(",")
        num_fields = len(first_line)
        if num_fields > 0:
            break
        else:
            first_line = []

    if "domain" in first_line:
        return [
            record(rec.get("index", idx), rec["domain"])
            for idx, rec in enumerate(csv.DictReader(content), start=1)
            if len(rec) > 0
            if rec["domain"].strip() != ""
        ]
    elif num_fields == 1:
        return [
            record(idx, *line)
            for idx, line in enumerate(csv.reader(content), start=1)
            if len(line) > 0
            if line[0].strip() != ""
        ]
    elif num_fields == 2:
        return [
            record(*line)
            for line in csv.reader(content)
            if len(line) > 0
            if line[1].strip() != ""
        ]
    else:
        raise ValueError("unrecognized file structure")
