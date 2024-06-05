import json
import operator
from os.path import dirname
from pathlib import Path
from sys import exit
from typing import List

import numpy as np
import pandas as pd
# noinspection PyUnresolvedReferences
import swifter
from pandas import DataFrame, Series
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split

from mlsast.logic import Project
from mlsast.util.helpers import (retrieve_source_location,
                                 src_loc_from_dbg_str, unzip)
from .analysisstep import AnalysisStep
from .basestep import requires_steps, step


class distance(AnalysisStep):
    """Implementation of the centroid based distance analysis.

    Args:
        AnalysisStep (AnalysisStep): The base class.
    """

    @requires_steps("svf", "neo4j")
    def __init__(self, project: Project) -> None:
        """Constructor of the distance analysis step.

        Args:
            project (Project): The current project.
        """
        super().__init__(project)

    def __str__(self) -> str:
        return type(self).__name__

    @step
    def run(self):
        self._compute_distance()

    def _compute_distance(self):
        """Executes all the steps necessary to compute the minimal distance of
        paths from a software project to centroids initialized on known defects.
        """
        conf = self.project.config

        # load paths from juliet test set
        paths = self._load_paths_from_model()

        # filter paths
        paths = self._filter_paths(paths)

        # embed paths from juliet test set
        embedded_paths = self._embed_paths(paths)

        # sample paths into train and test set to obtain optimal thresholds on
        # ground truth
        train_size = 0.5
        sampled_paths = self._sample_paths(embedded_paths, train_size)

        train_good_paths = sampled_paths[0]
        train_bad_paths = sampled_paths[1]
        test_good_paths = sampled_paths[2]
        test_bad_paths = sampled_paths[3]

        combined_test_paths = test_good_paths.append(test_bad_paths)

        # on which paths should the centroids be formed
        initialize_centroids_on_paths_of_type = conf.find("distance.centroids")

        if initialize_centroids_on_paths_of_type == "bad":
            centroids = self._get_centroids(train_bad_paths)
            comparison = operator.gt

        else:
            centroids = self._get_centroids(train_good_paths)
            comparison = operator.lt

        # estimate threshold on known paths
        centroids_with_thresholds = self._get_thresholds(
            combined_test_paths,
            centroids,
            comparison
        )

        # get paths to be analyzed
        paths_to_analyze = self._get_paths_to_analyze()

        # embed paths to be analyzed
        paths_to_analyze = self._embed_paths(paths_to_analyze)

        # compute minimal distance between centroids and data to test
        paths_to_analyze = self.distance_to_centroids(
            paths_to_analyze,
            centroids_with_thresholds
        )

        # generate report
        paths_with_matches = self._generate_report(
            paths_to_analyze,
            centroids_with_thresholds
        )

        merged_paths = self._merge_similar_paths(paths_with_matches)
        self._logger.info(
            f"In total {len(paths_to_analyze)} paths were detected and " \
            + f"{len(paths_with_matches)} paths were 'close' to " \
            + "centroids from the juliet test cases")

        self._logger.info(
            f"In total {len(paths_to_analyze)} paths were detected and {len(merged_paths)} "
            f"merged paths were 'close' to centroids from the juliet test cases")
        # save report in project_root
        self._save_report(paths_with_matches, "report")
        self._logger.info("report was saved")
        self._save_report(merged_paths, "merged_report")
        self._logger.info("merged report was saved")

    def _load_paths_from_model(self):
        """Load paths of known defects.

        Returns:
            DataFrame: A pandas dataframe containing the paths of known defects.
            Each path is labelled as either benign or unsafe.
        """

        conf = self.project.config
        parent_path = self.project.module_root.parent
        model_path = conf.find("distance.model_path", abort=True,
                               level="CRITICAL")
        extraction_path = parent_path / Path(dirname(model_path)) / "models.csv"

        models = unzip(parent_path / model_path).get("models.csv")

        with open(extraction_path, "w") as f:
            f.write(models)

        df = pd.read_csv(extraction_path)
        df["path"] = df["path"].swifter.progress_bar(False).apply(json.loads)

        return df

    def _filter_paths(self, paths: DataFrame):
        """Filter paths to keep certain defect classes or to exclude certain
        defect classes to initialize the model.

        Args:
            paths (DataFrame): DataFrame of paths of different defect classes.

        Returns:
            paths (DataFrame): DataFrame containing defect classes defined in the
            projects config.yaml file.
        """

        conf = self.project.config

        include_models = conf.find("distance.include_models", level="DEBUG",
                                   abort=False)
        exclude_models = conf.find("distance.exclude_models", level="DEBUG",
                                   abort=False)

        if include_models is None and exclude_models is None:
            self._logger.critical("No cwe classes were selected to " \
                                  + "initialize the model")
            exit(1)

        if include_models == "all":
            return paths

        elif isinstance(include_models, list):
            classes_to_include = [int(model.split("CWE-")[1]) \
                                  for model in include_models]

            return paths[paths["cwe"].isin(classes_to_include)]
        else:
            classes_to_exclude = [int(model.split("CWE-")[1]) \
                                  for model in exclude_models]

            return paths[~paths["cwe"].isin(classes_to_exclude)]

    def _embed_paths(self, paths: DataFrame):
        """Embeds the paths. Converts each path into a numerical vector.

        Args:
            paths (DataFrame): DataFrame of paths to be embedded. The property
            used for embedding is defined in the config.yaml (distance.node_property)
            of the project.

        Returns:
            paths (DataFrame): DataFrame of embedded paths.
        """

        def _apply_sequence(s: Series, node_property_to_embed: str):
            if node_property_to_embed is None:
                node_property_to_embed = "node_type"
            return s.swifter.progress_bar(False).apply(
                lambda path: [float(node[node_property_to_embed]) \
                                  if node[node_property_to_embed] \
                                  else -1 for node in path])

        def _apply_padding(s: Series, padding=-1.0) -> Series:
            upper = max(s.swifter.progress_bar(False).apply(len))

            return s.swifter.progress_bar(False).apply(
                lambda x: x + ([padding] * (upper - len(x))))

        def _apply_normalize(s: Series) -> Series:
            lower = 0
            upper = 0

            for item in s:
                lower = min(item) if min(item) < lower else lower
                upper = max(item) if max(item) > upper else upper

            return s.swifter.progress_bar(False).apply(
                lambda p: [(x - lower) / (upper - lower) for x in p])

        copied_paths = paths.copy()
        conf = self.project.config
        node_property_to_embed = conf.find("distance.node_property", abort=False, level="INFO")
        copied_paths["embed"] = _apply_sequence(copied_paths["path"], node_property_to_embed)
        copied_paths["embed"] = _apply_padding(copied_paths["embed"], -1)
        copied_paths["embed"] = _apply_normalize(copied_paths["embed"])

        return copied_paths

    def _sample_paths(self, paths: pd.DataFrame, train_size: float) \
            -> (List[pd.DataFrame]):
        """Split good and bad paths from model into train and test set.

        Args:
            paths (DataFrame): DataFrames of paths to be sampled.
            train_size (float): Size of the training sample.
        Returns:
            List[DataFrame]: A List of DataFrames containing the splits
            for good and bad training samples, as well as the good and bad
            test samples.
            In this order: [train_good, test_good, train_bad, test_bad]
        """

        good_paths = paths[paths["safe"]]
        bad_paths = paths[~paths["safe"]]

        train_good, test_good = train_test_split(
            good_paths, train_size=train_size, random_state=42)
        train_bad, test_bad = train_test_split(
            bad_paths, train_size=train_size, random_state=42)

        return [train_good, train_bad, test_good, test_bad]

    def _get_centroids(self, paths: DataFrame) -> DataFrame:
        """Compute centroids of the embedded paths for each defect class.

        Args:
            paths (DataFrame): DataFrame of paths.

        Returns:
            centroids (DataFrame): DataFrame of k centroids for each defect class.
        """
        conf = self.project.config

        clustering_type = conf.find(
            "distance.clustering_type",
            abort=True,
            level="CRITICAL"
        )

        expected_clusters = conf.find(
            "distance.expected_clusters",
            abort=True,
            level="CRITICAL"
        )

        # create centroids for each CWE
        unique_cwes = paths["cwe"].unique()

        centroids = []
        for unique_cwe in unique_cwes:
            selected_paths = paths[paths["cwe"] == unique_cwe]
            x_path = np.asarray(selected_paths["embed"].to_list())

            if x_path.shape[0] < expected_clusters:
                self._logger.warning("Not enough samples for cwe %s, " \
                                     "skipping this cwe.", unique_cwe)

                continue

            if clustering_type == "kmeans":
                kmeans = KMeans(n_clusters=expected_clusters, random_state=42)
                kmeans.fit(x_path)

                centroids.append({
                    "cwe": unique_cwe,
                    "centroids": kmeans.cluster_centers_
                })

            else:
                self._logger.critical("Clustering Algorithm not supported %s.",
                                      clustering_type)

        return pd.DataFrame.from_dict(centroids)

    def _get_thresholds(self, paths: DataFrame, centroids_raw: DataFrame,
                        operator):
        """Compute optimal thresholds on paths with known ground truth to
        distinguish benign and unsafe paths for the different defect classes.

        Args:
            paths (DataFrame): DataFrame of paths with known ground truth, regarding
            benign or unsafe.
            centroids_raw (DataFrame): DataFrame of centroids per defect class.
            operator (Operator): Comparison operator, either < or >, depends on the
            specified target in the config.yaml file of the project.

        Returns:
            centroids (DataFrame): DataFrame of centroids per defect class with the
            optimal threshold to distinguish beningn and unsafe paths in the test set.
        """

        centroids = centroids_raw.copy()
        centroids["auc"] = np.nan
        centroids["optimal_threshold"] = np.nan
        centroids["lower_threshold"] = np.nan
        centroids["upper_threshold"] = np.nan

        step_width = 0.2

        for index, row in centroids.iterrows():
            current_centroids = row["centroids"]
            cwe = row["cwe"]

            path_samples = paths[paths["cwe"] == cwe].copy()
            path_samples["distances"] = np.nan
            path_samples["min_distance"] = np.nan

            path_samples["distances"] = \
                path_samples["embed"].swifter.progress_bar(False).apply(
                    lambda path: [np.linalg.norm(centroid - np.asarray(path)) \
                                  for centroid in current_centroids])

            path_samples["min_distance"] = \
                path_samples["distances"].swifter.progress_bar(False).apply(min)

            lower_boundary = path_samples["min_distance"].min()
            upper_boundary = path_samples["min_distance"].max()

            tpr, fpr, thresholds = self._get_tpr_fpr(
                path_samples,
                lower_boundary,
                upper_boundary,
                step_width,
                operator
            )

            auc = np.abs(np.trapz(tpr, fpr))
            threshold = self._compute_best_threshold(fpr, tpr, thresholds)

            centroids.loc[index, "auc"] = auc
            centroids.loc[index, "optimal_threshold"] = threshold
            centroids.loc[index, "lower_threshold"] = lower_boundary
            centroids.loc[index, "upper_threshold"] = upper_boundary

        return centroids

    def _get_tpr_fpr(self, sampled_paths: DataFrame, lower_boundary: float,
                     upper_boundary: float, step_width: float, comparison):
        """Compute true positive and false positive rate for various thresholds,
        analogous to a receiver operating characteristic curve.

        Args:
            sampled_paths (DataFrame): DataFrame of paths for one defect class.
            lower_boundary (float): Minimal distance of sampled paths to centroids.
            upper_boundary (float): Maximal distance of sampled paths to centroids.
            step_width (float): Step width of the various comparisons.
            comparison: Comparison operation to perform, is either < or >.

        Returns:
            true_positive_rates (List[float]): True positive rates for various thresholds.
            false_positive_rates (List[float]): False positive rates for various thresholds.
            steps (np.array): Various thresholds.

        """


        df_temp = sampled_paths.copy()

        steps = np.arange(lower_boundary, upper_boundary \
                          + step_width, step_width)
        true_positive_rates = []
        false_positive_rates = []

        for step in steps:
            df_temp["pred_safe"] = \
                df_temp["min_distance"].swifter.progress_bar(False).apply(
                    lambda x: comparison(x, step))

            tp, tn, fp, fn = self._evaluate_run(df_temp)
            tpr = tp / (tp + fn)
            fpr = fp / (fp + tn)

            true_positive_rates.append(tpr)
            false_positive_rates.append(fpr)

        return true_positive_rates, false_positive_rates, steps

    def _compute_best_threshold(self, false_positive_rates: List[float],
                                true_positive_rates: List[float],
                                thresholds: List[float]):
        """Compute optimal threshold from geometric mean of true positive, false
        positive rates and their respective thresholds.

        Args:
            true_positive_rates (List[float]): True positive rates for various thresholds.
            false_positive_rates (List[float]): False positive rates for various thresholds.
            steps (np.array): Various thresholds.

        Returns:
            optimal_threshold (float): Optimal threshold.
        """
        gmeans = np.sqrt(np.asarray(true_positive_rates) \
                         * (1 - np.asarray(false_positive_rates)))
        max_index = np.argmax(gmeans)

        return thresholds[max_index]

    def _evaluate_run(self, df: DataFrame):
        """Compute true positives, true negatives, false positives and false
        negatives for the different paths from the test set.

        Args:
            df (DataFrame): DataFrame of paths with known ground truth.

        Returns:
            tp (int) : Number of true positives.
            tn (int) : Number of true negatives.
            fp (int) : Number of false positives.
            fn (int) : Number of false negatives.
        """
        tp = df[df.eval("not safe and not pred_safe")].shape[0]
        tn = df[df.eval("safe and pred_safe")].shape[0]
        fp = df[df.eval("safe and not pred_safe")].shape[0]
        fn = df[df.eval("not safe and pred_safe")].shape[0]

        return tp, tn, fp, fn

    def _get_paths_to_analyze(self):
        """Read paths exported by the previous step (neo4j) from the project directory.

        Returns:
            paths: DataFrame of paths.
        """

        def _read_paths(f_path: str) -> DataFrame:
            all_paths = {"proc": [], "path": [], "err": []}

            with open(f_path, "r") as file:
                for line in file:
                    row = json.loads(line)

                    f = row["f"]
                    path = row["path"]

                    reduced_path = []
                    for node in path.get("nodes"):
                        reduced_node = {}
                        props = node["properties"]

                        reduced_node.update({"full_inst":
                                                 props.get("full_inst", "")})
                        reduced_node.update({"src_loc":
                                                 props.get("src_loc", "")})
                        reduced_node.update({"ir_opcode":
                                                 props.get("ir_opcode", "")})
                        reduced_node.update({"n_hash":
                                                 props.get("n_hash", "")})
                        reduced_node.update({"node_type":
                                                 props.get("node_type", "")})
                        reduced_node.update({"func_name":
                                                 props.get("func_name", "")})
                        reduced_node.update({"cs_name":
                                                 props.get("cs_name", "")})
                        reduced_node.update({"node_name":
                                                 props.get("node_name", "")})
                        reduced_node.update({"id":
                                                 node.get("id", "")})

                        reduced_path.append(reduced_node)

                    all_paths.get("proc").append(f)
                    all_paths.get("path").append(reduced_path)
                    all_paths.get("err").append(False)

                df = DataFrame.from_dict(all_paths)
                # validate icfg
                for row in df.iterrows():
                    index = row[0]
                    path = row[1]["path"]
                    stack = []
                    for node in path:
                        if node["node_name"] == "CallICFGNode":
                            stack.append(node["cs_name"])
                        if node["node_name"] == "RetICFGNode":
                            if not stack:
                                df.at[index, "err"] = True
                                break
                            last_frame = stack.pop()
                            if last_frame != node["cs_name"]:
                                df.at[index, "err"] = True
                                break
                df = df.drop(df[df["err"]].index)
                df = df.drop("err", axis=1)
                df = df.reset_index(drop=True)
            return df

        path_neo_query_results = self.project.project_root \
                                 / "neo4j" / "export" / "query_results.json"
        paths = _read_paths(path_neo_query_results)

        return paths

    def distance_to_centroids(self, paths: DataFrame, centroids: DataFrame):
        """Computes the minimal distance between each path and a set of centroids.
        The minimal distance is computed for each defect class.

        Args:
            paths (DataFrame): DataFrame of paths.
            centroids (DataFrame): DataFrame of centroids, for each defect class (row)
            there are k centroids.

        Returns:
            paths (DataFrame): DataFrame of paths with minimal distance to centroids of
            each defect class.
        """

        for index, centroids_per_cwe in centroids.iterrows():
            cwe = centroids_per_cwe["cwe"]
            paths[f"distances_{cwe}"] = np.nan
            paths[f"distances_{cwe}"] = \
                paths["embed"].swifter.progress_bar(False).apply(
                    lambda path: [np.linalg.norm(centroid - np.asarray(path)) \
                                  for centroid in centroids_per_cwe["centroids"]])

            paths[f"min_distance_to_centroids_of_{cwe}"] = \
                paths[f"distances_{cwe}"].swifter.progress_bar(False).apply(
                    lambda distances: min(distances))

            paths.drop(columns=[f"distances_{cwe}"], inplace=True)

        return paths

    def _generate_report(self, paths: DataFrame, thresholds: DataFrame):
        """Generates report of paths that are close to centroids defined on
        known defects.

        Args:
            paths (DataFrame): DataFrame of paths.
            thresholds (DataFrame): DataFrame of thresholds per defect class.

        Returns:
            paths_with_matching_centroids (List[dict]): Dictionary of paths
            that are close to centroids defined on known defects. The dictionary
            contains the actual path, the corresponding source code and further
            values to display the results with the custom frontend.
        """
        conf = self.project.config
        code_delta = conf.find("distance.source_code_delta")
        scaling_factor = conf.find("distance.threshold_scaling")

        thresholds["scaled_threshold"] = \
            thresholds["optimal_threshold"] * scaling_factor

        paths_with_matching_centroids = []
        for _, path in paths.iterrows():
            matching_centroids, stats = \
                self._find_path_below_threshold(path, thresholds)

            if len(matching_centroids) > 0:
                source_code, line_dict, highlighted_lines, filenames = \
                    self._get_source_code(path, code_delta)

                paths_with_matching_centroids.append({
                    "original_path": path["path"],
                    "path": path["embed"],
                    "stats": stats,
                    "code": source_code,
                    "line_dict": line_dict,
                    "hl_lines": highlighted_lines,
                    "filenames": filenames})

        return paths_with_matching_centroids

    def _find_path_below_threshold(self, path: Series, thresholds: DataFrame):
        """Finds paths that are below a defined threshold.

        Args:
            path (Series): A single path.
            thresholds (DataFrame): A DataFrame of thresholds for each defect class.

        Returns:
            matching_classes (List[dict]): List of dictionaries, where each dictionary
            contains the defect class the path is close to, the actual minimal distance
            of the path to the centroids of this defect class, the threshold and the
            relative distance of the path to the centroids of this defect class (a value
            of 100 % means that the path is directly on the centroid)
            stats (List[dict]): List of dictionary, where each dictionary contains the cwe
            the path is close to as well as the relative distance of the path to the centroids
            of this defect class.
        """
        matching_classes = []
        stats = {}

        dist_path_cents = list(
            filter(lambda element:
                   element[0].startswith("min_distance_to_centroids_of_"),
                   list(path.items())))

        for item in dist_path_cents:
            cwe = item[0].split("min_distance_to_centroids_of_")[1]
            value = item[1]

            compare = thresholds[thresholds["cwe"] == int(cwe)]
            compare = compare["scaled_threshold"].values[0]

            thresh_percent = 100. / compare * value
            dist_percent = np.abs(thresh_percent - 100.)

            if value < compare:
                matching_classes.append({
                    "cwe": cwe, "distance": value,
                    "threshold": compare,
                    "value_in_percent_of_threshold": thresh_percent,
                    "dist_to_centroid_in_percentage": dist_percent
                })

                stats.update({f"CWE-{cwe}": dist_percent})

        matching_classes_sorted = list(sorted(matching_classes,
                                              key=lambda match:
                                              match["dist_to_centroid_in_percentage"],
                                              reverse=True))
        stats_sorted = dict(sorted(stats.items(), key=lambda item: item[1], reverse=True))

        return matching_classes_sorted, stats_sorted

    def _get_source_code(self, path: Series, delta: int):
        """Reads the related source code of a path.

        Args:
            path (Series): A single path.
            delta (int): Number of lines of source code to extract before and
            after the path.

        Returns:
            source_code (str): Source code of the path.
            line_dict (dict): Dictionary of line numbers. Where the keys are from
            '1' to 'n' with n = number of extracted lines. The values correspond
            to the extracted lines from the source code.
            highlighted_lines (List[int]): Lines of the different nodes, extracted
            from the llvm debug information.
            filenames (List[str]): List of filenames the path traverses over.
            """
        real_path = path["path"]
        source_location_of_nodes = \
            [self._normalize_dbg_infos(node["src_loc"]) \
             for node in real_path if node["src_loc"] != ""]
        relevant_source_locations = \
            self._get_relevant_source_locations(source_location_of_nodes)
        source_code, line_dict, highlighted_lines, filenames = \
            self._extract_source_code(relevant_source_locations, delta)
        return source_code, line_dict, highlighted_lines, filenames

    def _normalize_dbg_infos(self, debug_information: str):
        """Normalizes the llvm debug information.
        Args:
              debug_information (str): Debug information for one node.

        Returns:
              normalized_debug_information (str): Debug information without
              curly brackets.
        """
        return debug_information.replace("{", "").replace("}", "").strip()

    def _drop_duplicate_values(self, dictionary: dict):
        """Drops duplicate values from a dictionary.

        Args:
            dictionary (dict): A dictionary.

        Returns:
            result (dict): A dictionary without duplicate values.
            drop_index (List[int]): A list of indices of the values
            that where removed.
        """
        result = {}
        drop_index = []
        for index, key in enumerate(dictionary):
            if dictionary[key] not in result.values():
                result[key] = dictionary[key]
            else:
                drop_index.append(index)
        return result, drop_index

    def _reindex_dictionary(self, dictionary: dict):
        """Re-indexes a dictionary, so that the keys are ascending without gaps.

        Args:
            dictionary (dict): A dictionary.

        Returns:
            result (dict): A re-indexed dictionary.
        """
        result = {}
        for i, key in enumerate(dictionary):
            result[str(i + 1)] = dictionary[key]
        return result

    def _drop_lines(self, source_code: str, dropped_index: List[int]):
        """Drops specified lines from an extracted part of source code.

        Args:
            source_code (str): Extracted source code, containing line breaks.
            dropped_index (List[int]): List of line numbers to remove.

        Returns:
            source_code (str): Source code without lines that should be dropped.
        """
        lines = source_code.splitlines()
        line_index = list(range(len(lines)))
        for index in dropped_index:
            line_index.remove(index)
        line_index = np.asarray(line_index)
        lines = np.asarray(lines)
        kept_lines = lines[line_index]
        return "\n".join(kept_lines)

    def _get_relevant_source_locations(self, source_location_of_nodes: [str]):
        """Get relevant source code locations from llvm debug informations.

        Args:
            source_location_of_nodes (List[str]): List of llvm debug information
            e.g.: ['{ in line: 1066 file: upnphttp.c }']

        Returns:
            all_locations (DataFrame): A DataFrame containing the relevant line number
            as well as the corresponding filename, without duplicates.
        """
        all_locations = []
        for source_location in source_location_of_nodes:
            location = src_loc_from_dbg_str(source_location)
            all_locations.append(location)

        all_locations = pd.DataFrame.from_dict(all_locations)
        all_locations.drop_duplicates(inplace=True)

        return all_locations.sort_values(by=["line"])

    def _extract_source_code(self, source_locations: DataFrame, delta: int):
        """Extracts the source code for a source location.

        Args:
            source_locations (DataFrame): A DataFrame containing the relevant line number
            as well as the corresponding filename.
            delta (int): Number of lines before and after the path to extract.

        Returns:
            clean_code (str): Source code of the path.
            line_dict_reindexed (dict): Dictionary of line numbers. Where the keys are from
            '1' to 'n' with n = number of extracted lines. The values correspond
            to the extracted lines from the source code.
            highlighted_lines (List[int]): Lines of the different nodes, extracted
            from the llvm debug information.
            filenames (List[str): List of filenames the path traverses over.
        """
        # source_locations DataFrame: [[line_number, filename], ]
        line_dict = {}
        offset = 0

        all_source_code = ""
        for _, source_location in source_locations.iterrows():
            this_line = source_location["line"]
            this_file = source_location["file"]

            this_source_location = f"in line: {this_line} file: {this_file}"
            this_source_code = retrieve_source_location(
                this_source_location,
                self.project.project_root / self.project.code_path,
                delta=delta
            )

            number_of_lines = len(this_source_code.splitlines())
            number_offsets = list(range(max(this_line - delta, 1) \
                                        - this_line, delta + 1 + 1))

            # Add filename of extracted source code at top of code
            all_source_code += f"/* Extracted from: {this_file} */\n"
            all_source_code += this_source_code

            line_dict.update({
                str(offset + 1): max(this_line + number_offsets[0] - 1, 1)
            })

            offset += 1

            # create line_dict
            for n in range(number_of_lines):
                temp_dict = {str(n + 1 + offset): \
                                 this_line + number_offsets[n]}

                line_dict.update(temp_dict)

            offset += number_of_lines

        line_dict_dropped, dropped_index = self._drop_duplicate_values(line_dict)
        line_dict_reindexed = self._reindex_dictionary(line_dict_dropped)
        clean_code = self._drop_lines(all_source_code, dropped_index)
        # hacky, probably because of 'pos' in retrieve_source_location starts
        # with 0
        source_locations.at[source_locations[
                                source_locations["line"] == 0].index, "line"] = 1
        highlighted_lines = source_locations["line"].to_list()
        filenames = source_locations["file"].to_list()

        return clean_code, line_dict_reindexed, highlighted_lines, filenames

    def _merge_similar_paths(self, paths: List[dict]):
        """Merges similar paths. Paths that were extracted from the same file and have
        the same start and end node are merged.

        Args:
            paths (List[dict]): List of dictionaries, where each dictionary contains
            the actual path as well as further values about the path.

        Returns:
            merged_paths (List[dict]): Merged paths (paths from the same file and with the
            same start and end node).
        """
        paths_from_one_file = \
            [path for path in paths if np.unique(path["filenames"]).shape[0] == 1]
        paths_from_multiple_files = \
            [path for path in paths if np.unique(path["filenames"]).shape[0] != 1]
        start_end_nodes = []
        for path in paths_from_one_file:
            start_end_nodes.append(
                path["original_path"][0]["n_hash"] + "-" + path["original_path"][-1]["n_hash"]
            )

        start_end_nodes = np.asarray(start_end_nodes)
        unique_paths = np.unique(start_end_nodes)
        merged_paths = []
        merged_paths.extend(paths_from_multiple_files)
        for unique_path in unique_paths:
            idx = np.where(start_end_nodes == unique_path)
            these_paths = [paths_from_one_file[this_idx] for this_idx in idx[0]]
            merged_path = self._merge_paths(these_paths)
            merged_paths.append(merged_path)
        return merged_paths

    def _merge_stats(self, stats: List[dict]):
        """Merges statistics of a path.

        Args:
            stats (List[dict]): List of dictionaries, where each dictionary contains
            the distance to certain defect classes.

        Returns:
            mean_merged_stats (dict): A dictionary of the relative distance (value) to
            its defect class (key). If the input contained multiple distances the mean
            distance is returned.
        """
        merged_stats = pd.DataFrame.from_dict(stats)
        mean_merged_stats = merged_stats.mean()

        return mean_merged_stats.sort_values(ascending=False).to_dict()

    def _merge_paths(self, paths_to_merge: List[dict]):
        """Merges paths that were extracted from the same file and have the
         same start and end node.

        Args:
            paths (List[dict]): List of paths that were extracted from the same
            file and have the same start and end node.

        Returns:
            merged_path (dict): Merged path.
        """
        if len(paths_to_merge) == 1:
            return paths_to_merge[0]

        merged_path = {}
        hl_lines = []
        all_stats = []
        all_embedded_paths = []
        for path in paths_to_merge:
            hl_lines.extend(path["hl_lines"])
            all_stats.append(path["stats"])
            all_embedded_paths.append(path["path"])

        merged_lines = np.unique(hl_lines).tolist()
        merged_stats = self._merge_stats(all_stats)
        merged_embedded_path = self._merge_embeddings(all_embedded_paths)
        # extract source code with merged_lines and filename
        lines_with_filenames = pd.DataFrame.from_dict(
            {"line": merged_lines, "file": [path["filenames"][0]] * len(merged_lines)})
        conf = self.project.config
        delta = conf.find("distance.source_code_delta")
        source_code, line_dict, highlighted_lines, filenames = \
            self._extract_source_code(lines_with_filenames, delta)
        merged_path.update(
            {"stats": merged_stats, "code": source_code, "line_dict": line_dict,
             "hl_lines": highlighted_lines, "filenames": filenames,
             "path": merged_embedded_path})
        return merged_path

    def _save_report(self, paths: List[dict], filename: str):
        """Saves the report as json in the project root directory.

        Args:
            paths (List[dict]): Paths to be saved.
            filename (str): Filename used to save the paths.
        """
        with open(self.project.project_root / f"{filename}.json", "w") as f:
            json.dump(paths, f)

    def _merge_embeddings(self, embedded_paths: [[float]]):
        """Merges the embeddings of the paths by computing the mean across the
        embeddings.

        Args:
            embedded_paths ([[float]]): Array of embeddings.

        Returns:
            mean_embeddings (List[float]): Mean across the embeddings.
        """
        array = np.asarray(embedded_paths)
        mean_embeddings = array.mean(axis=0)
        return mean_embeddings.tolist()
