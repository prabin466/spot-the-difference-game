import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np


# ─────────────────────────────────────────────
#  Colour palette  (dark navy theme)
# ─────────────────────────────────────────────
BG_DARK      = "#0d1117"   # window background
BG_PANEL     = "#161b22"   # sidebar / status panel
BG_CARD      = "#1c2230"   # canvas card background
ACCENT       = "#58a6ff"   # blue accent (buttons, highlights)
ACCENT_HOVER = "#79b8ff"
SUCCESS      = "#3fb950"   # green  – found
DANGER       = "#f85149"   # red    – mistake / lose
WARNING      = "#d29922"   # yellow – reveal
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED   = "#8b949e"
BORDER       = "#30363d"

FONT_TITLE   = ("Georgia", 22, "bold")
FONT_HEADING = ("Georgia", 13, "bold")
FONT_BODY    = ("Courier New", 11)
FONT_LABEL   = ("Courier New", 10)
FONT_BTN     = ("Georgia", 11, "bold")

CANVAS_W = 520
CANVAS_H = 400
CIRCLE_R = 22          # radius drawn for each difference circle


class GameUI:
    """
    Tkinter front-end for the Spot-the-Difference game.

    Person 2 owns: __init__, _build_window, _build_sidebar,
                   _build_canvas_area, show_images, update_status,
                   reset_canvas, _cv_to_tk

    Person 3 owns: _on_canvas_click, draw_found, draw_revealed,
                   set_clicks_enabled, show_win_popup,
                   show_loss_popup, show_reveal_popup, show_error
    """

    # ─────────────────────────────────────────
    #  Person 2 – display / layout
    # ─────────────────────────────────────────

    def __init__(self, root, on_load_image, on_reveal, on_image_click):
        """
        Parameters
        ----------
        root            : tk.Tk root window
        on_load_image   : callable – triggered by "Load Image" button
        on_reveal       : callable – triggered by "Reveal" button
        on_image_click  : callable(image_x, image_y) – triggered by canvas click
        """
        self.root           = root
        self._on_load_image = on_load_image
        self._on_reveal     = on_reveal
        self._on_image_click = on_image_click

        # runtime state
        self._clicks_enabled  = False
        self._orig_tk_image   = None   # keep reference so GC won't delete it
        self._mod_tk_image    = None
        self._img_offset_x    = 0      # canvas padding offset (centred image)
        self._img_offset_y    = 0
        self._img_scale       = 1.0    # scale factor applied to fit canvas

        self._build_window()
        self._build_sidebar()
        self._build_canvas_area()

    # ── window skeleton ──────────────────────

    def _build_window(self):
        self.root.title("Spot the Difference")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        # ── title bar ──
        title_bar = tk.Frame(self.root, bg=BG_DARK, pady=14)
        title_bar.pack(fill="x", padx=24)

        tk.Label(
            title_bar,
            text="🔍  SPOT THE DIFFERENCE",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK,
        ).pack(side="left")

        tk.Label(
            title_bar,
            text="find all 5 hidden changes",
            font=FONT_LABEL,
            fg=TEXT_MUTED,
            bg=BG_DARK,
        ).pack(side="left", padx=(12, 0), pady=(8, 0))

        # thin divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=24)

    # ── sidebar (status + buttons) ───────────

    def _build_sidebar(self):
        self._sidebar = tk.Frame(self.root, bg=BG_PANEL, width=200)
        self._sidebar.pack(side="right", fill="y", padx=(0, 0))
        self._sidebar.pack_propagate(False)

        inner = tk.Frame(self._sidebar, bg=BG_PANEL, padx=18, pady=20)
        inner.pack(fill="both", expand=True)

        # ── status card ──
        card = tk.Frame(inner, bg=BG_CARD, padx=14, pady=14,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 18))

        tk.Label(card, text="GAME STATUS", font=("Courier New", 9, "bold"),
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=6)

        # remaining
        rem_row = tk.Frame(card, bg=BG_CARD)
        rem_row.pack(fill="x", pady=3)
        tk.Label(rem_row, text="Remaining", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side="left")
        self._lbl_remaining = tk.Label(rem_row, text="—", font=FONT_HEADING,
                                       fg=ACCENT, bg=BG_CARD)
        self._lbl_remaining.pack(side="right")

        # mistakes
        mis_row = tk.Frame(card, bg=BG_CARD)
        mis_row.pack(fill="x", pady=3)
        tk.Label(mis_row, text="Mistakes", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side="left")
        self._lbl_mistakes = tk.Label(mis_row, text="0 / 3", font=FONT_HEADING,
                                      fg=SUCCESS, bg=BG_CARD)
        self._lbl_mistakes.pack(side="right")

        # score
        sc_row = tk.Frame(card, bg=BG_CARD)
        sc_row.pack(fill="x", pady=3)
        tk.Label(sc_row, text="Total Score", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side="left")
        self._lbl_score = tk.Label(sc_row, text="0", font=FONT_HEADING,
                                   fg=WARNING, bg=BG_CARD)
        self._lbl_score.pack(side="right")

        # ── buttons ──
        self._btn_load = self._make_button(
            inner, "📂  Load Image", ACCENT, self._on_load_image)
        self._btn_load.pack(fill="x", pady=(0, 10))

        self._btn_reveal = self._make_button(
            inner, "👁  Reveal All", WARNING, self._on_reveal)
        self._btn_reveal.pack(fill="x")

        # ── legend ──
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=18)
        tk.Label(inner, text="LEGEND", font=("Courier New", 9, "bold"),
                 fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")

        for colour, label in [(SUCCESS, "Found difference"),
                              (DANGER,  "Wrong click"),
                              (ACCENT,  "Revealed (blue)")]:
            row = tk.Frame(inner, bg=BG_PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="●", font=("Courier New", 14),
                     fg=colour, bg=BG_PANEL).pack(side="left")
            tk.Label(row, text=label, font=FONT_LABEL,
                     fg=TEXT_MUTED, bg=BG_PANEL).pack(side="left", padx=6)

        # ── hint ──
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=18)
        hint = ("Click on the RIGHT image\nto mark differences.\n\n"
                "Max 3 mistakes allowed\nbefore the round ends.")
        tk.Label(inner, text=hint, font=FONT_LABEL, fg=TEXT_MUTED,
                 bg=BG_PANEL, justify="left", wraplength=160).pack(anchor="w")

    # ── canvas area ──────────────────────────

    def _build_canvas_area(self):
        area = tk.Frame(self.root, bg=BG_DARK)
        area.pack(side="left", fill="both", expand=True, padx=20, pady=16)

        labels_row = tk.Frame(area, bg=BG_DARK)
        labels_row.pack(fill="x")

        tk.Label(labels_row, text="ORIGINAL", font=("Courier New", 9, "bold"),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(side="left",
                                                  padx=(CANVAS_W // 2 - 40, 0))
        tk.Label(labels_row, text="MODIFIED  ← click here",
                 font=("Courier New", 9, "bold"), fg=ACCENT,
                 bg=BG_DARK).pack(side="right",
                                  padx=(0, CANVAS_W // 2 - 60))

        canvases_row = tk.Frame(area, bg=BG_DARK)
        canvases_row.pack(pady=(4, 0))

        # original canvas (left)
        orig_wrap = tk.Frame(canvases_row, bg=BORDER, padx=2, pady=2)
        orig_wrap.pack(side="left", padx=(0, 10))
        self._canvas_orig = tk.Canvas(
            orig_wrap, width=CANVAS_W, height=CANVAS_H,
            bg=BG_CARD, highlightthickness=0, cursor="arrow")
        self._canvas_orig.pack()

        # modified canvas (right)
        mod_wrap = tk.Frame(canvases_row, bg=ACCENT, padx=2, pady=2)
        mod_wrap.pack(side="left")
        self._canvas_mod = tk.Canvas(
            mod_wrap, width=CANVAS_W, height=CANVAS_H,
            bg=BG_CARD, highlightthickness=0, cursor="crosshair")
        self._canvas_mod.pack()
        self._canvas_mod.bind("<Button-1>", self._on_canvas_click)

        # placeholder text on both canvases
        for canvas, msg in [
            (self._canvas_orig, "Original image\nwill appear here"),
            (self._canvas_mod,  "Modified image\nwill appear here\n\n← Load an image to begin"),
        ]:
            canvas.create_text(
                CANVAS_W // 2, CANVAS_H // 2,
                text=msg, fill=TEXT_MUTED,
                font=FONT_BODY, justify="center", tags="placeholder")

    # ── helper: styled button ─────────────────

    @staticmethod
    def _make_button(parent, text, colour, command):
        btn = tk.Button(
            parent, text=text, command=command,
            font=FONT_BTN, fg=BG_DARK, bg=colour,
            activebackground=ACCENT_HOVER, activeforeground=BG_DARK,
            relief="flat", bd=0, padx=12, pady=10, cursor="hand2")

        def on_enter(_):
            btn.configure(bg=ACCENT_HOVER)

        def on_leave(_):
            btn.configure(bg=colour)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ── public display methods ────────────────

    def show_images(self, original_cv, modified_cv):
        """
        Convert OpenCV BGR images to Tkinter PhotoImages and draw on canvases.
        Images are scaled to fit the canvas while preserving aspect ratio.
        """
        self.reset_canvas()

        orig_tk, scale, off_x, off_y = self._cv_to_tk(original_cv)
        mod_tk,  _,     _,     _     = self._cv_to_tk(modified_cv)

        # remember for coordinate conversion
        self._img_scale    = scale
        self._img_offset_x = off_x
        self._img_offset_y = off_y

        # keep references (prevents garbage collection)
        self._orig_tk_image = orig_tk
        self._mod_tk_image  = mod_tk

        self._canvas_orig.create_image(off_x, off_y, anchor="nw",
                                       image=orig_tk, tags="image")
        self._canvas_mod.create_image(off_x, off_y, anchor="nw",
                                      image=mod_tk,  tags="image")

    def update_status(self, remaining, mistakes, max_mistakes, score):
        """Refresh all status labels in the sidebar."""
        self._lbl_remaining.config(text=str(remaining) if remaining >= 0 else "—")
        self._lbl_mistakes.config(
            text=f"{mistakes} / {max_mistakes}",
            fg=DANGER if mistakes >= max_mistakes else
               WARNING if mistakes > 0 else SUCCESS)
        self._lbl_score.config(text=str(score))

    def reset_canvas(self):
        """Clear both canvases completely (called before loading a new image)."""
        self._canvas_orig.delete("all")
        self._canvas_mod.delete("all")
        self._img_offset_x = 0
        self._img_offset_y = 0
        self._img_scale    = 1.0

    # ── internal helper ───────────────────────

    def _cv_to_tk(self, cv_image):
        """
        Convert an OpenCV BGR image → Tkinter PhotoImage, scaled to fit the canvas.
        Returns (PhotoImage, scale_factor, offset_x, offset_y).
        """
        h, w = cv_image.shape[:2]
        scale = min(CANVAS_W / w, CANVAS_H / h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(cv_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        rgb     = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        tk_img  = ImageTk.PhotoImage(pil_img)

        off_x = (CANVAS_W - new_w) // 2
        off_y = (CANVAS_H - new_h) // 2
        return tk_img, scale, off_x, off_y

    # ─────────────────────────────────────────
    #  Person 3 – interaction / popups
    # ─────────────────────────────────────────

    def _on_canvas_click(self, event):
        """
        Translate canvas pixel → original image coordinates, then fire the
        game callback.  Ignores clicks when disabled or outside the image.
        """
        if not self._clicks_enabled:
            return

        # convert canvas coords → image coords
        img_x = (event.x - self._img_offset_x) / self._img_scale
        img_y = (event.y - self._img_offset_y) / self._img_scale

        if img_x < 0 or img_y < 0:
            return

        self._on_image_click(int(img_x), int(img_y))

    def _draw_circle(self, region, colour):
        """
        Draw a circle on BOTH canvases centred on the difference region.
        Coordinates are converted from image space → canvas space.
        """
        cx, cy = region.center()
        r      = region.radius()

        # scale & offset  →  canvas coordinates
        canvas_cx = cx * self._img_scale + self._img_offset_x
        canvas_cy = cy * self._img_scale + self._img_offset_y
        canvas_r  = r  * self._img_scale

        for canvas in (self._canvas_orig, self._canvas_mod):
            canvas.create_oval(
                canvas_cx - canvas_r, canvas_cy - canvas_r,
                canvas_cx + canvas_r, canvas_cy + canvas_r,
                outline=colour, width=3)

    def draw_found(self, region):
        """Draw a red circle on both canvases for a correctly found difference."""
        self._draw_circle(region, SUCCESS)

    def draw_revealed(self, regions):
        """Draw blue circles on both canvases for all unrevealed differences."""
        for region in regions:
            self._draw_circle(region, ACCENT)

    def set_clicks_enabled(self, enabled: bool):
        """Enable or disable player clicks on the modified canvas."""
        self._clicks_enabled = enabled
        self._canvas_mod.config(
            cursor="crosshair" if enabled else "arrow")

    # ── popup dialogs ─────────────────────────

    def show_win_popup(self):
        self._popup(
            title="🎉  You Won!",
            message="Brilliant! You found all 5 differences.\n\nLoad another image to keep playing.",
            colour=SUCCESS,
        )

    def show_loss_popup(self, found, total):
        self._popup(
            title="💥  Too Many Mistakes",
            message=(f"You made 3 mistakes and the round is over.\n\n"
                     f"You found {found} out of {total} differences.\n\n"
                     f"Load a new image to try again."),
            colour=DANGER,
        )

    def show_reveal_popup(self):
        self._popup(
            title="👁  Differences Revealed",
            message="All hidden differences have been marked in blue.\n\nLoad a new image to play again.",
            colour=ACCENT,
        )

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    # ── custom popup window ───────────────────

    def _popup(self, title, message, colour):
        """Render a styled modal popup dialog."""
        win = tk.Toplevel(self.root)
        win.title("")
        win.configure(bg=BG_PANEL)
        win.resizable(False, False)
        win.grab_set()          # modal

        # centre over root
        self.root.update_idletasks()
        rx = self.root.winfo_x() + self.root.winfo_width()  // 2
        ry = self.root.winfo_y() + self.root.winfo_height() // 2
        win.geometry(f"360x220+{rx - 180}+{ry - 110}")

        # accent strip at top
        tk.Frame(win, bg=colour, height=5).pack(fill="x")

        body = tk.Frame(win, bg=BG_PANEL, padx=28, pady=22)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=title, font=FONT_HEADING,
                 fg=colour, bg=BG_PANEL).pack(anchor="w")

        tk.Label(body, text=message, font=FONT_LABEL,
                 fg=TEXT_PRIMARY, bg=BG_PANEL,
                 justify="left", wraplength=300).pack(anchor="w", pady=(10, 18))

        close_btn = tk.Button(
            body, text="OK", command=win.destroy,
            font=FONT_BTN, fg=BG_DARK, bg=colour,
            relief="flat", bd=0, padx=20, pady=6, cursor="hand2")
        close_btn.pack(anchor="e")
