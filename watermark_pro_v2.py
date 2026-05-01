import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont
import os
import json
from datetime import datetime
import shutil

# ============ GLOBAL SETTINGS ============
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
# =========================================

class FastSearchCombo(ctk.CTkFrame):
    """Ultra-fast searchable combobox using simple listbox approach"""
    def __init__(self, master, values, command=None, width=300, **kwargs):
        super().__init__(master, fg_color="transparent", width=width, **kwargs)
        
        self.all_values = values
        self.filtered_values = values[:]
        self.command = command
        self.dropdown_visible = False
        self.width = width
        
        # Main container with border
        self.container = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=8, border_width=1, border_color="#404040")
        self.container.pack(fill="x")
        
        # Entry and button in same row
        self.entry = ctk.CTkEntry(
            self.container,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            border_width=0,
            placeholder_text="Type to search font..."
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Simple toggle button
        self.toggle_btn = ctk.CTkButton(
            self.container,
            text="▼",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#1E90FF",
            command=self.toggle_dropdown,
            font=ctk.CTkFont(size=10)
        )
        self.toggle_btn.pack(side="right", padx=5)
        
        # Bind events
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<Down>", lambda e: self.show_dropdown())
        self.entry.bind("<Escape>", lambda e: self.hide_dropdown())
        
        # Dropdown frame (packed below)
        self.dropdown_frame = None
        
    def on_key_release(self, event):
        if event.keysym in ('Up', 'Down', 'Return', 'Escape'):
            return
            
        search = self.entry.get().lower().strip()
        if search:
            self.filtered_values = [v for v in self.all_values if search in v.lower()]
        else:
            self.filtered_values = self.all_values[:]
            
        if not self.dropdown_visible:
            self.show_dropdown()
        else:
            self.update_dropdown_content()
    
    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.hide_dropdown()
        else:
            self.show_dropdown()
    
    def show_dropdown(self):
        if self.dropdown_visible:
            return
            
        self.dropdown_visible = True
        self.toggle_btn.configure(text="▲")
        
        # Create dropdown frame
        self.dropdown_frame = ctk.CTkFrame(
            self,
            fg_color="#2B2B2B",
            corner_radius=8,
            border_width=1,
            border_color="#1E90FF"
        )
        self.dropdown_frame.pack(fill="x", pady=(2, 0))
        
        # Create scrollable frame inside
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.dropdown_frame,
            fg_color="transparent",
            height=200,
            scrollbar_button_color="#1E90FF",
            scrollbar_button_hover_color="#3578E6"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Bind scroll events to scrollable frame
        self.scroll_frame._parent_canvas.bind("<MouseWheel>", self.on_scroll)
        self.scroll_frame._parent_canvas.bind("<Button-4>", self.on_scroll)
        self.scroll_frame._parent_canvas.bind("<Button-5>", self.on_scroll)
        
        # Update content
        self.update_dropdown_content()
        
    def hide_dropdown(self):
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
            self.scroll_frame = None
        self.dropdown_visible = False
        self.toggle_btn.configure(text="▼")
    
    def update_dropdown_content(self):
        if not self.scroll_frame:
            return
            
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Show count
        count_label = ctk.CTkLabel(
            self.scroll_frame,
            text=f"📋 {len(self.filtered_values)} fonts found",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        count_label.pack(fill="x", padx=10, pady=(5, 5))
        
        # Add font items (limit to 200 for performance)
        for font_name in self.filtered_values[:200]:
            self.create_font_item(font_name)
    
    def create_font_item(self, font_name):
        """Create a single clickable font item"""
        item = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", height=35)
        item.pack(fill="x", padx=2, pady=1)
        item.pack_propagate(False)
        
        label = ctk.CTkLabel(
            item,
            text=f"    {font_name}",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color="#E0E0E0"
        )
        label.pack(fill="both", expand=True)
        
        # Bind hover and click events
        def on_enter(event, frame=item):
            frame.configure(fg_color="#1E90FF")
            
        def on_leave(event, frame=item):
            frame.configure(fg_color="transparent")
            
        def on_click(event, name=font_name):
            self.select_item(name)
        
        item.bind("<Enter>", on_enter)
        item.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        item.bind("<Button-1>", on_click)
        label.bind("<Button-1>", on_click)
    
    def on_scroll(self, event):
        """Handle scroll in dropdown"""
        if self.scroll_frame:
            if event.num == 4 or event.delta > 0:
                self.scroll_frame._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.scroll_frame._parent_canvas.yview_scroll(1, "units")
    
    def select_item(self, value):
        """Select a font from dropdown"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self.hide_dropdown()
        if self.command:
            self.command(value)
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class WatermarkApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Watermark Pro - Professional Image Watermarking Tool")
        self.window.geometry("1360x980")
        self.window.configure(fg_color="#0a0a0a")

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Settings file
        self.settings_file = os.path.join(os.path.dirname(__file__), "watermark_settings.json")
        
        self.default_settings = {
            "color": [30, 144, 255],
            "opacity": 200,
            "font": "Segoe UI",
            "size": 48,
            "position": "bottom-right",
            "rotation": 0,
            "text": "@Yuseph"
        }
        
        self.settings = self.load_settings()
        
        self.watermark_color = tuple(self.settings["color"] + [self.settings["opacity"]])
        self.watermark_opacity = self.settings["opacity"]
        self.font_family = self.settings["font"]
        self.watermark_size = self.settings["size"]
        self.watermark_position = self.settings["position"]
        self.rotation_angle = self.settings["rotation"]
        self.watermark_text = self.settings["text"]
        
        self.input_folder = ""
        self.output_folder = ""
        self.log_file = os.path.join(os.path.dirname(__file__), "processing_log.txt")
        
        self.create_backup = ctk.BooleanVar(value=True)
        self.create_thumbnail = ctk.BooleanVar(value=False)
        
        self.position_mode = ctk.StringVar(value="preset")
        self.x_percent = ctk.DoubleVar(value=50.0)
        self.y_percent = ctk.DoubleVar(value=50.0)
        
        # Common Windows fonts
        self.all_fonts = [
            "Arial", "Arial Black", "Arial Narrow", "Bahnschrift", "Calibri", "Calibri Light",
            "Cambria", "Cambria Math", "Candara", "Candara Light", "Comic Sans MS",
            "Consolas", "Constantia", "Corbel", "Corbel Light", "Courier New",
            "Ebrima", "Franklin Gothic Medium", "Gabriola", "Gadugi", "Georgia",
            "Impact", "Ink Free", "Javanese Text", "Leelawadee UI", "Lucida Console",
            "Lucida Sans Unicode", "Malgun Gothic", "Microsoft Himalaya",
            "Microsoft JhengHei", "Microsoft New Tai Lue", "Microsoft PhagsPa",
            "Microsoft Sans Serif", "Microsoft Tai Le", "Microsoft YaHei",
            "Microsoft Yi Baiti", "MingLiU-ExtB", "Mongolian Baiti", "MV Boli",
            "Myanmar Text", "Nirmala UI", "Palatino Linotype", "Segoe MDL2 Assets",
            "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Black",
            "Segoe UI Emoji", "Segoe UI Historic", "Segoe UI Light", "Segoe UI Semibold",
            "Segoe UI Semilight", "Segoe UI Symbol", "SimSun", "Sitka", "Sitka Small",
            "Sylfaen", "Symbol", "Tahoma", "Times New Roman", "Trebuchet MS",
            "Verdana", "Webdings", "Wingdings", "Yu Gothic", "Yu Gothic UI"
        ]
        
        self.setup_ui()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return self.default_settings.copy()

    def save_settings(self):
        try:
            current_settings = {
                "color": list(self.watermark_color[:3]),
                "opacity": self.watermark_opacity,
                "font": self.font_combo.get(),
                "size": self.watermark_size,
                "position": self.position_var.get(),
                "rotation": self.rotation_angle,
                "text": self.entry_text.get()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(current_settings, f, indent=4)
            self.status_label.configure(text="✓ Settings saved successfully!", text_color="#4CAF50")
            self.window.after(2500, self.reset_status)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")

    def reset_status(self):
        self.status_label.configure(text="● Ready to process images", text_color="#4CAF50")

    def update_font_preview(self, choice=None):
        try:
            selected_font = choice or self.font_combo.get()
            if selected_font:
                self.font_preview.configure(font=(selected_font, 38))
        except:
            pass

    def setup_ui(self):
        # Main scrollable container
        self.main_container = ctk.CTkScrollableFrame(
            self.window,
            corner_radius=0,
            fg_color="#0a0a0a",
            scrollbar_button_color="#1E90FF",
            scrollbar_button_hover_color="#3578E6"
        )
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Setup smooth scrolling
        self._setup_scrolling()

        # Header
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", pady=(35, 25), padx=45)

        ctk.CTkLabel(header, text="✨ WATERMARK PRO ✨", 
                    font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"), 
                    text_color="#1E90FF").pack()
        ctk.CTkLabel(header, text="Professional Batch Image Watermarking Tool",
                    font=ctk.CTkFont(size=18), text_color="#AAAAAA").pack(pady=8)

        # All sections
        self.create_folder_section().pack(fill="x", pady=10, padx=45)
        self.create_text_section().pack(fill="x", pady=10, padx=45)
        self.create_font_section().pack(fill="x", pady=10, padx=45)
        self.create_style_section().pack(fill="x", pady=10, padx=45)
        self.create_rotation_section().pack(fill="x", pady=10, padx=45)
        self.create_position_section().pack(fill="x", pady=10, padx=45)
        self.create_advanced_section().pack(fill="x", pady=10, padx=45)

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_frame.pack(pady=35, padx=45, fill="x")

        self.btn_save = ctk.CTkButton(
            btn_frame, text="💾 Save Settings", command=self.save_settings,
            height=52, width=250, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2ECC71", hover_color="#27AE60", corner_radius=14
        )
        self.btn_save.pack(side="left", padx=(0, 20))

        self.btn_start = ctk.CTkButton(
            btn_frame, text="🚀 Start Processing", command=self.process_images,
            height=52, font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1E90FF", hover_color="#3578E6", corner_radius=14,
            border_width=2, border_color="#FFFFFF"
        )
        self.btn_start.pack(side="left", fill="x", expand=True)

        # Status bar
        status_card = ctk.CTkFrame(self.main_container, fg_color="#1a1a1a", corner_radius=16)
        status_card.pack(fill="x", pady=(10, 40), padx=45)

        self.status_label = ctk.CTkLabel(
            status_card, text="● Ready to process images",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#4CAF50"
        )
        self.status_label.pack(pady=20)

    def _setup_scrolling(self):
        """Setup proper mousewheel scrolling"""
        def _on_mousewheel(event):
            canvas = self.main_container._parent_canvas
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")
        
        # Bind to the scrollable frame's canvas
        self.main_container._parent_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.main_container._parent_canvas.bind("<Button-4>", _on_mousewheel)
        self.main_container._parent_canvas.bind("<Button-5>", _on_mousewheel)
        
        # Also bind to main window for when mouse is anywhere
        self.window.bind("<MouseWheel>", _on_mousewheel)
        self.window.bind("<Button-4>", _on_mousewheel)
        self.window.bind("<Button-5>", _on_mousewheel)

    def create_card(self, title):
        card = ctk.CTkFrame(
            self.main_container,
            fg_color="#1a1a1a",
            corner_radius=14,
            border_width=1,
            border_color="#333333"
        )
        header_frame = ctk.CTkFrame(card, fg_color="#252525", height=40, corner_radius=12)
        header_frame.pack(fill="x", padx=1, pady=1)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(header_frame, text=title, 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#1E90FF").pack(side="left", padx=20, pady=8)
        return card

    def create_folder_section(self):
        card = self.create_card("📁 FOLDER SELECTION")
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(f, text="Input Folder:", font=ctk.CTkFont(size=14, weight="bold"), width=120).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(f, text="Browse", width=140, height=38, corner_radius=10,
                     command=self.select_input, font=ctk.CTkFont(size=13)).grid(row=0, column=1, padx=12)
        self.label_input = ctk.CTkLabel(f, text="Not selected", text_color="#888888", font=ctk.CTkFont(size=13))
        self.label_input.grid(row=0, column=2, sticky="w")

        ctk.CTkLabel(f, text="Output Folder:", font=ctk.CTkFont(size=14, weight="bold"), width=120).grid(row=1, column=0, sticky="w", pady=(12,0))
        ctk.CTkButton(f, text="Browse", width=140, height=38, corner_radius=10,
                     command=self.select_output, font=ctk.CTkFont(size=13)).grid(row=1, column=1, padx=12, pady=(12,0))
        self.label_output = ctk.CTkLabel(f, text="Not selected", text_color="#888888", font=ctk.CTkFont(size=13))
        self.label_output.grid(row=1, column=2, sticky="w", pady=(12,0))

        return card

    def create_text_section(self):
        card = self.create_card("🖊️ WATERMARK TEXT")
        self.entry_text = ctk.CTkEntry(
            card, height=50, placeholder_text="Enter your watermark text...",
            font=ctk.CTkFont(size=16), corner_radius=12, border_width=2,
            border_color="#333333"
        )
        self.entry_text.pack(fill="x", padx=25, pady=20)
        self.entry_text.insert(0, self.watermark_text)
        return card

    def create_font_section(self):
        card = self.create_card("🖋️ FONT SELECTION")
        
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=25, pady=(15, 10))
        
        ctk.CTkLabel(f, text="Font:", font=ctk.CTkFont(size=14, weight="bold"), width=60).pack(side="left")
        
        self.font_combo = FastSearchCombo(
            f, 
            values=self.all_fonts,
            command=self.update_font_preview,
            width=400
        )
        self.font_combo.pack(side="left", fill="x", expand=True, padx=(15, 0))
        self.font_combo.set(self.font_family)

        # Preview
        preview_frame = ctk.CTkFrame(card, fg_color="#252525", corner_radius=12, height=120)
        preview_frame.pack(fill="x", padx=25, pady=15)
        preview_frame.pack_propagate(False)

        self.font_preview = ctk.CTkLabel(preview_frame, text="AaBbCc 123 XYZ", 
                                       font=(self.font_family, 38), text_color="white")
        self.font_preview.pack(expand=True)

        return card

    def create_style_section(self):
        card = self.create_card("🎨 STYLE SETTINGS")
        
        # Size
        sf = ctk.CTkFrame(card, fg_color="transparent")
        sf.pack(fill="x", padx=25, pady=(15,8))
        ctk.CTkLabel(sf, text="Size:", font=ctk.CTkFont(size=14, weight="bold"), width=80).pack(side="left")
        self.size_slider = ctk.CTkSlider(sf, from_=12, to=300, command=self.update_size_label, width=400)
        self.size_slider.set(self.watermark_size)
        self.size_slider.pack(side="left", padx=12)
        self.size_label = ctk.CTkLabel(sf, text=f"{self.watermark_size} px", width=70, font=ctk.CTkFont(weight="bold", size=13))
        self.size_label.pack(side="left")

        # Opacity
        of = ctk.CTkFrame(card, fg_color="transparent")
        of.pack(fill="x", padx=25, pady=8)
        ctk.CTkLabel(of, text="Opacity:", font=ctk.CTkFont(size=14, weight="bold"), width=80).pack(side="left")
        self.opacity_slider = ctk.CTkSlider(of, from_=0, to=255, command=self.update_opacity_label, width=400)
        self.opacity_slider.set(self.watermark_opacity)
        self.opacity_slider.pack(side="left", padx=12)
        self.opacity_label = ctk.CTkLabel(of, text=f"{int(self.watermark_opacity/2.55)}%", width=70, font=ctk.CTkFont(weight="bold", size=13))
        self.opacity_label.pack(side="left")

        # Color
        cf = ctk.CTkFrame(card, fg_color="transparent")
        cf.pack(fill="x", padx=25, pady=8)
        ctk.CTkLabel(cf, text="Color:", font=ctk.CTkFont(size=14, weight="bold"), width=80).pack(side="left")
        ctk.CTkButton(cf, text="Pick Color", width=130, height=38, corner_radius=10,
                     command=self.choose_color, font=ctk.CTkFont(size=13)).pack(side="left", padx=12)
        hex_color = '#{:02x}{:02x}{:02x}'.format(*self.watermark_color[:3])
        self.color_preview = ctk.CTkLabel(cf, text=" ", fg_color=hex_color, width=60, height=35, corner_radius=8)
        self.color_preview.pack(side="left")

        return card

    def create_rotation_section(self):
        card = self.create_card("🔄 ROTATION")
        rf = ctk.CTkFrame(card, fg_color="transparent")
        rf.pack(fill="x", padx=25, pady=20)
        ctk.CTkLabel(rf, text="Angle:", font=ctk.CTkFont(size=14, weight="bold"), width=80).pack(side="left")
        self.rotation_slider = ctk.CTkSlider(rf, from_=0, to=360, number_of_steps=36,
                                           command=self.update_rotation_label, width=400)
        self.rotation_slider.set(self.rotation_angle)
        self.rotation_slider.pack(side="left", padx=12)
        self.rotation_label = ctk.CTkLabel(rf, text=f"{self.rotation_angle}°", width=70, font=ctk.CTkFont(weight="bold", size=13))
        self.rotation_label.pack(side="left")
        return card

    def create_position_section(self):
        card = self.create_card("📍 POSITION")

        mf = ctk.CTkFrame(card, fg_color="transparent")
        mf.pack(fill="x", padx=25, pady=(15,10))
        ctk.CTkLabel(mf, text="Mode:", font=ctk.CTkFont(size=14, weight="bold"), width=80).pack(side="left")
        ctk.CTkRadioButton(mf, text="Preset", variable=self.position_mode, 
                          value="preset", command=self.toggle_position_mode, font=ctk.CTkFont(size=13)).pack(side="left", padx=(0,30))
        ctk.CTkRadioButton(mf, text="Custom %", variable=self.position_mode, 
                          value="percentage", command=self.toggle_position_mode, font=ctk.CTkFont(size=13)).pack(side="left")

        self.preset_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.position_var = ctk.StringVar(value=self.watermark_position)

        r1 = ctk.CTkFrame(self.preset_frame, fg_color="transparent")
        r1.pack(pady=6)
        for text, val in [("Top Left", "top-left"), ("Top Right", "top-right"), ("Center", "center")]:
            ctk.CTkRadioButton(r1, text=text, variable=self.position_var, value=val, font=ctk.CTkFont(size=13)).pack(side="left", padx=25)

        r2 = ctk.CTkFrame(self.preset_frame, fg_color="transparent")
        r2.pack(pady=6)
        for text, val in [("Bottom Left", "bottom-left"), ("Bottom Right", "bottom-right")]:
            ctk.CTkRadioButton(r2, text=text, variable=self.position_var, value=val, font=ctk.CTkFont(size=13)).pack(side="left", padx=25)

        self.percent_frame = ctk.CTkFrame(card, fg_color="transparent")
        for axis, var, lbl, cmd in [("X", self.x_percent, "X (%):", self.update_x_label),
                                    ("Y", self.y_percent, "Y (%):", self.update_y_label)]:
            fr = ctk.CTkFrame(self.percent_frame, fg_color="transparent")
            fr.pack(fill="x", pady=8)
            ctk.CTkLabel(fr, text=lbl, width=80, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
            sl = ctk.CTkSlider(fr, from_=0, to=100, command=cmd, width=400)
            sl.pack(side="left", padx=12)
            if axis == "X":
                self.x_slider = sl
                self.x_slider.set(var.get())
                self.x_label = ctk.CTkLabel(fr, text=f"{int(var.get())}%", width=60, font=ctk.CTkFont(weight="bold", size=13))
                self.x_label.pack(side="left")
            else:
                self.y_slider = sl
                self.y_slider.set(var.get())
                self.y_label = ctk.CTkLabel(fr, text=f"{int(var.get())}%", width=60, font=ctk.CTkFont(weight="bold", size=13))
                self.y_label.pack(side="left")

        ctk.CTkLabel(self.percent_frame, text="0% = Left/Top • 50% = Center • 100% = Right/Bottom",
                    font=ctk.CTkFont(size=11, slant="italic"), text_color="#888").pack(pady=8)

        self.toggle_position_mode()
        return card

    def create_advanced_section(self):
        card = self.create_card("⚙️ ADVANCED OPTIONS")
        self.backup_check = ctk.CTkCheckBox(card, text="Create backup of original images",
                                          variable=self.create_backup, font=ctk.CTkFont(size=14))
        self.backup_check.pack(anchor="w", padx=25, pady=(15,8))

        self.thumb_check = ctk.CTkCheckBox(card, text="Create web thumbnails (150×150)",
                                          variable=self.create_thumbnail, font=ctk.CTkFont(size=14))
        self.thumb_check.pack(anchor="w", padx=25, pady=8)
        return card

    def toggle_position_mode(self):
        if self.position_mode.get() == "preset":
            self.preset_frame.pack(fill="x", padx=25, pady=12)
            self.percent_frame.pack_forget()
        else:
            self.preset_frame.pack_forget()
            self.percent_frame.pack(fill="x", padx=25, pady=12)

    def update_size_label(self, value):
        self.watermark_size = int(value)
        self.size_label.configure(text=f"{self.watermark_size} px")

    def update_opacity_label(self, value):
        self.watermark_opacity = int(value)
        self.opacity_label.configure(text=f"{int(value / 2.55)}%")
        if len(self.watermark_color) == 4:
            r, g, b, _ = self.watermark_color
            self.watermark_color = (r, g, b, self.watermark_opacity)

    def update_rotation_label(self, value):
        self.rotation_angle = int(value)
        self.rotation_label.configure(text=f"{self.rotation_angle}°")

    def update_x_label(self, value):
        self.x_percent.set(value)
        self.x_label.configure(text=f"{int(value)}%")

    def update_y_label(self, value):
        self.y_percent.set(value)
        self.y_label.configure(text=f"{int(value)}%")

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Watermark Color")
        if color[0]:
            rgb = tuple(map(int, color[0]))
            self.watermark_color = rgb + (self.watermark_opacity,)
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
            self.color_preview.configure(fg_color=hex_color)

    def get_position_coordinates(self, img_w, img_h, txt_w, txt_h):
        margin = 30
        if self.position_mode.get() == "preset":
            pos = self.position_var.get()
            if pos == "top-left":      return (margin, margin)
            elif pos == "top-right":   return (img_w - txt_w - margin, margin)
            elif pos == "bottom-left": return (margin, img_h - txt_h - margin)
            elif pos == "bottom-right":return (img_w - txt_w - margin, img_h - txt_h - margin)
            else:                      return ((img_w - txt_w)//2, (img_h - txt_h)//2)
        else:
            x = int((img_w - txt_w) * self.x_percent.get() / 100)
            y = int((img_h - txt_h) * self.y_percent.get() / 100)
            return (max(0, min(x, img_w - txt_w)), max(0, min(y, img_h - txt_h)))

    def select_input(self):
        self.input_folder = filedialog.askdirectory()
        if self.input_folder:
            self.label_input.configure(text=f"✓ {os.path.basename(self.input_folder)}", text_color="#4CAF50")

    def select_output(self):
        self.output_folder = filedialog.askdirectory()
        if self.output_folder:
            self.label_output.configure(text=f"✓ {os.path.basename(self.output_folder)}", text_color="#4CAF50")

    def log_message(self, msg):
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except:
            pass

    def process_images(self):
        if not self.input_folder:
            messagebox.showerror("Error", "Please select input folder!")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Please select output folder!")
            return

        self.watermark_text = self.entry_text.get().strip() or "@Yuseph"

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        backup_folder = os.path.join(self.output_folder, "backup_originals") if self.create_backup.get() else None
        thumb_folder = os.path.join(self.output_folder, "thumbnails") if self.create_thumbnail.get() else None

        if backup_folder:
            os.makedirs(backup_folder, exist_ok=True)
        if thumb_folder:
            os.makedirs(thumb_folder, exist_ok=True)

        count = 0
        self.btn_start.configure(state="disabled", text="⏳ Processing...")

        self.log_message(f"=== Started processing: {self.input_folder} ===")
        self.log_message(f"Watermark: '{self.watermark_text}' | Font: {self.font_combo.get()} | Size: {self.watermark_size}")

        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                input_path = os.path.join(self.input_folder, filename)
                output_path = os.path.join(self.output_folder, filename)

                if backup_folder:
                    shutil.copy2(input_path, os.path.join(backup_folder, filename))

                self.add_watermark(input_path, output_path)

                if thumb_folder:
                    try:
                        with Image.open(input_path) as img:
                            img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                            thumb_path = os.path.join(thumb_folder, f"thumb_{filename}")
                            img.save(thumb_path, 'PNG' if filename.lower().endswith('.png') else 'JPEG', quality=85)
                    except:
                        pass

                count += 1
                self.status_label.configure(text=f"🔄 Processing: {filename}", text_color="#FFAA33")
                self.window.update()

        self.status_label.configure(text=f"✅ Successfully processed {count} images!", text_color="#4CAF50")
        self.btn_start.configure(state="normal", text="🚀 Start Processing")

        messagebox.showinfo("Success", f"🎉 Processing completed!\n\n{count} images watermarked successfully.\nLog file saved.")

    def add_watermark(self, input_path, output_path):
        try:
            image = Image.open(input_path).convert("RGBA")
            txt_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(txt_layer)

            font_name = self.font_combo.get()
            font = None
            
            try:
                font = ImageFont.truetype(font_name + ".ttf", self.watermark_size)
            except:
                try:
                    font = ImageFont.truetype(font_name, self.watermark_size)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", self.watermark_size)
                    except:
                        font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), self.watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x, y = self.get_position_coordinates(image.width, image.height, text_width, text_height)

            if self.rotation_angle != 0:
                padding = 30
                txt_img = Image.new('RGBA', (text_width + padding*2, text_height + padding*2), (0,0,0,0))
                txt_draw = ImageDraw.Draw(txt_img)
                txt_draw.text((padding, padding), self.watermark_text, fill=self.watermark_color, font=font)
                rotated = txt_img.rotate(self.rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)
                paste_x = x - (rotated.width - text_width) // 2
                paste_y = y - (rotated.height - text_height) // 2
                txt_layer.paste(rotated, (paste_x, paste_y), rotated)
            else:
                draw.text((x, y), self.watermark_text, fill=self.watermark_color, font=font)

            watermarked = Image.alpha_composite(image, txt_layer)

            if output_path.lower().endswith('.png'):
                watermarked.save(output_path, 'PNG')
            else:
                watermarked.convert("RGB").save(output_path, 'JPEG', quality=95, optimize=True)

        except Exception as e:
            self.log_message(f"Error processing {os.path.basename(input_path)}: {e}")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = WatermarkApp()
    app.run()
# End