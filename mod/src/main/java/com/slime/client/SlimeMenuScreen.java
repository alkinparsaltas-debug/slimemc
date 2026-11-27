package com.slime.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Options;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.screens.ConnectScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen;
import net.minecraft.client.gui.screens.worldselection.SelectWorldScreen;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.List;

public class SlimeMenuScreen extends Screen {
    private static final String SERVER_IP = "85.106.146.49:26262";

    private enum Tab { HERO, VILLAGES, HUD, ABOUT }
    private Tab tab = Tab.HERO;
    private final VillageChapter chapter = new VillageChapter();
    private final List<IconCard> icons = new ArrayList<>();
    private long heroBorn = 0;
    private static boolean heroEnteredOnce = false;
    private int cardX, cardY, cardW, cardH;
    private int wrapX, wrapW;

    public SlimeMenuScreen() {
        super(Component.empty());
    }

    @Override
    protected void init() {
        int centerX = this.width / 2;
        boolean inWorld = Minecraft.getInstance().level != null;

        cardW = Math.min(340, this.width - 32);
        cardH = Math.min(196, this.height - 28);
        cardX = (this.width - cardW) / 2;
        cardY = (this.height - cardH) / 2;

        wrapW = Math.min(540, this.width - 40);
        wrapX = (this.width - wrapW) / 2;

        this.clearWidgets();
        List<AbstractWidget> ws = new ArrayList<>();

        if (tab != Tab.HERO) {
            ws.add(new TabButton(centerX - 150, 12, 70, Component.literal("Ana Menü"), () -> false, b -> go(Tab.HERO)));
            ws.add(new TabButton(centerX - 72, 12, 68, Component.literal("Köyler"), () -> tab == Tab.VILLAGES, b -> go(Tab.VILLAGES)));
            ws.add(new TabButton(centerX + 4, 12, 60, Component.literal("HUD"), () -> tab == Tab.HUD, b -> go(Tab.HUD)));
            ws.add(new TabButton(centerX + 72, 12, 72, Component.literal("Hakkında"), () -> tab == Tab.ABOUT, b -> go(Tab.ABOUT)));
        }

        int top = Math.max(46, (this.height - 220) / 2);

        switch (tab) {
            case HERO -> {
                int pad = 18;
                int innerW = cardW - pad * 2;
                int bx = cardX + pad;
                int y1 = cardY + 98;
                int y2 = cardY + 128;
                int y3 = cardY + 154;

                if (!inWorld) {
                    ws.add(DepthButton.solid(Component.literal("▶  Sunucuya Bağlan"),
                            bx, y1, innerW, 24, b -> connectToServer(SERVER_IP)));

                    int halfW = (innerW - 8) / 2;
                    ws.add(DepthButton.pill(Component.literal("Tek Oyunculu"),
                            bx, y2, halfW, 20, b -> Minecraft.getInstance().setScreen(new SelectWorldScreen(this))));
                    ws.add(DepthButton.pill(Component.literal("Ayarlar"),
                            bx + halfW + 8, y2, innerW - halfW - 8, 20, b -> openOptions()));

                    int thirdW = (innerW - 12) / 3;
                    ws.add(DepthButton.pill(Component.literal("HUD Ayarları"),
                            bx, y3, thirdW, 20, b -> go(Tab.HUD)));
                    ws.add(DepthButton.pill(Component.literal("Köyler"),
                            bx + thirdW + 6, y3, thirdW, 20, b -> go(Tab.VILLAGES)));
                    ws.add(DepthButton.pill(Component.literal("Çıkış"),
                            bx + (thirdW + 6) * 2, y3, innerW - (thirdW + 6) * 2, 20, b -> Minecraft.getInstance().stop()));
                } else {
                    ws.add(DepthButton.solid(Component.literal("Oyuna Dön"),
                            bx, y1, innerW, 24, b -> this.onClose()));

                    int halfW = (innerW - 8) / 2;
                    ws.add(DepthButton.pill(Component.literal("HUD Ayarları"),
                            bx, y2, halfW, 20, b -> go(Tab.HUD)));
                    ws.add(DepthButton.pill(Component.literal("Köyleri Keşfet"),
                            bx + halfW + 8, y2, innerW - halfW - 8, 20, b -> go(Tab.VILLAGES)));

                    ws.add(DepthButton.pill(Component.literal("Hakkında"),
                            bx, y3, innerW, 20, b -> go(Tab.ABOUT)));
                }
            }
            case VILLAGES -> {
                icons.clear();
                int gap = 8;
                int itemW = (wrapW - gap * 5) / 6;
                icons.add(new IconCard(new ItemStack(Blocks.OAK_PLANKS), Component.literal("Meşe"), wrapX, top + 144, itemW, 54));
                icons.add(new IconCard(new ItemStack(Blocks.COBBLESTONE), Component.literal("Yonu Taşı"), wrapX + (itemW + gap), top + 144, itemW, 54));
                icons.add(new IconCard(new ItemStack(Blocks.HAY_BLOCK), Component.literal("Saman"), wrapX + (itemW + gap) * 2, top + 144, itemW, 54));
                icons.add(new IconCard(new ItemStack(Blocks.SANDSTONE), Component.literal("Kumtaşı"), wrapX + (itemW + gap) * 3, top + 144, itemW, 54));
                icons.add(new IconCard(new ItemStack(Blocks.CACTUS), Component.literal("Kaktüs"), wrapX + (itemW + gap) * 4, top + 144, itemW, 54));
                icons.add(new IconCard(new ItemStack(Items.WATER_BUCKET), Component.literal("Su"), wrapX + (itemW + gap) * 5, top + 144, itemW, 54));
            }
            case HUD -> {
                SlimeConfig c = SlimeConfig.get();
                ws.add(new ToggleCard("HUD Açık", wrapX, top, wrapW, () -> c.hudEnabled = !c.hudEnabled, () -> c.hudEnabled));
                ws.add(new ToggleCard("FPS", wrapX, top + 30, wrapW, () -> c.hudFps = !c.hudFps, () -> c.hudFps));
                ws.add(new ToggleCard("CPS", wrapX, top + 60, wrapW, () -> c.hudCps = !c.hudCps, () -> c.hudCps));
                ws.add(new ToggleCard("Koordinatlar", wrapX, top + 90, wrapW, () -> c.hudCoords = !c.hudCoords, () -> c.hudCoords));
                ws.add(new ToggleCard("Azaltılmış Hareket", wrapX, top + 120, wrapW, () -> c.motionReduced = !c.motionReduced, () -> c.motionReduced));
                ws.add(new ScaleCard(wrapX, top + 150, wrapW));
                ws.add(DepthButton.pill(Component.literal("−"), wrapX + wrapW - 96, top + 152, 28, 20,
                        b -> { c.hudScale = Math.max(0.8, c.hudScale - 0.1); c.save(); }));
                ws.add(DepthButton.pill(Component.literal("+"), wrapX + wrapW - 62, top + 152, 28, 20,
                        b -> { c.hudScale = Math.min(1.4, c.hudScale + 0.1); c.save(); }));
            }
            case ABOUT -> {
                icons.clear();
                int gap = 10;
                int itemW = (wrapW - gap * 3) / 4;
                icons.add(new IconCard(new ItemStack(Items.CLOCK), Component.literal("FPS"), wrapX, top + 115, itemW, 56));
                icons.add(new IconCard(new ItemStack(Items.IRON_SWORD), Component.literal("CPS"), wrapX + (itemW + gap), top + 115, itemW, 56));
                icons.add(new IconCard(new ItemStack(Items.COMPASS), Component.literal("XYZ"), wrapX + (itemW + gap) * 2, top + 115, itemW, 56));
                icons.add(new IconCard(new ItemStack(Blocks.SLIME_BLOCK), Component.literal("Slime"), wrapX + (itemW + gap) * 3, top + 115, itemW, 56));
            }
        }

        if (tab != Tab.HERO) {
            ws.add(DepthButton.pill(Component.literal("← Ana Menü"), wrapX, this.height - 32, 86, 20, b -> go(Tab.HERO)));
        }
        if (inWorld) {
            ws.add(DepthButton.pill(Component.literal("Kapat"), wrapX + wrapW - 70, this.height - 32, 70, 20, b -> this.onClose()));
        }

        for (AbstractWidget w : ws) this.addRenderableWidget(w);
    }

