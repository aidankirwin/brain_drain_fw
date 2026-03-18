import tkinter as tk
from app import App
from test import test

mode = 'DEMO'

if __name__ == "__main__":
    if mode == 'DEMO':
        root = tk.Tk()
        app = App(root)
        root.mainloop()
        
    elif mode == 'TEST':
        test()