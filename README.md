# Slime Client 26.2 — Özel Minecraft İstemcisi ve Başlatıcı

Bu paket, **Minecraft 26.2** için kendi özel istemcini (**SlimeClient-26.2.jar**), masaüstü başlatıcını (**SlimeLauncher.exe**) ve tek tıkla kurulum sihirbazını (**SlimeClient-Setup.exe**) içerir.

---

## Yöntem 1: Bilgisayara Hiçbir Program Kurmadan Bulutta `.exe` ve `.jar` Üretme (En Kolay)

Bilgisayarında Java veya Python kurulu olmasa bile ücretsiz bir **GitHub** hesabı ile tek tıkla derleme yapabilirsin:

1. [github.com](https://github.com) adresine gir ve sağ üstten **+** simgesine basıp **New repository** (Yeni depo) oluştur (örneğin adı `SlimeClient` olsun).
2. Açılan sayfada **"uploading an existing file"** bağlantısına tıkla.
3. Bu ZIP dosyasının içindeki **`SlimeClient-26.2` klasörünün içindeki tüm dosya ve klasörleri** (`.github`, `mod`, `launcher`, `README.md`, `build_local.bat`) seçip sayfaya sürükle ve **Commit changes** butonuna bas.
4. Üst menüden **Actions** sekmesine tıkla. Otomatik başlayan **"Build Slime Client 26.2"** işleminin yeşil tik (yaklaşık 2-3 dakika) olmasını bekle.
5. İşlemin içine gir ve en alttaki **Artifacts** bölümünden **`SlimeClient-26.2-Release`** dosyasına tıklayarak hazır **`SlimeClient-Setup.exe`** kurulum sihirbazını indir!

---

## Yöntem 2: Kendi Bilgisayarında Tek Tıkla Derleme (Windows)

Bilgisayarında **Java 21+** ve **Python 3.10+** kuruluysa:
1. Klasördeki **`build_local.bat`** dosyasına çift tıkla.
2. İşlem bittiğinde **`release/`** klasörünün içinde `SlimeClient-Setup.exe`, `SlimeLauncher.exe` ve `SlimeClient-26.2.jar` hazır olarak oluşacaktır.

---

## Özellikler
- **Minecraft 26.2 + Fabric Loader** altyapısı
- **Çevrimdışı (Crackli) Hesap Desteği** ve kayıtlı profil ayarları
- **Özel Slime HUD:** Ekranda anlık FPS, CPS (Tıklama Hızı) ve Koordinat göstergesi
- **Performans & İşaretleme Paketi:** Sodium, Lithium, Entity Culling, ImmediatelyFast, Ping Wheel ve Zoomify otomatik kurulumu
