import tkinter as tk
from .util.logging import logging
#Custom Textbox that grows with the text
#Yes its very inefficient, but it works
#Also adds a placeholder
class GrowingTextBox(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<<Modified>>', lambda e: self.after(50, self.on_change))  # limit updates to once every 50 ms
        self.config(height=1)
        self.lines = 1

    # Whenever the text changes, update the height of the textbox
    def on_change(self, event=None):
        if self.edit_modified():
            total_lines = self.count('1.0', 'end', 'displaylines')
            if total_lines != self.lines:
                self.lines = total_lines
                self.config(height=total_lines)
            self.edit_modified(False)
