from setuptools import setup, find_packages


setup(
    name = "bsi-mlsast-frontend",
    version = "1.0",
	author = "Bernhard Berger, Hendrik Rothe, Karsten Sohr, Lara Luhrmann, Lorenz Hüther, " \
        "Marcus-Sebastian Schröder, Sebastian Eken, Stefan Edelkamp",
    author_email = "n/a",
    description = ("This is the protoype of an ML-SAST tool developed as part of the BSI project " \
        "447"),
    license = "Apache 2.0",
    keywords = "ML, ML-SAST, static analyis, machine learning, security testing",
    url = "n/a",
    packages = find_packages(include=["frontend", "__main.py__"], exclude=["mlsast.tests"]),
    long_description = "See Readme",
)

