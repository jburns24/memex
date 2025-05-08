WIDTH, HEIGH = 800, 600
import tkinter

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGH,
        )
        self.canvas.pack()

    def load(self, url):
        body = url.request()
        t = self.lex(body)

        HSTEP, VSTEP = 13, 18
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in t:
            self.canvas.create_text(cursor_x, cursor_y, text=c)
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
            else:
                cursor_x += HSTEP


    def lex(self, body):
        text = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif in_tag == False:
                text += c
        return text
