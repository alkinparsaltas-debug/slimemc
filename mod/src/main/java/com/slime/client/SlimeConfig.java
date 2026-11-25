package com.slime.client;

import net.fabricmc.loader.api.FabricLoader;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;

public final class SlimeConfig {
    public boolean hudEnabled = true;
    public boolean hudFps = true;
    public boolean hudCps = true;
    public boolean hudCoords = true;
    public boolean motionReduced = false;
    public double hudScale = 1.0;

    private static final SlimeConfig I = new SlimeConfig();
    public static SlimeConfig get() { return I; }

    private static Path file() {
        return FabricLoader.getInstance().getConfigDir().resolve("slimeclient.properties");
    }

    public static void load() {
        Properties p = new Properties();
        try (InputStream in = Files.newInputStream(file())) { p.load(in); } catch (IOException ignored) {}
        I.hudEnabled = bool(p, "hud.enabled", true);
        I.hudFps = bool(p, "hud.fps", true);
        I.hudCps = bool(p, "hud.cps", true);
        I.hudCoords = bool(p, "hud.coords", true);
        I.motionReduced = bool(p, "motion.reduced", false);
        I.hudScale = dbl(p, "hud.scale", 1.0);
    }

    public void save() {
        Properties p = new Properties();
        p.setProperty("hud.enabled", String.valueOf(hudEnabled));
        p.setProperty("hud.fps", String.valueOf(hudFps));
        p.setProperty("hud.cps", String.valueOf(hudCps));
        p.setProperty("hud.coords", String.valueOf(hudCoords));
        p.setProperty("motion.reduced", String.valueOf(motionReduced));
        p.setProperty("hud.scale", String.valueOf(hudScale));
        try (OutputStream out = Files.newOutputStream(file())) { p.store(out, "Slime Client 26.2"); }
        catch (IOException ignored) {}
    }

    private static boolean bool(Properties p, String k, boolean d) {
        String v = p.getProperty(k);
        return v == null ? d : Boolean.parseBoolean(v);
    }

    private static double dbl(Properties p, String k, double d) {
        try { return Double.parseDouble(p.getProperty(k, String.valueOf(d))); } catch (Exception e) { return d; }
    }
}
