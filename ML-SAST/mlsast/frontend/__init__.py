""" The frontend module encapsulates all functionality related to the user interface. It processes
    the command line arguments and executes the respective software components.

    ## frontend.argparser

    This module simply contains the definitions of all command line parameters and makes them
    available through the `argparser.parse_args()` function.
"""
__all__ = ["argparser"]

from . import argparser
