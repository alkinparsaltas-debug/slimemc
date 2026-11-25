package com.slime.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;

import java.util.ArrayList;
import java.util.List;

/** kind=gaming: hero ilk ekranda yalnız, her sekme = bir ekran, equal edges, tek footer kredisi. */
public class SlimeMenuScreen extends Screen {
    private enum Tab { HERO, VILLAGES, HUD, ABOUT }
    private Tab tab = Tab.HERO;
    private final boolean[] sel = new boolean[1];
    private final VillageChapter chapter = new VillageChapter();
    private final List<IconCard> icons = new ArrayList<>();
    private long heroBorn = 0;
    private static boolean heroEnteredOnce = false;
    private int wrapX, wrapW;

    public SlimeMenuScreen() {
        super(Component.empty());
    }

    @Override
    protected void init() {
        wrapW = Math.min(560, this.width - 48);
        wrapX = (this.width - wrapW) / 2;
        this.clearWidgets();
        List<AbstractWidget> ws = new ArrayList<>();

        // nav-centre (gaming deal): hero ekranında sekme yok (kural 3: hero alone)
        if (tab != Tab.HERO) {
            TabButton t1 = new TabButton(wrapX + wrapW / 2 - 120, 18, 80, Component.literal("Köyler"), sel, b -> go(Tab.VILLAGES));
            TabButton t2 = new TabButton(wrapX + wrapW / 2 - 20, 18, 60, Component.literal("HUD"), sel, b -> go(Tab.HUD));
            TabButton t3 = new TabButton(wrapX + wrapW / 2 + 60, 18, 60, Component.literal("Hakkında"), sel, b -> go(Tab.ABOUT));
            sel[0] = true;
            ws.add(t1); ws.add(t2); ws.add(t3);
        }

        int top = 56;
        switch (tab) {
            case HERO -> {
                ws.add(DepthButton.solid(Component.literal("Oyuna Dön"),
                        wrapX + wrapW / 2 - 90, top + 96, 180, 22, b -> this.onClose()));
                ws.add(DepthButton.pill(Component.literal("Köyleri Keşfet"),
                        wrapX + wrapW / 2 - 70, top + 124, 140, 22, b -> go(Tab.VILLAGES)));
            }
            case VILLAGES -> {
                icons.clear();
                icons.add(new IconCard(new ItemStack(Blocks.OAK_PLANKS), Component.literal("Meşe"), wrapX, top + 150, 84, 56));
                icons.add(new IconCard(new ItemStack(Blocks.COBBLESTONE), Component.literal("Yonu Taşı"), wrapX + 94, top + 150, 84, 56));
                icons.add(new IconCard(new ItemStack(Blocks.HAY_BLOCK), Component.literal("Saman"), wrapX + 188, top + 150, 84, 56));
                icons.add(new IconCard(new ItemStack(Blocks.SANDSTONE), Component.literal("Kumtaşı"), wrapX + 282, top + 150, 84, 56));
                icons.add(new IconCard(new ItemStack(Blocks.CACTUS), Component.literal("Kaktüs"), wrapX + 376, top + 150, 84, 56));
                icons.add(new IconCard(new ItemStack(Blocks.WATER), Component.literal("Su"), wrapX + 470, top + 150, 84, 56));
            }
            case HUD -> {
                SlimeConfig c = SlimeConfig.get();
                ws.add(new ToggleCard("HUD Açık", wrapX, top, wrapW, () -> c.hudEnabled = !c.hudEnabled, () -> c.hudEnabled));
                ws.add(new ToggleCard("FPS", wrapX, top + 30, wrapW, () -> c.hudFps = !c.hudFps, () -> c.hudFps));
                ws.add(new ToggleCard("CPS", wrapX, top + 60, wrapW, () -> c.hudCps = !c.hudCps, () -> c.hudCps));
                ws.add(new ToggleCard("Koordinatlar", wrapX, top + 90, wrapW, () -> c.hudCoords = !c.hudCoords, () -> c.hudCoords));
                ws.add(new ToggleCard("Azaltılmış Hareket", wrapX, top + 120, wrapW, () -> c.motionReduced = !c.motionReduced, () -> c.motionReduced));
                ScaleCard sc = new ScaleCard(wrapX, top + 150, wrapW);
                ws.add(sc);
                ws.add(DepthButton.pill(Component.literal("−"), wrapX + wrapW - 96, top + 152, 28, 20,
                        b -> { c.hudScale = Math.max(0.8, c.hudScale - 0.1); c.save(); }));
                ws.add(DepthButton.pill(Component.literal("+"), wrapX + wrapW - 62, top + 152, 28, 20,
                        b -> { c.hudScale = Math.min(1.4, c.hudScale + 0.1); c.save(); }));
            }
            case ABOUT -> {
                icons.clear();
                icons.add(new IconCard(new ItemStack(Items.CLOCK), Component.literal("FPS"), wrapX, top + 120, 84, 56));
                icons.add(new IconCard(new ItemStack(Items.IRON_SWORD), Component.literal("CPS"), wrapX + 94, top + 120, 84, 56));
                icons.add(new IconCard(new ItemStack(Items.COMPASS), Component.literal("XYZ"), wrapX + 188, top + 120, 84, 56));
                icons.add(new IconCard(new ItemStack(Blocks.SLIME_BLOCK), Component.literal("Slime"), wrapX + 282, top + 120, 84, 56));
            }
        }
        ws.add(DepthButton.pill(Component.literal("Kapat"), wrapX + wrapW - 70, this.height - 34, 70, 20, b -> this.onClose()));
        for (AbstractWidget w : ws) this.addRenderableWidget(w);
    }

