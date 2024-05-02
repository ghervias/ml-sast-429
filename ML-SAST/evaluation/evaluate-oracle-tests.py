import json
import os
from re import split
from typing import List

import pandas as pd

defects_zlib = [
    {"lib": "zlib",
     "hash": "6a043145ca6e9c55184013841a67b2fef87e44c0",
     "affected_function": [
         {"filename": "inftrees.c", "lines": [57, 184, 188, 190, 191, 196, 219, 223, 224, 225]}
     ]},
    {"lib": "zlib",
     "hash": "e54e1299404101a5a9d0cf5e45512b543967f958",
     "affected_function": [{"filename": "inflate.c", "lines": [1509, 1511]}]
     },
    {"lib": "zlib",
     "hash": "9aaec95e82117c1cb0f9624264c3618fc380cecb",
     "affected_function": [
         {"filename": "inffast.c",
          "lines": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 99, 101, 122, 124, 137,
                    144, 153, 155, 168, 171, 199, 205, 210, 216, 222, 233, 235, 240, 251, 257, 258, 259, 263, 265, 271,
                    272, 273, 277, 279, 316, 317]}
     ]},
    {"lib": "zlib",
     "hash": "d1d577490c15a0c6862473d7576352a9f18ef811",
     "affected_function": [{"filename": "crc32", "lines": [281, 303, 312]}]
     }
]
defects_miniupnp = [
    # miniupnp
    {"lib": "miniupnp",
     "hash": "79cca974a4c2ab1199786732a67ff6d898051b78",
     "affected_function": [
         {"filename": "miniupnpc/igd_desc_parse.c", "lines": [18]}]
     },
    {"lib": "miniupnp",
     "hash": "140ee8d2204b383279f854802b27bdb41c1d5d1a",
     "affected_function": [
         {"filename": "minissdpd/minissdpd.c", "lines": [661, 656]}]
     },
    {"lib": "miniupnp",
     "hash": "b238cade9a173c6f751a34acf8ccff838a62aa47",
     "affected_function": [
         {"filename": "minissdpd/minissdpd.c", "lines": [850, 972, 990, 1008]},
         {"filename": "minissdpd/testminissdpd.c", "lines": [68, 184, 185, 186, 187, 188, 189, 190, 191, 192]}]
     },
    {"lib": "miniupnp",
     "hash": "7aeb624b44f86d335841242ff427433190e7168a",
     "affected_function": [
         {"filename": "miniupnpc/upnpreplyparse.c", "lines": [107, 108, 109]},
         {"filename": "miniupnpd/upnpreplyparse.c", "lines": [107, 108, 109]}
     ]
     },
    {"lib": "miniupnp",
     "hash": "cb8a02af7a5677cf608e86d57ab04241cf34e24f",
     "affected_function": [
         {"filename": "miniupnpd/pcpserver.c", "lines": [180]}]
     }
]
defects_libtiff = [
    {"lib": "libtiff",
     "hash": "ce6841d9e41d621ba23cf18b190ee6a23b2cc833",
     "affected_function": [
         {"filename": "tools/gif2tiff.c", "lines": [403]},
     ]
     },
    {"lib": "libtiff",
     "hash": "5ad9d8016fbb60109302d558f7edb2cb2a3bb8e3",
     "affected_function": [
         {"filename": "tools/tiffcp.c", "lines": [1341, 1526]},
     ]
     },
    {"lib": "libtiff",
     "hash": "ae9365db1b271b62b35ce018eac8799b1d5e8a53",
     "affected_function": [
         {"filename": "tools/tiffcrop.c", "lines": [822, 823, 824, 825, 826, 827, 828, 831, 832, 833]},
     ]
     },
    {"lib": "libtiff",
     "hash": "3ca657a8793dd011bf869695d72ad31c779c3cc1",
     "affected_function": [
         {"filename": "libtiff/tif_predict.c",
          "lines": [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 276, 282, 326, 333, 354, 261, 364, 371, 385, 395,
                    398, 435, 436, 459, 462, 471, 478, 518, 526, 548, 544, 549, 557, 569, 575, 583, 593, 594, 596, 628,
                    663]},
     ]
     },
    {"lib": "libtiff",
     "hash": "b18012dae552f85dcc5c57d3bf4e997a15b1cc1c",
     "affected_function": [
         {"filename": "libtiff/tif_next.c", "lines": [40, 125]},
     ]
     },
    {"lib": "libtiff",
     "hash": "5c080298d59efa53264d7248bbe3a04660db6ef7",
     "affected_function": [
         {"filename": "tools/tiffcp.c", "lines": [594, 1787]},
     ]
     },
    {"lib": "libtiff",
     "hash": "9657bbe3cdce4aaa90e07d50c1c70ae52da0ba6a",
     "affected_function": [
         {"filename": "tools/tiffcrop.c", "lines": [3701]},
     ]
     },
    {"lib": "libtiff",
     "hash": "9a72a69e035ee70ff5c41541c8c61cd97990d018",
     "affected_function": [
         {"filename": "libtiff/tif_dirread.c",
          "lines": [5505, 5506, 5537, 5541, 5542, 5543, 5544, 5546, 5548, 5565, 5569, 5576, ]},
         {"filename": "libtiff/tif_strip.c", "lines": [66, 67, 68, 69, 70, 71, 72, 73, 74]},
     ]
     },
    {"lib": "libtiff",
     "hash": "1044b43637fa7f70fb19b93593777b78bd20da86",
     "affected_function": [
         {"filename": "libtiff/tif_luv.c", "lines": [1575, 1576, 1577, 1578]},
         {"filename": "libtiff/tif_pixarlog.c", "lines": [1246, 1247]},
     ]
     },
    {"lib": "libtiff",
     "hash": "5397a417e61258c69209904e652a1f409ec3b9df",
     "affected_function": [
         {"filename": "tools/tiffcp.c", "lines": [988]},
     ]
     },
    {"lib": "libtiff",
     "hash": "43bc256d8ae44b92d2734a3c5bc73957a4d7c1ec",
     "affected_function": [
         {"filename": "libtiff/tif_ojpeg.c", "lines": [787]},
     ]
     },
    {"lib": "libtiff",
     "hash": "438274f938e046d33cb0e1230b41da32ffe223e1",
     "affected_function": [
         {"filename": "libtiff/tif_read.c", "lines": [349, ]},
     ]
     },
    {"lib": "libtiff",
     "hash": "c7153361a4041260719b340f73f2f76",
     "affected_function": [
         {"filename": "tools/tiff2pdf.c", "lines": [2898]},
     ]
     },
    {"lib": "libtiff",
     "hash": "787c0ee906430b772f33ca50b97b8b5ca070faec",
     "affected_function": [
         {"filename": "tools/tiffcp.c", "lines": [1166, 1323, 1351]},
     ]
     },
    {"lib": "libtiff",
     "hash": "391e77fcd217e78b2c51342ac3ddb7100ecacdd2",
     "affected_function": [
         {"filename": "libtiff/tif_pixarlog.c", "lines": [675]},
     ]
     },
    {"lib": "libtiff",
     "hash": "3c5eb8b1be544e41d2c336191bc4936300ad7543",
     "affected_function": [
         {"filename": "libtiff/tif_unix.c", "lines": [260, 261, 262]},
     ]
     },
    {"lib": "libtiff",
     "hash": "6a984bf7905c6621281588431f384e79d11a2e33",
     "affected_function": [
         {"filename": "libtiff/tif_predict.c", "lines": [412, 643]},
     ]
     },
]
defects_openjpeg = [
    {"lib": "openjpeg",
     "hash": "c16bc057ba3f125051c9966cf1f5b68a05681de4",
     "affected_function": [
         {"filename": "src/lib/openjp2/pi.c", "lines": [1240]}]
     },
    {"lib": "openjpeg",
     "hash": "e078172b1c3f98d2219c37076b238fb759c751ea",
     "affected_function": [
         {"filename": "src/lib/openjp2/tcd.c", "lines": [685]}]
     },
    {"lib": "openjpeg",
     "hash": "940100c28ae28931722290794889cf84a92c5f6f",
     "affected_function": [
         {"filename": "src/lib/openjp2/j2k.c", "lines": [5562]}]
     },
    {"lib": "openjpeg",
     "hash": "dcac91b8c72f743bda7dbfa9032356bc8110098a",
     "affected_function": [
         {"filename": "src/lib/openjp2/j2k.c", "lines": [835, 836, 11575, 11618]}]
     },
    {"lib": "openjpeg",
     "hash": "afb308b9ccbe129608c9205cf3bb39bbefad90b9",
     "affected_function": [
         {"filename": "src/lib/openjp2/tcd.c", "lines": [1191]}]
     },
    {"lib": "openjpeg",
     "hash": "e5285319229a5d77bf316bb0d3a6cbd3cb8666d9",
     "affected_function": [
         {"filename": "src/bin/jp2/convert.c", "lines": [1188]}]
     },
    {"lib": "openjpeg",
     "hash": "2cd30c2b06ce332dede81cccad8b334cde997281",
     "affected_function": [
         {"filename": "src/bin/jp2/convert.c", "lines": [775]}]
     },
    {"lib": "openjpeg",
     "hash": "baf0c1ad4572daa89caa3b12985bdd93530f0dd7",
     "affected_function": [
         {"filename": "src/bin/jp2/convertbmp.c", "lines": [393]}]
     },
    {"lib": "openjpeg",
     "hash": "d27ccf01c68a31ad62b33d2dc1ba2bb1eeaafe7b",
     "affected_function": [
         {"filename": "src/lib/openjp2/pi.c", "lines": [358, 370]}]
     },
    {"lib": "openjpeg",
     "hash": "397f62c0a838e15d667ef50e27d5d011d2c79c04",
     "affected_function": [{"filename": "src/lib/openjp2/tcd.c", "lines": [1185]}]
     },
    {"lib": "openjpeg",
     "hash": "162f6199c0cd3ec1c6c6dc65e41b2faab92b2d91",
     "affected_function": [
         {"filename": "src/bin/common/color.c", "lines": [849]}]
     },
    {"lib": "openjpeg",
     "hash": "15f081c89650dccee4aa4ae66f614c3fdb268767",
     "affected_function": [
         {"filename": "src/bin/common/color.c",
          "lines": [94, 100, 107, 108, 109, 124, 125, 126, 127, 134, 136, 141, 148, 149, 150, 156, 163, 172, 173, 174,
                    175, 176, 177, 178, 179, 180, 181, 182, 186, 187, 188, 189, 196, 198, 203, 210, 211, 212213, 214,
                    216, 221, 233, 243, 245, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 279, 280, 281, 282,
                    327, 328]},
         {"filename": "src/bin/jp2/convertbmp.c", "lines": [970]}
     ]
     },
    {"lib": "openjpeg",
     "hash": "8ee335227bbcaf1614124046aa25e53d67b11ec3",
     "affected_function": [
         {"filename": "src/bin/jp2/convertbmp.c", "lines": [537, 544]}]
     },
    {"lib": "openjpeg",
     "hash": "c58df149900df862806d0e892859b41115875845",
     "affected_function": [
         {"filename": "src/lib/openjp2/pi.c", "lines": [766, 767, 768, 769, 770, 771, 772, 773]}]
     },
    {"lib": "openjpeg",
     "hash": "c277159986c80142180fbe5efb256bbf3bdf3edc",
     "affected_function": [
         {"filename": "src/lib/openmj2/pi.c",
          "lines": [114, 115, 116, 156, 157, 158, 256, 257, 258, 356, 357, 358, 454, 455, 456]}]
     },
    {"lib": "openjpeg",
     "hash": "c5bd64ea146162967c29bd2af0cbb845ba3eaaaf",
     "affected_function": [
         {"filename": "src/lib/openmj2/pi.c", "lines": [225, 226, 318, 319, 409, 410]}]
     },
    {"lib": "openjpeg",
     "hash": "5d00b719f4b93b1445e6fb4c766b9a9883c57949",
     "affected_function": [
         {"filename": "src/lib/openjp2/pi.c", "lines": [711, 712, 713, 714]},
         {"filename": "src/lib/openjp2/tcd.c", "lines": [704, 705, 706, 707]}
     ]
     },
    {"lib": "openjpeg",
     "hash": "ef01f18dfc6780b776d0674ed3e7415c6ef54d24",
     "affected_function": [
         {"filename": "src/lib/openjp2/pi.c", "lines": [1244]}]
     },
]


