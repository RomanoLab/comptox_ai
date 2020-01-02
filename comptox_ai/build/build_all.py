#!/usr/bin/env python3

"""Main build/installer script for ComptoxAI's ontology and graph database."""

from tqdm import tqdm

import numpy as np
from textwrap import dedent
import owlready2
import pandas as pd

from blessed import (
    Terminal,
)  # blessed is a fork of blessings, which is a replacement for curses
import os, sys
import glob
from enum import Enum, unique
import configparser
from dataclasses import dataclass

import ipdb

import comptox_ai.build.databases
from comptox_ai.build import databases


CONFIG_FILE = "../../CONFIG.cfg"

OWL_RDF_FILE = "https://www.w3.org/2002/07/owl.rdf"

cnf = configparser.ConfigParser()
cnf.read(CONFIG_FILE)
DATA_PREFIX = cnf["DATA"]["prefix"]
DATA_TEMPDIR = cnf["DATA"]["tempdir"]
DATA_LOCKFILE = cnf["DATA"]["lockfile"]

ONTOLOGY_FNAME = os.path.join(DATA_PREFIX, "comptox_ai", "comptox.rdf")
ONTOLOGY_CHECKPOINT_FNAME = os.path.join(
    DATA_PREFIX, "comptox_ai", "comptox_checkpoint.rdf"
)
ONTOLOGY_CHECKPOINT_LOCKFILE_FNAME = DATA_LOCKFILE
ONTOLOGY_POPULATED_FNAME = os.path.join(DATA_PREFIX, "comptox_ai", "comptox_full.rdf")
ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"


@dataclass
class Config:
    data_prefix: str
    data_tempdir: str
    data_lockfile: str


config = Config(DATA_PREFIX, DATA_TEMPDIR, DATA_LOCKFILE)


@unique
class TermStatus(Enum):
    CLOSED = 0
    OPEN = 1


def show_lines(stdscr, lines):
    stdscr.clear()
    for i, line in enumerate(lines):
        stdscr.addstr((i + 1) * 2, 10, line)
    stdscr.refresh()


def extract_all(stdscr, dbs, ont):
    OWL = owlready2.get_ontology(OWL_RDF_FILE).load()

    dbs_parsed = []

    for db in dbs:
        db_ins = db(scr=stdscr, config=config)
        db_ins.prepopulate(OWL, ont)
        db_ins.fetch_raw_data()
        db_ins.parse(OWL, ont)

    return dbs_parsed


def transform_all(stdscr, dbs):
    pass


def load_all(stdscr):
    pass


def build_ontology(stdscr, ont):
    """Load the unpopulated ontology, then populate it with individuals from
    external data sources.
    
    Parameters
    ----------
    stdscr : curses.window
        Main Curses window for this application
    ont : owlready2.namespace.Ontology
        ComptoxAI ontology, without any individuals (yet).
    
    Returns
    -------
    owlready2.namespace.Ontology
        The ComptoxAI ontology, now populated with individuals.
    """

    # db_parse_order = [databases.Hetionet, databases.CTD, databases.EPA]
    db_parse_order = [databases.Hetionet, databases.CTD]

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

    def getchar(self, valid_chars: list = []):
        """Read a single character from stdin using `blessed`s API.

        Note that 'q' and 'Q' will ALWAYS quit the application when entered at a
        prompt, and can't be overridden.
        
        Parameters
        ----------
        valid_chars : list
            A list of characters that are valid inputs for the particular
            context.
        """

        valid_chars = [str(x) for x in valid_chars]

        with self.term.cbreak():

            # Respond to "press any key to continue"
            if valid_chars == []:
                _ = self.term.inkey()
                return None

            val = None
            while val not in (u"q", u"Q"):
                val = self.term.inkey()
                if val in valid_chars:
                    return val
            sys.exit(0)

    def clear(self):
        print(self.term.clear())

    def move_cursor(self, y, x):
        """Move cursor to the given(y,x) coordinate, using curses conventions.
        """
        print(self.term.move(y, x))

    def draw_text_page(self, text: str):
        print(text)
        _ = self.getchar()

    def draw_menu_page(self, info_text: str, menu_opts: list):
        self.clear()
        self.move_cursor(2, 2)

        print(info_text)
        [print("({0}): {1}".format(i + 1, opt)) for i, opt in enumerate(menu_opts)]

        print()
        print("(Enter 'q' or 'Q' to quit at any time)")
        print()

        usr_input = self.getchar(list(range(1, len(menu_opts))))

        return usr_input

    def draw_progress_page(self, heading: str):
        self.clear()
        self.move_cursor(2, 2)
        print(heading)

    def add_progress_step(self, step_text: str, step_num: int):
        self.move_cursor(2 + (2 * step_num), 2)
        print(step_text)

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

    For more information, see the documentation at http://comptox.ai.

    Press any key to continue."""
    scr.draw_text_page(welcome)

    # ComptoxAI's ontology (this should be more flexible in the future):
    ont = owlready2.get_ontology(ONTOLOGY_FNAME).load()

    while True:
        print()
        choice = int(
            scr.draw_menu_page(
                "Please select an action from the following options:",
                [
                    "Build ontology",
                    "Load a partially complete previous run",
                    "Print ontology statistics",
                    "Save ontology to disk",
                    "Export ontology into Neo4j graph database.",
                ],
            )
        )

        if choice == 1:
            ont = build_ontology(scr, ont)
        elif choice == 2:
            ont = load_incomplete_run(scr, ont)
        elif choice == 3:
            print_ontology_stats(scr, ont)
        elif choice == 4:
            save_ontology(scr, ont)
        elif choice == 5:
            export_ontology(scr, ont)

    # Clear screen, proceed
    scr.close_terminal()


def print_ontology_stats(scr: ScreenManager, ont: owlready2.namespace.Ontology):

    num_classes = sum(1 for _ in ont.classes())
    num_individuals = sum(1 for _ in ont.individuals())
    num_dps = sum(1 for _ in ont.data_properties())
    num_ops = sum(1 for _ in ont.object_properties())

    scr.clear()
    scr.move_cursor(2, 2)
    print("  ===ONTOLOGY STATISTICS===")
    print()

    print("  Number of classes:           {0}".format(num_classes))
    print("  Number of data properties:   {0}".format(num_dps))
    print("  Number of object properties: {0}".format(num_ops))
    print()
    print("  Number of individuals:       {0}".format(num_individuals))
    print("  Number of relations:         {0}".format("[UNIMPLEMENTED]"))
    print()
    print("  (Press any key to continue)")
    _ = scr.getchar()


def save_ontology(scr: ScreenManager, ont: owlready2.namespace.Ontology):
    save_message = """\n\n\n
    Saving the populated ComptoxAI ontology to the local filesystem as
    an OWL2 document (in RDF/XML syntax).

    Full path and filename:
    {0}

    When you are happy with the populated ontology, the next step is
    to read its contents into a Neo4j graph database. For detailed
    instructions, please refer to http://comptox.ai/docs/guide/building.html.\n\n
    """.format(
        ONTOLOGY_POPULATED_FNAME
    )

    scr.draw_text_page(save_message)

    print("   Saving to disk...")
    ont.save(ONTOLOGY_POPULATED_FNAME, format="rdfxml")


def load_incomplete_run(scr: ScreenManager, ont: owlready2.namespace.Ontology):
    # TODO: Complete this function!
    
    return ont


if __name__ == "__main__":
    main()
