package com.slime.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** Derinlikli buton: hover'da 2px kalkar, tıklamada step atar (kural 5). */
public class DepthButton extends Button {
    static final OnPress NOOP = b -> {};

    private final boolean primary;
    private final boolean pill;
    private double hoverT = 0;
    private long pressAt = Long.MIN_VALUE;

    public DepthButton(int x, int y, int w, int h, Component msg, OnPress p, boolean primary, boolean pill) {
        super(x, y, w, h, msg, p, DEFAULT_NARRATION);
        this.primary = primary;
        this.pill = pill;
    }

    static DepthButton solid(Component m, int x, int y, int w, int h, OnPress p) {
        return new DepthButton(x, y, w, h, m, p, true, false);
    }
    static DepthButton pill(Component m, int x, int y, int w, int h, OnPress p) {
        return new DepthButton(x, y, w, h, m, p, false, true);
    }

    @Override
    public void onClick(double mx, double my) {
        pressAt = System.currentTimeMillis();
        super.onClick(mx, my);
    }

    @Override
    protected void renderWidget(GuiGraphics g, int mx, int my, float d) {
        Font font = Minecraft.getInstance().font;
        hoverT = SlimeMotion.approach(hoverT, isHovered() ? 1 : 0, d, SlimeTheme.HOVER_MS);
        double pr = SlimeMotion.clamp01((System.currentTimeMillis() - pressAt) / (double) SlimeTheme.PRESS_MS);
        double curve = Math.sin(pr * Math.PI);
        int lift = (int) Math.round(-2 * hoverT + 1.5 * curve);
        int depth = Math.max(0, (int) Math.round(SlimeTheme.DEPTH_CARD - 2 * curve));
        int face = primary ? SlimeTheme.ACCENT : SlimeTheme.SURFACE_2;
        int side = primary ? SlimeTheme.ACCENT_DK : 0xFF0F1418;
        int r = pill ? getHeight() / 2 : SlimeTheme.RADIUS;
        DepthPanel.panel(g, getX(), getY() + lift, getWidth(), getHeight(), r, depth, face, side, hoverT);
        int col = primary ? 0xFF06210A : (isHovered() ? SlimeTheme.INK : SlimeTheme.MUTED);
        g.drawCenteredString(font, this.getMessage(),
                this.getX() + this.getWidth() / 2, this.getY() + (this.getHeight() - 9) / 2 + lift, col);
        if (this.isFocused()) DepthPanel.focusRing(g, getX() - 2, getY() + lift - 2, getWidth() + 4, getHeight() + 4);
    }
}

/** Sekme butonu: underline hover/seçili'de 0->tam genişlik çizilir (kural 5). */
class TabButton extends Button {
    private double drawT = 0;
    private final boolean[] selected;

    TabButton(int x, int y, int w, Component msg, boolean[] selected, OnPress p) {
        super(x, y, w, 18, msg, p, DEFAULT_NARRATION);
        this.selected = selected;
    }

    @Override
    protected void renderWidget(GuiGraphics g, int mx, int my, float d) {
        Font font = Minecraft.getInstance().font;
        boolean on = active && selected[0];
        double target = (on || isHovered()) ? 1 : 0;
        drawT = SlimeMotion.approach(drawT, target, d, 200);
        int col = on ? SlimeTheme.ACCENT : (isHovered() ? SlimeTheme.INK : SlimeTheme.MUTED);
        g.drawString(font, this.getMessage(), getX() + (getWidth() - font.width(this.getMessage())) / 2,
                getY() + 4, col, true);
        int uw = (int) Math.round(getWidth() * drawT);
        g.fill(getX() + (getWidth() - uw) / 2, getY() + getHeight() - 2,
                getX() + (getWidth() - uw) / 2 + uw, getY() + getHeight(),
                SlimeTheme.withAlpha(on ? SlimeTheme.ACCENT : SlimeTheme.INK, 0.85));
    }
}

