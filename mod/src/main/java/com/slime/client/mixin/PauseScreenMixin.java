package com.slime.client.mixin;

import com.slime.client.SlimeMenuScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(PauseScreen.class)
public class PauseScreenMixin extends Screen {
    protected PauseScreenMixin(Component title) { super(title); }

    @Inject(method = "init()V", at = @At("RETURN"))
    private void slime$addMenuButton(CallbackInfo ci) {
        this.addRenderableWidget(new com.slime.client.DepthButton(
                this.width / 2 - 100, this.height / 2 + 84, 200, 20,
                Component.literal("Slime Client Menü"),
                b -> Minecraft.getInstance().setScreen(new SlimeMenuScreen()), true, false));
    }
}