    private void go(Tab t) {
        this.tab = t;
        this.init();
    }

    private void connectToServer(String ip) {
        Minecraft mc = Minecraft.getInstance();
        ServerAddress addr = ServerAddress.parseString(ip);
        ServerData data = new ServerData("SlimeTowny", ip, ServerData.Type.OTHER);
        for (Method m : ConnectScreen.class.getDeclaredMethods()) {
            Class<?>[] p = m.getParameterTypes();
            if (Modifier.isStatic(m.getModifiers())
                    && p.length >= 4
                    && p[0] == Screen.class
                    && p[1] == Minecraft.class
                    && p[2] == ServerAddress.class
                    && p[3] == ServerData.class) {
                try {
                    m.setAccessible(true);
                    if (p.length == 6) {
                        m.invoke(null, this, mc, addr, data, false, null);
                        return;
                    }
                    if (p.length == 5) {
                        m.invoke(null, this, mc, addr, data, false);
                        return;
                    }
                    if (p.length == 4) {
                        m.invoke(null, this, mc, addr, data);
                        return;
                    }
                } catch (Exception ignored) {}
            }
        }
        mc.setScreen(new JoinMultiplayerScreen(this));
    }

    private void openOptions() {
        Minecraft mc = Minecraft.getInstance();
        String[] names = {
                "net.minecraft.client.gui.screens.options.OptionsScreen",
                "net.minecraft.client.gui.screens.OptionsScreen"
        };
        for (String name : names) {
            try {
                Class<?> cls = Class.forName(name);
                Screen screen = (Screen) cls.getConstructor(Screen.class, Options.class).newInstance(this, mc.options);
                mc.setScreen(screen);
                return;
            } catch (Exception ignored) {}
        }
    }

