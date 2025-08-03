import tkinter
import tkinter.font

WIDTH, HEIGH = 800, 600  # Window dimensions in pixels
HSTEP, VSTEP = 13, 18  # Horizontal and vertical spacing between characters
SCROLL_STEP = 100  # Number of pixels to scroll with each down key press
HEADERS = [
    "User-Agent: Memex/1.0",
    "Accept: text/html",
    "Accept-Language: en-US,en;q=0.9",
]


class Browser:
    """
    A simple browser implementation that can render text from web pages.
    Uses tkinter for the GUI component.
    """

    def __init__(self):
        """
        Initialize the browser window and canvas for rendering content.

        Sets up:
        - Vertical scroll position
        - Main application window
        - Key bindings for scrolling
        - Canvas for rendering text
        """
        self.scroll = 0  # Tracks vertical scroll position in pixels
        self.window = tkinter.Tk()  # Create the main application window
        self.window.bind("<Down>", self.scrolldown)  # Bind down arrow key to scroll
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGH,
        )
        self.canvas.pack()  # Add canvas to the window

    def scrolldown(self, e):
        """
        Handle down arrow key press to scroll content downward.

        Args:
            e: Event object (not used but required by tkinter bind)
        """
        self.scroll += SCROLL_STEP
        self.draw()  # Redraw content with updated scroll position

    def draw(self):
        """
        Render text content on the canvas.
        Draws each character at its calculated position.

        Implements a basic viewport culling - only drawing characters
        that are currently visible within the scroll viewport.
        """
        self.canvas.delete("all")  # Clear the canvas before redrawing
        for x, y, c in self.display_text:
            # Skip characters below the visible area
            if y > self.scroll + HEIGH:
                continue
            # Skip characters above the visible area
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c, anchor="nw")

    def layout(self, text):
        """
        Calculate the position of each character for rendering.
        Implements simple text layout with basic line wrapping.

        Args:
            text: String of text content to be displayed

        Returns:
            List of tuples containing (x_position, y_position, character)
            for each character in the text
        """
        display_text = []
        font = tkinter.font.Font()
        cursor_x, cursor_y = HSTEP, VSTEP  # Start position for text layout
        for word in text.split():
            w = font.measure(word)
            if cursor_x + w > WIDTH - HSTEP:
                # Calling .metrics() with "linespace" gives me back just that one metric
                cursor_y += font.metrics("linespace") * 1.25  # Move down a line
                cursor_x = HSTEP  # Reset to the left margin
            else:
                cursor_x += HSTEP
                display_text.append((cursor_x, cursor_y, word))
                cursor_x += w + font.measure(" ")  # Move to the next character position
        return display_text

    def load(self, url):
        """
        Load and render content from a given URL.

        Args:
            url: URL object with a request method that returns HTML content

        Process:
        1. Fetch content from URL
        2. Parse HTML to extract text
        3. Calculate text layout positions
        4. Draw the content
        """
        body = url.request(HEADERS)  # Get HTML content from the URL
        t = self.lex(body)  # Parse HTML and extract text
        self.display_text = self.layout(t)  # Calculate layout positions
        self.draw()  # Render the content to the canvas

    def lex(self, body):
        """
        Parse HTML content and extract only the text (removing HTML tags).
        This is a very simple HTML parser that strips tags but doesn't handle entities or other HTML features.

        Args:
            body: HTML content as a string

        Returns:
            String containing only the text content (no HTML tags)
        """
        text = ""
        in_tag = False  # Flag to track if we're currently inside an HTML tag
        for c in body:
            if c == "<":
                in_tag = True  # Start of a tag
            elif c == ">":
                in_tag = False  # End of a tag
            elif not in_tag:
                text += c  # If not in a tag, add character to text
        return text
