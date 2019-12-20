#!/usr/bin/env python3

"""Main build/installer script for ComptoxAI's ontology and graph database."""

from tqdm import tqdm

import numpy as np
from textwrap import dedent
from owlready2 import get_ontology
import pandas as pd

from blessed import Terminal
import os, sys
import termios, tty
import glob


import comptox_ai.build.databases
from comptox_ai.build import databases

ONTOLOGY_FNAME = "../../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"

INT_UNICODE_OFFSET = int(ord("0"))

# Values for TERM_STATUS:
CLOSED = 0
OPEN = 1


def getchar():
    """Return a single character from stdin

    see: https://gist.github.com/jasonrdsouza/1901709
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def show_lines(stdscr, lines):
    stdscr.clear()
    for i, line in enumerate(lines):
        stdscr.addstr((i + 1) * 2, 10, line)
    stdscr.refresh()


def extract_all(stdscr, dbs, ont):
    OWL = get_ontology("http://www.w3.org/2002/07/owl#")

    dbs_parsed = []

    for db in dbs:
        db_ins = db(scr=stdscr)
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
    def __init__(self):
        """Terminal instance is entirely self contained - no need to instantiate
        and pass the object in at initialization.
        """
        self.term = Terminal()
        self.term_status = OPEN
        self.term.enter_fullscreen()
        self.term.clear()

    def draw_text_page(self, text: str):
        print(text)
        _ = getchar()

    def draw_menu_page(self, info_text: str, menu_opts: list):
        self.term.clear()
        print(info_text)
        usr_input = getchar()
        return usr_input

    def close_terminal(self):
        self.term.exit_fullscreen()
        self.term_status = CLOSED

    def __del__(self):
        if self.term_status:
            self.close_terminal()


def main():
    scr = ScreenManager()

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
    
    # Print summary

    # Clean up

    # Clear screen, proceed
    scr.close_terminal()


if __name__=="__main__":
    main()
