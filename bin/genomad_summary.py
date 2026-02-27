#!/usr/bin/env python3
import sys
import json
import argparse
import pandas as pd
from pathlib import Path

__version__ = "0.0.1"


def init_argparser():
    parser = argparse.ArgumentParser(
        prog="genomad_summary",
        description="A terse, high-level JSON summary of genomad outputs.",
    )

    parser.add_argument(
        dest="summary_dir",
        type=str,
        help="Specify path to genomad summary folder",
    )

    return parser


def get_genomad_summary_file_dict(input_genomad_run_summary_folder_path):
    """
    Takes in a path to a "summary" folder produced
    by geNomad. Returns a dictionary of the output files
    found in that folder.
    """
    summary_folder_path = Path(input_genomad_run_summary_folder_path)

    return {
        "_".join(x.name.split(".")[-2:]): x.name
        for x in summary_folder_path.glob("*.fastq_*.*")
    }


def generate_summary_of_fastq_virus_tsv(input_genomad_run_summary_folder_path):
    genomad_summary_file_dict = get_genomad_summary_file_dict(
        input_genomad_run_summary_folder_path
    )

    fastq_virus_summary_tsv = Path(
        input_genomad_run_summary_folder_path,
        genomad_summary_file_dict.get("fastq_virus_summary_tsv"),
    )

    ## escape hatch for a failed run
    if not fastq_virus_summary_tsv:
        return None

    summary_df = pd.read_csv(fastq_virus_summary_tsv, sep="\t")

    ## main set of metrics
    return_dict = {
        "total_readcount": len(summary_df),
        "viral_readcount": len(
            list(filter(lambda x: x.startswith("Viruses"), summary_df["taxonomy"]))
        ),
        "viral_readcount_with_hallmark": len(
            list(filter(lambda x: x > 0, summary_df["n_hallmarks"]))
        ),
        "unclassified_readcount": len(
            list(filter(lambda x: x == "Unclassified", summary_df["taxonomy"]))
        ),
    }

    ## additional derived metric
    ## arbitrarily round to 5 d.p
    return_dict["classified_ratio"] = round(
        (return_dict["total_readcount"] - return_dict["unclassified_readcount"])
        / return_dict["total_readcount"],
        5,
    )

    return return_dict


def generate_summary_of_fastq_plasmid_tsv(input_genomad_run_summary_folder_path):
    genomad_summary_file_dict = get_genomad_summary_file_dict(
        input_genomad_run_summary_folder_path
    )

    fastq_plasmid_summary_tsv = Path(
        input_genomad_run_summary_folder_path,
        genomad_summary_file_dict.get("fastq_plasmid_summary_tsv"),
    )

    ## escape hatch for a failed run
    if not fastq_plasmid_summary_tsv:
        return None

    summary_df = pd.read_csv(fastq_plasmid_summary_tsv, sep="\t", keep_default_na=False)

    ## main set of metrics
    return_dict = {
        "plasmid_readcount": len(summary_df),
        "plasmid_readcount_with_amr_genes": len(
            list(filter(lambda x: x != "NA", summary_df["amr_genes"]))
        ),
        "plasmid_readcount_with_conjugation_genes": len(
            list(filter(lambda x: x != "NA", summary_df["conjugation_genes"]))
        ),
        "plasmid_readcount_with_hallmark_genes": len(
            list(filter(lambda x: x > 0, summary_df["n_hallmarks"]))
        ),
    }

    return return_dict


def load_genomad_summary_json(input_genomad_run_summary_folder_path):
    genomad_summary_file_dict = get_genomad_summary_file_dict(
        input_genomad_run_summary_folder_path
    )

    summary_json = Path(
        input_genomad_run_summary_folder_path,
        genomad_summary_file_dict.get("fastq_summary_json"),
    )

    ## escape hatch for a failed run
    if not summary_json:
        return None

    summary_dict = json.loads(Path(summary_json).read_text())

    return summary_dict


def generate_summary(input_genomad_run_summary_folder_path):
    virus_result = generate_summary_of_fastq_virus_tsv(
        input_genomad_run_summary_folder_path
    )
    plasmid_result = generate_summary_of_fastq_plasmid_tsv(
        input_genomad_run_summary_folder_path
    )
    genomad_json = load_genomad_summary_json(input_genomad_run_summary_folder_path)

    return_dict = {
        "virus_summary": virus_result,
        "plasmid_summary": plasmid_result,
        "genomad_summary": genomad_json,
        "artifacts": get_genomad_summary_file_dict(
            input_genomad_run_summary_folder_path
        ),
    }

    return return_dict


def generate_summary_json(input_genomad_run_summary_folder_path):
    return json.dumps(
        generate_summary(input_genomad_run_summary_folder_path),
        indent=4,
    )


def main():
    args = init_argparser().parse_args()

    genomad_run_summary_folder = args.summary_dir

    summary_json = generate_summary_json(genomad_run_summary_folder)

    sys.stdout.write(summary_json)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
