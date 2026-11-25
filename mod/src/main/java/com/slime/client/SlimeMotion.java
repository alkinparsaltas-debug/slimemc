package com.slime.client;

/** Animasyon motoru. Kural: hero bir kez girer; reduced motion'da her şey durur. */
public final class SlimeMotion {
    private SlimeMotion() {}

    public static double clamp01(double t) { return t < 0 ? 0 : Math.min(t, 1); }
    public static double easeOutCubic(double t) { return 1 - Math.pow(1 - t, 3); }

    public static double enter(double ageMs) {
        if (SlimeConfig.get().motionReduced) return 1;
        return easeOutCubic(clamp01(ageMs / (double) SlimeTheme.ENTER_MS));
    }

    /** 0..1..0 yumuşak nabız (loop). */
    public static double loop(long nowMs, int seconds) {
        if (SlimeConfig.get().motionReduced) return 0.5;
        double p = (nowMs % (seconds * 1000L)) / (double) (seconds * 1000L);
        return 0.5 - 0.5 * Math.cos(p * 2 * Math.PI);
    }

    /** delta tabanlı yumuşak yaklaşım (hoverT gibi). */
    public static double approach(double current, double target, float delta, double ms) {
        if (SlimeConfig.get().motionReduced) return target;
        double k = Math.min(1.0, (delta * 20f) * (SlimeTheme.HOVER_MS / (double) ms));
        return current + (target - current) * Math.min(1.0, Math.max(0.0, k));
    }
}
