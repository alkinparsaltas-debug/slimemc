# -*- coding: utf-8 -*-
"""Slime Client için ortak modern arayüz bileşenleri (saf Tkinter, ek paket gerektirmez)."""
import tkinter as tk

# ---- Renk paleti ---------------------------------------------------------
BG = "#0A0F0C"          # ana arka plan
SIDEBAR = "#0E1511"     # sol menü
CARD = "#131B16"        # kartlar
CARD_HI = "#18221C"     # kart üstü / hover
BORDER = "#203027"      # ince çizgiler
ACCENT = "#22C55E"      # ana yeşil
ACCENT_HI = "#4ADE80"   # hover yeşil
ACCENT_DK = "#15803D"   # koyu yeşil
TEXT = "#E8F5EC"
MUTED = "#7F9A89"
DIM = "#4F6658"
DANGER = "#F87171"

FONT = "Segoe UI"


def lerp_color(c1: str, c2: str, t: float) -> str:
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    r = [int(a[i] + (b[i] - a[i]) * t) for i in range(3)]
    return "#%02x%02x%02x" % tuple(r)


def rrect(c: tk.Canvas, x1, y1, x2, y2, r, **kw):
    """Yuvarlatılmış köşeli dikdörtgen çizer."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return c.create_polygon(pts, smooth=True, **kw)


# ---- Buton ---------------------------------------------------------------
class RButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=40, radius=12,
                 bg=ACCENT, hover=ACCENT_HI, fg="#04130A", parent_bg=BG,
                 font=(FONT, 10, "bold"), outline=None):
        super().__init__(parent, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self._text = text
        self._cmd = command
        self._radius = radius
        self._base = bg
        self._hover = hover
        self._fg = fg
        self._font = font
        self._outline = outline
        self._cur = bg
        self._enabled = True
        self._anim = None
        self._pressed = False
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._fade(self._hover))
        self.bind("<Leave>", lambda e: self._fade(self._base))
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            w, h = int(self["width"]), int(self["height"])
        off = 1 if self._pressed else 0
        rrect(self, 1, 1 + off, w - 1, h - 1, self._radius, fill=self._cur,
              outline=self._outline or "")
        self.create_text(w / 2, h / 2 + off, text=self._text, fill=self._fg, font=self._font)

    def _fade(self, target, steps=6):
        if not self._enabled:
            return
        if self._anim:
            self.after_cancel(self._anim)
        start = self._cur

        def step(i=1):
            self._cur = lerp_color(start, target, i / steps)
            self._draw()
            if i < steps:
                self._anim = self.after(16, lambda: step(i + 1))
            else:
                self._anim = None
        step()

    def _press(self, _e):
        if self._enabled:
            self._pressed = True
            self._draw()

    def _release(self, e):
        if not self._enabled:
            return
        self._pressed = False
        self._draw()
        if 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height() and self._cmd:
            self._cmd()

    def configure_button(self, text=None, bg=None, hover=None, fg=None, enabled=None):
        if text is not None:
            self._text = text
        if bg is not None:
            self._base = bg
            self._cur = bg
        if hover is not None:
            self._hover = hover
        if fg is not None:
            self._fg = fg
        if enabled is not None:
            self._enabled = enabled
            self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()


# ---- Kart ----------------------------------------------------------------
class Card(tk.Canvas):
    """Yuvarlak köşeli kart. İçeriği `card.inner` içine yerleştir."""

    def __init__(self, parent, parent_bg=BG, fill=CARD, outline=BORDER, radius=16, pad=18):
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, height=40)
        self._fill = fill
        self._outline = outline
        self._radius = radius
        self._pad = pad
        self.inner = tk.Frame(self, bg=fill)
        self._win = self.create_window(pad, pad, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._on_resize)
        self.inner.bind("<Configure>", self._on_inner)

    def set_outline(self, color):
        self._outline = color
        self._redraw()

    def _on_inner(self, _e):
        want = self.inner.winfo_reqheight() + self._pad * 2
        if int(self.cget("height")) != want:
            self.configure(height=want)

    def _on_resize(self, e):
        self.itemconfigure(self._win, width=max(10, e.width - self._pad * 2))
        self._redraw()

    def _redraw(self):
        self.delete("bg")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10 or h < 10:
            return
        rrect(self, 1, 1, w - 1, h - 1, self._radius, fill=self._fill,
              outline=self._outline, tags="bg")
        self.tag_lower("bg")


# ---- Aç/Kapa anahtarı ----------------------------------------------------
class Toggle(tk.Canvas):
    def __init__(self, parent, variable: tk.BooleanVar, parent_bg=CARD, command=None):
        super().__init__(parent, width=46, height=26, bg=parent_bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.var = variable
        self._cmd = command
        self.bind("<Button-1>", self._toggle)
        self.var.trace_add("write", lambda *a: self._draw())
        self._draw()

    def _toggle(self, _e=None):
        self.var.set(not self.var.get())
        if self._cmd:
            self._cmd()

    def _draw(self):
        self.delete("all")
        on = self.var.get()
        rrect(self, 1, 1, 45, 25, 12, fill=ACCENT if on else "#26332B", outline="")
        x = 33 if on else 13
        self.create_oval(x - 9, 4, x + 9, 22, fill="#FFFFFF" if on else "#8DA396", outline="")


# ---- İlerleme çubuğu -----------------------------------------------------
class ProgressBar(tk.Canvas):
    def __init__(self, parent, width=320, height=8, parent_bg=BG):
        super().__init__(parent, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, bd=0)
        self._pct = 0.0
        self.bind("<Configure>", lambda e: self._draw())
        self._draw()

    def set(self, pct: float):
        self._pct = max(0.0, min(100.0, pct))
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            w, h = int(self["width"]), int(self["height"])
        rrect(self, 0, 0, w, h, h / 2, fill="#16211B", outline="")
        fw = int(w * self._pct / 100.0)
        if fw > h:
            rrect(self, 0, 0, fw, h, h / 2, fill=ACCENT, outline="")
        elif fw > 0:
            self.create_oval(0, 0, h, h, fill=ACCENT, outline="")


# ---- Sol menü satırı -----------------------------------------------------
class NavItem(tk.Canvas):
    def __init__(self, parent, icon, text, command, parent_bg=SIDEBAR):
        super().__init__(parent, height=44, bg=parent_bg, highlightthickness=0,
                         bd=0, cursor="hand2")
        self._icon, self._text, self._cmd = icon, text, command
        self._parent_bg = parent_bg
        self._active = False
        self._hover = False
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<Button-1>", lambda e: self._cmd())

    def set_active(self, v: bool):
        self._active = v
        self._draw()

    def _set_hover(self, v):
        self._hover = v
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10:
            return
        if self._active:
            rrect(self, 0, 2, w, h - 2, 12, fill="#143322", outline="")
            rrect(self, 0, 12, 4, h - 12, 2, fill=ACCENT, outline="")
        elif self._hover:
            rrect(self, 0, 2, w, h - 2, 12, fill="#121C16", outline="")
        col = ACCENT_HI if self._active else (TEXT if self._hover else MUTED)
        self.create_text(22, h / 2, text=self._icon, fill=col, font=(FONT, 12), anchor="w")
        self.create_text(52, h / 2, text=self._text, fill=col,
                         font=(FONT, 10, "bold" if self._active else "normal"), anchor="w")


# ---- Slime küpü çizimi ---------------------------------------------------
def draw_slime(c: tk.Canvas, cx, cy, size, squash=1.0, tag="slime"):
    """cx,cy: taban orta noktası. squash<1 basık, >1 uzamış."""
    w = size * (2 - squash)
    h = size * squash
    x1, x2 = cx - w / 2, cx + w / 2
    y2, y1 = cy, cy - h
    rr = size * 0.22
    # gölge
    sw = w * 0.9
    c.create_oval(cx - sw / 2, cy + 4, cx + sw / 2, cy + 14, fill="#0C1C13", outline="", tags=tag)
    # dış gövde
    rrect(c, x1, y1, x2, y2, rr, fill="#22C55E", outline="#4ADE80", width=2, tags=tag)
    # iç çekirdek
    m = size * 0.16
    rrect(c, x1 + m, y1 + m, x2 - m, y2 - m, rr * 0.6, fill="#16A34A", outline="", tags=tag)
    # parlama
    c.create_oval(x1 + w * 0.12, y1 + h * 0.10, x1 + w * 0.26, y1 + h * 0.20,
                  fill="#BBF7D0", outline="", tags=tag)
    # gözler + ağız
    ey = y1 + h * 0.42
    es = size * 0.11
    for ex in (cx - w * 0.19, cx + w * 0.19):
        c.create_rectangle(ex - es, ey - es * 1.2, ex + es, ey + es * 1.2,
                           fill="#052E16", outline="", tags=tag)
    c.create_rectangle(cx - es * 0.9, ey + h * 0.22, cx + es * 0.9, ey + h * 0.22 + es * 0.9,
                       fill="#052E16", outline="", tags=tag)
