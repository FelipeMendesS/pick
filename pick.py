#!/usr/bin/env python

import curses
import inspect
import argparse
import os
from utils import printstr, pbcopy
from table_view import TableView

# TODO: Select mode
# TODO: Scroll for big tables (curses pad)

INDENT = " " * 4


ss = inspect.cleandoc

parser = argparse.ArgumentParser(prog='pick',
                                 description="""Interactively lets the user pick a cell in a table given to the
                                                standard input. The delimiter for the columns may be chosen, whereas
                                                lines are always delimited by \\n.""")

# Provided by the .sh entry file, thus not public
parser.add_argument('input', help=argparse.SUPPRESS)
parser.add_argument('output', help=argparse.SUPPRESS)

parser.add_argument('-d', '--delimiter', default=None,
                    help="Delimiter to split the columns of the table, defaults to any whitespace char.")


def draw(stdscr, offset, table):
    top_offset, left_offset = offset

    # Clear
    stdscr.clear()

    # Draw table
    table.draw(stdscr, top_offset, left_offset)
    top_offset += table.height + 1
    stdscr.move(top_offset, left_offset)

    # Draw instructions
    printstr(stdscr, "[q] abort / [arrows] move / [space] select / [c] clear selection", curses.color_pair(3))
    printstr(stdscr, "[enter] print and copy selected cells (protip: use `pbpaste | ...` to pipe forward)", curses.color_pair(3))
    printstr(stdscr)

    # Output preview
    if not table.selection:
        printstr(stdscr, "Nothing selected", curses.color_pair(3))
    else:
        printstr(stdscr, "{} cells selected".format(len(table.selection)), curses.color_pair(3))
        for content in table.selection_content:
            printstr(stdscr, INDENT + content, curses.color_pair(1))
        printstr(stdscr)

    # Refresh
    stdscr.refresh()


def main():
    args = parser.parse_args()
    with open(args.input, 'r') as f:
        lines = f.readlines()
    d = args.delimiter
    output = curses.wrapper(main_curses, lines, d)
    if output:
        pbcopy(output)
        with open(args.output, 'w') as f:
            f.write(output + os.linesep)

def process_output(table):
    if table.selection:
        cells = table.selection_content
        return os.linesep.join(cells)
    else:
        return None


# TODO: Non-uniform table (with merges and different size of columns/rows)
def main_curses(stdscr, lines, d):
    curses.curs_set(0)
    curses.init_pair(1, 251, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(3, 8, curses.COLOR_BLACK)

    offset = (1, 1)
    table = TableView(lines, d)
    draw(stdscr, offset, table)

    while True:
        c = stdscr.getch()
        if c == ord('q'):
            return
        elif c in TableView.DIRECTIONS.keys():
            di, dj = TableView.DIRECTIONS[c]
            table.move(di, dj)
        elif c == ord(' '):
            table.toggle_select()
        elif c == ord('c'):
            table.clear_selection()
        elif c == ord('\n') or c == curses.KEY_ENTER:
            print('<enter> => print and copy selected cells')
            return process_output(table)
        draw(stdscr, offset, table)


if __name__ == '__main__':
    exit(main())

raise AssertionError('Only use this script from a terminal')