def load_report(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def save_report(filepath, report):
    with open(filepath, "w") as f:
        json.dump(report, f)


def filter_report_for_filenames(report: List[dict], filenames: List[str]):
    matching_reports = []
    for item in report:
        names_in_filenames = []
        for filename in filenames:
            if is_name_in_filenames(filename, item["filenames"]):
                names_in_filenames.append(True)
        if any(names_in_filenames):
            matching_reports.append(item)
    return matching_reports


def is_name_in_filenames(name, filenames):
    for filename in filenames:
        if name in filename:
            return True
    return False


def normalize_llvm_debug_information(debug_information: str):
    return debug_information.replace("{", "").replace("}", "").strip()


def src_loc_from_dbg_str(dbg_str):
    """ Helper that finds a file location given as a debug string in
    LLVM format.

    Args:
        dbg_str: The LLVM debug location
    Returns:
        str: The location (line) and the file name.
    """

    loc = {'line': 0, 'file': False}
    match = split(r'\s*ln:\s*(\d+).*fl:.', dbg_str)
    if match and len(match) == 3:
        loc['line'] = int(match[1])
        loc['file'] = match[2]
    else:
        match = split(r'\s*in line:\s*(\d+).*file:.', dbg_str)
        if match and len(match) == 3:
            loc['line'] = int(match[1])
            loc['file'] = match[2]
    return loc


def get_relevant_source_locations(source_location_of_nodes: List[str]):
    """Get relevant llvm debug code.
    Input:
        ['{ in line: 1066 file: upnphttp.c }', '{ ln: 1071  cl: 9  fl: upnphttp.c }']
    """
    all_locations = []
    for source_location in source_location_of_nodes:
        location = src_loc_from_dbg_str(source_location)
        all_locations.append(location)

    all_locations = pd.DataFrame.from_dict(all_locations)
    all_locations.drop_duplicates(inplace=True)

    return all_locations.sort_values(by=["line"])


def filter_reports_by_line_number(reports: List[dict], affected_functions: List[dict]):
    """Filter reports that have a line number which is also in the defect.
    Paths that have been merged, do not contain the original path. Only non-
    merged paths contain the original path. From merged paths the line numbers
    can be checked directly, while from non-merged paths the line numbers for
    the different files need to be extracted.

    Args:
        reports (List[dict]): Reported paths detected by the ml-sast-prototype

    Returns:
        List[dict]: Paths which line number matches the defect.
    """
    matching_reports = []
    for item in reports:
        if ("original_path" in item.keys()):
            source_locations = [normalize_llvm_debug_information(node["src_loc"]) for node in item["original_path"] if
                                node["src_loc"] != ""]
        else:
            line_numbers = item["hl_lines"]
            file_names = item["filenames"]
            source_locations = [f"in line: {line_numbers[x]} file: {file_names[x]}" for x in range(len(line_numbers))]

        relevant_source_locations = get_relevant_source_locations(source_locations)
        possible_match = []
        for affected_function in affected_functions:
            these_relevant_source_locations = relevant_source_locations[
                relevant_source_locations["file"].str.contains(affected_function["filename"])]
            possible_match.extend(
                [affected_function["lines"][x] in these_relevant_source_locations["line"].values for x in
                 range(len(affected_function["lines"]))])
        if any(possible_match):
            matching_reports.append(item)
    return matching_reports


CURRENT_DIR = os.getcwd()
RESULT_PARENT_PATH = f"{CURRENT_DIR}/results/lib/"
PATH_TO_RESULT_CSV = f"{CURRENT_DIR}/results/paths_stats.csv"
THRESHOLD_VALUE = "1.0"

all_defects = []
all_defects.extend(defects_zlib)
all_defects.extend(defects_openjpeg)
all_defects.extend(defects_libtiff)
all_defects.extend(defects_miniupnp)

collected_data = []

for one_defect in all_defects:

    filepath_detected = os.path.join(RESULT_PARENT_PATH, one_defect["lib"], one_defect["hash"], THRESHOLD_VALUE,
                                     "report.json")
    filepath_merged = os.path.join(RESULT_PARENT_PATH, one_defect["lib"], one_defect["hash"], THRESHOLD_VALUE,
                                   "merged_report.json")
    filepath_filtered_reports = os.path.join(RESULT_PARENT_PATH, one_defect["lib"], one_defect["hash"], THRESHOLD_VALUE,
                                             "filtered_report.json")

    merged_reports = load_report(filepath_merged)
    detected_reports = load_report(filepath_detected)
    number_of_merged_paths = len(merged_reports)
    number_of_detected_paths = len(detected_reports)

    filenames_from_defect = [one_defect["affected_function"][x]["filename"] for x in
                             range(len(one_defect["affected_function"]))]
    matching_reports_by_filenames = filter_report_for_filenames(detected_reports, filenames_from_defect)

    matching_reports_by_filenames_and_linenumbers = filter_reports_by_line_number(
        matching_reports_by_filenames, one_defect["affected_function"])

    number_of_filtered_paths = len(matching_reports_by_filenames_and_linenumbers)

    if number_of_filtered_paths > 0:
        save_report(filepath_filtered_reports, matching_reports_by_filenames_and_linenumbers)

    collected_data.append({
        "lib": one_defect["lib"],
        "hash": one_defect["hash"],
        "number_of_paths_below_threshold": number_of_detected_paths,
        "number_of_merged_paths_below_threshold": number_of_merged_paths,
        "number_of_paths_that_overlap_the_defect": number_of_filtered_paths
    })

collected_data = pd.DataFrame.from_dict(collected_data)
collected_data.to_csv(PATH_TO_RESULT_CSV)