    @Override
    public boolean shouldCloseOnEsc() {
        return Minecraft.getInstance().level != null;
    }

    @Override
    public void render(GuiGraphics g, int mx, int my, float d) {
        long now = System.currentTimeMillis();
        if (heroBorn == 0) heroBorn = now;

        renderBackdrop(g, now);

        if (tab == Tab.HERO) {
            renderHeroCard(g, now);
        } else {
            int top = Math.max(46, (this.height - 220) / 2);
            g.drawString(this.font, Component.literal(switch (tab) {
                case VILLAGES -> "Köyler";
                case HUD -> "HUD Ayarları";
                default -> "Hakkında";
            }), wrapX, top - 14, SlimeTheme.ACCENT, true);

            if (tab == Tab.VILLAGES) chapter.render(g, wrapX, top, wrapW, 132, mx, my, d);
            if (tab == Tab.ABOUT) renderAbout(g, top, now);
            for (IconCard ic : icons) ic.render(g, mx, my, d, now);
        }

        super.render(g, mx, my, d);

        g.drawCenteredString(this.font, Component.literal("Slime Client 26.2 • Fabric"),
                this.width / 2, this.height - 11, SlimeTheme.withAlpha(SlimeTheme.MUTED, 0.7));
    }

    private void renderBackdrop(GuiGraphics g, long now) {
        g.fill(0, 0, this.width, this.height, 0xFF0A0D10);

        int glowH = this.height / 2;
        for (int i = 0; i < glowH; i += 2) {
            double k = 1.0 - (i / (double) glowH);
            g.fill(0, i, this.width, i + 2, SlimeTheme.withAlpha(0xFF173822, k * 0.38));
        }

        int gridCol = SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.045);
        for (int gx = 0; gx < this.width; gx += 32) {
            g.fill(gx, 0, gx + 1, this.height, gridCol);
        }
        for (int gy = 0; gy < this.height; gy += 32) {
            g.fill(0, gy, this.width, gy + 1, gridCol);
        }

