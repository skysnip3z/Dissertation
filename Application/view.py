# -*- coding: utf-8 -*-
"""

@author: Ali
"""
import tkinter as tk # Python GUI Library

# MVC Architecture - View
class View:
    def __init__(self, ctrl):
        self.window = tk.Tk()
        self.ctrl = ctrl
        self.main_frame = self.set_frame(self.window)
        self.review_lst = [] # List of reviews from search
        # Review selection & viewing
        self.review_lbox = None 
        self.review_txt = None
        # User Input Field
        self.input_search = None    
        # Buttons
        self.btn_search = None
        self.btn_save_file = None
        self.btn_load_file = None
        # Radio Buttons
        self.rd_var = tk.IntVar()
        self.rd_btn_simple = None
        self.rd_btn_pred = None
        self.rd_btn_adapt = None
        # Labels
        self.lbl_search = None 
        self.lbl_review = None
        self.lbl_review_display = None
        self.lbl_search_result = None
        self.lbl_search_mode = None

        
    def set_grid(self, cols, rows):
        for i in range(cols):
            unif = str(i)
            unifs = str(i*3)
            self.window.columnconfigure(i, weight=1, uniform=unif, minsize=16)
            self.window.rowconfigure(i, weight=1, uniform=unifs, minsize=16)
            
        #self.window.columnconfigure([x for x in range(cols)], weight=1, uniform='x', minsize=16)
        #self.window.rowconfigure([x for x in range(rows)], weight=1, uniform='x', minsize=16)
        
    def set_frame(self, root):
        frame = tk.Frame(root)
        return frame
        
    # Review ListBox    
    def set_review_lbox(self, list_):
        self.review_lst = None
        self.review_lst = tk.StringVar(value=list_)
        lbox = tk.Listbox(self.window, listvariable=self.review_lst, relief="solid")
        lbox.config(font=("Ariel", 12))
        return lbox
    
    # Review Display
    def set_review_txt(self, text="N/A"):
        txt = tk.Text(self.window, relief="solid", wrap="word")
        txt.config(font=("Ariel", 13))
        self.update_txt_box(txt, text)
        return txt
    
    def update_txt_box(self, txt_box, text):
        txt_box.config(state="normal")
        txt_box.delete("1.0", tk.END)
        txt_box.insert(tk.END, text)
        txt_box.config(state="disabled")
        txt_box.config(padx=5)
    
    # Product search entry - user input
    def set_input_search(self):
        search = tk.Entry(self.window, relief="solid")
        search.grid(column=1, row=1, rowspan=1, columnspan=2, sticky="nsew")
        search.config(font=("Ariel", 12))
        return search
    
    # Generic Label
    def set_label_x(self, label):
        lbl = tk.Label(self.window, wraplength=800, text=label)
        lbl.config(font=("Ariel", 12))
        return lbl
    
    # Generic Button    
    def set_btn_x(self, label):
        btn = tk.Button(self.window, text=label, wraplength=200, relief="solid")
        btn.config(font=("Ariel", 12))
        return btn
    
    def set_rd_btn_x(self, label, val):
        rd_btn = tk.Radiobutton(self.window, text=label,
                                variable=self.rd_var, value=val,
                                command=self.send_search_mode)
        rd_btn.config(font=("Ariel", 12))
        return rd_btn
        
    # Window Positioning
    def set_window_pos(self):
        wHeight = self.window.winfo_height()
        wWidth = self.window.winfo_width()
        finalWidth = int((self.window.winfo_screenwidth()/3)-(wWidth/2))
        finalHeight = int((self.window.winfo_screenheight()/4)-(wHeight/2))
        
        # Place window 
        self.window.geometry("+{}+{}".format(finalWidth, finalHeight))
        self.window.resizable(False, False)

    def get_input_search(self):
        text = self.input_search.get()
        text.strip()
        return text
        
    # Event - when btn_search is pressed    
    def send_asin(self, event):
        text = self.get_input_search()
        if len(text) != 10:
            self.display_review_data(0, text)
            return 0
        data = self.ctrl.get_review_data(text)
        self.display_review_data(data, text)
    
    # Update view to reflect review if found/not found
    def display_review_data(self, data, asin):
        if isinstance(data, list):
            self.lbl_search_result["text"] = "Product Found: " + asin
            self.review_lst = data
            self.update_lst_box(self.review_lst)
        else:
            self.lbl_search_result["text"] = "Product Not Found: " + asin 
            self.review_lst = None
            self.update_lst_box(self.review_lst)
    
    # List box updates with review counts
    def update_lst_box(self, data):
        self.review_lbox.delete(0, tk.END)
        if isinstance(data, list):
            for r in range(len(data)):
                if int(data[r][0]) == 1:
                    self.review_lbox.insert(tk.END, "Review " + str(r+1) + " (Positive)")
                else:
                    self.review_lbox.insert(tk.END, "Review " + str(r+1) + " (Negative)")
        else:
            self.review_lbox.insert(tk.END, "N/A")
            self.update_txt_box(self.review_txt, "")
    
    # Shows review text based on user selection
    def show_review(self, event):
        indxs = self.review_lbox.curselection()
        if isinstance(self.review_lst, list) and len(indxs) == 1:
            indx = int(indxs[0])
            self.update_txt_box(self.review_txt, self.review_lst[indx][1])
        else:
            self.update_txt_box(self.review_txt, "")
    
    # Sends search mode preference to controller
    def send_search_mode(self):
        self.ctrl.set_search_mode(self.rd_var.get())
    
    # Sends user save event to controller and enacts response thereof
    def send_save_file(self, event):
        err_msg = "Error: No Data to Write"
        try:
            if self.ctrl.reviews != None and len(self.review_lst) > 4:
                self.ctrl.save_reviews()
                self.lbl_search_result["text"] = "Success: File Saved"
            else:
                self.lbl_search_result["text"] = err_msg
        except TypeError:
            self.lbl_search_result["text"] = err_msg
    
    # Sends user load event to controller and enacts response thereof
    def send_load_file(self, event):
        data = self.ctrl.load_reviews()
        err_msg = "Error: Incompatible File (Possibly Modified)"
        if len(data) != 0:
            try:
                self.update_lst_box(data)
                self.review_lst = data
                self.lbl_search_result["text"] = "Success: File Loaded"
            except ValueError:
                self.lbl_search_result["text"] = err_msg
        else:
            self.lbl_search_result["text"] = err_msg
    
    # Start main view loop after constructing view
    def start_view(self):
        self.window.title("Amazon Reviews' Sentiment Tool")
        list_ = ["N/A"]
        
        # Grid Formatting & UI Components (incl. Frames)
        self.set_grid(24, 24)    
        
        # Widget Instantiations
        # Review selection & viewing
        self.review_lbox = self.set_review_lbox(list_) 
        self.review_txt = self.set_review_txt() 
        # User Input
        self.input_search = self.set_input_search()
        
        # Radio Buttons
        self.rd_btn_simple = self.set_rd_btn_x("Simple (Amazon-Based)", 1)
        self.rd_btn_pred = self.set_rd_btn_x("Predictive (AI-Based)", 2)
        self.rd_btn_adapt = self.set_rd_btn_x("Adaptive (Both)", 3)
        
        # Buttons
        self.btn_search = self.set_btn_x("Search ASIN")    
        self.btn_save_file = self.set_btn_x("Save Results")    
        self.btn_load_file = self.set_btn_x("Load Results")    
        
        # Labels
        self.lbl_search = self.set_label_x("Search:") 
        self.lbl_review = self.set_label_x("Reviews List:") 
        self.lbl_review_display = self.set_label_x("Review Display:")
        self.lbl_search_result = self.set_label_x("")
        self.lbl_search_mode = self.set_label_x("Search Mode:")
        
        
        # Widget Positioning through 24x24 grids
        self.lbl_search.grid(column=1, row=0, rowspan=1, columnspan=2, sticky="w")
        self.lbl_review.grid(column=1, row=6, rowspan=1, columnspan=2, sticky="w")
        self.lbl_review_display.grid(column=4, row=6, rowspan=1, columnspan=2, sticky="w")
        self.lbl_search_result.grid(column=6, row=1, rowspan=1, sticky="nsw")
        self.lbl_search_mode.grid(column=1, row=3, columnspan=1, sticky="w")
        self.rd_btn_simple.grid(column=2, row=3, columnspan=6, sticky="w")
        self.rd_btn_pred.grid(column=2, row=4, columnspan=6, sticky="w")
        self.rd_btn_adapt.grid(column=2, row=5, columnspan=7, sticky="w")   
        self.review_txt.grid(column=4, row=7, rowspan=16, columnspan=19, sticky="nsew")
        self.review_lbox.grid(column=1, row=7, rowspan=16, columnspan=2, sticky="nsew")
        self.btn_search.grid(column=4, row=1, rowspan=1, columnspan=1, sticky="nsw")
        self.btn_save_file.grid(column=20, row=1, rowspan=1, columnspan=1, sticky="nsw")
        self.btn_load_file.grid(column=22, row=1, rowspan=1, columnspan=1, sticky="nsw")
        
        # Binding Events - Widgets
        self.btn_search.bind("<Button-1>", self.send_asin)
        self.btn_save_file.bind("<Button-1>", self.send_save_file)
        self.btn_load_file.bind("<Button-1>", self.send_load_file)
        self.review_lbox.bind("<<ListboxSelect>>", self.show_review)
        
        # Widow Positioning
        self.set_window_pos()
        
        # Tkinter Main
        self.window.mainloop()
        