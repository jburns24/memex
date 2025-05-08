from url import URL
from browser import Browser
import tkinter

if __name__ == "__main__":
    import sys
    browser = Browser()
    browser.load(url=URL(sys.argv[1]))
    tkinter.mainloop()

# https://browser.engineering/http.html
