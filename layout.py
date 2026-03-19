import tkinter as tk
# from PIL import Image, ImageTk
from tkinter.font import Font

# Top Panel (status info)
class LayoutDesigns(tk.Frame):
    def __init__(self, parent, controller):

        super().__init__(parent, bg="white")
        self.controller = controller
        self.images = {}  # keep references to images to avoid garbage collection

    def irrigate_activate(self, event=None):
        self.controller.irrigate()

    def header(self, title="Monitor"):   
        status_frame = tk.Frame(self, height=120, bg="white")
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        # create the frame to display sensor info
        connection_frame=tk.Frame(status_frame, bg="white")
        connection_frame.pack(anchor="w", padx=(20,0), pady=(10, 0))
        
        # import the icon
        # connection_image = Image.open("Icons/loading-arrows.png")
        # connection_image = connection_image.resize((35, 35), Image.LANCZOS) # resize here if necessary
        # conn_image = ImageTk.PhotoImage(connection_image)

        # connection_label = tk.Label(connection_frame, image=conn_image, bg="white")
        # connection_label.image = conn_image
        # connection_label.pack(side="left")

        # sensor connection status label
        tk.Label(
            connection_frame,
            text="Sensor Connected",
            fg="black",
            font=("Helvetica", 14),
            bg="white"
        ).pack(anchor="w", padx=2, pady=(10, 0))
        
        battery_frame = tk.Frame(status_frame, bg="white")
        battery_frame.pack(anchor="w", padx=20, pady=(10, 0))

        # battery_image = Image.open("Icons/battery-level-icon.png")
        # battery_image = battery_image.resize((35, 35), Image.LANCZOS)
        # tk_image = ImageTk.PhotoImage(battery_image)

        # battery_label = tk.Label(battery_frame, image=tk_image, bg="white")
        # battery_label.image = tk_image
        # battery_label.pack(side="left", padx=(0, 1))

        tk.Label(
            battery_frame,
            text="73%",
            fg="black",
            font=("Helvetica", 14),
            bg="white"
        ).pack(side="left")
        
        # create a horizontal divider
        divider_line1 = tk.Frame(self, height=20, bg="white")
        divider_line1.pack(fill="x")
        divider_line1.pack_propagate(False) # stop the divider from resizing
        tk.Frame(divider_line1, height=1, bg="black").pack(fill="x", pady=(15, 0)) # draw the time

        divider_line2 = tk.Frame(self, height=20, bg="white")
        divider_line2.pack(fill="x")
        divider_line2.pack_propagate(False)

        line = tk.Frame(divider_line2, height=3, bg="black")
        line.place(relx=0, rely=0.5, relwidth=1)

        monitor_label = tk.Label(divider_line2, text=title, font=("Helvetica", 14), bg="black", fg="white", padx=10)
        monitor_label.place(relx=0.5, rely=0.5, anchor="center")

    def colour_header(self, title="Drain", card_bg="purple"):   
        status_frame = tk.Frame(self, height=60, bg="white")
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)

        self.irrigate_btn = tk.Label(
        status_frame,
        text="Irrigate",
        font=("Helvetica", 20), # Slightly smaller for header
        bg="#D8E6FA",
        fg="#3D84E7",
        width=15,
        height=2,
        borderwidth=0.5,
        highlightbackground="blue",
        highlightthickness=1
    )
        # place it at the far right (relx=0.95) and middle vertically (rely=0.5)
        self.irrigate_btn.place(relx=0.95, rely=0.6, anchor="e")
        self.irrigate_btn.bind("<Button-1>", self.irrigate_activate)
        
        # create a horizontal divider
        divider_line1 = tk.Frame(self, height=40, bg="white")
        divider_line1.pack(fill="x")
        divider_line1.pack_propagate(False) # stop the divider from resizing
        tk.Frame(divider_line1, height=1, bg="black").pack(fill="x", pady=(15, 0)) # draw the time

        divider_line2 = tk.Frame(self, height=40, bg="white")
        divider_line2.pack(fill="x")
        divider_line2.pack_propagate(False)

        line = tk.Frame(divider_line2, height=3, bg=card_bg)
        line.place(relx=0, rely=0.5, relwidth=1)

        monitor_label = tk.Label(divider_line2, text=title, font=("Helvetica", 14), bg=card_bg, fg="white", padx=10)
        monitor_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def back_btn(self, controller, screen, label="Back"):

        btn = tk.Label(
            self,
            text=label,
            font=("Helvetica", 20),
            bg="white",
            fg="black",
            width=10,
            height=2,
            borderwidth=1,
            relief="solid",
            padx=4
        )
        btn.pack(pady=(350,0))
        btn.place(relx=0.15, rely=0.9, anchor="center")
        btn.bind("<Button-1>", lambda e: controller.show(screen))

    def next_btn(self, controller, screen, label="Next"):
       
        btn = tk.Label(
            self,
            text=label,
            font=("Helvetica", 20),
            bg="black",
            fg="white",
            width=10,
            height=2
        )
        btn.pack(pady=(350, 0))
        btn.place(relx=0.85, rely=0.9, anchor="center")
        btn.bind("<Button-1>", lambda e: controller.show(screen))

        