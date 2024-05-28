from json import load
from re import match
from os import remove
from os.path import dirname
from pathlib import Path
from typing import List
from zipfile import ZipFile

from pandas import DataFrame, read_csv


def get_percent_bar(percent: float, width: int):
    """Generates the stat bars used to represent the closeness of an
    path to a centroid.

    Args:
        percent (float): The percentage as a float between 0.0 and 100.0
        width (int): The maximum width of the bar in terms of characters.
    """

    bar = "▒" * int(width * (percent / 100))

    return bar


def open_report(file_path: str, lower: int, upper: int, block: list,
        regex: str) -> list:
    """Opens a report file in json format and deserializes it into a
    usable format for the front end.

    Args:
        path (str): The path to the json file.
        lower (int): Lower bound in percent for the reports to be filtered.
        upper (int): Upper bound in percent for the reports to be filtered.
        block (list): Block list for unwanted reports of certain models.
        regex (str): Regex string to filter reported paths by function.
    Returns:
        list: The list of (filtered) reports.
    """

    reports = []

    json = None
    with open(file_path) as f:
        json = load(f)

    for report in json:
        block = [b.strip() for b in block]
        lines = {int(k): int(v) for k, v in report.get("line_dict").items()}
        stats = {k: float(v) for k, v in report.get("stats").items()}
        stats = dict(filter(lambda s: s[1] > lower and s[1] < upper \
                                      and s[0] not in block, stats.items()))

        if not stats:
            continue

        hl_lines = [int(i) for i in report.get("hl_lines")]

        path = list(filter(lambda y: bool(y),
                           [x for x in report.get("original_path")]))

        if not path:
            continue

        proc = path[0].get("func_name")
        if not proc or not match(regex, proc):
                continue

        code = report.get("code").replace("\t", "    ")
        model_path = report.get("model_path")

        reports.append({
            "line_dict": lines,
            "stats": stats,
            "hl_lines": hl_lines,
            "path": path,
            "code": code,
            "model_path": model_path
        })

    return reports

def unzip(model_path: str) -> dict:
    """ Simple helper function that unzips a file provided by it's path. The
    files contained within the zipfile must be text files.

    Args:
        file_path (str): The file path.
        file_name (str): The name of the file to be extracted.
    Returns (DataFrame): A Pandas DataFrame object containing the model paths.
    """

    files = {}

    with ZipFile(model_path) as zfile:
        for member in zfile.namelist():
            with zfile.open(member) as unzipped:
                files.update({member: unzipped.read().decode()})

    data = files.get("models.csv")
    ext_path = Path(dirname(model_path), "models.csv")

    with open(ext_path, "w") as f:
        f.write(data)

    df = read_csv(ext_path)

    return df

def tozip(model_path: str, df: DataFrame, delete=False) -> dict:
    """ Simple helper function that zips a file provided it's content as a
    string and the filename within the zip file as well as the path of the zip
    file itself. The files contained within the zipfile must be text files.

    Args:
        model_path (str): Path to model zip file.
        df (DataFrame): The DataFrame to be persisted.
        delete (bool): Whether the csv file should be deleted after zipping.
    """

    ext_path = Path(dirname(model_path), "models.csv")
    df.to_csv(ext_path, index=False)

    with open(ext_path) as models:
        with ZipFile(model_path, "w") as zip_file:
            zip_file.writestr("models.csv", models.read())

    if delete:
        remove(ext_path)


def extract_func_names(paths: List[dict]):
    """Extract function name of first node for each path.

    Args:
        paths (list(dict)): A list of paths.

    Returns:
        function_names (list[str]): The function names for the
        first node of each path.
    """
    function_names = []
    for path in paths:
        func_name = path[0].get("func_name")
        function_names.append(str(func_name))

    return function_names