/** Aç/kapa kartı: config'i yazar, state noktası + hover lift. */
class ToggleCard extends DepthButton {
    private final String label;
    private final Runnable toggle;
    private final java.util.function.BooleanSupplier state;

    ToggleCard(String label, int x, int y, int w, Runnable toggle, java.util.function.BooleanSupplier state) {
        super(x, y, w, 24, Component.literal(label), b -> { toggle.run(); }, false, false);
        this.label = label;
        this.toggle = toggle;
        this.state = state;
    }

    @Override
    public void onClick(double mx, double my) {
        super.onClick(mx, my);
        toggle.run();
        SlimeConfig.get().save();
    }

    @Override
    protected void renderWidget(GuiGraphics g, int mx, int my, float d) {
        super.renderWidget(g, mx, my, d);
        Font font = Minecraft.getInstance().font;
        boolean on = state.getAsBoolean();
        int cx = getX() + getWidth() - 14, cy = getY() + getHeight() / 2 - 2;
        DepthPanel.roundRect(g, cx - 8, cy - 4, 16, 8, 4, on ? SlimeTheme.ACCENT_DK : 0xFF3A4048);
        DepthPanel.roundRect(g, on ? cx : cx - 6, cy - 3, 6, 6, 3, on ? SlimeTheme.ACCENT : SlimeTheme.MUTED);
        g.drawString(font, Component.literal(label), getX() + 10, getY() + (getHeight() - 9) / 2,
                SlimeTheme.INK, true);
    }
}

/** HUD ölçek kartı: - / + step butonları. */
class ScaleCard extends DepthButton {
    ScaleCard(int x, int y, int w) {
        super(x, y, w, 24, Component.literal("HUD Ölçeği"), b -> {}, false, false);
        addSubButtons(x, y, w);
    }
    private void addSubButtons(int x, int y, int w) {
        // Alt butonlar ebeveyn Screen tarafından eklenir (initTab içinde) - burada sadece render.
    }
    @Override
    protected void renderWidget(GuiGraphics g, int mx, int my, float d) {
        super.renderWidget(g, mx, my, d);
        Font font = Minecraft.getInstance().font;
        String scaleText = String.format("%.1fx", SlimeConfig.get().hudScale);
        g.drawString(font, Component.literal(scaleText),
                getX() + getWidth() - 10 - font.width(scaleText),
                getY() + (getHeight() - 9) / 2, SlimeTheme.ACCENT, true);
    }
}

/** Gerçek item ikonlu kart: loop 3 s nabız + hover zoom 1.02-1.03 (kural 5/7). Caption YOK (kural 1). */
class IconCard {
    final ItemStack icon;
    final Component label;
    final int x, y, w, h;
    private double hoverT = 0;

    IconCard(ItemStack icon, Component label, int x, int y, int w, int h) {
        this.icon = icon; this.label = label; this.x = x; this.y = y; this.w = w; this.h = h;
    }

    boolean hovered(int mx, int my) { return mx >= x && mx < x + w && my >= y && my < y + h; }

    void render(GuiGraphics g, int mx, int my, float d, long now) {
        Font font = Minecraft.getInstance().font;
        hoverT = SlimeMotion.approach(hoverT, hovered(mx, my) ? 1 : 0, d, SlimeTheme.HOVER_MS);
        double pulse = SlimeMotion.loop(now, SlimeTheme.LOOP_S);
        double zoom = 1.0 + 0.02 * hoverT + 0.01 * pulse;
        int lift = (int) Math.round(-2 * hoverT);
        DepthPanel.panel(g, x, y + lift, w, h, SlimeTheme.RADIUS, SlimeTheme.DEPTH_CARD,
                SlimeTheme.SURFACE, 0xFF0F1418, hoverT);
        g.pose().pushPose();
        g.pose().translate(x + w / 2f, y + h / 2f - 4, 0);
        g.pose().scale((float) zoom, (float) zoom, 1f);
        g.renderItem(icon, -8, -8);
        g.pose().popPose();
        g.drawCenteredString(font, label, x + w / 2, y + h - 14,
                hoverT > 0.5 ? SlimeTheme.INK : SlimeTheme.MUTED);
    }
}

