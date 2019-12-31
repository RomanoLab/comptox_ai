#!/usr/bin/env python3

"""Main build/installer script for ComptoxAI's ontology and graph database."""

from tqdm import tqdm

import numpy as np
from textwrap import dedent
from owlready2 import get_ontology
import pandas as pd

from blessed import Terminal  # blessed is a fork of blessings, which is a replacement for curses
import os, sys, platform
system = platform.system()
import glob
from enum import Enum, unique

import ipdb

import comptox_ai.build.databases
from comptox_ai.build import databases

# see: https://codereview.stackexchange.com/a/118726
# and: https://gist.github.com/jasonrdsouza/1901709
if system == "Windows":
    # Windows doesn't provide termios
    import msvcrt
    def getch():
        return msvcrt.getch()
else:
    import tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

ONTOLOGY_FNAME = "../../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"

INT_UNICODE_OFFSET = int(ord("0"))

# enums:
@unique
class TermStatus(Enum):
    CLOSED = 0
    OPEN = 1
@unique
class InputType(Enum):
    INT = 0
    CHAR = 1
    STR = 2
    FLOAT = 3


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
        self.term_status = TermStatus.OPEN
        self.term.enter_fullscreen()
        self.clear()

    @classmethod
    def validate_input(cls, user_input, valid_type: Enum = InputType.INT):
        given_type = user_input.__class__
        if valid_type == InputType.INT:
            return given_type == int
        elif valid_type == InputType.CHAR:
            return (given_type == char) and (len(user_input) == 1)
        elif valid_type == InputType.STR:
            return (given_type == char) and (len(user_input) >= 1)
        elif valid_type == InputType.FLOAT:
            return given_type == float
        else:
            raise ValueError("Error: Invalid input value.")


    def clear(self):
        print(self.term.clear())

    def move_cursor(self, y, x):
        """Move cursor to the given(y,x) coordinate, using curses conventions.
        """
        print(self.term.move(y, x))

    def draw_text_page(self, text: str):
        print(text)
        _ = getch()

    def draw_menu_page(self, info_text: str, menu_opts: list):
        self.clear()

        self.move_cursor(2,2)
        print(info_text)

        [print(opt) for opt in menu_opts]
        
        
        valid_input = False
        while not valid_input:
            usr_input = int(getch())
            valid_input = self.validate_input(usr_input, valid_type=InputType.INT)

        ipdb.set_trace()
        return usr_input

    def close_terminal(self):
        self.term.exit_fullscreen()
        self.term_status = TermStatus.CLOSED

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
