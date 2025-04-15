import json
from subprocess import check_output
import sys
from functools import reduce

manifest_file = "manifest.json"


def map_results(acc: list[str], line: str) -> list[str]:
    if line.strip() != "":
        acc.append(line)
    return acc


def main():
    result = check_output([sys.executable, "-m", "pip", "freeze"], encoding="utf8")
    data = None

    req_json = reduce(map_results, result.split("\n"), [])
    with open(manifest_file, "r") as manifest:
        data = json.load(manifest)
        data["requirements"] = req_json

    if data is not None:
        with open(manifest_file, "w") as manifest:
            json.dump(data, fp=manifest, indent=2)


if __name__ == "__main__":
    main()
