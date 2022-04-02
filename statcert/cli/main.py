import asyncio
import random
import sys

from tqdm import tqdm
from tranco import Tranco

from .. import (
    run_operation,
    CheckOCSP,
    CertAiohttp,
    Record,
)
from .options import parse_options
from .inputs import get_domains_from_file
from .summary import create_summary
from .outputs import write_output, print_record


def main(args=None):
    if args is None:
        args = sys.argv
    options = parse_options(args)

    log = print if options["log_summary"] else lambda *_: None

    input_list = get_input_list(
        arg_list=options["inp_list"],
        inp_type=options["inp_type"],
        range=options["inp_range"],
        rand=options["inp_random"],
        log=log,
    )
    records = [Record(**inp) for inp in input_list]

    log("fetching certificates...")
    if options["log_progress"]:
        pbar = tqdm(total=len(input_list), unit="cert")
        log = pbar.write
    else:
        pbar = None

    operations = [CertAiohttp()]
    if options.inp_ocsp:
        operations.append(CheckOCSP())
    results = []

    async def done_cb(res):
        results.append(res)
        if pbar:
            pbar.update()
        if options["log_results"]:
            is_detailed = options["log_results"] > 1
            print(print_record(res, detailed=is_detailed)+"\n")

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        results = asyncio.run(run_operation(
            operations, records, callback=done_cb)
        )
    except KeyboardInterrupt:
        pass

    if pbar:
        pbar.close()
        log = print

    summary = create_summary([vars(rec) for rec in results])
    log(f"fetched {summary['https_support']} certificates.\n")

    print_summary(summary, log, detailed=(options.log_summary > 1))

    if options["out_file"]:
        write_output(
            records=results,
            file=options["out_file"],
            format=options["out_format"],
        )


def get_input_list(arg_list, inp_type, range=(0, None), rand=False, log=print):
    log("loading records...")

    if inp_type == "tranco":
        input_list = [
            {
                "index": idx,
                "domain": dom,
            }
            for idx, dom in enumerate(Tranco().list().list, 1)
        ]
    elif inp_type == "file":
        with open(arg_list[0]) as file:
            input_list = get_domains_from_file(file)
    else:
        input_list = [
            {
                "index": idx,
                "domain": dom,
            }
            for idx, dom in enumerate(arg_list, start=1)
        ]

    if rand:
        random.shuffle(input_list)

    start, end = range
    start = start - 1 if start > 0 else start
    end = end or len(input_list)
    input_list = input_list[start:end]

    log(f"loaded {len(input_list)} records.\n")

    return input_list


def print_summary(sums, print_func, ocsp=False, detailed=False):
    total = sums["total"]
    conn = sums["connected"]
    https = sums["https_support"]
    no_cert = sums["only_http"]
    pol_t = sums["policy_types"]
    errs = sums["errors"]

    print_func("=== SUMMARY ===")
    print_func(f"received {total} domains;")

    print_func(f"succesfully connected to {conn} ({conn/total:.2%}) servers"
               f" ({sum(errs.values())} ("
               f"{sum(errs.values())/total:.2%}) errors);")

    if detailed:
        print_func(f"error types:\n"+"\n".join(
            f"\t{k}: {v} ({(v/sum(errs.values())) if sum(errs.values()) > 0 else 0:.2%})" for k, v in errs.items()))

    print_func(f"{https} ({(https/conn) if conn > 0 else 0:.2%}) of which supported HTTPS,"
               f" and {no_cert} ({(no_cert/conn) if conn > 0 else 0:.2%}) didn't;")

    print_func(f"policy types: {pol_t['EV']} EV"
               f" ({(pol_t['EV']/sum(pol_t.values())) if sum(pol_t.values()) > 0 else 0:.2%}),"
               f" {pol_t['OV']} OV ({(pol_t['OV']/sum(pol_t.values())) if sum(pol_t.values()) > 0 else 0:.2%}) and"
               f" {pol_t['DV']} DV ({(pol_t['DV']/sum(pol_t.values())) if sum(pol_t.values()) > 0 else 0:.2%})"
               f" and {pol_t['unknown']} unknown"
               f" ({(pol_t['unknown']/sum(pol_t.values())) if sum(pol_t.values()) > 0 else 0:.2%});\n")

    if sums.get("ocsp"):
        print_func(f"ocsp status: ")
        for st, num in sums.get("ocsp").items():
            print_func(f"\t{st}: {num} ({num/https:.2%})")
