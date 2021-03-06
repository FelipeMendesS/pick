import curses
import os


class TableView(object):

    DIRECTIONS = {
        curses.KEY_UP: (-1, 0),
        curses.KEY_RIGHT: (0, 1),
        curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1),
    }

    # string[][] table
    # int[] column_widths
    # (int, int)[] selection
    # (int, int) position

    def __init__(self, lines, d):
        self.table = [line.rstrip(os.linesep).split(d) for line in lines]
        self._column_widths = self._get_column_widths(self.table)
        self._column_offsets = self._get_column_offsets(self._column_widths)
        self.selection = []
        self.position = (0, 0)

    def draw(self, stdscr, table_pad, top_offset, left_offset):
        """ Draws the table into screen stdscr with top left corner being (i, j).

        :param stdscr: Standard screen that just contains some information
        :param table_pad: pad to draw table into
        :param top_offset: Top offset
        :param left_offset: Left offset
        """
        mi, mj = stdscr.getmaxyx()
        for i, row in enumerate(self.table):
            for j, content in enumerate(row):
                cell = (i, j)

                width = self._column_widths[j]
                content = content.ljust(width)

                flags = 0
                if cell == self.position:
                    flags |= curses.color_pair(2)
                elif cell in self.selection:
                    flags |= curses.A_REVERSE
                else:
                    flags |= curses.color_pair(1)

                j = self._column_offsets[j]
                # +1 to leave the top table within one row of the top
                table_pad.addstr(i, j, content, flags)

        i, j = self.position
        if i > top_offset + mi / 2 - 1:
            top_offset += 1
        elif i < top_offset:
            top_offset -= 1
        if (self._column_offsets[j + 1] >
                mj + self._column_offsets[left_offset]):
            left_offset += 1
        elif j < left_offset:
            left_offset -= 1
        return top_offset, left_offset

    def move(self, di, dj):
        i, j = self.position
        i = self._limit(i + di, 0, len(self.table) - 1)
        j = self._limit(j + dj, 0, len(self.table[i]) - 1)
        self.position = (i, j)

    def toggle_select(self):
        if self.position in self.selection:
            self.selection.remove(self.position)
        else:
            self.selection.append(self.position)

    def clear_selection(self):
        del self.selection[:]

    def select_column(self):
        _, j = self.position
        for i, row in enumerate(self.table):
            if j >= len(row):
                continue
            c = (i, j)
            if c in self.selection:
                self.selection.remove(c)
            self.selection.append(c)

    def get(self, cell):
        i, j = cell
        return self.table[i][j]

    def get_column_offset(self, left_offset):
        return self._column_offsets[left_offset]

    @property
    def selection_content(self):
        return [self.get(c) for c in self.selection]

    @property
    def height(self):
        return len(self.table)

    @property
    def width(self):
        return sum(self._column_widths)

    @property
    def column_number(self):
        return len(self.table)

    @staticmethod
    def _limit(x, a, b):
        return max(a, min(b, x))

    @staticmethod
    def _get_column_widths(table):
        widths = []
        for row in table:
            for j, cell in enumerate(row):
                w = len(cell)
                if j < len(widths):
                    widths[j] = max(widths[j], w)
                else:
                    assert j == len(widths)
                    widths.append(w)
        return [w + 2 for w in widths]

    @staticmethod
    def _get_column_offsets(widths):
        n = len(widths)
        offsets = [0] * (n + 1)
        for i in xrange(1, n + 1):
            offsets[i] = offsets[i - 1] + widths[i - 1]
        return offsets
