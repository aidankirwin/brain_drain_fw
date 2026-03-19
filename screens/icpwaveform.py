import tkinter as tk
from layout import LayoutDesigns
from dataCollect import DataBuffer

class ICPWaveform(LayoutDesigns):

    def __init__(self, parent, controller, data_buffer : DataBuffer):
        super().__init__(parent, controller)
        self.controller = controller
        self.data_buffer = data_buffer

        # Save old ICP values for redrawing logic
        self.old_icp_min = None
        self.old_icp_max = None

        # State tracking
        self.active_widget = None
        self.is_draining = True

        self.target_icp_value = None
        
        self.colour_header(title="ICP-Based Drainage", card_bg="#38B380")
        self.setup_ui()
        self.create_numpad()

    # Make waveform scale with ICP values (5-25 mmHg mapped to canvas height)
    def draw_y_axis_scale(self, scaled_min, scaled_max):

        if self.old_icp_max is None or scaled_max > self.old_icp_max + 2 or scaled_min < self.old_icp_min - 2:
            self.y_axis_canvas.delete("y_axis")  # remove old scale

            # Define scale values across the visible range
            icp_range = scaled_max - scaled_min
            scale_values = [
                scaled_min,
                scaled_min + icp_range * 0.25,
                scaled_min + icp_range * 0.5,
                scaled_min + icp_range * 0.75,
                scaled_max
            ]

            for val in scale_values:
                # Convert ICP value to Y coordinate using the same formula as the waveform
                normalized = (val - scaled_min) / (scaled_max - scaled_min)
                y = self.waveform_height - int(normalized * (self.waveform_height - 1))

                # Draw tick mark at the right edge (flush against the waveform canvas)
                self.y_axis_canvas.create_line(80, y, 90, y, fill="black", tags="y_axis")

                # Draw label to the left of the tick mark
                self.y_axis_canvas.create_text(
                    76, y,
                    text=f"{val:.1f}",
                    anchor="e",
                    font=("Helvetica", 12),
                    fill="black",
                    tags="y_axis"
                )

            # Draw the vertical axis line along the right edge of the y_axis canvas
            self.y_axis_canvas.create_line(90, -10, 90, self.waveform_height, fill="black", width=2, tags="y_axis")
        
        else:
            return  # No need to redraw if ICP range hasn't changed
        
        self.old_icp_min = scaled_min
        self.old_icp_max = scaled_max

    def toggle_drainage(self, event=None):
        if self.is_draining:
            self.set_btn.config(text="Start Drainage", bg="#d7f0e6", fg="#38B380")
            self.is_draining = False
            self.controller.fetch_drainage_state(self.is_draining)
        else:
            self.set_btn.config(text="Stop Drainage", bg="black", fg="white")
            self.is_draining = True
            self.controller.fetch_drainage_state(self.is_draining)

    def create_numpad(self):
        # The Frame
        self.numpad_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="raised")
        
        # Helper Entry (Hidden) to manage string manipulation
        self.hidden_entry = tk.Entry(self)

        # Logic
        def numpad_click(label):
            if not self.active_widget: return
            
            if label == '⌫':
                current = self.hidden_entry.get()
                self.hidden_entry.delete(0, tk.END)
                self.hidden_entry.insert(0, current[:-1])
            elif label == 'Clear':
                self.hidden_entry.delete(0, tk.END)
            elif label == 'Done':
                if self.target_icp_value is not None:
                    self.controller.update_target_icp(self.target_icp_value)
                self.numpad_frame.place_forget()
                return
            else:
                self.hidden_entry.insert(tk.END, label)
            
            # Update the big display
            self.update_display_text()

        # UI for Numpad
        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Clear', '0', '⌫', 'Done']
        for i, label in enumerate(buttons):
            r, c = i // 3, i % 3
            colspan = 3 if label == 'Done' else 1
            b = tk.Button(self.numpad_frame, text=label, font=("Helvetica", 18, "bold"),
                          command=lambda l=label: numpad_click(l))
            b.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=2, pady=2)

        for i in range(3): self.numpad_frame.columnconfigure(i, weight=1)
        for i in range(5): self.numpad_frame.rowconfigure(i, weight=1)

    def show_numpad(self, event, widget):
        self.active_widget = widget
        
        ranges = widget.tag_ranges("val")
        if ranges:
            current_val = widget.get(ranges[0], ranges[1]).strip()
        else:
            current_val = "" # Start fresh if the tag was deleted
            
        self.hidden_entry.delete(0, tk.END)
        self.hidden_entry.insert(0, current_val)
        
        self.numpad_frame.place(relx=0.5, rely=1.0, relwidth=1.0, height=350, anchor="s")
        self.numpad_frame.lift()
        return "break"

    def update_display_text(self):
        # Get the current value from the hidden entry
        val = self.hidden_entry.get()

        # Grab ICP value
        try:
            self.target_icp_value = int(val) if val else None
        except ValueError:
            self.target_icp_value = None

        widget = self.active_widget
        widget.configure(state="normal")
        
        # 1. Try to find the existing "val" tag
        ranges = widget.tag_ranges("val")
        
        if ranges:
            # Tag exists: delete the old and insert the new
            start, end = ranges[0], ranges[1]
            widget.delete(start, end)
            widget.insert(start, val, ("big_font", "val"))
        else:
            # Tag is GONE (deleted all numbers): 
            content = widget.get("1.0", tk.END)
            if "mmHg" in content:
                # Find the index of "mmHg"
                idx = widget.search("mmHg", "1.0")
                # Insert the new number and RE-APPLY the "val" tag
                widget.insert(idx, val, ("big_font", "val"))
            else:
                # Absolute fallback: just put it at the end
                widget.insert(tk.END, val, ("big_font", "val"))
        
        widget.configure(state="disabled")
    
    def update_current_volume(self):
        self.waveform.after(30, self.update_waveform)

    def dismiss_numpad(self, event=None):
    # Only hide if the click wasn't inside the numpad itself
    # We check if the widget clicked is a child of the numpad_frame
        if hasattr(self, 'numpad_frame'):
            self.numpad_frame.place_forget()

    def setup_ui(self):
        self.configure(bg="#d7f0e6")

        outer_frame = tk.Frame(self, highlightbackground="#38B380", highlightthickness=3, bg="white")
        outer_frame.pack(padx=20, pady=20, fill="both", expand=True)

        grid_container = tk.Frame(outer_frame, bg="black")
        grid_container.pack(pady=(40, 10), padx=20, fill="x")

        # --- CURRENT ICP ---
        self.current_icp = tk.Text(grid_container, bg="white", fg="#4FA542", height=8, width=15, 
                                   borderwidth=0, padx=10, pady=10, highlightthickness=0)
        self.current_icp.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(1,1), pady=(1,1))
        
        self.current_icp.tag_configure('big_font', font=('Helvetica', 70), justify='center')
        self.current_icp.tag_configure('normal_font', font=('Helvetica', 20), justify='center')
        self.current_icp.tag_configure('small_font', font=('Helvetica', 16), justify='right')
        
        self.current_icp.insert(tk.END, "\n", "small_font")
        self.current_icp.insert(tk.END, "Current ICP:\n", "normal_font")
        self.current_icp.insert(tk.END, "10", "big_font")
        self.current_icp.insert(tk.END, "mmHg\n", "small_font")
        
        self.current_icp.configure(state='disabled')

        # --- TARGET ICP ---
        self.target_icp = tk.Text(grid_container, bg="white", fg="black", height=8, width=20, 
                                  borderwidth=0, padx=10, pady=5, highlightthickness=0)
        self.target_icp.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0,1), pady=(1,0))
        
        self.target_icp.tag_configure('big_font', font=('Helvetica', 70), justify='center')
        self.target_icp.tag_configure('normal_font', font=('Helvetica', 20), justify='center')
        self.target_icp.tag_configure('small_font', font=('Helvetica', 16), justify='right')
        
        self.target_icp.tag_configure("val", font=('Helvetica', 70))
        # This setting helps the tag 'grab' new characters typed at its edges
        self.target_icp.tag_raise("val")

        self.target_icp.insert(tk.END, "\n", "small_font")
    
        self.target_icp.insert(tk.END, "Target ICP: \n", "normal_font") 
        self.target_icp.insert(tk.END, "12", ("big_font", "val")) 
        self.target_icp.insert(tk.END, " mmHg", "normal_font")

        self.target_icp.bind("<Button-1>", lambda e: self.show_numpad(e, self.target_icp))

        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)
        for i in range(3): grid_container.rowconfigure(i, weight=1)

        # --- VOLUME BOXES (Static) ---
        self.vdbag = tk.Text(grid_container, bg="white", fg="black", height=8, borderwidth=0, highlightthickness=0, padx=10, pady=5)
        self.vdbag.grid(row=2, column=0, sticky="nsew", padx=(1,0), pady=(0,1))
        self.vdbag.tag_configure('normal_font', font=('Helvetica', 20), justify='right')
        self.vdbag.insert(tk.END, "\nVolume in \nDrainage Bag:\n", "normal_font")
        self.vdbag.configure(state="disabled")

        self.vdbagnum = tk.Text(grid_container, bg="white", fg="black", height=2, borderwidth=0, highlightthickness=0, padx=10, pady=5)
        self.vdbagnum.grid(row=2, column=1, sticky="nsew", padx=(0,1), pady=(1,1))
        self.vdbagnum.tag_configure('big_font', font=('Helvetica', 70), justify='left')
        self.vdbagnum.tag_configure('normal_font', font=('Helvetica', 20), justify='left')

        self.vdbagnum.insert(tk.END, "\n", "small_font")
        
        self.vdbagnum.insert(tk.END, "150", "big_font")
        self.vdbagnum.insert(tk.END, "ml", "normal_font")
        self.vdbagnum.configure(state="disabled")

        # --- WAVEFORM ---
        grid_container_2 = tk.Frame(outer_frame, bg="black")
        grid_container_2.pack(pady=(20, 10), padx=40, fill="x")

        # Y-axis scale canvas sits to the left of the waveform
        self.y_axis_canvas = tk.Canvas(
            grid_container_2,
            bg="white",
            width=90,
            height=350
        )
        self.y_axis_canvas.pack(side="left", padx=(1, 0), pady=1)

        self.waveform = tk.Canvas(
            grid_container_2,
            bg="white",
            height=350
        )
        self.waveform.pack(side="left", fill="both", expand=True, padx=(0, 1), pady=1)

        # For waveform drawing
        self.waveform_width = 800
        self.waveform_height = 300
        self.waveform_buffer = [20] * self.waveform_width  # Start with midline

        # --- BOTTOM BUTTONS ---
        self.set_btn = tk.Label(self, text="Stop Drainage", font=("Helvetica", 20), bg="black", 
                               fg="white", width=15, height=2, relief="raised")
        self.set_btn.place(relx=0.82, rely=0.92, anchor="center")
        self.set_btn.bind("<Button-1>", self.toggle_drainage)

        '''
        mode_btn = tk.Label(self, text="Switch Mode", font=("Helvetica", 20), bg="#F3EAF9", 
                            fg="#8e44ad", width=15, height=2, highlightthickness=1, highlightbackground="#8e44ad")
        mode_btn.place(relx=0.2, rely=0.92, anchor="center")
        mode_btn.bind("<Button-1>", lambda e: self.controller.show("VolumeWaveform"))
        '''
        
        # Bind to the main screen background
        self.bind("<Button-1>", self.dismiss_numpad)

        # Bind to the outer white frame
        outer_frame.bind("<Button-1>", self.dismiss_numpad)

        # Bind to the waveform section (so clicking the graph area also closes it)
        self.waveform.bind("<Button-1>", self.dismiss_numpad)

        # Bind to the Volume section
        self.vdbag.bind("<Button-1>", self.dismiss_numpad)
        self.vdbagnum.bind("<Button-1>", self.dismiss_numpad)

        # Start waveform update loop
        self.update_waveform()

    def update_waveform(self):
        
        # Try to get a batch of N new points
        display_batch_icp = self.data_buffer.fetch_buffer('icp', 'display')
        display_batch_vd = self.data_buffer.fetch_buffer('load1', 'display')
        
        # If not enough new data yet, skip drawing
        if display_batch_icp is None:
            self.waveform.after(30, self.update_waveform)
            return
        
        # update the "current ICP" text
        self.current_icp.configure(state=tk.NORMAL)
        self.current_icp.delete("1.0", tk.END)
        self.current_icp.insert(tk.END, "\n", "small_font")
        self.current_icp.insert(tk.END, "Current ICP:\n", "normal_font")
        self.current_icp.insert(tk.END, f"{sum(display_batch_icp) / len(display_batch_icp) :.1f}", "big_font")
        self.current_icp.insert(tk.END, "mmHg\n", "small_font")
        self.current_icp.config(state=tk.DISABLED)

        # update the "current volume" text
        self.vdbag.configure(state="enabled")
        self.vdbagnum.configure(state="enabled")
        self.vdbag.delete("1.0", tk.END)
        self.vdbagnum.delete("1.0", tk.END)
        self.vdbag.insert(tk.END, "\nVolume in \nDrainage Bag:\n", "normal_font")
        self.vdbagnum.insert(tk.END, "\n", "small_font")
        self.vdbagnum.insert(tk.END, f"{sum(display_batch_vd) / len(display_batch_vd) :.1f}", "big_font")
        self.vdbagnum.insert(tk.END, "ml", "normal_font")
        self.vdbagnum.configure(state="disabled")
        self.vdbag.configure(state="disabled")
        
        # Append new points into the sliding waveform window
        for icp_val in display_batch_icp:
            self.waveform_buffer.pop(0)
            self.waveform_buffer.append(icp_val)

        # Compute min/max from the full buffer so scaling is stable
        icp_min = min(self.waveform_buffer)
        icp_max = max(self.waveform_buffer) + 1  # +1 to avoid division by zero if all values are the same

        scaled_min = icp_min
        scaled_max = icp_max

        # Redraw scale in case ICP range has changed
        self.draw_y_axis_scale(scaled_min, scaled_max)

        # Convert waveform_buffer → canvas coordinates
        points = []
        for x, icp_val in enumerate(self.waveform_buffer):
            normalized = (icp_val - scaled_min) / (scaled_max - scaled_min)
            y = self.waveform_height - int(normalized * (self.waveform_height - 1))
            points.extend([x, y])

        # Redraw
        self.waveform.delete('wave')
        self.waveform.delete('target_line')
        if len(points) >= 4:
            self.waveform.create_line(points, fill='#38B380', width=2, tags='wave')

        # Draw target ICP horizontal line
        target = self.controller.target_icp
        if scaled_min < target < scaled_max:
            normalized_target = (target - scaled_min) / (scaled_max - scaled_min)
            y_target = self.waveform_height - int(normalized_target * (self.waveform_height - 1))
            self.waveform.create_line(0, y_target, self.waveform_width, y_target,
                                      fill='red', width=1, dash=(4, 4), tags='target_line')

        # Schedule next frame
        self.waveform.after(30, self.update_waveform)