/** Referans fotoğrafların GUI karşılığı: düz köy <-> çöl köyü bölüm anı (photo-chapters). */
class VillageChapter {
    private static final ItemStack[] PLAINS = {
            stack(net.minecraft.world.level.block.Blocks.OAK_LOG), stack(net.minecraft.world.level.block.Blocks.HAY_BLOCK),
            stack(net.minecraft.world.level.block.Blocks.OAK_PLANKS), stack(net.minecraft.world.level.block.Blocks.COBBLESTONE),
            stack(net.minecraft.world.level.block.Blocks.GRASS_BLOCK), stack(net.minecraft.world.item.Items.LANTERN),
            stack(net.minecraft.world.item.Items.WHEAT), stack(net.minecraft.world.level.block.Blocks.WATER),
            stack(net.minecraft.world.item.Items.POPPY), stack(net.minecraft.world.item.Items.DANDELION),
            stack(net.minecraft.world.level.block.Blocks.OAK_FENCE) };
    private static final ItemStack[] DESERT = {
            stack(net.minecraft.world.level.block.Blocks.SAND), stack(net.minecraft.world.level.block.Blocks.SANDSTONE),
            stack(net.minecraft.world.level.block.Blocks.CACTUS), stack(net.minecraft.world.level.block.Blocks.HAY_BLOCK),
            stack(net.minecraft.world.item.Items.DEAD_BUSH), stack(net.minecraft.world.item.Items.WHEAT),
            stack(net.minecraft.world.level.block.Blocks.SANDSTONE), stack(net.minecraft.world.level.block.Blocks.SAND) };
    private static final int COLS = 7, ROWS = 3;
    private long start = System.currentTimeMillis();
    private boolean wasHover = false;

    private static ItemStack stack(net.minecraft.world.level.block.Block b) { return new ItemStack(b); }
    private static ItemStack stack(net.minecraft.world.item.Item i) { return new ItemStack(i); }

    void render(GuiGraphics g, int x, int y, int w, int h, int mx, int my, float d) {
        long now = System.currentTimeMillis();
        boolean hov = mx >= x && mx < x + w && my >= y && my < y + h;
        if (hov && !wasHover) start = now;          // hover'da loop restart (kural 5)
        wasHover = hov;
        double t = SlimeMotion.clamp01((now - start) / (double) SlimeTheme.CHAPTER_MS);
        double slide;
        if (t < 0.35) slide = 0;
        else if (t < 0.5) slide = (t - 0.35) / 0.15;
        else if (t < 0.85) slide = 1;
        else slide = 1 - (t - 0.85) / 0.15;
        if (SlimeConfig.get().motionReduced) slide = 0;
        float s = 2.5f;
        int iw = (int) (COLS * 16 * s), ih = (int) (ROWS * 16 * s);
        int cx = x + (w - iw) / 2, cy = y + (h - ih) / 2;
        DepthPanel.panel(g, x, y, w, h, SlimeTheme.RADIUS, SlimeTheme.DEPTH_PANEL,
                SlimeTheme.SURFACE, 0xFF0F1418, 0.2);
        g.enableScissor(x + 2, y + 2, x + w - 2, y + h - 2);
        drawScene(g, PLAINS, (int) (cx - slide * (iw + 24)), cy, s);
        drawScene(g, DESERT, (int) (cx + (1 - slide) * (iw + 24)), cy, s);
        g.disableScissor();
    }

    private void drawScene(GuiGraphics g, ItemStack[] tiles, int ox, int oy, float s) {
        int idx = 0;
        for (int row = 0; row < ROWS; row++) {
            for (int col = 0; col < COLS; col++) {
                ItemStack st = tiles[idx % tiles.length];
                idx++;
                g.pose().pushPose();
                g.pose().translate(ox + col * 16f * s, oy + row * 16f * s, 0);
                g.pose().scale(s, s, 1f);
                g.renderItem(st, 0, 0);
                g.pose().popPose();
            }
        }
    }
}
