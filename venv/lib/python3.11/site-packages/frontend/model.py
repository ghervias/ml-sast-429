from .util import unzip, tozip, extract_func_names
import pandas as pd

class Model():
    """Wrapper class for the model that we may need to make changes to. The
    models are HDF5 files that contain a single pandas DataFrame.
    """

    def __init__(self, model_path: str) -> None:
        """Constructor for the model wrapper.

        Args:
            model_path (str): Absolute path to the hdf model. The model itself
            must be available under the key: "/model".
        """

        self.model_path = model_path

        self.df = unzip(model_path)

    def persist(self, selections: tuple) -> None:
        """Persists selected paths in the model.

        Args:
            selections (list): A list of tuples that contain each the name of
            the model as the first element and a single path as the second
            element.
        """

        models = [int(x[0].split("-")[1]) for x in selections]
        paths = [x[1] for x in selections]
        function_names = extract_func_names(paths)
        df = pd.DataFrame.from_dict({"cwe": models, "path": paths, "proc": function_names})
        df["cwe"] = df["cwe"].astype("int")
        df["safe"] = False
        self.df = pd.concat([self.df, df], axis=0)

        tozip(self.model_path, self.df, delete=True)