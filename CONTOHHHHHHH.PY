import subprocess
import xml.etree.ElementTree as ET
import time
import re


# =========================================================
# KONFIGURASI
# =========================================================

ADB = r"D:\Programer\platform-tools-latest-windows\platform-tools\adb.exe"

MAX_TAP_STORY = 1000
MAX_REFRESH = 2
WAIT_OPEN_STORY = 1.0
WAIT_NEXT_STORY = 0.1
CHECK_STORY_EVERY = 5
UI_RETRY = 5
UI_RETRY_DELAY = 0.4
WAIT_REFRESH = 2.0
WAIT_BACK = 1.0
MAX_BACK_FALLBACK = 2


# =========================================================
# TAMBAHAN UNTUK STARTUP HP
#
# URUTAN:
# 1. Cek layar HP
# 2. Kalau mati → nyalakan
# 3. Swipe dari bawah → atas untuk unlock
# 4. Android Home 2x
# 5. Baru lanjut ke Instagram
# =========================================================

WAIT_WAKE_SCREEN = 1.5
WAIT_UNLOCK = 1.5
WAIT_STARTUP_HOME = 1.0
UNLOCK_DURATION = 500


# =========================================================
# TAMBAHAN UNTUK RECOVERY HOME
# =========================================================

MAX_HOME_RECOVERY_ATTEMPTS = 10

WAIT_ANDROID_HOME = 1.0

WAIT_OPEN_INSTAGRAM = 2.0


# =========================================================
# TAMBAHAN UNTUK MENUNGGU INSTAGRAM SETELAH DIBUKA
# =========================================================

WAIT_INSTAGRAM_START_RETRY = 0.5
MAX_INSTAGRAM_START_RETRY = 3

MAX_INSTAGRAM_HOME_REFRESH_RETRY = 10


# =========================================================
# TAMBAHAN UNTUK ACCOUNT SWITCHER
#
# Dipakai di akhir program:
#
# Instagram Home
#       ↓
# Hold Profile 1 detik
#       ↓
# Account Switcher
#       ↓
# Deteksi jumlah akun
# =========================================================

WAIT_PROFILE_HOLD = 1.0
WAIT_ACCOUNT_SWITCHER = 1.5
ACCOUNT_SWITCHER_UI_RETRY = 10
ACCOUNT_SWITCHER_UI_RETRY_DELAY = 0.5


# =========================================================
# ADB HELPER
# =========================================================

