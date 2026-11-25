package com.slime.client;

import net.minecraft.client.gui.GuiGraphics;

/** 3D panel: katmanlı gölge + dışa-vurum (extrusion) + yüz + bevel. Tilt YOK (kural 5). */
public final class DepthPanel {
    private DepthPanel() {}

    public static void roundRect(GuiGraphics g, int x, int y, int w, int h, int r, int argb) {
        if (w <= 0 || h <= 0) return;
        r = Math.max(0, Math.min(r, Math.min(w / 2, h / 2)));
        int x2 = x + w, y2 = y + h;
        for (int row = y; row < y2; row++) {
            int dt = row - y, db = y2 - 1 - row;
            int inset = 0;
            if (dt < r) inset = r - (int) Math.sqrt(Math.max(0.0, (double) (r * r - (r - dt) * (r - dt))));
            else if (db < r) inset = r - (int) Math.sqrt(Math.max(0.0, (double) (r * r - (r - db) * (r - db))));
            g.fill(x + inset, row, x2 - inset, row + 1, argb);
        }
    }

    public static void outline(GuiGraphics g, int x, int y, int w, int h, int t, int argb) {
        g.fill(x, y, x + w, y + t, argb);
        g.fill(x, y + h - t, x + w, y + h, argb);
        g.fill(x, y + t, x + t, y + h - t, argb);
        g.fill(x + w - t, y + t, x + w, y + h - t, argb);
    }

    public static void focusRing(GuiGraphics g, int x, int y, int w, int h) {
        outline(g, x, y, w, h, 1, SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.9));
    }

    /** lift 0..1 -> gölge büyür ve yumuşar (hover'da kart 2px kalkar). */
    public static void shadow(GuiGraphics g, int x, int y, int w, int h, int r, double lift) {
        int layers = 3 + (int) Math.round(lift * 2);
        for (int i = layers; i >= 1; i--) {
            int off = i + (int) Math.round(lift * i);
            int a = (int) (22 + 10 * lift) * (layers - i + 1) / layers;
            roundRect(g, x - off + 2, y - off + 3, w + off * 2, h + off * 2, r + off,
                    SlimeTheme.withAlpha(SlimeTheme.SHADOW, a / 60.0));
        }
    }

    /** depth>0 -> alt/sağ kenar görünür = 3D kalınlık hissi. */
    public static void panel(GuiGraphics g, int x, int y, int w, int h, int r,
                             int depth, int face, int side, double lift) {
        shadow(g, x, y, w, h, r, lift);
        if (depth > 0) roundRect(g, x + 1, y + depth, w, h, r, side);   // alt kenar
        roundRect(g, x, y, w, h, r, face);                              // ön yüz
        g.fill(x + r, y, x + w - r, y + 1,
                SlimeTheme.withAlpha(0xFFFFFFFF, 0.10));                // üst bevel
        g.fill(x, y + r, x + 1, y + h - r,
                SlimeTheme.withAlpha(0xFFFFFFFF, 0.05));                // sol bevel
    }
}
