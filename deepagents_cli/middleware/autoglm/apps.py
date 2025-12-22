"""App name to package name mapping for Android applications.

This module provides mappings between user-friendly app names and their Android package names.
Used by the phone agent to launch apps using the Launch action.

Source: Adapted from Open-AutoGLM project
Original: https://github.com/zai-org/Open-AutoGLM
File: phone_agent/config/apps.py

The mapping includes:
- Chinese apps (微信, 淘宝, 抖音, etc.)
- International apps (Chrome, Gmail, WhatsApp, etc.)
- System apps (Settings, Clock, Contacts, etc.)
- Multiple name variations for the same app (case-insensitive, with/without spaces, etc.)
"""

# Comprehensive app name to package name mapping
APP_PACKAGES: dict[str, str] = {
    # ========== Chinese Social & Messaging ==========
    "微信": "com.tencent.mm",
    "QQ": "com.tencent.mobileqq",
    "微博": "com.sina.weibo",
    # ========== Chinese E-commerce ==========
    "淘宝": "com.taobao.taobao",
    "京东": "com.jingdong.app.mall",
    "拼多多": "com.xunmeng.pinduoduo",
    "淘宝闪购": "com.taobao.taobao",
    "京东秒送": "com.jingdong.app.mall",
    # ========== Chinese Lifestyle & Social ==========
    "小红书": "com.xingin.xhs",
    "豆瓣": "com.douban.frodo",
    "知乎": "com.zhihu.android",
    # ========== Chinese Maps & Navigation ==========
    "高德地图": "com.autonavi.minimap",
    "百度地图": "com.baidu.BaiduMap",
    # ========== Chinese Food & Services ==========
    "美团": "com.sankuai.meituan",
    "大众点评": "com.dianping.v1",
    "饿了么": "me.ele",
    "肯德基": "com.yek.android.kfc.activitys",
    # ========== Chinese Travel ==========
    "携程": "ctrip.android.view",
    "铁路12306": "com.MobileTicket",
    "12306": "com.MobileTicket",
    "去哪儿": "com.Qunar",
    "去哪儿旅行": "com.Qunar",
    "滴滴出行": "com.sdu.didi.psnger",
    # ========== Chinese Video & Entertainment ==========
    "bilibili": "tv.danmaku.bili",
    "抖音": "com.ss.android.ugc.aweme",
    "快手": "com.smile.gifmaker",
    "腾讯视频": "com.tencent.qqlive",
    "爱奇艺": "com.qiyi.video",
    "优酷视频": "com.youku.phone",
    "芒果TV": "com.hunantv.imgo.activity",
    "红果短剧": "com.phoenix.read",
    # ========== Chinese Music & Audio ==========
    "网易云音乐": "com.netease.cloudmusic",
    "QQ音乐": "com.tencent.qqmusic",
    "汽水音乐": "com.luna.music",
    "喜马拉雅": "com.ximalaya.ting.android",
    # ========== Chinese Reading ==========
    "番茄小说": "com.dragon.read",
    "番茄免费小说": "com.dragon.read",
    "七猫免费小说": "com.kmxs.reader",
    # ========== Chinese Productivity ==========
    "飞书": "com.ss.android.lark",
    "QQ邮箱": "com.tencent.androidqqmail",
    # ========== Chinese AI & Tools ==========
    "豆包": "com.larus.nova",
    # ========== Chinese Health & Fitness ==========
    "keep": "com.gotokeep.keep",
    "美柚": "com.lingan.seeyou",
    # ========== Chinese News & Information ==========
    "腾讯新闻": "com.tencent.news",
    "今日头条": "com.ss.android.article.news",
    # ========== Chinese Real Estate ==========
    "贝壳找房": "com.lianjia.beike",
    "安居客": "com.anjuke.android.app",
    # ========== Chinese Finance ==========
    "同花顺": "com.hexin.plat.android",
    # ========== Chinese Games ==========
    "星穹铁道": "com.miHoYo.hkrpg",
    "崩坏：星穹铁道": "com.miHoYo.hkrpg",
    "恋与深空": "com.papegames.lysk.cn",
    # ========== Android System Apps ==========
    "AndroidSystemSettings": "com.android.settings",
    "Android System Settings": "com.android.settings",
    "Android  System Settings": "com.android.settings",
    "Android-System-Settings": "com.android.settings",
    "Settings": "com.android.settings",
    "AudioRecorder": "com.android.soundrecorder",
    "audiorecorder": "com.android.soundrecorder",
    "Clock": "com.android.deskclock",
    "clock": "com.android.deskclock",
    "Contacts": "com.android.contacts",
    "contacts": "com.android.contacts",
    "Files": "com.android.fileexplorer",
    "files": "com.android.fileexplorer",
    "File Manager": "com.android.fileexplorer",
    "file manager": "com.android.fileexplorer",
    # ========== Finance & Productivity Apps ==========
    "Bluecoins": "com.rammigsoftware.bluecoins",
    "bluecoins": "com.rammigsoftware.bluecoins",
    "Broccoli": "com.flauschcode.broccoli",
    "broccoli": "com.flauschcode.broccoli",
    # ========== Travel & Booking Apps ==========
    "Booking.com": "com.booking",
    "Booking": "com.booking",
    "booking.com": "com.booking",
    "booking": "com.booking",
    "BOOKING.COM": "com.booking",
    "Expedia": "com.expedia.bookings",
    "expedia": "com.expedia.bookings",
    # ========== Google Apps ==========
    "Chrome": "com.android.chrome",
    "chrome": "com.android.chrome",
    "Google Chrome": "com.android.chrome",
    "gmail": "com.google.android.gm",
    "Gmail": "com.google.android.gm",
    "GoogleMail": "com.google.android.gm",
    "Google Mail": "com.google.android.gm",
    "GoogleFiles": "com.google.android.apps.nbu.files",
    "googlefiles": "com.google.android.apps.nbu.files",
    "FilesbyGoogle": "com.google.android.apps.nbu.files",
    "GoogleCalendar": "com.google.android.calendar",
    "Google-Calendar": "com.google.android.calendar",
    "Google Calendar": "com.google.android.calendar",
    "google-calendar": "com.google.android.calendar",
    "google calendar": "com.google.android.calendar",
    "GoogleChat": "com.google.android.apps.dynamite",
    "Google Chat": "com.google.android.apps.dynamite",
    "Google-Chat": "com.google.android.apps.dynamite",
    "GoogleClock": "com.google.android.deskclock",
    "Google Clock": "com.google.android.deskclock",
    "Google-Clock": "com.google.android.deskclock",
    "GoogleContacts": "com.google.android.contacts",
    "Google-Contacts": "com.google.android.contacts",
    "Google Contacts": "com.google.android.contacts",
    "google-contacts": "com.google.android.contacts",
    "google contacts": "com.google.android.contacts",
    "GoogleDocs": "com.google.android.apps.docs.editors.docs",
    "Google Docs": "com.google.android.apps.docs.editors.docs",
    "googledocs": "com.google.android.apps.docs.editors.docs",
    "google docs": "com.google.android.apps.docs.editors.docs",
    "Google Drive": "com.google.android.apps.docs",
    "Google-Drive": "com.google.android.apps.docs",
    "google drive": "com.google.android.apps.docs",
    "google-drive": "com.google.android.apps.docs",
    "GoogleDrive": "com.google.android.apps.docs",
    "Googledrive": "com.google.android.apps.docs",
    "googledrive": "com.google.android.apps.docs",
    "GoogleFit": "com.google.android.apps.fitness",
    "googlefit": "com.google.android.apps.fitness",
    "GoogleKeep": "com.google.android.keep",
    "googlekeep": "com.google.android.keep",
    "GoogleMaps": "com.google.android.apps.maps",
    "Google Maps": "com.google.android.apps.maps",
    "googlemaps": "com.google.android.apps.maps",
    "google maps": "com.google.android.apps.maps",
    "Google Play Books": "com.google.android.apps.books",
    "Google-Play-Books": "com.google.android.apps.books",
    "google play books": "com.google.android.apps.books",
    "google-play-books": "com.google.android.apps.books",
    "GooglePlayBooks": "com.google.android.apps.books",
    "googleplaybooks": "com.google.android.apps.books",
    "GooglePlayStore": "com.android.vending",
    "Google Play Store": "com.android.vending",
    "Google-Play-Store": "com.android.vending",
    "GoogleSlides": "com.google.android.apps.docs.editors.slides",
    "Google Slides": "com.google.android.apps.docs.editors.slides",
    "Google-Slides": "com.google.android.apps.docs.editors.slides",
    "GoogleTasks": "com.google.android.apps.tasks",
    "Google Tasks": "com.google.android.apps.tasks",
    "Google-Tasks": "com.google.android.apps.tasks",
    # ========== Education & Learning ==========
    "Duolingo": "com.duolingo",
    "duolingo": "com.duolingo",
    # ========== Notes & Organization ==========
    "Joplin": "net.cozic.joplin",
    "joplin": "net.cozic.joplin",
    # ========== Food Delivery ==========
    "McDonald": "com.mcdonalds.app",
    "mcdonald": "com.mcdonalds.app",
    # ========== Maps & Navigation ==========
    "Osmand": "net.osmand",
    "osmand": "net.osmand",
    # ========== Music Players ==========
    "PiMusicPlayer": "com.Project100Pi.themusicplayer",
    "pimusicplayer": "com.Project100Pi.themusicplayer",
    "RetroMusic": "code.name.monkey.retromusic",
    "retromusic": "code.name.monkey.retromusic",
    # ========== Social Media ==========
    "Quora": "com.quora.android",
    "quora": "com.quora.android",
    "Reddit": "com.reddit.frontpage",
    "reddit": "com.reddit.frontpage",
    "Telegram": "org.telegram.messenger",
    "temu": "com.einnovation.temu",
    "Temu": "com.einnovation.temu",
    "Tiktok": "com.zhiliaoapp.musically",
    "tiktok": "com.zhiliaoapp.musically",
    "Twitter": "com.twitter.android",
    "twitter": "com.twitter.android",
    "X": "com.twitter.android",
    "WeChat": "com.tencent.mm",
    "wechat": "com.tencent.mm",
    "Whatsapp": "com.whatsapp",
    "WhatsApp": "com.whatsapp",
    # ========== Utilities ==========
    "SimpleCalendarPro": "com.scientificcalculatorplus.simplecalculator.basiccalculator.mathcalc",
    "SimpleSMSMessenger": "com.simplemobiletools.smsmessenger",
    "VLC": "org.videolan.vlc",
}