def adb_run(*args):
    return subprocess.run(
        [ADB, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


# =========================================================
# CEK STATUS LAYAR HP
# =========================================================

def layar_hp_menyala():

    result = adb_run(
        "shell",
        "dumpsys",
        "power"
    )

    output = result.stdout.lower()

    indikator_mati = [
        "display power: state=off",
        "mscreenon=false",
        "mscreenstate=off",
        "mwakefulness=asleep",
        "mwakefulness=dozing"
    ]

    for indikator in indikator_mati:
        if indikator.lower() in output:
            return False

    indikator_nyala = [
        "display power: state=on",
        "mscreenon=true",
        "mscreenstate=on",
        "mwakefulness=awake"
    ]

    for indikator in indikator_nyala:
        if indikator.lower() in output:
            return True

    print(
        "⚠️ Status layar tidak dapat dipastikan."
    )

    return True


# =========================================================
# NYALAKAN LAYAR HP
# =========================================================

def wake_hp():

    print()

    print(
        "💡 Mengecek kondisi layar HP..."
    )

    layar_menyala = layar_hp_menyala()

    if layar_menyala:

        print(
            "✅ Layar HP sudah menyala."
        )

        return True

    print()

    print(
        "🌙 Layar HP sedang mati."
    )

    print(
        "⚡ Menyalakan layar HP..."
    )

    adb_run(
        "shell",
        "input",
        "keyevent",
        "26"
    )

    time.sleep(WAIT_WAKE_SCREEN)

    if layar_hp_menyala():

        print(
            "✅ Layar HP berhasil dinyalakan."
        )

        return True

    print(
        "⚠️ Layar belum dapat dipastikan menyala."
    )

    return True


# =========================================================
# CEK UKURAN LAYAR HP
# =========================================================

def get_screen_size():

    result = adb_run(
        "shell",
        "wm",
        "size"
    )

    output = result.stdout

    matches = re.findall(
        r"(?:Physical size|Override size):\s*(\d+)x(\d+)",
        output
    )

    if matches:

        width, height = map(
            int,
            matches[-1]
        )

        if width > 0 and height > 0:
            return width, height

    print(
        "⚠️ Ukuran layar tidak terdeteksi."
    )

    print(
        "➡️ Menggunakan ukuran default 720x1600."
    )

    return 720, 1600


# =========================================================
# UNLOCK HP DENGAN SWIPE BAWAH → ATAS
# =========================================================

def unlock_hp():

    print()

    print(
        "🔓 Melakukan unlock HP..."
    )

    width, height = get_screen_size()

    x = width // 2

    y_awal = int(height * 0.90)

    y_akhir = int(height * 0.25)

    print(
        f"📱 Ukuran layar: {width}x{height}"
    )

    print(
        f"⬆️ Swipe unlock: "
        f"({x}, {y_awal}) → "
        f"({x}, {y_akhir})"
    )

    adb_run(
        "shell",
        "input",
        "swipe",
        str(x),
        str(y_awal),
        str(x),
        str(y_akhir),
        str(UNLOCK_DURATION)
    )

    time.sleep(WAIT_UNLOCK)

    print(
        "✅ Swipe unlock selesai."
    )


# =========================================================
# ANDROID HOME 2X UNTUK STARTUP
# =========================================================

def startup_android_home_2x():

    print()

    print(
        "🏠 Menuju Android Home 2x..."
    )

    for i in range(2):

        print(
            f"📱 Android Home {i + 1}/2"
        )

        adb_run(
            "shell",
            "input",
            "keyevent",
            "3"
        )

        time.sleep(WAIT_STARTUP_HOME)

    print(
        "✅ Android Home sudah ditekan 2x."
    )


# =========================================================
# STARTUP HP
# =========================================================

def startup_hp():

    print()

    print(
        "🚀 Menjalankan startup HP..."
    )

    print()

    print(
        "1️⃣ Mengecek / menyalakan layar..."
    )

    wake_hp()

    print()

    print(
        "2️⃣ Melakukan unlock..."
    )

    unlock_hp()

    print()

    print(
        "3️⃣ Menuju Android Home 2x..."
    )

    startup_android_home_2x()

    print()

    print(
        "✅ Startup HP selesai."
    )

    print(
        "➡️ Melanjutkan ke Instagram Story Bot..."
    )


# =========================================================
# CEK FOREGROUND APP
# =========================================================

def get_foreground_package():

    result = adb_run(
        "shell",
        "dumpsys",
        "window",
        "windows"
    )

    output = result.stdout

    match = re.search(
        r'mCurrentFocus=.*?\s([a-zA-Z0-9._-]+)/',
        output
    )

    if match:
        return match.group(1)

    match = re.search(
        r'mFocusedApp=.*?\s([a-zA-Z0-9._-]+)/',
        output
    )

    if match:
        return match.group(1)

    return ""


# =========================================================
# TAP
# =========================================================

def tap(x, y, show_log=True):

    if show_log:

        print(
            f"👆 Tap: ({x}, {y})"
        )

    adb_run(
        "shell",
        "input",
        "tap",
        str(x),
        str(y)
    )


# =========================================================
# BACK 1X
# =========================================================

def tekan_back():

    print(
        "⬅️ Menekan Back 1x..."
    )

    adb_run(
        "shell",
        "input",
        "keyevent",
        "4"
    )

    time.sleep(WAIT_BACK)


# =========================================================
# ANDROID HOME
# =========================================================

def tekan_android_home():

    print(
        "📱 Menekan Android Home..."
    )

    adb_run(
        "shell",
        "input",
        "keyevent",
        "3"
    )

    time.sleep(WAIT_ANDROID_HOME)


# =========================================================
# UI XML INSTAGRAM
# =========================================================

def get_ui_xml():

    for percobaan in range(
        1,
        UI_RETRY + 1
    ):

        dump = adb_run(
            "shell",
            "uiautomator",
            "dump",
            "--compressed",
            "/sdcard/window.xml"
        )

        if dump.returncode == 0:

            hasil = adb_run(
                "shell",
                "cat",
                "/sdcard/window.xml"
            )

            xml = hasil.stdout

            if (
                xml
                and "<hierarchy" in xml
                and 'package="com.instagram.android"' in xml
            ):
                return xml

        print(
            f"⚠️ Gagal mengambil UI XML "
            f"(percobaan {percobaan}/{UI_RETRY})"
        )

        if dump.stderr:

            print(
                "   ",
                dump.stderr.strip()
            )

        time.sleep(UI_RETRY_DELAY)

    print(
        "❌ UI XML Instagram gagal diambil."
    )

    return ""


# =========================================================
# UI XML UNIVERSAL
# =========================================================

def get_any_ui_xml():

    for percobaan in range(
        1,
        UI_RETRY + 1
    ):

        dump = adb_run(
            "shell",
            "uiautomator",
            "dump",
            "--compressed",
            "/sdcard/any_window.xml"
        )

        if dump.returncode == 0:

            hasil = adb_run(
                "shell",
                "cat",
                "/sdcard/any_window.xml"
            )

            xml = hasil.stdout

            if (
                xml
                and "<hierarchy" in xml
            ):
                return xml

        print(
            f"⚠️ UI Universal gagal "
            f"(percobaan {percobaan}/{UI_RETRY})"
        )

        if dump.stderr:

            print(
                "   ",
                dump.stderr.strip()
            )

        time.sleep(UI_RETRY_DELAY)

    print(
        "❌ UI Universal gagal diambil."
    )

    return ""


# =========================================================
# PARSE XML
# =========================================================

def parse_xml(xml):

    if not xml:
        return None

    try:
        return ET.fromstring(xml)

    except ET.ParseError:
        return None


# =========================================================
# CARI INSTAGRAM ORI
# =========================================================

def cari_instagram_ori():

    xml = get_any_ui_xml()

    if not xml:
        return None

    root = parse_xml(xml)

    if root is None:
        return None

    kandidat = []

    for node in root.iter("node"):

        text = node.attrib.get(
            "text",
            ""
        )

        content_desc = node.attrib.get(
            "content-desc",
            ""
        )

        clickable = node.attrib.get(
            "clickable",
            "false"
        )

        bounds = node.attrib.get(
            "bounds",
            ""
        )

        if (
            text != "Instagram"
            and
            content_desc != "Instagram"
        ):
            continue

        if clickable != "true":
            continue

        if not bounds:
            continue

        angka = re.findall(
            r"\d+",
            bounds
        )

        if len(angka) != 4:
            continue

        x1, y1, x2, y2 = map(
            int,
            angka
        )

        if (
            x2 <= x1
            or
            y2 <= y1
        ):
            continue

        x = (x1 + x2) // 2
        y = (y1 + y2) // 2

        kandidat.append({
            "x": x,
            "y": y,
            "bounds": bounds
        })

    if not kandidat:

        print(
            "❌ Icon Instagram tidak ditemukan."
        )

        return None

    kandidat.sort(
        key=lambda item: item["x"]
    )

    instagram_ori = kandidat[0]

    print()

    print(
        f"📱 Ditemukan {len(kandidat)} icon Instagram."
    )

    for i, item in enumerate(
        kandidat,
        start=1
    ):

        print(
            f"   Instagram {i}: "
            f"({item['x']}, {item['y']}) "
            f"{item['bounds']}"
        )

    print()

    print(
        "✅ Instagram ORI dipilih "
        "karena berada paling kiri."
    )

    print(
        f"📍 Posisi: "
        f"({instagram_ori['x']}, "
        f"{instagram_ori['y']})"
    )

    return (
        instagram_ori["x"],
        instagram_ori["y"]
    )


# =========================================================
# BUKA INSTAGRAM ORI DARI ANDROID HOME
# =========================================================

def buka_instagram_dari_android_home():

    print()

    print(
        "🚨 Instagram sudah keluar "
        "ke aplikasi lain."
    )

    print(
        "🛟 Memulai recovery..."
    )

    print()

    print(
        "🏠 Menuju Android Home..."
    )

    tekan_android_home()
    tekan_android_home()

    package = get_foreground_package()

    print(
        "📱 Foreground setelah Android Home:",
        package
    )

    print()

    print(
        "🔎 Mencari Instagram ORI..."
    )

    posisi = None

    for percobaan in range(10):

        posisi = cari_instagram_ori()

        if posisi is not None:
            break

        print(
            f"⚠️ Instagram belum ditemukan "
            f"(percobaan {percobaan + 1}/10)"
        )

        time.sleep(0.5)

    if posisi is None:

        print()

        print(
            "❌ Instagram ORI tidak ditemukan."
        )

        return False

    x, y = posisi

    print()

    print(
        f"📱 Membuka Instagram ORI "
        f"di ({x}, {y})..."
    )

    tap(x, y)

    print()

    print(
        f"⏳ Menunggu {WAIT_OPEN_INSTAGRAM} detik "
        f"setelah tap Instagram..."
    )

    time.sleep(WAIT_OPEN_INSTAGRAM)

    instagram_aktif = False

    for percobaan in range(
        1,
        MAX_INSTAGRAM_START_RETRY + 1
    ):

        package = get_foreground_package()

        print(
            f"   🔍 Cek Instagram "
            f"{percobaan}/{MAX_INSTAGRAM_START_RETRY}: "
            f"{package or 'tidak diketahui'}"
        )

        if package == "com.instagram.android":

            instagram_aktif = True

            print(
                "✅ Foreground Instagram terdeteksi."
            )

            break

        time.sleep(
            WAIT_INSTAGRAM_START_RETRY
        )

    if not instagram_aktif:

        print()

        print(
            "⚠️ Foreground Instagram belum "
            "terdeteksi secara normal."
        )

        print(
            "➡️ Tapi Instagram mungkin sedang "
            "dalam proses loading."
        )

        print(
            "➡️ Tetap mencoba refresh "
            "Home Instagram 2x..."
        )

    else:

        print()

        print(
            "🏠 Instagram sudah masuk."
        )

        print(
            "➡️ Lanjut refresh "
            "Home Instagram 2x..."
        )

    print()

    print(
        "🔄 Mencoba refresh menggunakan "
        "icon Home Instagram 2x..."
    )

    refresh_berhasil = False

    for percobaan in range(
        1,
        MAX_INSTAGRAM_HOME_REFRESH_RETRY + 1
    ):

        print()

        print(
            f"🔄 Percobaan refresh "
            f"{percobaan}/"
            f"{MAX_INSTAGRAM_HOME_REFRESH_RETRY}"
        )

        if refresh_instagram_home_2x():

            refresh_berhasil = True

            print(
                "✅ Refresh Home Instagram 2x berhasil."
            )

            break

        print(
            "⚠️ Home Instagram belum siap."
        )

        if percobaan < MAX_INSTAGRAM_HOME_REFRESH_RETRY:

            print(
                "⏳ Menunggu UI Instagram..."
            )

            time.sleep(1.0)

    if not refresh_berhasil:

        print()

        print(
            "❌ Home Instagram tidak berhasil "
            "ditemukan setelah Instagram dibuka."
        )

        print(
            "❌ Recovery Instagram gagal."
        )

        return False

    print()

    print(
        "🔍 Melakukan deteksi screen "
        "setelah Home Instagram 2x..."
    )

    time.sleep(1.0)

    screen = get_instagram_screen()

    print()

    print(
        "📱 Setelah recovery:",
        screen
    )

    if screen == "Instagram Home":

        print(
            "✅ Recovery berhasil."
        )

        print(
            "🏠 Instagram Home berhasil "
            "terdeteksi setelah refresh."
        )

        return True

    print()

    print(
        "⚠️ Instagram terbuka tetapi "
        "belum terdeteksi sebagai Home."
    )

    print(
        "🔄 Mencoba refresh Home 2x sekali lagi..."
    )

    time.sleep(1.0)

    if refresh_instagram_home_2x():

        time.sleep(1.0)

        screen = get_instagram_screen()

        print()

        print(
            "📱 Kondisi setelah refresh tambahan:",
            screen
        )

        if screen == "Instagram Home":

            print(
                "✅ Recovery berhasil."
            )

            return True

    print()

    print(
        "❌ Instagram terbuka tetapi Home "
        "tetap tidak terdeteksi."
    )

    return False


# =========================================================
# CEK FOREGROUND DAN RECOVERY OTOMATIS
# =========================================================

def recovery_jika_keluar_instagram():

    package = get_foreground_package()

    if (
        package
        and
        package != "com.instagram.android"
    ):

        print()

        print(
            f"🚨 Terdeteksi aplikasi lain:"
            f" {package}"
        )

        return buka_instagram_dari_android_home()

    return True


# =========================================================
# DETEKSI LAYAR INSTAGRAM
# =========================================================

def get_instagram_screen():

    package = get_foreground_package()

    if (
        package
        and
        package != "com.instagram.android"
    ):
        return "Bukan Instagram"

    xml = get_ui_xml()

    if not xml:
        return "UI Error"

    root = parse_xml(xml)

    if root is None:
        return "XML Error"

    story_viewer = False
    home_title = False
    home_feed_tab_selected = False
    reels_tab_selected = False
    reels_viewer = False
    reels_media = False
    reels_title = False
    profile_action_bar = False
    profile_container = False
    user_detail_fragment = False

    for node in root.iter("node"):

        resource_id = node.attrib.get(
            "resource-id",
            ""
        )

        content_desc = node.attrib.get(
            "content-desc",
            ""
        )

        selected = node.attrib.get(
            "selected",
            "false"
        )

        text = node.attrib.get(
            "text",
            ""
        )

        # =================================================
        # STORY
        # =================================================

        if (
            resource_id
            == "com.instagram.android:id/reel_viewer_root"
        ):
            story_viewer = True

        # =================================================
        # HOME
        # =================================================

        if (
            resource_id
            == "com.instagram.android:id/title_logo"
            and
            "Kabar Beranda Instagram"
            in content_desc
        ):
            home_title = True

        if (
            resource_id
            == "com.instagram.android:id/feed_tab"
            and
            content_desc == "Beranda"
            and
            selected == "true"
        ):
            home_feed_tab_selected = True

        # =================================================
        # REELS
        # =================================================

        if (
            resource_id
            == "com.instagram.android:id/clips_tab"
            and
            content_desc == "Reels"
            and
            selected == "true"
        ):
            reels_tab_selected = True

        if (
            resource_id
            == "com.instagram.android:id/clips_viewer_view_pager"
        ):
            reels_viewer = True

        if (
            resource_id
            == "com.instagram.android:id/clips_media_component"
        ):
            reels_media = True

        if (
            resource_id
            == "com.instagram.android:id/clips_viewer_action_bar_title"
            and
            (
                text == "Reels"
                or
                content_desc == "Reels"
            )
        ):
            reels_title = True

        # =================================================
        # PROFILE
        # =================================================

        if (
            resource_id
            == "com.instagram.android:id/profile_action_bar"
        ):
            profile_action_bar = True

        if (
            resource_id
            == "com.instagram.android:id/profile_header_container"
        ):
            profile_container = True

        if (
            resource_id
            == "com.instagram.android:id/user_detail_fragment"
        ):
            user_detail_fragment = True

    # =====================================================
    # PENTING:
    # REELS DICEK SEBELUM STORY
    #
    # Saat transisi, XML kadang bisa membawa marker
    # dari layar sebelumnya + layar berikutnya.
    #
    # Kalau ada marker Reels, kita lebih baik anggap
    # sudah Reels daripada salah menganggap Story.
    # =====================================================

    if (
        reels_viewer
        or
        reels_media
        or
        reels_title
    ):
        return "Instagram Reels"

    # =====================================================
    # STORY
    # =====================================================

    if story_viewer:
        return "Instagram Story"

    # =====================================================
    # REELS TAB
    # =====================================================

    if reels_tab_selected:
        return "Instagram Reels"

    # =====================================================
    # HOME
    # =====================================================

    if (
        home_title
        and
        home_feed_tab_selected
    ):
        return "Instagram Home"

    # =====================================================
    # PROFILE
    # =====================================================

    if (
        profile_action_bar
        or
        profile_container
        or
        user_detail_fragment
    ):
        return "Instagram Profile"

    return "Instagram - layar lain"

# =========================================================
# CARI TOMBOL HOME INSTAGRAM
# =========================================================

def cari_tombol_home():

    xml = get_ui_xml()

    if not xml:
        return None

    root = parse_xml(xml)

    if root is None:
        return None

    for node in root.iter("node"):

        resource_id = node.attrib.get(
            "resource-id",
            ""
        )

        content_desc = node.attrib.get(
            "content-desc",
            ""
        )

        clickable = node.attrib.get(
            "clickable",
            "false"
        )

        bounds = node.attrib.get(
            "bounds",
            ""
        )

        if (
            resource_id
            == "com.instagram.android:id/feed_tab"
            and
            content_desc == "Beranda"
            and
            clickable == "true"
            and
            bounds
        ):

            angka = re.findall(
                r"\d+",
                bounds
            )

            if len(angka) != 4:
                continue

            x1, y1, x2, y2 = map(
                int,
                angka
            )

            if (
                x2 <= x1
                or
                y2 <= y1
            ):
                continue

            x = (x1 + x2) // 2
            y = (y1 + y2) // 2

            return x, y

    return None


# =========================================================
# REFRESH HOME INSTAGRAM 2X
# =========================================================

def refresh_instagram_home_2x():

    print()

    berhasil = 0

    for i in range(2):

        posisi_home = cari_tombol_home()

        if posisi_home is None:

            print(
                f"❌ Icon Home Instagram "
                f"tidak ditemukan pada klik {i + 1}/2."
            )

            return False

        x, y = posisi_home

        print(
            f"🏠 Klik Home Instagram "
            f"{i + 1}/2 → ({x}, {y})"
        )

        tap(x, y)

        berhasil += 1

        time.sleep(WAIT_BACK)

    if berhasil == 2:

        print(
            "✅ Home Instagram sudah diklik 2x."
        )

        time.sleep(WAIT_REFRESH)

        return True

    return False


# =========================================================
# KEMBALI KE HOME
# =========================================================

def kembali_ke_home():

    print()

    print(
        "🏠 Recovery: menuju Home Instagram..."
    )

    for percobaan in range(
        1,
        MAX_HOME_RECOVERY_ATTEMPTS + 1
    ):

        print()

        print(
            f"🔄 Percobaan recovery Home "
            f"{percobaan}/"
            f"{MAX_HOME_RECOVERY_ATTEMPTS}"
        )

        screen = get_instagram_screen()

        print(
            "📱 Kondisi saat recovery:",
            screen
        )

        if screen == "Instagram Home":

            print(
                "✅ Sudah berada di Instagram Home."
            )

            return True

        if screen == "Bukan Instagram":

            print()

            print(
                "🚨 Recovery mendeteksi "
                "Instagram sudah keluar."
            )

            print(
                "🛟 Membuka kembali Instagram..."
            )

            berhasil = buka_instagram_dari_android_home()

            if berhasil:

                print()

                print(
                    "✅ Instagram berhasil dibuka kembali."
                )

                continue

            print()

            print(
                "❌ Gagal membuka kembali Instagram."
            )

            continue

        posisi_home = cari_tombol_home()

        if posisi_home is not None:

            x, y = posisi_home

            print()

            print(
                f"🏠 Tombol Home ditemukan "
                f"→ ({x}, {y})"
            )

            print(
                "👆 Klik Home Instagram..."
            )

            tap(x, y)

            time.sleep(WAIT_BACK)

            screen = get_instagram_screen()

            print()

            print(
                "📱 Setelah klik Home:",
                screen
            )

            if screen == "Instagram Home":

                print()

                print(
                    "✅ Berhasil kembali ke Instagram Home."
                )

                return True

            print()

            print(
                "⚠️ Sudah klik Home tetapi "
                "belum terdeteksi sebagai Home."
            )

            print(
                "➡️ Recovery akan dilanjutkan..."
            )

            continue

        print()

        print(
            "❌ Tombol Home tidak ditemukan."
        )

        print(
            "🛟 Menggunakan alternatif Back..."
        )

        tekan_back()

        screen = get_instagram_screen()

        print()

        print(
            "📱 Setelah Back:",
            screen
        )

        if screen == "Instagram Home":

            print()

            print(
                "✅ Berhasil kembali ke Instagram Home "
                "menggunakan Back."
            )

            return True

        print()

        print(
            "⚠️ Belum Home."
        )

        print(
            "➡️ Akan mencoba recovery lagi..."
        )

    print()

    print(
        "❌ Batas maksimum recovery Home tercapai."
    )

    print(
        "📱 Melakukan final check..."
    )

    final_screen = get_instagram_screen()

    print(
        "📱 Final screen:",
        final_screen
    )

    if final_screen == "Instagram Home":

        print(
            "✅ Final check memastikan sudah Home."
        )

        return True

    print(
        "❌ Posisi akhir masih belum dapat "
        "dipastikan sebagai Instagram Home."
    )

    return False


# =========================================================
# REFRESH HOME INSTAGRAM
# =========================================================

def refresh_home():

    print()

    print(
        "🔄 Refresh Instagram Home..."
    )

    adb_run(
        "shell",
        "input",
        "swipe",
        "360",
        "300",
        "360",
        "650",
        "500"
    )

    print(
        f"⏳ Menunggu {WAIT_REFRESH} detik..."
    )

    time.sleep(WAIT_REFRESH)

    print(
        "✅ Refresh selesai."
    )


# =========================================================
# CARI SEMUA STORY BELUM DILIHAT
# =========================================================

def cari_semua_story_belum_dilihat():

    xml = get_ui_xml()

    if not xml:
        return []

    root = parse_xml(xml)

    if root is None:
        return []

    stories = []

    for node in root.iter("node"):

        content_desc = node.attrib.get(
            "content-desc",
            ""
        )

        bounds = node.attrib.get(
            "bounds",
            ""
        )

        clickable = node.attrib.get(
            "clickable",
            "false"
        )

        class_name = node.attrib.get(
            "class",
            ""
        )

        if not (
            content_desc.startswith("Cerita ")
            and
            "Belum dilihat" in content_desc
            and
            bounds
        ):
            continue

        if (
            clickable != "true"
            and
            class_name != "android.widget.Button"
        ):
            continue

        angka = re.findall(
            r"\d+",
            bounds
        )

        if len(angka) != 4:
            continue

        x1, y1, x2, y2 = map(
            int,
            angka
        )

        if (
            x2 <= x1
            or
            y2 <= y1
        ):
            continue

        x = (x1 + x2) // 2
        y = (y1 + y2) // 2

        stories.append({
            "x": x,
            "y": y,
            "content_desc": content_desc,
            "bounds": bounds
        })

    unik = {}

    for story in stories:

        key = (
            story["x"],
            story["y"]
        )

        unik[key] = story

    stories = list(
        unik.values()
    )

    stories.sort(
        key=lambda story:
            story["x"]
    )

    return stories


# =========================================================
# VALIDASI STORY
#
# Dipakai untuk memastikan kalau layar benar-benar Story.
# Kalau pembacaan pertama masih terlihat Story tetapi
# sebenarnya sedang transisi ke Reels, pengecekan kedua
# akan menangkap perubahan tersebut.
# =========================================================

def validasi_story():

    screen_pertama = get_instagram_screen()

    # Kalau langsung bukan Story, jangan dianggap Story.
    if screen_pertama != "Instagram Story":

        return screen_pertama

    # Tunggu sebentar supaya transisi Instagram selesai.
    time.sleep(0.15)

    screen_kedua = get_instagram_screen()

    # Kalau berubah menjadi Reels, langsung laporkan Reels.
    if screen_kedua == "Instagram Reels":

        return "Instagram Reels"

    # Kalau berubah menjadi Home, laporkan Home.
    if screen_kedua == "Instagram Home":

        return "Instagram Home"

    # Kalau keluar Instagram.
    if screen_kedua == "Bukan Instagram":

        return "Bukan Instagram"

    # Kalau tetap Story, berarti cukup valid.
    if screen_kedua == "Instagram Story":

        return "Instagram Story"

    # Kalau layar lain.
    return screen_kedua


# =========================================================
# TONTON STORY
# =========================================================

def tonton_story():

    print()

    print(
        "📖 Mulai menonton Story..."
    )

    print(
        f"⚡ Jeda tap: "
        f"{WAIT_NEXT_STORY} detik"
    )

    jumlah_tap = 0

    while jumlah_tap < MAX_TAP_STORY:

        # =================================================
        # CEK FOREGROUND
        # =================================================

        package = get_foreground_package()

        if (
            package
            and
            package != "com.instagram.android"
        ):

            print()

            print(
                f"🚨 Instagram keluar "
                f"ke aplikasi lain: {package}"
            )

            berhasil = buka_instagram_dari_android_home()

            if berhasil:

                print()

                print(
                    "🔄 Recovery berhasil."
                )

                print(
                    "🏠 Instagram sudah kembali ke Home."
                )

                final_screen = get_instagram_screen()

                print(
                    "📱 Final check setelah recovery:",
                    final_screen
                )

                if final_screen == "Instagram Home":
                    return True

                print(
                    "⚠️ Recovery belum benar-benar Home."
                )

                berhasil = kembali_ke_home()

                if berhasil:

                    final_screen = get_instagram_screen()

                    if final_screen == "Instagram Home":
                        return True

                print(
                    "❌ Tidak berhasil memastikan Home."
                )

                return False

            print(
                "❌ Recovery gagal."
            )

            return False

        # =================================================
        # TAP STORY
        # =================================================

        tap(
            650,
            700,
            show_log=False
        )

        jumlah_tap += 1

        time.sleep(
            WAIT_NEXT_STORY
        )

        # =================================================
        # CEK SETIAP 5 TAP
        # =================================================

        if (
            jumlah_tap
            %
            CHECK_STORY_EVERY
            != 0
        ):
            continue

        # =================================================
        # VALIDASI LAYAR
        # =================================================

        screen = validasi_story()

        print(
            f"👁️ Setelah "
            f"{jumlah_tap} tap → "
            f"{screen}"
        )

        # =================================================
        # MASIH STORY
        # =================================================

        if screen == "Instagram Story":

            continue

        # =================================================
        # STORY SELESAI → HOME
        # =================================================

        if screen == "Instagram Home":

            print()

            print(
                "🏠 Story sudah selesai."
            )

            time.sleep(1)

            final_screen = get_instagram_screen()

            print(
                "📱 Final check:",
                final_screen
            )

            if final_screen == "Instagram Home":

                print(
                    "✅ Sudah dipastikan berada "
                    "di Instagram Home."
                )

                return True

            print()

            print(
                "⚠️ Final check berubah."
            )

            print(
                "🛟 Menjalankan recovery menuju Home..."
            )

            berhasil = kembali_ke_home()

            if berhasil:

                final_screen = get_instagram_screen()

                print(
                    "📱 Final check recovery:",
                    final_screen
                )

                if final_screen == "Instagram Home":

                    print(
                        "✅ Berhasil memastikan Home."
                    )

                    return True

            print(
                "❌ Gagal memastikan posisi akhir Home."
            )

            return False

        # =================================================
        # UI ERROR
        # =================================================

        if (
            screen == "UI Error"
            or
            screen == "XML Error"
        ):

            print(
                "⚠️ UI belum terbaca."
            )

            print(
                "➡️ Story dianggap masih berjalan."
            )

            continue

        # =================================================
        # KELUAR INSTAGRAM
        # =================================================

        if screen == "Bukan Instagram":

            print()

            print(
                "🚨 Story keluar dari Instagram."
            )

            berhasil = buka_instagram_dari_android_home()

            if berhasil:

                print(
                    "✅ Instagram berhasil dibuka."
                )

                final_screen = get_instagram_screen()

                print(
                    "📱 Setelah recovery:",
                    final_screen
                )

                if final_screen == "Instagram Home":
                    return True

                berhasil = kembali_ke_home()

                if berhasil:

                    final_screen = get_instagram_screen()

                    if final_screen == "Instagram Home":
                        return True

            print(
                "❌ Recovery gagal."
            )

            return False

        # =================================================
        # REELS / LAYAR LAIN
        # =================================================

        print()

        print(
            f"⚠️ Terdeteksi layar lain: {screen}"
        )

        if screen == "Instagram Reels":

            print(
                "🎬 TERDETEKSI MASUK REELS!"
            )

            print(
                "🛑 Menghentikan tap Story."
            )

            print(
                "🛟 Wajib kembali ke Instagram Home..."
            )

        else:

            print(
                "🛟 Menjalankan Recovery menuju Home..."
            )

        # =================================================
        # RECOVERY
        # =================================================

        berhasil = kembali_ke_home()

        if berhasil:

            final_screen = get_instagram_screen()

            print()

            print(
                "📱 Final check setelah recovery:",
                final_screen
            )

            if final_screen == "Instagram Home":

                print(
                    "✅ Sudah benar-benar berada di Home."
                )

                return True

        print()

        print(
            "❌ Recovery belum berhasil memastikan Home."
        )

        return False

    # =====================================================
    # MAX TAP
    # =====================================================

    print()

    print(
        "⚠️ Batas maksimum tap Story tercapai."
    )

    print(
        "🛟 Memastikan posisi akhir di Home..."
    )

    berhasil = kembali_ke_home()

    if berhasil:

        final_screen = get_instagram_screen()

        if final_screen == "Instagram Home":

            print(
                "✅ Posisi akhir dipastikan Home."
            )

            return True

    print(
        "❌ Posisi akhir tidak dapat dipastikan Home."
    )

    return False

# =========================================================
# CARI TOMBOL PROFILE INSTAGRAM
# =========================================================

def cari_tombol_profile():

    xml = get_ui_xml()

    if not xml:
        return None

    root = parse_xml(xml)

    if root is None:
        return None

    kandidat = []

    for node in root.iter("node"):

        resource_id = node.attrib.get(
            "resource-id",
            ""
        )

        content_desc = node.attrib.get(
            "content-desc",
            ""
        )

        clickable = node.attrib.get(
            "clickable",
            "false"
        )

        bounds = node.attrib.get(
            "bounds",
            ""
        )

        if (
            resource_id
            == "com.instagram.android:id/profile_tab"
            and
            clickable == "true"
            and
            bounds
        ):

            kandidat.append(node)

            continue

        if (
            content_desc.lower()
            in ["profil", "profile"]
            and
            clickable == "true"
            and
            bounds
        ):

            kandidat.append(node)

    if not kandidat:
        return None

    def posisi(node):

        bounds = node.attrib["bounds"]

        angka = re.findall(
            r"\d+",
            bounds
        )

        if len(angka) != 4:
            return 0, 0

        x1, y1, x2, y2 = map(
            int,
            angka
        )

        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2
        )

    kandidat.sort(
        key=lambda node: (
            posisi(node)[0],
            posisi(node)[1]
        ),
        reverse=True
    )

    node = kandidat[0]

    bounds = node.attrib["bounds"]

    angka = re.findall(
        r"\d+",
        bounds
    )

    if len(angka) != 4:
        return None

    x1, y1, x2, y2 = map(
        int,
        angka
    )

    if (
        x2 <= x1
        or
        y2 <= y1
    ):
        return None

    x = (x1 + x2) // 2
    y = (y1 + y2) // 2

    return {
        "x": x,
        "y": y,
        "bounds": bounds
    }


# =========================================================
# HOLD PROFILE 1 DETIK
# =========================================================

def tahan_profile_1_detik():

    print()

    print(
        "🔎 Mencari tombol Profile Instagram..."
    )

    posisi = None

    for percobaan in range(
        1,
        ACCOUNT_SWITCHER_UI_RETRY + 1
    ):

        posisi = cari_tombol_profile()

        if posisi is not None:
            break

        print(
            f"⚠️ Tombol Profile belum ditemukan "
            f"(percobaan "
            f"{percobaan}/"
            f"{ACCOUNT_SWITCHER_UI_RETRY})"
        )

        time.sleep(
            ACCOUNT_SWITCHER_UI_RETRY_DELAY
        )

    if posisi is None:

        print()

        print(
            "❌ Tombol Profile Instagram tidak ditemukan."
        )

        return False

    x = posisi["x"]
    y = posisi["y"]

    print()

    print(
        "✅ Tombol Profile ditemukan."
    )

    print(
        f"📍 Bounds: {posisi['bounds']}"
    )

    print(
        f"📍 Titik tengah: ({x}, {y})"
    )

    print()

    print(
        "👆 Menahan tombol Profile selama "
        f"{WAIT_PROFILE_HOLD} detik..."
    )

    adb_run(
        "shell",
        "input",
        "swipe",
        str(x),
        str(y),
        str(x),
        str(y),
        str(int(WAIT_PROFILE_HOLD * 1000))
    )

    print(
        "✅ Hold Profile selesai."
    )

    time.sleep(
        WAIT_ACCOUNT_SWITCHER
    )

    return True

# =========================================================
# CARI RECYCLER VIEW ACCOUNT SWITCHER
# =========================================================

def cari_recycler_view(root):

    for node in root.iter("node"):

        class_name = node.attrib.get(
            "class",
            ""
        )

        scrollable = node.attrib.get(
            "scrollable",
            "false"
        )

        if (
            class_name
            == "androidx.recyclerview.widget.RecyclerView"
            and
            scrollable == "true"
        ):

            return node

    return None


# =========================================================
# CARI AKUN TERAKHIR YANG TERLIHAT
# =========================================================

def cari_akun_terakhir(root):

    recycler = cari_recycler_view(root)

    if recycler is None:

        print(
            "❌ RecyclerView Account Switcher tidak ditemukan."
        )

        return None

    kandidat = []

    for node in recycler.iter("node"):

        class_name = node.attrib.get(
            "class",
            ""
        )

        clickable = node.attrib.get(
            "clickable",
            "false"
        )

        bounds = node.attrib.get(
            "bounds",
            ""
        )

        content_desc = node.attrib.get(
            "content-desc",
            ""
        ).strip()

        if class_name != "android.view.ViewGroup":
            continue

        if clickable != "true":
            continue

        if not bounds:
            continue

        if content_desc in [
            "Tambahkan Instagram",
            "Tutup"
        ]:
            continue

        angka = re.findall(
            r"\d+",
            bounds
        )

        if len(angka) != 4:
            continue

        x1, y1, x2, y2 = map(
            int,
            angka
        )

        if (
            x2 <= x1
            or
            y2 <= y1
        ):
            continue

        username = ""

        for child in node.iter("node"):

            child_text = child.attrib.get(
                "text",
                ""
            ).strip()

            child_desc = child.attrib.get(
                "content-desc",
                ""
            ).strip()

            if child_text:

                if (
                    "Komentar" not in child_text
                    and
                    "obrolan" not in child_text
                    and
                    "lainnya" not in child_text
                ):

                    username = child_text
                    break

            if child_desc:

                if (
                    "Komentar" not in child_desc
                    and
                    "obrolan" not in child_desc
                    and
                    "lainnya" not in child_desc
                ):

                    username = child_desc
                    break

        if not username:

            username = content_desc

        kandidat.append({
            "username": username,
            "x": (x1 + x2) // 2,
            "y": (y1 + y2) // 2,
            "bounds": bounds
        })

    if not kandidat:

        print(
            "❌ Tidak menemukan akun."
        )

        return None

    kandidat.sort(
        key=lambda akun: akun["y"]
    )

    print()

    print(
        "👥 Akun yang terlihat setelah scroll:"
    )

    for i, akun in enumerate(
        kandidat,
        start=1
    ):

        print(
            f"{i}. {akun['username']} "
            f"→ ({akun['x']}, {akun['y']})"
        )

    akun_terakhir = kandidat[-1]

    print()

    print(
        f"🎯 Akun paling bawah: "
        f"{akun_terakhir['username']}"
    )

    return akun_terakhir


# =========================================================
# SCROLL ACCOUNT SWITCHER
# =========================================================

def scroll_account_list():

    print()

    print(
        "⬇️ Scroll daftar akun sedikit ke bawah..."
    )

    adb_run(
        "shell",
        "input",
        "swipe",
        "360",
        "1000",
        "360",
        "700",
        "500"
    )

    time.sleep(1.0)

    print(
        "✅ Scroll selesai."
    )


# =========================================================
# TEKAN AKUN PALING BAWAH
# =========================================================

def tekan_akun_terakhir():

    print()

    print(
        "🔎 Mencari akun paling bawah..."
    )

    xml = get_ui_xml()

    if not xml:

        print(
            "❌ UI Account Switcher gagal dibaca."
        )

        return False

    root = parse_xml(xml)

    if root is None:

        print(
            "❌ XML Account Switcher gagal diparse."
        )

        return False

    akun = cari_akun_terakhir(root)

    if akun is None:
        return False

    print()

    print(
        f"👆 Menekan akun: "
        f"{akun['username']}"
    )

    tap(
        akun["x"],
        akun["y"]
    )

    time.sleep(
        WAIT_ACCOUNT_SWITCHER
    )

    print(
        f"✅ Akun {akun['username']} sudah ditekan."
    )

    return True

# =========================================================
# HITUNG AKUN INSTAGRAM
#
# TIDAK ADA USERNAME YANG DI-HARDCODE.
# =========================================================

def hitung_akun_instagram(xml):

    if not xml:
        return 0

    root = parse_xml(xml)

    if root is None:
        return 0

    recycler_views = []

    for node in root.iter("node"):

        class_name = node.attrib.get(
            "class",
            ""
        )

        if (
            class_name
            == "androidx.recyclerview.widget.RecyclerView"
        ):

            recycler_views.append(node)

    if not recycler_views:

        print(
            "⚠️ RecyclerView Account Switcher tidak ditemukan."
        )

        return 0

    account_recycler = None

    for recycler in recycler_views:

        if (
            recycler.attrib.get(
                "scrollable",
                "false"
            )
            == "true"
        ):

            account_recycler = recycler

            break

    if account_recycler is None:

        account_recycler = recycler_views[0]

    kandidat_akun = []

    for node in account_recycler.iter("node"):

        class_name = node.attrib.get(
            "class",
            ""
        )

        content_desc = node.attrib.get(
            "content-desc",
            ""
        ).strip()

        clickable = node.attrib.get(
            "clickable",
            "false"
        )

        long_clickable = node.attrib.get(
            "long-clickable",
            "false"
        )

        bounds = node.attrib.get(
            "bounds",
            ""
        )

        selected = node.attrib.get(
            "selected",
            "false"
        )

        if class_name != "android.view.ViewGroup":
            continue

        if clickable != "true":
            continue

        if long_clickable != "true":
            continue

        if not content_desc:
            continue

        if content_desc in [
            "Tambahkan Instagram",
            "Tutup"
        ]:
            continue

        if not bounds:
            continue

        angka = re.findall(
            r"\d+",
            bounds
        )

        if len(angka) != 4:
            continue

        x1, y1, x2, y2 = map(
            int,
            angka
        )

        if (
            x2 <= x1
            or
            y2 <= y1
        ):
            continue

        username_text = ""

        for child in node.iter("node"):

            child_text = child.attrib.get(
                "text",
                ""
            ).strip()

            child_content_desc = child.attrib.get(
                "content-desc",
                ""
            ).strip()

            child_class = child.attrib.get(
                "class",
                ""
            )

            if (
                child_class == "android.view.View"
                and
                child_text
            ):

                username_text = child_text

                break

            if (
                child_class == "android.view.View"
                and
                child_content_desc
            ):

                username_text = child_content_desc

                break

            if (
                child_class == "android.widget.TextView"
                and
                child_text
            ):

                username_text = child_text

                break

        if not username_text:
            continue

        kandidat_akun.append({
            "username": username_text,
            "bounds": bounds,
            "selected": selected,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })

    unik = {}

    for akun in kandidat_akun:

        key = (
            akun["username"],
            akun["x1"],
            akun["y1"],
            akun["x2"],
            akun["y2"]
        )

        unik[key] = akun

    kandidat_akun = list(
        unik.values()
    )

    kandidat_akun.sort(
        key=lambda akun: (
            akun["y1"],
            akun["x1"]
        )
    )

    jumlah_akun = len(
        kandidat_akun
    )

    print()

    print(
        "========================================================="
    )

    print(
        "📊 HASIL ANALISIS ACCOUNT SWITCHER"
    )

    print(
        "========================================================="
    )

    print()

    print(
        f"👥 Kandidat node akun: {jumlah_akun}"
    )

    print()

    if jumlah_akun == 0:

        print(
            "⚠️ Tidak ada node akun yang cocok."
        )

        print(
            "➡️ Struktur Account Switcher mungkin berubah."
        )

    else:

        for i, akun in enumerate(
            kandidat_akun,
            start=1
        ):

            status = ""

            if akun["selected"] == "true":
                status = " ← AKUN AKTIF"

            print(
                f"{i}. {akun['username']}"
                f"{status}"
            )

            print(
                f"   📍 {akun['bounds']}"
            )

    print()

    print(
        "========================================================="
    )

    print(
        f"🎯 TOTAL AKUN INSTAGRAM: {jumlah_akun}"
    )

    print(
        "========================================================="
    )

    return jumlah_akun


# =========================================================
# BUKA ACCOUNT SWITCHER DAN HITUNG AKUN
#
# PERBAIKAN PENTING:
#
# Fungsi ini TIDAK lagi menggunakan
# get_foreground_package() sebagai syarat awal.
#
# Kalau foreground terbaca kosong:
#     TIDAK ADA RECOVERY.
#
# Kita hanya percaya pada screen detector.
#
# Karena sebelum fungsi ini dipanggil, program sudah
# memastikan Instagram berada di Home.
# =========================================================

def proses_account_switcher_akhir():

    print()

    print(
        "========================================================="
    )

    print(
        "👥 PROSES DETEKSI JUMLAH AKUN INSTAGRAM"
    )

    print(
        "========================================================="
    )

    # =====================================================
    # LANGSUNG CEK SCREEN
    #
    # TIDAK CEK FOREGROUND PACKAGE DI SINI.
    #
    # Ini yang mencegah:
    #
    # Foreground kosong
    #       ↓
    # dianggap keluar Instagram
    #       ↓
    # Android Home
    #       ↓
    # buka Instagram lagi
    #
    # =====================================================

    print()

    screen = get_instagram_screen()

    print(
        "📱 Screen sebelum Account Switcher:",
        screen
    )

    # =====================================================
    # KALAU MEMANG SUDAH HOME
    # LANGSUNG LANJUT KE PROFILE.
    # =====================================================

    if screen == "Instagram Home":

        print()

        print(
            "✅ Instagram Home sudah terdeteksi."
        )

        print(
            "➡️ Tidak menjalankan recovery."
        )

    else:

        # =================================================
        # HANYA RECOVERY KALAU SCREEN MEMANG BUKAN HOME
        # =================================================

        print()

        print(
            "⚠️ Screen belum Instagram Home."
        )

        print(
            "🛟 Memastikan Home terlebih dahulu..."
        )

        berhasil = kembali_ke_home()

        if not berhasil:

            print()

            print(
                "❌ Gagal memastikan Instagram Home."
            )

            return 0

        # =================================================
        # FINAL CHECK SETELAH RECOVERY
        # =================================================

        screen = get_instagram_screen()

        print()

        print(
            "📱 Screen setelah memastikan Home:",
            screen
        )

        if screen != "Instagram Home":

            print()

            print(
                "❌ Instagram Home belum dapat dipastikan."
            )

            return 0

        print()

        print(
            "✅ Instagram Home berhasil dipastikan."
        )

    # =====================================================
    # HOLD PROFILE
    # =====================================================

    print()

    print(
        "🏠 Instagram Home sudah dipastikan."
    )

    berhasil = tahan_profile_1_detik()

    if not berhasil:

        print()

        print(
            "❌ Gagal melakukan hold Profile."
        )

        return 0

    # =====================================================
    # ACCOUNT SWITCHER SUDAH DIBUKA
    # =====================================================

    print()

    print(
        "🔍 Membaca Account Switcher..."
    )

    # =====================================================
    # AMBIL UI ACCOUNT SWITCHER
    # =====================================================

    for percobaan in range(
        1,
        ACCOUNT_SWITCHER_UI_RETRY + 1
    ):

        print()

        print(
            f"🔎 Membaca Account Switcher "
            f"{percobaan}/"
            f"{ACCOUNT_SWITCHER_UI_RETRY}..."
        )

        xml = get_ui_xml()

        if xml:

            jumlah = hitung_akun_instagram(xml)

            if jumlah > 0:

                print()

                print(
                    "✅ Account Switcher berhasil dibaca."
                )

                print()

                print(
                    f"🎯 TOTAL AKUN INSTAGRAM: {jumlah}"
                )

                return jumlah

        print(
            "⚠️ Account Switcher belum terbaca."
        )

        if percobaan < ACCOUNT_SWITCHER_UI_RETRY:

            time.sleep(
                ACCOUNT_SWITCHER_UI_RETRY_DELAY
            )

    print()

    print(
        "❌ Jumlah akun Instagram gagal dideteksi."
    )

    return 0


# =========================================================
# PROGRAM UTAMA
# =========================================================

print()

print(
    "🚀 Instagram Story Bot dimulai..."
)


# =========================================================
# STARTUP HP
# =========================================================

startup_hp()


# =========================================================
# CEK APLIKASI AKTIF SEBELUM REFRESH AWAL
# =========================================================

print()

print(
    "🔍 Mengecek aplikasi aktif..."
)

package_awal = get_foreground_package()

print(
    "📱 Aplikasi aktif:",
    package_awal or "tidak diketahui"
)


# =========================================================
# KALAU BUKAN INSTAGRAM → RECOVERY DULU
# =========================================================

if package_awal != "com.instagram.android":

    print()

    print(
        "⚠️ Aplikasi aktif bukan Instagram."
    )

    print(
        "🛟 Langsung menjalankan recovery..."
    )

    berhasil = buka_instagram_dari_android_home()

    if not berhasil:

        print()

        print(
            "❌ Recovery awal gagal."
        )

        print(
            "🛑 Program dihentikan."
        )

        raise SystemExit

    print()

    print(
        "✅ Instagram berhasil dibuka."
    )

    print(
        "🏠 Home Instagram sudah diklik 2x."
    )

else:

    print()

    print(
        "✅ Instagram terdeteksi sebagai "
        "aplikasi aktif."
    )


# =========================================================
# REFRESH AWAL
# =========================================================

print()

print(
    "🔄 Refresh awal Instagram..."
)

refresh_home()


# =========================================================
# CEK POSISI
# =========================================================

print()

print(
    "🔍 Mengecek posisi Instagram..."
)

screen = get_instagram_screen()

print(
    "📱 Kondisi awal:",
    screen
)


# =========================================================
# KALAU KELUAR DARI INSTAGRAM
# =========================================================

if screen == "Bukan Instagram":

    print()

    print(
        "🚨 Ternyata Instagram sudah keluar "
        "lagi dari foreground."
    )

    print(
        "🛟 Menjalankan recovery ulang..."
    )

    berhasil = buka_instagram_dari_android_home()

    if not berhasil:

        print(
            "❌ Recovery awal gagal."
        )

        raise SystemExit

    screen = get_instagram_screen()

    print(
        "📱 Setelah recovery:",
        screen
    )


# =========================================================
# KALAU BUKAN HOME
# =========================================================

if screen != "Instagram Home":

    print()

    print(
        "⚠️ Posisi awal bukan Home."
    )

    print(
        "🛟 Menjalankan Recovery..."
    )

    berhasil = kembali_ke_home()

    if not berhasil:

        print()

        print(
            "❌ Tidak berhasil kembali ke Home."
        )

        print(
            "➡️ Buka Instagram → Home secara manual."
        )

        raise SystemExit

    print()

    print(
        "✅ Posisi awal sudah kembali ke Home."
    )


# =========================================================
# CEK STORY AWAL
# =========================================================

print()

print(
    "🔎 Mengecek Story setelah Home dipastikan..."
)

stories_awal = cari_semua_story_belum_dilihat()

print()

print(
    f"📊 Story belum dilihat: "
    f"{len(stories_awal)}"
)


# =========================================================
# TIDAK ADA STORY
# =========================================================

if not stories_awal:

    print()

    print(
        "✅ Tidak ada Story yang belum dilihat."
    )

    print(
        "🏠 Posisi akhir: Instagram Home."
    )

    print(
        "➡️ Program akan lanjut ke proses akhir."
    )

    print()

# =========================================================
# PINDAH KE AKUN BERIKUTNYA
#
# Dipakai setelah akun sebelumnya selesai diproses.
# =========================================================

def pindah_ke_akun_berikutnya():

    print()

    print(
        "🔄 Mempersiapkan perpindahan ke akun berikutnya..."
    )

    # =====================================================
    # WAJIB PASTIKAN INSTAGRAM HOME
    # =====================================================

    screen = get_instagram_screen()

    print(
        "📱 Kondisi sebelum pindah akun:",
        screen
    )

    if screen != "Instagram Home":

        print()

        print(
            "⚠️ Belum berada di Instagram Home."
        )

        print(
            "🛟 Recovery sampai benar-benar Home..."
        )

        berhasil = kembali_ke_home()

        if not berhasil:

            print(
                "❌ Gagal kembali ke Home."
            )

            return False

        # =================================================
        # CEK ULANG SETELAH RECOVERY
        # =================================================

        screen = get_instagram_screen()

        print(
            "📱 Kondisi setelah recovery:",
            screen
        )

        if screen != "Instagram Home":

            print(
                "❌ Home belum dapat dipastikan."
            )

            return False

    # =====================================================
    # DI SINI BARU BOLEH HOLD PROFILE
    # =====================================================

    print()

    print(
        "✅ Instagram Home sudah dipastikan."
    )

    print()

    print(
        "👥 Membuka Account Switcher..."
    )

    berhasil = tahan_profile_1_detik()

    if not berhasil:

        print(
            "❌ Gagal membuka Account Switcher."
        )

        return False

    # =====================================================
    # SCROLL ACCOUNT SWITCHER
    # =====================================================

    scroll_account_list()

    # =====================================================
    # PILIH AKUN PALING BAWAH
    # =====================================================

    berhasil = tekan_akun_terakhir()

    if not berhasil:

        print(
            "❌ Gagal memilih akun berikutnya."
        )

        return False

    # =====================================================
    # TUNGGU AKUN MASUK
    # =====================================================

    time.sleep(
        WAIT_ACCOUNT_SWITCHER
    )

    screen = get_instagram_screen()

    print()

    print(
        "📱 Screen setelah pindah akun:",
        screen
    )

    # =====================================================
    # WAJIB HOME SETELAH PINDAH AKUN
    # =====================================================

    if screen != "Instagram Home":

        print()

        print(
            "⚠️ Setelah pindah akun belum Home."
        )

        print(
            "🛟 Recovery menuju Home..."
        )

        berhasil = kembali_ke_home()

        if not berhasil:

            print(
                "❌ Gagal memastikan Home setelah pindah akun."
            )

            return False

        # =================================================
        # FINAL CHECK SETELAH RECOVERY
        # =================================================

        screen = get_instagram_screen()

        print(
            "📱 Final check setelah recovery:",
            screen
        )

        if screen != "Instagram Home":

            print(
                "❌ Home masih belum dapat dipastikan."
            )

            return False

    print()

    print(
        "✅ Berhasil pindah akun."
    )

    print(
        "🏠 Posisi sudah dipastikan Instagram Home."
    )

    return True

# =========================================================
# STATE PROGRAM
# =========================================================

jumlah_refresh = 1
story_selesai = False
sudah_refresh_awal = True
sudah_refresh_setelah_story = False


# =========================================================
# LOOP UTAMA
# =========================================================

while True:

    screen = get_instagram_screen()

    print()

    print(
        "📱 Kondisi HP:",
        screen
    )

    # =====================================================
    # KALAU KELUAR DARI INSTAGRAM
    # =====================================================

    if screen == "Bukan Instagram":

        print()

        print(
            "🚨 Instagram tidak lagi menjadi "
            "aplikasi aktif."
        )

        print(
            "🛟 Menjalankan recovery..."
        )

        berhasil = buka_instagram_dari_android_home()

        if berhasil:

            print(
                "✅ Instagram kembali."
            )

            print(
                "🏠 Home Instagram sudah diklik 2x."
            )

            story_selesai = False

            continue

        print(
            "❌ Recovery gagal."
        )

        break

    # =====================================================
    # HOME
    # =====================================================

    if screen == "Instagram Home":

        print(
            "🏠 Instagram Home terdeteksi."
        )

        if story_selesai:

            if not sudah_refresh_setelah_story:

                jumlah_refresh += 1

                sudah_refresh_setelah_story = True

                print()

                print(
                    f"🔄 Refresh ke-"
                    f"{jumlah_refresh}/"
                    f"{MAX_REFRESH}"
                )

                refresh_home()

                stories = (
                    cari_semua_story_belum_dilihat()
                )

                print()

                print(
                    f"🔎 Setelah refresh, "
                    f"Story belum dilihat: "
                    f"{len(stories)}"
                )

                if stories:

                    print(
                        "📌 Story ditemukan setelah refresh."
                    )

                    story = stories[0]

                    print()

                    print(
                        "🎯 Membuka Story terakhir:"
                    )

                    print(
                        "📌",
                        story["content_desc"]
                    )

                    print(
                        "📍",
                        story["x"],
                        story["y"]
                    )

                    tap(
                        story["x"],
                        story["y"]
                    )

                    time.sleep(
                        WAIT_OPEN_STORY
                    )

                    berhasil = tonton_story()

                    if berhasil:

                        final_screen = get_instagram_screen()

                        print()

                        print(
                            "📱 Final check program:",
                            final_screen
                        )

                        if final_screen == "Instagram Home":

                            print()

                            print(
                                "🏁 Story terakhir selesai."
                            )

                            print(
                                "🏠 Posisi akhir sudah "
                                "dipastikan Home."
                            )

                            print(
                                "🛑 Tidak ada refresh lagi."
                            )

                            print(
                                "🎉 Program selesai."
                            )

                        else:

                            print()

                            print(
                                "⚠️ Story terakhir selesai "
                                "tetapi belum Home."
                            )

                            print(
                                "🛟 Memastikan Home sebelum program selesai..."
                            )

                            home_berhasil = kembali_ke_home()

                            if home_berhasil:

                                final_screen = get_instagram_screen()

                                print()

                                print(
                                    "📱 Final check:",
                                    final_screen
                                )

                                if final_screen == "Instagram Home":

                                    print(
                                        "🏠 Home berhasil dipastikan."
                                    )

                                    print(
                                        "🎉 Program selesai."
                                    )

                                else:

                                    print(
                                        "❌ Home masih belum dapat dipastikan."
                                    )

                            else:

                                print(
                                    "❌ Gagal memastikan posisi akhir Home."
                                )

                    else:

                        print()

                        print(
                            "❌ Story terakhir gagal."
                        )

                    break

                print(
                    "✅ Tidak ada Story baru."
                )

                print(
                    "🏠 Posisi tetap di Home."
                )

                print(
                    "🛑 Program selesai."
                )

                break

            else:

                print(
                    "🛑 Refresh setelah Story "
                    "sudah dilakukan."
                )

                break

        stories = (
            cari_semua_story_belum_dilihat()
        )

        print(
            f"🔎 Story belum dilihat: "
            f"{len(stories)}"
        )

        if stories:

            story = stories[0]

            print()

            print(
                "🎯 Membuka Story pertama:"
            )

            print(
                "📌",
                story["content_desc"]
            )

            print(
                "📍",
                story["x"],
                story["y"]
            )

            tap(
                story["x"],
                story["y"]
            )

            time.sleep(
                WAIT_OPEN_STORY
            )

            berhasil = tonton_story()

            if berhasil:

                story_selesai = True

                time.sleep(0.5)

                continue

            print(
                "❌ Story pertama gagal."
            )

            break

        else:

            print(
                "✅ Tidak ada Story "
                "'Belum dilihat'."
            )

            print(
                "🏠 Posisi akhir: Home."
            )

            break

    # =====================================================
    # STORY
    # =====================================================

    elif screen == "Instagram Story":

        print(
            "📖 Saat ini berada di Story."
        )

        berhasil = tonton_story()

        if berhasil:

            story_selesai = True

            time.sleep(0.5)

            continue

        print(
            "❌ Story gagal diselesaikan."
        )

        break

    # =====================================================
    # UI ERROR
    # =====================================================

    elif (
        screen == "UI Error"
        or
        screen == "XML Error"
    ):

        print()

        print(
            "⚠️ UI Instagram belum terbaca."
        )

        print(
            "🔄 Akan mencoba lagi..."
        )

        time.sleep(1)

        continue

    # =====================================================
    # SELAIN HOME / STORY
    # =====================================================

    else:

        print()

        print(
            f"⚠️ Bukan Home: {screen}"
        )

        print(
            "🛟 Menjalankan Recovery..."
        )

        berhasil = kembali_ke_home()

        if berhasil:

            print(
                "✅ Recovery berhasil."
            )

            story_selesai = False

            continue

        print()

        print(
            "❌ Recovery gagal."
        )

        break


# =========================================================
# SELESAI
#
# SEBELUM PROGRAM BENAR-BENAR SELESAI:
#
# 1. Pastikan Home
# 2. Cari Profile
# 3. Hold Profile 1 detik
# 4. Buka Account Switcher
# 5. Hitung jumlah akun
# =========================================================

print()

print(
    "========================================================="
)

print(
    "🏁 MENJALANKAN PROSES AKHIR PROGRAM..."
)

print(
    "========================================================="
)


# =========================================================
# PASTIKAN HOME SEKALI LAGI
# =========================================================

final_screen = get_instagram_screen()

print()

print(
    "📱 Screen sebelum proses akhir:",
    final_screen
)

if final_screen != "Instagram Home":

    print()

    print(
        "⚠️ Posisi akhir belum Home."
    )

    print(
        "🛟 Memastikan Home sebelum Account Switcher..."
    )

    home_final = kembali_ke_home()

    if home_final:

        final_screen = get_instagram_screen()

        print()

        print(
            "📱 Screen setelah recovery akhir:",
            final_screen
        )

    else:

        print()

        print(
            "❌ Gagal memastikan Home."
        )


# =========================================================
# ACCOUNT SWITCHER
# =========================================================

jumlah_akun_akhir = proses_account_switcher_akhir()

print()

if jumlah_akun_akhir > 0:

    print(
        "========================================================="
    )

    print(
        f"👥 TOTAL AKUN INSTAGRAM: {jumlah_akun_akhir}"
    )

    print(
        "========================================================="
    )

else:

    print(
        "⚠️ Jumlah akun Instagram tidak berhasil dideteksi."
    )


# =========================================================
# PENGULANGAN AKUN INSTAGRAM
#
# AKUN PERTAMA SUDAH DIPROSES.
# AKUN BERIKUTNYA AKAN DIPROSES DI SINI.
# =========================================================

if jumlah_akun_akhir > 1:

    print()

    print(
        "========================================================="
    )

    print(
        "👥 MEMULAI PENGULANGAN AKUN INSTAGRAM"
    )

    print(
        "========================================================="
    )

    # Akun pertama SUDAH diproses.
    # Jadi sisa akun = total akun - 1.
    sisa_akun = jumlah_akun_akhir - 1

    print()

    print(
        f"🔢 Total akun Instagram: "
        f"{jumlah_akun_akhir}"
    )

    print(
        f"✅ Akun pertama sudah diproses."
    )

    print(
        f"🔢 Sisa akun yang harus diproses: "
        f"{sisa_akun}"
    )

       # =====================================================
    # LOOP AKUN
    # =====================================================

    for putaran in range(1, sisa_akun + 1):

        print()

        print(
            "========================================================="
        )

        print(
            f"👥 PENGULANGAN AKUN "
            f"{putaran}/{sisa_akun}"
        )

        print(
            "========================================================="
        )

        # =====================================================
        # PUTARAN PERTAMA
        # =====================================================

        if putaran == 1:

            print()

            print(
                "📌 Account Switcher masih terbuka."
            )

            print(
                "⬇️ Langsung scroll ke bawah..."
            )

            scroll_account_list()

            print()

            print(
                "👆 Memilih akun paling bawah..."
            )

            berhasil = tekan_akun_terakhir()

            if not berhasil:

                print(
                    "❌ Gagal memilih akun."
                )

                break

        # =====================================================
        # PUTARAN SELANJUTNYA
        # =====================================================

        else:

            berhasil = pindah_ke_akun_berikutnya()

            if not berhasil:

                print(
                    "❌ Gagal pindah ke akun berikutnya."
                )

                break

        # =====================================================
        # PASTIKAN HOME
        # =====================================================

        time.sleep(
            WAIT_ACCOUNT_SWITCHER
        )

        screen = get_instagram_screen()

        print()

        print(
            "📱 Kondisi akun setelah dipilih:",
            screen
        )

        if screen != "Instagram Home":

            print(
                "🛟 Memastikan kembali ke Home..."
            )

            berhasil = kembali_ke_home()

            if not berhasil:

                print(
                    "❌ Gagal memastikan Home."
                )

                break

        # =====================================================
        # PROSES STORY AKUN INI
        # =====================================================

        print()

        print(
            "🔎 Mengecek Story akun ini..."
        )

        stories_akun = cari_semua_story_belum_dilihat()

        print()

        print(
            f"📊 Story belum dilihat: "
            f"{len(stories_akun)}"
        )

        if stories_akun:

            story = stories_akun[0]

            print()

            print(
                "🎯 Membuka Story:"
            )

            print(
                "📌",
                story["content_desc"]
            )

            print(
                "📍",
                story["x"],
                story["y"]
            )

            tap(
                story["x"],
                story["y"]
            )

            time.sleep(
                WAIT_OPEN_STORY
            )

            berhasil = tonton_story()

            if not berhasil:

                print(
                    "❌ Story akun ini gagal diproses."
                )

                break

            print()

            print(
                "✅ Story akun ini selesai."
            )

        else:

            print()

            print(
                "✅ Tidak ada Story belum dilihat."
            )

        # =====================================================
        # PASTIKAN KEMBALI KE HOME
        # =====================================================

        berhasil = kembali_ke_home()

        if not berhasil:

            print(
                "❌ Gagal kembali ke Home."
            )

            break

        print()

        print(
            f"✅ AKUN {putaran}/{sisa_akun} SELESAI."
        )

else:

    print()

    print(
        "👤 Hanya ada 1 akun Instagram."
    )

    print(
        "➡️ Tidak ada pengulangan akun."
    )


print()

print(
    "🎉 PROGRAM SELESAI."
)