    private void go(Tab t) { this.tab = t; this.init(); }

    @Override
    public void render(GuiGraphics g, int mx, int my, float d) {
        long now = System.currentTimeMillis();
        if (heroBorn == 0) heroBorn = now;
        // dark-band zemin (gaming deal)
        g.fill(0, 0, this.width, this.height, SlimeTheme.BG);
        for (int i = 0; i < 120; i++) {
            g.fill(0, i, this.width, i + 1, SlimeTheme.withAlpha(SlimeTheme.BG_SOFT, (120 - i) / 240.0));
        }
        if (tab == Tab.HERO) renderHero(g, now);
        else {
            heading(g, switch (tab) {
                case VILLAGES -> "Köyler";
                case HUD -> "HUD Ayarları";
                default -> "Hakkında";
            });
            if (tab == Tab.VILLAGES) chapter.render(g, wrapX, 56, wrapW, 130, mx, my, d);
            if (tab == Tab.ABOUT) renderAbout(g, now);
            for (IconCard ic : icons) ic.render(g, mx, my, d, now);
        }
        super.render(g, mx, my, d);
        // tek footer kredi satırı (kural 1)
        g.drawCenteredString(this.font, Component.literal("Doku ve ikonlar: Minecraft vanilla • Slime Client © 2026"),
                this.width / 2, this.height - 12, SlimeTheme.MUTED);
    }

    private void heading(GuiGraphics g, String s) {
        g.drawString(this.font, Component.literal(s), wrapX, 40, SlimeTheme.ACCENT, true);
    }

    private void renderHero(GuiGraphics g, long now) {
        double e = heroEnteredOnce ? 1 : SlimeMotion.enter(now - heroBorn);
        if (e >= 1) heroEnteredOnce = true;
        int dy = (int) Math.round((1 - e) * 12);
        int a = (int) Math.round(e * 255);
        g.pose().pushPose();
        g.pose().translate(0, dy, 0);
        g.drawCenteredString(this.font, Component.literal("Slime Client 26.2"),
                this.width / 2, 96, SlimeTheme.withAlpha(SlimeTheme.INK, e));
        g.drawCenteredString(this.font, Component.literal("Özel istemci • Fabric 26.2 • FPS, CPS ve koordinat HUD'i"),
                this.width / 2, 116, SlimeTheme.withAlpha(SlimeTheme.MUTED, e));
        // tek hard fact ilk ekranda (copy kuralı)
        g.drawCenteredString(this.font, Component.literal("Sodium + Lithium + EntityCulling + ImmediatelyFast hazır"),
                this.width / 2, 132, SlimeTheme.withAlpha(SlimeTheme.HAY, e));
        g.pose().popPose();
        if (a < 255) g.fill(0, 0, 0, 0, 0); // (alpha zaten renklerde)
    }

    private void renderAbout(GuiGraphics g, long now) {
        // type moment: sürüm büyük set (kural: bir type moment)
        double pulse = SlimeMotion.loop(now, 4);
        int col = SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.75 + 0.25 * pulse);
        g.drawCenteredString(this.font, Component.literal("26.2"), this.width / 2, 70, col);
        // close-word (gaming deal)
        g.drawCenteredString(this.font, Component.literal("SlimeMC"), this.width / 2, 96, SlimeTheme.WOOD, true);
    }
}
