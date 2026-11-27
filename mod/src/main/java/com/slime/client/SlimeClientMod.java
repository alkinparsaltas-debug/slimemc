package com.slime.client;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.command.v2.ClientCommandManager;
import net.fabricmc.fabric.api.client.command.v2.ClientCommandRegistrationCallback;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;

public class SlimeClientMod implements ClientModInitializer {

    public static final String MOD_ID = "slimeclient";

    @Override
    public void onInitializeClient() {
        SlimeConfig.load();

        ClientTickEvents.END_CLIENT_TICK.register(SlimeHud.TICK);
        HudRenderCallback.EVENT.register(SlimeHud::render);

        ClientCommandRegistrationCallback.EVENT.register((dispatcher, registry) ->
                dispatcher.register(ClientCommandManager.literal("slime")
                        .executes(ctx -> {
                            ctx.getSource().getMinecraft().setScreen(new SlimeMenuScreen());
                            return 1;
                        })));
    }
}
