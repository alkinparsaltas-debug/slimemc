package com.slime.client;

/** Tasarım tokenları. kind=gaming -> dark-band + palet referans fotoğraflardan. Mor YOK (kural 6). */
public final class SlimeTheme {
    private SlimeTheme() {}

    public static final int BG        = 0xFF0E1114;
    public static final int BG_SOFT   = 0xFF151A1F;
    public static final int SURFACE   = 0xFF1D242B;
    public static final int SURFACE_2 = 0xFF242C35;

    public static final int ACCENT    = 0xFF55FF55; // mevcut HUD markası
    public static final int ACCENT_DK = 0xFF2F8F2F;
    public static final int HAY       = 0xFFD9A648; // foto: saman balyası
    public static final int WOOD      = 0xFF9C7F4E; // foto: meşe ev
    public static final int COBBLE    = 0xFF7D7D7D; // foto: temel taşı
    public static final int SAND      = 0xFFDBD3A0; // foto: çöl köyü
    public static final int CACTUS    = 0xFF3FA03F;
    public static final int WATER     = 0xFF3F76E4;

    public static final int INK       = 0xFFF2F5F2;
    public static final int MUTED     = 0xFF9AA6A0;
    public static final int SHADOW    = 0x59000000;

    public static final int RADIUS = 4;            // soft radius
    public static final int DEPTH_CARD = 3;        // 3D dışa-vurum derinliği
    public static final int DEPTH_PANEL = 4;

    public static final int ENTER_MS = 320;
    public static final int HOVER_MS = 120;
    public static final int PRESS_MS = 90;
    public static final int LOOP_S = 3;            // kart loop 2.5-4 s -> 3 s
    public static final int CHAPTER_MS = 3400;     // köy bölüm döngüsü

    public static int withAlpha(int argb, double a) {
        int al = (int) Math.round(((argb >>> 24) & 0xFF) * Math.max(0.0, Math.min(1.0, a)));
        return (al << 24) | (argb & 0x00FFFFFF);
    }
}
