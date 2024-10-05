import sys
import customtkinter as ctk

# The default scrolling speed is so slow that it's almost unusable.
# there is no way to customize the scrolling speed in ctkinter, so we have to create our own class.
class FastScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Bind mouse wheel event to custom scrolling method
        # Bind mouse enter and leave events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_leave(self, event):
        self.unbind_all("<MouseWheel>")
    
    def on_mouse_wheel(self, event):
        if sys.platform.startswith("win"):
            if self._shift_pressed:
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview("scroll", -int(event.delta), "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -int(event.delta), "units")
        elif sys.platform == "darwin":
            if self._shift_pressed:
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview("scroll", -event.delta, "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -event.delta, "units")
        else:
            if self._shift_pressed:
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview("scroll", -event.delta, "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -event.delta, "units")