        for (int i = 0; i < 14; i++) {
            double speed = 0.018 + (i % 4) * 0.006;
            int px = (int) ((i * 97 + (now * speed * 0.4)) % Math.max(1, this.width));
            int py = (int) (this.height - ((now * speed + i * 53) % Math.max(1, this.height)));
            int size = (i % 3 == 0) ? 3 : 2;
            g.fill(px, py, px + size, py + size, SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.22));
        }
    }

    private void renderHeroCard(GuiGraphics g, long now) {
        double e = heroEnteredOnce ? 1 : SlimeMotion.enter(now - heroBorn);
        if (e >= 1) heroEnteredOnce = true;
        int dy = (int) Math.round((1 - e) * 10);
        double pulse = SlimeMotion.loop(now, SlimeTheme.LOOP_S);

        int cx = cardX;
        int cy = cardY + dy;

        DepthPanel.panel(g, cx, cy, cardW, cardH, 6, 5,
                SlimeTheme.withAlpha(0xFF141A20, 0.96), 0xFF080B0E, 0.35);
        DepthPanel.outline(g, cx, cy, cardW, cardH, 1,
                SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.22 + 0.12 * pulse));

        g.fill(cx + 24, cy, cx + cardW - 24, cy + 2,
                SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.75 + 0.25 * pulse));

        DepthPanel.roundRect(g, cx + cardW - 44, cy + 10, 32, 14, 4, SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.16));
        g.drawCenteredString(this.font, Component.literal("26.2"), cx + cardW - 28, cy + 13, SlimeTheme.ACCENT);

        int iconY = cy + 12 + (int) Math.round(Math.sin(pulse * Math.PI) * -2);
        g.pose().pushMatrix();
        g.pose().translate(this.width / 2f - 12f, iconY);
        g.pose().scale(1.5f, 1.5f);
        g.renderItem(new ItemStack(Blocks.SLIME_BLOCK), 0, 0);
        g.pose().popMatrix();

        g.drawCenteredString(this.font, Component.literal("SLIME CLIENT"),
                this.width / 2, cy + 41, SlimeTheme.INK);
        g.drawCenteredString(this.font, Component.literal("Özel PvP & Towny İstemcisi"),
                this.width / 2, cy + 54, SlimeTheme.MUTED);

        int pillW = cardW - 36;
        int pillX = cx + 18;
        int pillY = cy + 69;
        DepthPanel.roundRect(g, pillX, pillY, pillW, 20, 4, 0xFF0D1216);
        DepthPanel.outline(g, pillX, pillY, pillW, 20, 1, SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.25));

        int dotCol = SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.65 + 0.35 * pulse);
        DepthPanel.roundRect(g, pillX + 10, pillY + 7, 6, 6, 3, dotCol);
        g.drawString(this.font, Component.literal(SERVER_IP), pillX + 22, pillY + 6, SlimeTheme.INK, false);
        g.drawString(this.font, Component.literal("HAZIR"),
                pillX + pillW - 10 - this.font.width("HAZIR"), pillY + 6, SlimeTheme.ACCENT, false);
    }

    private void renderAbout(GuiGraphics g, int top, long now) {
        DepthPanel.panel(g, wrapX, top, wrapW, 96, 6, 4, SlimeTheme.SURFACE, 0xFF0B0E11, 0.2);
        double pulse = SlimeMotion.loop(now, 4);
        int col = SlimeTheme.withAlpha(SlimeTheme.ACCENT, 0.75 + 0.25 * pulse);
        g.drawCenteredString(this.font, Component.literal("SLIME CLIENT 26.2"), this.width / 2, top + 20, col);
        g.drawCenteredString(this.font, Component.literal("Sunucu: " + SERVER_IP), this.width / 2, top + 40, SlimeTheme.INK);
        g.drawCenteredString(this.font, Component.literal("FPS, CPS, Koordinat HUD ve 3D Arayüz"), this.width / 2, top + 58, SlimeTheme.MUTED);
    }
}
