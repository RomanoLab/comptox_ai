#!/usr/bin/env python3

"""Main build/installer script for ComptoxAI's ontology and graph database."""

from tqdm import tqdm

import numpy as np
from textwrap import dedent
from owlready2 import get_ontology
import pandas as pd

import curses
from curses import wrapper
import os, sys
import glob


import databases

ONTOLOGY_FNAME = "../../../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../../../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"

INT_UNICODE_OFFSET = int(ord("0"))


def show_lines(stdscr, lines):
    stdscr.clear()
    for i, line in enumerate(lines):
        stdscr.addstr((i + 1) * 2, 10, line)
    stdscr.refresh()


def extract_all(stdscr, dbs, ont):
    OWL = get_ontology("http://www.w3.org/2002/07/owl#")

    dbs_parsed = []

    for db in dbs:
        db_ins = db()
        db_ins.prepopulate()
        db_ins.fetch_raw_data()
        db_ins.parse(OWL, ont)

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
    stdscr : curses.window
        Main Curses window for this application
    
    Returns
    -------
    owlready2.namespace.Ontology
        The ComptoxAI ontology, now populated with individuals.
    """
    # ComptoxAI's ontology (this should be more flexible in the future):
    ont = get_ontology(ONTOLOGY_FNAME).load()

    db_parse_order = [databases.Hetionet, databases.CTD, databases.EPA]

    dbs = extract_all(stdscr, db_parse_order, ont)

    transform_all(stdscr, dbs)

    return ont


def export_ontology(stdscr):
    pass


class ScreenManager(object):
    """Manager for a curses window that acts as a user interface for the build
    application.

    This is designed to be easily generalized to other applications, but should
    probably be refactored to be even more generalizable at some point.
    """
    def __init__(self, scr: curses.window):
        self.scr = scr

    def clear_screen(self):
        self.scr.clear()
        self.scr.refresh()

    def draw_text_page(self, text):
        self.clear_screen()

        self.scr.addstr(text)
        self.scr.getkey()

    def draw_menu_page(self, info_text, menu_options):
        self.clear_screen()
        
        self.scr.addstr(10, 10, info_text)
        for i, mo in enumerate(menu_options):
            self.scr.addstr(10+((i+1)*2), 10, mo)

        valid_entry = False
        while not valid_entry:
            c = self.scr.getch()
            try:
                int_c = c - INT_UNICODE_OFFSET
            except ValueError:
                continue  # User gave non-integer input

            print(int_c)

            if 0 < int_c <= len(menu_options):
                valid_entry = True

        self.clear_screen()

        return int_c

    def draw_progress_page(self):
        pass

    def close_application(self):
        self.scr.clear()
        self.scr.addstr(10, 10, "Terminating program - press any key to continue.")
        self.scr.refresh()
        self.scr.getkey()


def main(stdscr):
    scr = ScreenManager(stdscr)

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
    scr.draw_text_page(welcome)

    # Enter program itself; add modules; export; etc...
    choice = scr.draw_menu_page(
        "Please select an action from the following options:",
        [
            "(1) Build ontology.",
            "(2) Export ontology into Neo4j graph database."
        ]
    )
    if choice == 1:
        build_ontology(scr)
    elif choice == 2:
        export_ontology(scr)

    # EXTRACT

    # TRANSFORM

    # LOAD

    # Print summary

    # Clean up

    # Clear screen, proceed
    scr.close_application()


wrapper(main)