def get_package_name(app_name: str) -> str | None:
    """Get the Android package name for an app by its display name.

    This function performs a case-sensitive lookup in the APP_PACKAGES dictionary.
    For case-insensitive or fuzzy matching, use find_package_name() instead.

    Args:
        app_name: The display name of the app (e.g., "微信", "Chrome", "Gmail").

    Returns:
        The Android package name (e.g., "com.tencent.mm") if found, None otherwise.

    Examples:
        >>> get_package_name("微信")
        "com.tencent.mm"
        >>> get_package_name("Chrome")
        "com.android.chrome"
        >>> get_package_name("NonExistentApp")
        None
    """
    return APP_PACKAGES.get(app_name)


def find_package_name(app_name: str) -> str | None:
    """Find the Android package name for an app with fuzzy matching.

    This function tries multiple strategies to find the app:
    1. Exact match (case-sensitive)
    2. Case-insensitive match
    3. Match after removing spaces and special characters

    Args:
        app_name: The display name of the app.

    Returns:
        The Android package name if found, None otherwise.

    Examples:
        >>> find_package_name("chrome")  # Lowercase
        "com.android.chrome"
        >>> find_package_name("google maps")  # Lowercase with space
        "com.google.android.apps.maps"
        >>> find_package_name("Gmail")  # Mixed case
        "com.google.android.gm"
    """
    # Try exact match first
    package = APP_PACKAGES.get(app_name)
    if package:
        return package

    # Try case-insensitive match
    app_name_lower = app_name.lower()
    for name, package in APP_PACKAGES.items():
        if name.lower() == app_name_lower:
            return package

    # Try matching after removing spaces and hyphens
    app_name_normalized = app_name.replace(" ", "").replace("-", "").lower()
    for name, package in APP_PACKAGES.items():
        name_normalized = name.replace(" ", "").replace("-", "").lower()
        if name_normalized == app_name_normalized:
            return package

    return None


