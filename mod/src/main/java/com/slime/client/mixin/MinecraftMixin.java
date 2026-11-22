package com.slime.client.mixin;

import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(Minecraft.class)
public class MinecraftMixin {

    @Inject(method = "createTitle", at = @At("RETURN"), cancellable = true, require = 0)
    private void slime$modifyTitle(CallbackInfoReturnable<String> cir) {
        cir.setReturnValue("Slime Client 26.2 | " + cir.getReturnValue());
    }
}
