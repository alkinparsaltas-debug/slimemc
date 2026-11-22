package com.slime.client;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;

import java.util.ArrayDeque;
import java.util.Deque;

public class SlimeClientMod implements ClientModInitializer {

    private static final Deque<Long> LEFT_CLICKS = new ArrayDeque<>();
    private static boolean wasAttackDown = false;

    @Override
    public void onInitializeClient() {
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            if (client.options == null) return;
            boolean isDown = client.options.keyAttack.isDown();
            long now = System.currentTimeMillis();
            if (isDown && !wasAttackDown) {
                LEFT_CLICKS.addLast(now);
            }
            wasAttackDown = isDown;
            while (!LEFT_CLICKS.isEmpty() && now - LEFT_CLICKS.peekFirst() > 1000L) {
                LEFT_CLICKS.removeFirst();
            }
        });

        HudRenderCallback.EVENT.register((guiGraphics, deltaTracker) -> {
            Minecraft client = Minecraft.getInstance();
            if (client.player == null || client.options.hideGui) return;

            int fps = client.getFps();
            int cps = LEFT_CLICKS.size();
            BlockPos pos = client.player.blockPosition();

            String header = "SLIME CLIENT 26.2";
            String stats = String.format("FPS: %d  |  CPS: %d  |  XYZ: %d, %d, %d", fps, cps, pos.getX(), pos.getY(), pos.getZ());

            int width = Math.max(client.font.width(header), client.font.width(stats)) + 16;

            // Yari saydam koyu arka plan ve sol tarafta slime yesili serit
            guiGraphics.fill(6, 6, 6 + width, 34, 0x88101216);
            guiGraphics.fill(6, 6, 8, 34, 0xFF55FF55);

            guiGraphics.drawString(client.font, Component.literal(header), 13, 10, 0xFF55FF55, true);
            guiGraphics.drawString(client.font, Component.literal(stats), 13, 22, 0xFFFFFFFF, true);
        });
    }
}