def get_app_name(package_name: str) -> str | None:
    """Get the app display name from its Android package name.

    If multiple app names map to the same package, returns the first match found.

    Args:
        package_name: The Android package name (e.g., "com.tencent.mm").

    Returns:
        The display name of the app (e.g., "微信") if found, None otherwise.

    Examples:
        >>> get_app_name("com.tencent.mm")
        "微信"
        >>> get_app_name("com.android.chrome")
        "Chrome"
        >>> get_app_name("com.unknown.package")
        None
    """
    for name, package in APP_PACKAGES.items():
        if package == package_name:
            return name
    return None


def list_supported_apps() -> list[str]:
    """Get a list of all supported app names.

    Returns:
        List of app display names sorted alphabetically.

    Examples:
        >>> apps = list_supported_apps()
        >>> "微信" in apps
        True
        >>> "Chrome" in apps
        True
    """
    return sorted(set(APP_PACKAGES.keys()))


def list_supported_packages() -> list[str]:
    """Get a list of all supported package names.

    Returns:
        List of unique Android package names sorted alphabetically.

    Examples:
        >>> packages = list_supported_packages()
        >>> "com.tencent.mm" in packages
        True
        >>> "com.android.chrome" in packages
        True
    """
    return sorted(set(APP_PACKAGES.values()))


def is_app_supported(app_name: str) -> bool:
    """Check if an app is supported (with fuzzy matching).

    Args:
        app_name: The display name of the app.

    Returns:
        True if the app is supported, False otherwise.

    Examples:
        >>> is_app_supported("微信")
        True
        >>> is_app_supported("chrome")  # Lowercase
        True
        >>> is_app_supported("NonExistentApp")
        False
    """
    return find_package_name(app_name) is not None
