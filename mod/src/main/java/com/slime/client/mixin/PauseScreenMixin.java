package com.slime.client.mixin;

import com.slime.client.DepthButton;
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

    @Inject(method = "init(Lnet/minecraft/client/Minecraft;II)V", at = @At("RETURN"))
    private void slime$addMenuButton(Minecraft client, int w, int h, CallbackInfo ci) {
        this.addRenderableWidget(new DepthButton(
                this.width / 2 - 100, this.height / 2 + 100, 200, 20,
                Component.literal("Slime Client Menü"),
                b -> client.setScreen(new SlimeMenuScreen()), true, false));
    }
}
