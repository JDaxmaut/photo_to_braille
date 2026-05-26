import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps, ImageDraw
import os
import math
import threading

from photo_to_ascii import image_to_braille

# ─── Music Player Palette ─────────────────────────────────────────────
BG = "#121110"
SURFACE = "#1A1817"
CARD = "#1E1C1B"
ALBUM_BG = "#181615"
ACCENT = "#E5A93C"
ACCENT_HOVER = "#D49A2E"
ACCENT_DIM = "#A87D2A"
TEXT = "#FFFFFF"
TEXT_DIM = "#7D7A77"
TEXT_MUTED = "#5A5755"
DIVIDER = "#2A2827"
BTN_BORDER = "#E5A93C"
BTN_BG = "#1A1817"
BTN_HOVER = "#22201F"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEAD = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)
FONT_MED = ("Segoe UI", 14, "bold")
FONT_BTN = ("Segoe UI", 13, "bold")
FONT_TRACK = ("Segoe UI", 11)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

TB_HEIGHT = 40
RESIZE_TOL = 5


class PhotoToBrailleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("")
        self.geometry("1100x680")
        self.configure(fg_color=BG)
        self.minsize(900, 580)

        self.image_path = None
        self.preview_photo = None
        self.save_dir = os.getcwd()
        self.converting = False

        self.width_var = ctk.IntVar(value=120)
        self.invert_var = ctk.BooleanVar(value=False)
        self.sensitivity_var = ctk.DoubleVar(value=1.0)

        self._drag_start = {"x": 0, "y": 0, "wx": 0, "wy": 0}
        self._resize_dir = None
        self._maximized = False
        self._normal_geo = None
        self._is_dragging = False

        self._create_title_bar()
        self._create_body()

        self._title_bar.bind("<Button-1>", self._drag_start_move)
        self._title_bar.bind("<B1-Motion>", self._drag_move)
        self.bind("<Map>", self._on_map, add="+")

    # ═══════════════════════════════════════════════════════════════
    #  Title Bar
    # ═══════════════════════════════════════════════════════════════

    def _create_title_bar(self):
        self._title_bar = tk.Frame(
            self, bg=BG, height=TB_HEIGHT, highlightthickness=0,
        )
        self._title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._title_bar.grid_propagate(False)
        self._title_bar.columnconfigure(0, weight=1)

        # Thin accent bottom line
        tk.Frame(self._title_bar, bg=ACCENT, height=1).place(
            relx=0, rely=1.0, relwidth=1, anchor="sw",
        )

        tk.Label(
            self._title_bar,
            text="Photo to Braille Converter",
            font=("Segoe UI", 11, "bold"),
            bg=BG, fg=TEXT, anchor="w",
        ).place(x=16, rely=0.5, anchor="w")

        self._create_win_buttons()

    def _create_win_buttons(self):
        btn_bg = BG
        btn_size = 46

        self._close_btn = tk.Label(
            self._title_bar, text="\u2715",
            font=("Segoe UI", 10), bg=btn_bg, fg=TEXT_DIM,
            anchor="center", width=4,
        )
        self._close_btn.place(relx=1.0, rely=0.5, anchor="e")
        self._close_btn.bind("<Enter>", lambda e: self._close_btn.configure(bg="#2A1818", fg=TEXT))
        self._close_btn.bind("<Leave>", lambda e: self._close_btn.configure(bg=btn_bg, fg=TEXT_DIM))
        self._close_btn.bind("<Button-1>", lambda e: self.destroy())

        self._max_btn = tk.Label(
            self._title_bar, text="\u25A1",
            font=("Segoe UI", 10), bg=btn_bg, fg=TEXT_DIM,
            anchor="center", width=4,
        )
        self._max_btn.place(relx=1.0, rely=0.5, anchor="e", x=-btn_size)
        self._max_btn.bind("<Enter>", lambda e: self._max_btn.configure(bg=DIVIDER, fg=TEXT))
        self._max_btn.bind("<Leave>", lambda e: self._max_btn.configure(bg=btn_bg, fg=TEXT_DIM))
        self._max_btn.bind("<Button-1>", lambda e: self._toggle_maximize())

        self._min_btn = tk.Label(
            self._title_bar, text="\u2212",
            font=("Segoe UI", 10), bg=btn_bg, fg=TEXT_DIM,
            anchor="center", width=4,
        )
        self._min_btn.place(relx=1.0, rely=0.5, anchor="e", x=-btn_size * 2)
        self._min_btn.bind("<Enter>", lambda e: self._min_btn.configure(bg=DIVIDER, fg=TEXT))
        self._min_btn.bind("<Leave>", lambda e: self._min_btn.configure(bg=btn_bg, fg=TEXT_DIM))
        self._min_btn.bind("<Button-1>", lambda e: self.iconify())

    def _toggle_maximize(self):
        if not self._maximized:
            self._normal_geo = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
            self._maximized = True
            self._max_btn.configure(text="\u29C9")
        else:
            if self._normal_geo:
                self.geometry(self._normal_geo)
            self._maximized = False
            self._max_btn.configure(text="\u25A1")

    # ─── Window drag ─────────────────────────────────────────────

    def _drag_start_move(self, event):
        self._drag_start["x"] = event.x_root
        self._drag_start["y"] = event.y_root
        self._drag_start["wx"] = self.winfo_x()
        self._drag_start["wy"] = self.winfo_y()
        self._is_dragging = True
        if self._maximized:
            self._toggle_maximize()

    def _drag_move(self, event):
        if not self._is_dragging:
            return
        dx = event.x_root - self._drag_start["x"]
        dy = event.y_root - self._drag_start["y"]
        self.geometry(
            f"+{self._drag_start['wx'] + dx}+{self._drag_start['wy'] + dy}"
        )

    # ─── Resize ───────────────────────────────────────────────────

    def _on_map(self, event=None):
        self.overrideredirect(True)
        self.bind("<Motion>", self._on_motion, add="+")
        self.bind("<Button-1>", self._on_edge_press, add="+")
        self.bind("<B1-Motion>", self._on_edge_drag, add="+")
        self.bind("<ButtonRelease-1>", self._on_edge_release, add="+")

    def _get_resize_dir(self, event):
        x = event.x_root - self.winfo_x()
        y = event.y_root - self.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        t = RESIZE_TOL
        d = ""
        if x <= t:
            d += "w"
        elif x >= w - t:
            d += "e"
        if y <= t:
            d += "n"
        elif y >= h - t:
            d += "s"
        return d or None

    def _set_cursor(self, d):
        m = {
            "n": "sb_v_double_arrow",
            "s": "sb_v_double_arrow",
            "w": "sb_h_double_arrow",
            "e": "sb_h_double_arrow",
            "ne": "ne_crossing",
            "nw": "nw_crossing",
            "se": "se_crossing",
            "sw": "sw_crossing",
        }
        self.config(cursor=m.get(d, ""))

    def _on_motion(self, event):
        self._set_cursor(self._get_resize_dir(event))

    def _on_edge_press(self, event):
        d = self._get_resize_dir(event)
        if d:
            self._resize_dir = d
            self._drag_start["x"] = event.x_root
            self._drag_start["y"] = event.y_root
            self._drag_start["wx"] = self.winfo_x()
            self._drag_start["wy"] = self.winfo_y()
            self._drag_start["ww"] = self.winfo_width()
            self._drag_start["wh"] = self.winfo_height()

    def _on_edge_drag(self, event):
        if not self._resize_dir:
            return
        d = self._resize_dir
        dx = event.x_root - self._drag_start["x"]
        dy = event.y_root - self._drag_start["y"]
        x = self._drag_start["wx"]
        y = self._drag_start["wy"]
        w = self._drag_start["ww"]
        h = self._drag_start["wh"]

        if "w" in d:
            x += dx
            w -= dx
        if "e" in d:
            w += dx
        if "n" in d:
            y += dy
            h -= dy
        if "s" in d:
            h += dy

        mw, mh = self.minsize()
        w = max(w, mw)
        h = max(h, mh)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_edge_release(self, event):
        self._resize_dir = None

    # ═══════════════════════════════════════════════════════════════
    #  Body: Left (settings) + Right (album art)
    # ═══════════════════════════════════════════════════════════════

    def _create_body(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=5)

        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.grid(row=1, column=0, columnspan=2, sticky="nsew")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=5)
        body.grid_rowconfigure(0, weight=1)

        self._create_left_panel(body)
        self._create_right_panel(body)

    # ─── LEFT: Settings like track list ───────────────────────────

    def _create_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=(16, 20))
        left.grid_rowconfigure(0, weight=0)
        left.grid_rowconfigure(1, weight=0)
        left.grid_rowconfigure(2, weight=0)
        left.grid_rowconfigure(3, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(
            left, text="Настройки",
            font=FONT_TITLE, text_color=TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        self._create_track_slider(left, 1,
            label="Ширина арта",
            variable=self.width_var,
            from_=30, to=250, steps=220,
            value_label=self._on_width_change,
            suffix=" симв.",
        )

        self._create_track_slider(left, 2,
            label="Порог яркости",
            variable=self.sensitivity_var,
            from_=0.3, to=2.0, steps=170,
            value_label=self._on_sensitivity_change,
            suffix="",
        )

        self._create_track_toggle(left, 3)

        # Spacer
        spacer = ctk.CTkFrame(left, fg_color="transparent")
        spacer.grid(row=4, column=0, sticky="sew")
        spacer.grid_columnconfigure(0, weight=1)
        spacer.grid_rowconfigure(0, weight=1)

        # Save path
        save_frame = ctk.CTkFrame(
            spacer, fg_color=CARD, corner_radius=6, border_width=0,
        )
        save_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        save_frame.grid_columnconfigure(0, weight=1)
        save_frame.grid_columnconfigure(1, weight=0)

        self.save_path_label = ctk.CTkLabel(
            save_frame,
            text=f"  {self.save_dir}",
            font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w",
        )
        self.save_path_label.grid(row=0, column=0, sticky="w", padx=12, pady=8)

        ctk.CTkButton(
            save_frame,
            text="...",
            font=("Segoe UI", 12, "bold"),
            fg_color="transparent", hover_color=DIVIDER,
            text_color=TEXT_DIM,
            width=30, height=26, corner_radius=4,
            command=self._select_save_dir,
        ).grid(row=0, column=1, padx=(0, 6))

        # Convert button
        self.convert_btn = ctk.CTkButton(
            spacer,
            text="КОНВЕРТИРОВАТЬ",
            font=FONT_BTN,
            fg_color=BG,
            hover_color=BTN_HOVER,
            text_color=ACCENT,
            border_width=1,
            border_color=ACCENT,
            corner_radius=6,
            height=40,
            command=self._start_conversion,
        )
        self.convert_btn.grid(row=1, column=0, sticky="ew", pady=(0, 4))

        self.status_label = ctk.CTkLabel(
            spacer,
            text="",
            font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w",
        )
        self.status_label.grid(row=2, column=0, sticky="w")

    def _create_track_slider(self, parent, row, label, variable,
                              from_, to, steps, value_label, suffix):
        card = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        card.grid_columnconfigure(0, weight=1)

        # Label row
        lbl_frame = ctk.CTkFrame(card, fg_color="transparent")
        lbl_frame.grid(row=0, column=0, sticky="ew", pady=(10, 2))
        lbl_frame.grid_columnconfigure(0, weight=1)
        lbl_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            lbl_frame, text=label,
            font=FONT_HEAD, text_color=TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self_val = ctk.CTkLabel(
            lbl_frame, text="",
            font=("Segoe UI", 11), text_color=ACCENT, anchor="e",
        )
        self_val.grid(row=0, column=1, sticky="e")

        # Store reference by label
        if label == "Ширина арта":
            self.width_value_label = self_val
        else:
            self.sens_value_label = self_val

        # Thin slider line
        slider = ctk.CTkSlider(
            card, from_=from_, to=to, number_of_steps=steps,
            variable=variable,
            command=value_label,
            fg_color="#2A2827",
            progress_color=ACCENT,
            button_color=TEXT,
            button_hover_color=ACCENT,
            height=3,
        )
        slider.grid(row=1, column=0, sticky="ew", pady=(2, 2))

        # Hint row
        hint_text = {
            "Ширина арта": "меньше — компактнее, больше — детальнее",
            "Порог яркости": "меньше — темнее, больше — светлее",
        }.get(label, "")

        if hint_text:
            ctk.CTkLabel(
                card, text=hint_text,
                font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w",
            ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        # Thin divider
        tk.Frame(card, bg=DIVIDER, height=1).grid(
            row=3, column=0, sticky="ew",
        )

        # Trigger initial value display
        value_label(None)

    def _on_width_change(self, _=None):
        self.width_value_label.configure(
            text=f"{self.width_var.get()} симв."
        )

    def _on_sensitivity_change(self, _=None):
        self.sens_value_label.configure(
            text=f"{self.sensitivity_var.get():.2f}"
        )

    def _create_track_toggle(self, parent, row):
        card = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        card.grid_columnconfigure(0, weight=1)

        tf = ctk.CTkFrame(card, fg_color="transparent")
        tf.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        tf.grid_columnconfigure(0, weight=1)
        tf.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            tf, text="Инверсия (негатив)",
            font=FONT_HEAD, text_color=TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkSwitch(
            tf, text="",
            variable=self.invert_var,
            command=self._on_invert_change,
            fg_color="#2A2827",
            progress_color=ACCENT,
            button_color=TEXT,
            button_hover_color=ACCENT,
        ).grid(row=0, column=1)

        tk.Frame(card, bg=DIVIDER, height=1).grid(
            row=1, column=0, sticky="ew", pady=(6, 0),
        )

    def _on_invert_change(self):
        if self.image_path:
            self._update_preview()

    # ─── RIGHT: Album art ─────────────────────────────────────────

    def _create_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=(16, 20))
        right.grid_columnconfigure(0, weight=1)

        # Make it mimic a record/album view
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=0)
        right.grid_rowconfigure(2, weight=0)

        # Album art container
        self.album_frame = ctk.CTkFrame(
            right, fg_color=ALBUM_BG, corner_radius=10,
            border_width=1, border_color=DIVIDER,
        )
        self.album_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 12))

        self._show_album_placeholder()

        # Track name (filename)
        self.track_name_label = ctk.CTkLabel(
            right,
            text="\u2014",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT, anchor="w",
        )
        self.track_name_label.grid(row=1, column=0, sticky="w", pady=(0, 2))

        # Resolution / size
        self.track_info_label = ctk.CTkLabel(
            right,
            text="",
            font=FONT_BODY,
            text_color=TEXT_DIM, anchor="w",
        )
        self.track_info_label.grid(row=2, column=0, sticky="w")

    def _show_album_placeholder(self):
        for w in self.album_frame.winfo_children():
            w.destroy()

        self.album_frame.grid_propagate(False)

        self.album_canvas = tk.Canvas(
            self.album_frame,
            bg=ALBUM_BG, highlightthickness=0, bd=0, relief="flat",
        )
        self.album_canvas.pack(fill="both", expand=True)

        self.album_canvas.bind("<Configure>", self._redraw_album_placeholder)
        self.album_canvas.bind("<Button-1>", lambda e: self._select_image())

        # Store hover state for visual feedback
        self._album_hover = False
        self.album_canvas.bind(
            "<Enter>", lambda e: self._set_album_hover(True)
        )
        self.album_canvas.bind(
            "<Leave>", lambda e: self._set_album_hover(False)
        )

        # Trigger initial draw
        self._album_cw = 0
        self._album_ch = 0

    def _set_album_hover(self, hover):
        self._album_hover = hover
        if self.image_path:
            return  # don't redraw placeholder if image loaded
        self._redraw_album_placeholder()

    def _redraw_album_placeholder(self, event=None):
        w = self.album_canvas.winfo_width()
        h = self.album_canvas.winfo_height()
        if w < 20 or h < 20:
            return

        self.album_canvas.delete("all")
        self._album_cw = w
        self._album_ch = h

        bc = ACCENT if self._album_hover else DIVIDER

        # Square inset for album art
        side = min(w, h) - 20
        x0 = (w - side) / 2
        y0 = (h - side) / 2

        # Outer border
        self.album_canvas.create_rectangle(
            x0, y0, x0 + side, y0 + side,
            outline=bc, width=1.5,
        )

        # Icon: simple music note / play symbol
        cx = w / 2
        cy = h / 2
        s = 20

        # Play triangle
        self.album_canvas.create_polygon(
            cx - s * 0.4, cy - s * 0.6,
            cx - s * 0.4, cy + s * 0.6,
            cx + s * 0.5, cy,
            fill="", outline=TEXT_MUTED, width=2,
        )

        # Text
        self.album_canvas.create_text(
            cx, cy + s + 16,
            text="Загрузите изображение",
            font=("Segoe UI", 12),
            fill=TEXT_MUTED, anchor="center",
        )
        self.album_canvas.create_text(
            cx, cy + s + 36,
            text="нажмите для выбора",
            font=("Segoe UI", 10),
            fill=TEXT_MUTED, anchor="center",
        )

    def _update_preview(self):
        if not self.image_path or not os.path.exists(self.image_path):
            self.track_info_label.configure(text="")
            self._show_album_placeholder()
            return

        for w in self.album_frame.winfo_children():
            w.destroy()

        try:
            img = Image.open(self.image_path)
        except Exception:
            self._show_album_placeholder()
            return

        af_w = self.album_frame.winfo_width()
        af_h = self.album_frame.winfo_height()
        if af_w < 40:
            af_w = 300
        if af_h < 40:
            af_h = 300

        # Square album art
        side = min(af_w, af_h) - 8
        if side < 40:
            side = 200
        if side < 40:
            side = af_w - 8

        # Crop to square from center
        w_img, h_img = img.size
        sq = min(w_img, h_img)
        left = (w_img - sq) // 2
        top = (h_img - sq) // 2
        img_sq = img.crop((left, top, left + sq, top + sq))
        img_sq = img_sq.convert("RGB")
        if self.invert_var.get():
            img_sq = ImageOps.invert(img_sq)

        img_sq.thumbnail((side, side), Image.LANCZOS)

        # Corner rounding mask
        mask = Image.new("L", img_sq.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        r = 10
        draw_mask.rounded_rectangle(
            (0, 0, img_sq.width - 1, img_sq.height - 1),
            radius=r, fill=255,
        )
        img_sq.putalpha(mask)

        self.preview_photo = ctk.CTkImage(
            light_image=img_sq, dark_image=img_sq,
            size=img_sq.size,
        )

        img_btn = ctk.CTkButton(
            self.album_frame,
            image=self.preview_photo, text="",
            fg_color="transparent",
            hover_color="#2A2827",
            corner_radius=10,
            command=self._select_image,
        )
        img_btn.pack(fill="both", expand=True)

        # Update track info
        fname = os.path.basename(self.image_path)
        name_no_ext = os.path.splitext(fname)[0]
        ext = os.path.splitext(fname)[1].upper()

        self.track_name_label.configure(text=name_no_ext)

        fsize = os.path.getsize(self.image_path)
        if fsize < 1024:
            ss = f"{fsize} B"
        elif fsize < 1024 * 1024:
            ss = f"{fsize / 1024:.1f} KB"
        else:
            ss = f"{fsize / (1024 * 1024):.1f} MB"

        orig_w, orig_h = img.size
        self.track_info_label.configure(
            text=f"{ext}  \u2022  {orig_w}\u00d7{orig_h}  \u2022  {ss}"
        )

        self.status_label.configure(
            text="готово к конвертации",
            text_color=TEXT_DIM,
        )

    # ═══════════════════════════════════════════════════════════════
    #  Actions
    # ═══════════════════════════════════════════════════════════════

    def _select_image(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("Все файлы", "*.*"),
            ],
        )
        if path:
            self._load_image(path)

    def _load_image(self, path):
        if not os.path.exists(path):
            return
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
            messagebox.showwarning(
                "Формат не поддерживается",
                "Пожалуйста, выберите файл изображения.",
            )
            return
        self.image_path = path
        self._update_preview()

    def _select_save_dir(self):
        path = filedialog.askdirectory(
            title="Папка для сохранения",
            initialdir=self.save_dir,
        )
        if path:
            self.save_dir = path
            self.save_path_label.configure(text=f"  {path}")

    def _start_conversion(self):
        if not self.image_path:
            self.status_label.configure(
                text="сначала выберите изображение",
                text_color=TEXT_DIM,
            )
            return
        if self.converting:
            return

        self.converting = True
        self.convert_btn.configure(
            text="КОНВЕРТАЦИЯ\u2026",
            state="disabled",
            fg_color=DIVIDER,
            border_color=DIVIDER,
            text_color=TEXT_MUTED,
        )
        self.status_label.configure(
            text="конвертация\u2026",
            text_color=ACCENT_DIM,
        )

        t = threading.Thread(target=self._convert, daemon=True)
        t.start()

    def _convert(self):
        try:
            width = self.width_var.get()
            sensitivity = self.sensitivity_var.get()
            invert = self.invert_var.get()

            result = image_to_braille(self.image_path, width=width, sensitivity=sensitivity)

            if invert:
                lines = result.split("\n")
                inverted = []
                for line in lines:
                    inv = []
                    for ch in line:
                        cp = ord(ch)
                        if 0x2800 <= cp <= 0x28FF:
                            inv.append(chr(0x28FF - (cp - 0x2800)))
                        elif cp == 0x0020:
                            inv.append("\u28FF")
                        else:
                            inv.append(ch)
                    inverted.append("".join(inv))
                result = "\n".join(inverted)

            base = os.path.splitext(os.path.basename(self.image_path))[0]
            out_path = os.path.join(self.save_dir, f"{base}_braille.txt")

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result)

            lines = result.split("\n")
            line_len = len(lines[0]) if lines else 0
            self.after(0, self._on_convert_success, out_path, len(lines), line_len)

        except Exception as e:
            self.after(0, self._on_convert_error, str(e))

    def _on_convert_success(self, path, num_lines, line_len):
        self.converting = False
        self.convert_btn.configure(
            text="КОНВЕРТИРОВАТЬ",
            state="normal",
            fg_color=BG,
            border_color=ACCENT,
            text_color=ACCENT,
        )
        self.status_label.configure(
            text=f"сохранено: {os.path.basename(path)}  ({num_lines} строк, {line_len} симв.)",
            text_color=ACCENT,
        )

    def _on_convert_error(self, msg):
        self.converting = False
        self.convert_btn.configure(
            text="КОНВЕРТИРОВАТЬ",
            state="normal",
            fg_color=BG,
            border_color=ACCENT,
            text_color=ACCENT,
        )
        self.status_label.configure(
            text=f"ошибка: {msg}",
            text_color=TEXT_DIM,
        )


if __name__ == "__main__":
    app = PhotoToBrailleApp()
    app.mainloop()
