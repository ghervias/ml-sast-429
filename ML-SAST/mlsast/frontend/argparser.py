from argparse import ArgumentParser

def parse_args():
    """ Processes the arguments that are passed to the program during invocation.

    Returns:
        The parsed arguments as an object, arguments are mapped into the namespace as attributes.
        Refer to python's `argparse` documentation.
    """

    parser = ArgumentParser(description="ML-SAST Prototype for BSI Project 447")

    parser.add_argument("-p", "--project", help="Path to the project dirctory.",
                        type=str, required=True)

    return parser.parse_args()
