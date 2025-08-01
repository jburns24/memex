import tkinter

WIDTH, HEIGH = 800, 600
HSTEP, VSTEP = 13, 18  # Horizontal and vertical spacing between characters


class Browser:
    """
    A simple browser implementation that can render text from web pages.
    Uses tkinter for the GUI component.
    """

    def __init__(self):
        """
        Initialize the browser window and canvas for rendering content.
        """
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGH,
        )
        self.canvas.pack()

    def draw(self):
        """
        Render text content on the canvas.
        Draws each character at its calculated position.
        """
        for x, y, c in self.display_text:
            self.canvas.create_text(x, y, text=c)

    def layout(self, t):
        """
        Calculate the position of each character for rendering.

        Args:
            t: String of text content to be displayed

        Returns:
            List of tuples containing (x_position, y_position, character)
            for each character in the text
        """
        display_text = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in t:
            display_text.append((cursor_x, cursor_y, c))
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
            else:
                cursor_x += HSTEP
        return display_text

    def load(self, url):
        """
        Load and render content from a given URL.

        Args:
            url: URL object with a request method that returns HTML content

        Renders the text content character by character, wrapping when reaching the window width.
        """
        body = url.request()
        t = self.lex(body)
        self.display_text = self.layout(t)
        self.draw()

    def lex(self, body):
        """
        Parse HTML content and extract only the text (removing HTML tags).

        Args:
            body: HTML content as a string

        Returns:
            String containing only the text content (no HTML tags)
        """
        text = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                text += c
        return text
