import tkinter as tk
from layout import LayoutDesigns
from tkinter.font import Font

class VolumeWaveform(LayoutDesigns): 
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        self.colour_header(title="Volume-Based Drainage", card_bg="#8e44ad")
       
        self.bg_purple = "#8e44ad"
        self.faded_purple = "#F3EAF8"  # Very light lavender
        self.setup_ui()

    def setup_ui(self):

        # 1. SET THE OUTERMOST BACKGROUND
        self.faded_purple = "#F3EAF9" 
        self.configure(bg=self.faded_purple)

        # 2. CREATE THE BORDERED BOX
        outer_frame = tk.Frame(self, 
                            highlightbackground="#8e44ad", 
                            highlightthickness=3, 
                            bg="white")
        outer_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 4. THE DATA GRID
        grid_container = tk.Frame(outer_frame, bg="black") # Border lines
        grid_container.pack(pady=(40, 10), padx=20, fill="x")

        current_icp = tk.Text(
            grid_container, # Use grid_container to keep the black border lines
            bg="white",
            fg="#4FA542",
            height=5,       
            width=15,       
            borderwidth=0,
            padx=10,
            pady=10,
            highlightthickness=0
        )
        # Use rowspan=2 so it aligns with the two boxes on the right
        current_icp.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(1,1), pady=(1,1))

        current_icp.tag_configure('big_font', font=('Helvetica', 70), justify='center')
        current_icp.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        current_icp.tag_configure('small_font', font=('Helvetica', 10), justify='right')

        current_icp.insert(tk.END, "Current ICP:\n\n", "normal_font")
        current_icp.insert(tk.END, "10", "big_font")
        current_icp.insert(tk.END, "mmHg", "small_font")
        
        # Disable editing so it acts like a Label
        current_icp.configure(state="disabled")

        # Make sure these rows and columns have weight otherwise they will stay 0 pixels wide/tall
        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)
        grid_container.rowconfigure(2, weight=1)

        # Current ICP
        current_icp = tk.Text(
            grid_container, # Use grid_container to keep the black border lines
            bg="white",
            fg="#4FA542",
            height=5,       
            width=15,       
            borderwidth=0,
            padx=10,
            pady=10,
            highlightthickness=0
        )
        # Use rowspan=2 so it aligns with the two boxes on the right
        current_icp.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(1,1), pady=(1,1))

        current_icp.tag_configure('big_font', font=('Helvetica', 70), justify='center')
        current_icp.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        current_icp.tag_configure('small_font', font=('Helvetica', 10), justify='right')

        current_icp.insert(tk.END, "Current ICP:\n\n", "normal_font")
        current_icp.insert(tk.END, "10", "big_font")
        current_icp.insert(tk.END, "mmHg", "small_font")
        
        # Disable editing so it acts like a Label
        current_icp.configure(state="disabled")

        # --- RE-ENABLE THE OTHER CELLS ---
        # Make sure these rows and columns have weight 
        # otherwise they will stay 0 pixels wide/tall
        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)
        grid_container.rowconfigure(2, weight=1)

        # ICP Interval
        icp = tk.Text(
            grid_container, # Use grid_container to keep the black border lines
            bg="white",
            fg="black",
            height=5,       
            width=20,       
            borderwidth=0,
            padx=10,
            pady=5,
            highlightthickness=0
        )

        icp.grid(row=0, column=1, rowspan=1, sticky="nsew", padx=(0,1), pady=(1,0))

        icp.tag_configure('big_font', font=('Helvetica', 40), justify='center')
        icp.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        icp.tag_configure('small_font', font=('Helvetica', 10), justify='right')

        icp.insert(tk.END, "ICP Interval: \n", "normal_font")
        icp.insert(tk.END, "5-20", "big_font")
        icp.insert(tk.END, "mmHg", "normal_font")
        
        # Disable editing so it acts like a Label
        icp.configure(state="disabled")

        dflowrate = tk.Text(
            grid_container, # Use grid_container to keep the black border lines
            bg="white",
            fg="black",
            height=5,       
            width=20,       
            borderwidth=0,
            padx=10,
            pady=5,
            highlightthickness=0
        )

        dflowrate.grid(row=1, column=1, rowspan=1, sticky="nsew", padx=(0,1), pady=(1,0))

        dflowrate.tag_configure('big_font', font=('Helvetica', 40), justify='center')
        dflowrate.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        dflowrate.tag_configure('small_font', font=('Helvetica', 10), justify='right')

        dflowrate.insert(tk.END, "Drainage Flow Rate: \n", "normal_font")
        dflowrate.insert(tk.END, "12", "big_font")
        dflowrate.insert(tk.END, "mL/hr", "normal_font")
        
        # Disable editing so it acts like a Label
        dflowrate.configure(state="disabled")

        maxvol = tk.Text(
            grid_container, 
            bg="white",
            fg="black",
            height=5,
            width=20,
            borderwidth=0,
            padx=10,
            pady=5,
            highlightthickness=0
        )
        
        maxvol.grid(row=2, column=0, columnspan=1, sticky="nsew", padx=(1,1), pady=(0,1)) # Empty cell to push the two boxes up 

        maxvol.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        maxvol.tag_configure('big_font', font=('Helvetica', 40), justify='center')
        maxvol.tag_configure('small_font', font=('Helvetica', 10), justify='center')

        maxvol.insert(tk.END, "Max. Volume: \n", "normal_font")
        maxvol.insert(tk.END, "5-20", "big_font")
        maxvol.insert(tk.END, "mL", "normal_font")

        maxvol.configure(state="disabled")

        vdbag = tk.Text(
            grid_container, 
            bg="white",
            fg="black",
            height=5,
            width=20,
            borderwidth=0,
            padx=10,
            pady=5,
            highlightthickness=0
        )

        vdbag.grid(row=2, column=1, columnspan=1, sticky="nsew", padx=(0,1), pady=(1,1)) # Empty cell to push the two boxes up 

        vdbag.tag_configure('big_font', font=('Helvetica', 40), justify='center')
        vdbag.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        vdbag.tag_configure('small_font', font=('Helvetica', 10), justify='center')

        vdbag.insert(tk.END, "Volume in Drainage Bag: \n", "normal_font")
        vdbag.insert(tk.END, "150", "big_font")
        vdbag.insert(tk.END, "mL", "normal_font")
        vdbag.configure(state="disabled")
    
        back_btn = tk.Label(
            self, 
            text="Off",
            font=("Helvetica", 20),
            bg="white",
            fg="black",
            width=10,
            height=2,
            borderwidth=0,
            relief="solid",
            padx=4
        )
        back_btn.pack(pady=(350, 0))
        back_btn.place(relx=0.2, rely=0.55, anchor="center")

        back_btn = tk.Label(
            self, 
            text="Waveform",
            font=("Helvetica", 20),
            bg="#D3D3D3",
            fg="black",
            width=10,
            height=2,
            borderwidth=0,
            relief="solid",
            padx=4
        )
        back_btn.pack(pady=(350, 0))
        back_btn.place(relx=0.5, rely=0.55, anchor="center")

        set_btn = tk.Label(
            self,
            text="Irrigation",
            font=("Helvetica", 20),
            bg="white",
            fg="black",
            width=10,
            height=2,
            borderwidth=0,
            relief="solid",
            padx=4
        )
        set_btn.pack(pady=(350, 0))
        set_btn.place(relx=0.8, rely=0.55, anchor="center")

        grid_container_2 = tk.Frame(outer_frame, bg="black") # Border lines
        grid_container_2.pack(pady=(50, 10), padx=40, fill="x")

        # WAVEFORM GRAPH SECTION
        waveform = tk.Text(
            grid_container_2, # Use grid_container_2 to keep the black border lines
            bg="white",
            fg="black",
            height=16,       
            width=30,       
            borderwidth=0,
            padx=30,
            pady=20,
            highlightthickness=0
        )
        # Use rowspan=2 so it aligns with the two boxes on the right
        waveform.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="nsew", padx=(1,1), pady=(1,1))

        waveform.tag_configure('big_font', font=('Helvetica', 70), justify='center')
        waveform.tag_configure('normal_font', font=('Helvetica', 14), justify='center')
        waveform.tag_configure('small_font', font=('Helvetica', 10), justify='right')

        waveform.insert(tk.END, "Replace with waveform graph", "normal_font")
        
        grid_container_2.columnconfigure(0, weight=1)
        grid_container_2.columnconfigure(1, weight=1)
        grid_container_2.rowconfigure(0, weight=1)
        grid_container_2.rowconfigure(1, weight=1)
        grid_container_2.rowconfigure(2, weight=1)

        waveform.configure(state="disabled")

        back_btn = tk.Label(
            self, 
            text="Back",
            font=("Helvetica", 20),
            bg="white",
            fg="black",
            width=10,
            height=2,
            borderwidth=0.5,
            relief="solid",
            padx=4
        )
        back_btn.pack(pady=(350,0))
        back_btn.place(relx=0.15, rely=0.92, anchor="center")

        set_btn = tk.Label(
            self,
            text="Stop Drainage",
            font=("Helvetica", 20),
            bg="black",
            fg="white",
            width=15,
            height=2, 
            borderwidth=0.5
        )
        set_btn.pack(pady=(350, 0))
        set_btn.place(relx=0.82, rely=0.92, anchor="center")

        set_btn.bind("<Button-1>", lambda e: controller.show("HomeScreen")) 
        back_btn.bind("<Button-1>", lambda e: controller.show("VolumeBasedDrainScreen")) # on left click, go to the next page # always add this line when creating non-default button
