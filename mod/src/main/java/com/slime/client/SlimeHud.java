package com.slime.client;

import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.ArrayDeque;
import java.util.Deque;

public final class SlimeHud {
    private static final Deque<Long> CLICKS = new ArrayDeque<>();
    private static boolean wasAttackDown = false;
    private static long bornAt = 0;
    private static boolean enteredOnce = false;

    public static final ClientTickEvents.EndTick TICK = client -> {
        if (client.options == null) return;
        boolean isDown = client.options.keyAttack.isDown();
        long now = System.currentTimeMillis();
        if (isDown && !wasAttackDown) CLICKS.addLast(now);
        wasAttackDown = isDown;
        while (!CLICKS.isEmpty() && now - CLICKS.peekFirst() > 1000L) CLICKS.removeFirst();
    };

    public static void render(GuiGraphics g, DeltaTracker dt) {
        SlimeConfig c = SlimeConfig.get();
        Minecraft mc = Minecraft.getInstance();
        if (!c.hudEnabled || mc.player == null || mc.options.hideGui) return;
        long now = System.currentTimeMillis();
        if (bornAt == 0) bornAt = now;
        double e = enteredOnce ? 1 : SlimeMotion.enter(now - bornAt);
        if (e >= 1) enteredOnce = true;
        int lift = (int) Math.round((1 - e) * 10);

        int fps = mc.getFps();
        int cps = CLICKS.size();
        BlockPos pos = mc.player.blockPosition();

        StringBuilder stats = new StringBuilder();
        if (c.hudFps) stats.append(String.format("FPS %d", fps));
        if (c.hudCps) stats.append(stats.length() > 0 ? "   " : "").append(String.format("CPS %d", cps));
        if (c.hudCoords) stats.append(stats.length() > 0 ? "   " : "").append(String.format("%d %d %d", pos.getX(), pos.getY(), pos.getZ()));
        if (stats.length() == 0) stats.append("HUD");

        String header = "SLIME CLIENT 26.2";
        int tw = Math.max(mc.font.width(header), mc.font.width(stats.toString()));
        int w = (int) ((tw + 40) * c.hudScale);
        int h = (int) (34 * c.hudScale);
        int x = 6, y = 6 + lift;

        DepthPanel.panel(g, x, y, w, h, SlimeTheme.RADIUS, SlimeTheme.DEPTH_PANEL,
                SlimeTheme.withAlpha(SlimeTheme.SURFACE, e), 0xFF0F1418, 0.3 * e);
        double pulse = SlimeMotion.loop(now, SlimeTheme.LOOP_S);
        g.fill(x, y, x + 2, y + h, SlimeTheme.withAlpha(SlimeTheme.ACCENT, e * (0.6 + 0.4 * pulse)));

        renderItem(g, new ItemStack(Items.CLOCK), x + 8, y + 5);
        renderItem(g, new ItemStack(Items.IRON_SWORD), x + 8, y + 17);

        g.drawString(mc.font, Component.literal(header), x + 26, y + 6, SlimeTheme.withAlpha(SlimeTheme.ACCENT, e), true);
        g.drawString(mc.font, Component.literal(stats.toString()), x + 26, y + 18, SlimeTheme.withAlpha(SlimeTheme.INK, e), true);
    }

    private static void renderItem(GuiGraphics g, ItemStack s, int x, int y) {
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(0.6f, 0.6f);
        g.renderItem(s, 0, 0);
        g.pose().popMatrix();
    }
}
