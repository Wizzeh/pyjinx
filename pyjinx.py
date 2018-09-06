import curses
import curses.ascii
from time import sleep, process_time

"""Basic class for a console application.

This class handles initialization of a display and command window
using curses. The main way to extend this class is by extending
the functionality of parse_command and tick. If the tick rate is
set to None, then the application will tick whenever a character
is entered. Otherwise, it should tick roughly at tick_rate.
"""


class ConsoleApplication:
    def __init__(self, tick_rate=1 / 30):
        self.tick_rate = tick_rate

        self.quit = False
        self.input_str = ""
        self.display = None
        self.command = None

        self.rows = 0
        self.cols = 0

    def init_screen(self):
        # Initialize windows and configure curses settings.

        stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

        LINES, COLS = stdscr.getmaxyx()
        self.display = curses.newwin(LINES - 2, COLS)
        self.command = curses.newwin(2, COLS, LINES - 2, 0)

        rows, cols = self.display.getmaxyx()
        self.rows = rows
        self.cols = cols

        curses.noecho()
        curses.cbreak()

        if self.tick_rate is not None:
            self.command.nodelay(True)
        self.command.keypad(True)

    def cleanup_screen(self):
        # Deconfigure curses settings so as not to mess up the terminal.

        self.command.keypad(False)
        if self.tick_rate is not None:
            self.command.nodelay(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def setup(self):
        self.display.border()
        self.command.addstr(" > ")

        self.display.refresh()
        self.command.refresh()

    def run(self):
        try:
            self.init_screen()

            self.setup()

            time = process_time()
            while not self.quit:
                curr_time = process_time()
                dt = curr_time - time
                time = curr_time

                self.tick(dt)

                ch = self.command.getch()

                # If no character is inputted on nodelay mode,
                # getch will return -1.
                if ch >= 0:
                    self.parse_input(ch)

                self.command.clear()
                self.command.addstr(" > " + self.input_str)
                self.command.refresh()

                if self.tick_rate is not None:
                    sleep(self.tick_rate)

        finally:
            self.cleanup_screen()

    def tick(self, dt):
        """Carry out the functionality of the program.
        
        Depending on the value of self.tick_rate, this function is either
        called roughly every self.tick_rate (if self.tick_rate is not None),
        or else at the beginning of the program and after every key input.
        The default implementation doesn't do anything; you're encouraged to
        extend or override this method.
        
        Arguments:
            dt {float} -- Time since the last tick (in seconds).
        """
        pass

    def parse_input(self, ch):
        """Accept a single-character console input.
        
        This method is called whenever a key is pressed on the command
        window. Mostly for making the console window actually work.
        
        Arguments:
            ch {number} -- Encoded identity of the character.
        """
        if curses.ascii.isprint(ch):
            self.input_str += curses.ascii.unctrl(ch)
        if ch == curses.ascii.NL:
            self.parse_command(self.input_str)
            self.input_str = ""
        if ch == curses.ascii.BS:
            self.input_str = self.input_str[:-1]

    def parse_command(self, cmd):
        """Take a full command after submission and do something with it.
        
        The default implementation of parse_command only handles quitting.
        It's a good idea to extend this function if you want to add more
        functionality to your program.
        
        Arguments:
            cmd {str} -- The full string entered by the user
        """
        if cmd == 'quit':
            self.quit = True

    def alert_message(self, msg, color=0):
        """Print a message at the bottom of the display.

        This method prints a message centered and on the bottom
        of the display, where a border is normally drawn. If you
        don't call this after drawing the border, the message will
        probably be overwritten. If you are drawing a border, it's
        often best visually to pad your message with spaces.

        Arguments:
            msg {str} -- Message to display

        Keyword Arguments:
            color {number} -- Color pair code for message (default: {0})
        """
        self.display.addstr(self.rows - 1,
                            (self.cols // 2) - (len(msg) // 2),
                            msg,
                            color)

    def top_message(self, msg, color=0):
        """Print a message at the top of the display.

        Works like alert_message, except it prints at the top.

        Arguments:
            msg {str} -- Message to display

        Keyword Arguments:
            color {number} -- Color pair code for message (default: {0})
        """
        self.display.addstr(0,
                            (self.cols // 2) - (len(msg) // 2),
                            msg,
                            color)

if __name__ == '__main__':
    app = ConsoleApplication()
    app.run()
