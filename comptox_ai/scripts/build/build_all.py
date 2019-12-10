#!/usr/bin/env python3

"""Main build/installer script for ComptoxAI's ontology and graph database."""

from tqdm import tqdm

import numpy as np
from textwrap import dedent
from owlready2 import get_ontology
import pandas as pd

from curses import wrapper
from functools import wraps
import os, sys
import glob


import databases

ONTOLOGY_FNAME = "../../../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../../../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"



def show_lines(stdscr, lines):
    stdscr.clear()
    for i, line in enumerate(lines):
        stdscr.addstr((i+1) * 2, 10, line)
    stdscr.refresh()

# def track_step(stdscr):
#     def inner_function(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             stdscr.addstr(20,20, "Testing!")
#             func(*args, **kwargs)
#         return wrapper
#     return inner_function


def extract_all(stdscr, dbs):
    OWL = get_ontology("http://www.w3.org/2002/07/owl#")

    dbs_parsed = []

    for db in dbs:
        db_ins = db()
        db_ins.prepopulate()
        db_ins.fetch_raw_data()
        db_ins.parse(OWL)

    return dbs_parsed
        

def transform_all(stdscr, dbs):
    pass

def load_all(stdscr):
    pass

def build_ontology(stdscr):
    """Load the unpopulated ontology, then populate it with individuals from
    external data sources.
    
    Parameters
    ----------
    stdscr : _curses.window
        Main Curses window for this application
    
    Returns
    -------
    owlready2.namespace.Ontology
        The ComptoxAI ontology, now populated with individuals.
    """
    # ComptoxAI's ontology (this should be more flexible in the future):
    ont = get_ontology(ONTOLOGY_FNAME).load()

    db_parse_order = [
        databases.Hetionet,
        databases.CTD,
        databases.EPA
    ]

    dbs = extract_all(stdscr, db_parse_order)

    transform_all(stdscr, dbs)

    return ont


def export_ontology(stdscr):
    pass


def main(stdscr):
    stdscr.clear()

    ##############################
    # Program logic goes here:

    # Print welcome message
    welcome = """\n\n\n
    === COMPTOXAI BUILD UTILITY ===

    Copyright (c) 2019 Joseph D. Romano

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    Press any key to continue."""
    stdscr.addstr(welcome)
    stdscr.getkey()

    # Enter program itself; add modules; export; etc...
    stdscr.clear()
    stdscr.addstr(10, 10, "Please select an option from the following:")
    stdscr.addstr(12, 10, "(1) Build ontology.")
    stdscr.addstr(14, 10, "(2) Export ontology into Neo4j graph database.")

    valid_entry = False
    while not valid_entry:
        c = stdscr.getch()
        if c == ord("1"):
            valid_entry = True
            build_ontology(stdscr)
        elif c == ord("2"):
            valid_entry = True
            export_ontology(stdscr)

    # EXTRACT

    # TRANSFORM

    # LOAD

    # Print summary

    # Clean up

    # Clear screen, proceed
    stdscr.clear()
    stdscr.addstr(10, 10, "Terminating program - press any key to continue.")
    stdscr.refresh()

    ##############################

    stdscr.getkey()


wrapper(main)
