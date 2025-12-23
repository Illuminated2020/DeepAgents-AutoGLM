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


# ========== iOS App Bundle IDs ==========
# Mapping of app names to iOS bundle IDs (from Open-AutoGLM/phone_agent/config/apps_ios.py)

APP_PACKAGES_IOS: dict[str, str] = {
    # Tencent Apps (腾讯系)
    "微信": "com.tencent.xin",
    "企业微信": "com.tencent.ww",
    "微信读书": "com.tencent.weread",
    "微信听书": "com.tencent.wehear",
    "QQ": "com.tencent.mqq",
    "QQ音乐": "com.tencent.QQMusic",
    "QQ阅读": "com.tencent.qqreaderiphone",
    "QQ邮箱": "com.tencent.qqmail",
    "QQ浏览器": "com.tencent.mttlite",
    "TIM": "com.tencent.tim",
    "微视": "com.tencent.microvision",
    "腾讯新闻": "com.tencent.info",
    "腾讯视频": "com.tencent.live4iphone",
    "腾讯动漫": "com.tencent.ied.app.comic",
    "腾讯微云": "com.tencent.weiyun",
    "腾讯体育": "com.tencent.sportskbs",
    "腾讯文档": "com.tencent.txdocs",
    "腾讯翻译君": "com.tencent.qqtranslator",
    "腾讯课堂": "com.tencent.edu",
    "腾讯地图": "com.tencent.sosomap",
    "小鹅拼拼": "com.tencent.dwdcoco",
    "全民k歌": "com.tencent.QQKSong",
    # Alibaba Apps (阿里系)
    "支付宝": "com.alipay.iphoneclient",
    "钉钉": "com.laiwang.DingTalk",
    "闲鱼": "com.taobao.fleamarket",
    "淘宝": "com.taobao.taobao4iphone",
    "斗鱼": "tv.douyu.live",
    "天猫": "com.taobao.tmall",
    "口碑": "com.taobao.kbmeishi",
    "饿了么": "me.ele.ios.eleme",
    "高德地图": "com.autonavi.amap",
    "UC浏览器": "com.ucweb.iphone.lowversion",
    "一淘": "com.taobao.etaocoupon",
    "飞猪": "com.taobao.travel",
    "虾米音乐": "com.xiami.spark",
    "淘票票": "com.taobao.movie.MoviePhoneClient",
    "优酷": "com.youku.YouKu",
    "菜鸟裹裹": "com.cainiao.cnwireless",
    "土豆视频": "com.tudou.tudouiphone",
    # ByteDance Apps (字节系)
    "抖音": "com.ss.iphone.ugc.Aweme",
    "抖音极速版": "com.ss.iphone.ugc.aweme.lite",
    "抖音火山版": "com.ss.iphone.ugc.Live",
    "Tiktok": "com.zhiliaoapp.musically",
    "飞书": "com.bytedance.ee.lark",
    "今日头条": "com.ss.iphone.article.News",
    "西瓜视频": "com.ss.iphone.article.Video",
    "皮皮虾": "com.bd.iphone.super",
    # Meituan Apps (美团系)
    "美团": "com.meituan.imeituan",
    "美团外卖": "com.meituan.itakeaway",
    "大众点评": "com.dianping.dpscope",
    "美团优选": "com.meituan.iyouxuan",
    "美团优选团长": "com.meituan.igrocery.gh",
    "美团骑手": "com.meituan.banma.homebrew",
    "美团开店宝": "com.meituan.imerchantbiz",
    "美团拍店": "com.meituan.pai",
    "美团众包": "com.meituan.banma.crowdsource",
    "美团买菜": "com.baobaoaichi.imaicai",
    # JD Apps (京东系)
    "京东": "com.360buy.jdmobile",
    "京东读书": "com.jd.reader",
    # NetEase Apps (网易系)
    "网易新闻": "com.netease.news",
    "网易云音乐": "com.netease.cloudmusic",
    "网易邮箱大师": "com.netease.macmail",
    "网易严选": "com.netease.yanxuan",
    "网易公开课": "com.netease.videoHD",
    "网易有道词典": "youdaoPro",
    "有道云笔记": "com.youdao.note.YoudaoNoteMac",
    # Baidu Apps (百度系)
    "百度": "com.baidu.BaiduMobile",
    "百度网盘": "com.baidu.netdisk",
    "百度贴吧": "com.baidu.tieba",
    "百度地图": "com.baidu.map",
    "百度阅读": "com.baidu.yuedu",
    "百度翻译": "com.baidu.translate",
    "百度文库": "com.baidu.Wenku",
    "百度视频": "com.baidu.videoiphone",
    "百度输入法": "com.baidu.inputMethod",
    # Kuaishou Apps (快手系)
    "快手": "com.jiangjia.gif",
    "快手极速版": "com.kuaishou.nebula",
    # Other Popular Apps
    "哔哩哔哩": "tv.danmaku.bilianime",
    "bilibili": "tv.danmaku.bilianime",
    "芒果TV": "com.hunantv.imgotv",
    "苏宁易购": "SuningEMall",
    "微博": "com.sina.weibo",
    "微博极速版": "com.sina.weibolite",
    "微博国际": "com.weibo.international",
    "墨客": "com.moke.moke.iphone",
    "豆瓣": "com.douban.frodo",
    "知乎": "com.zhihu.ios",
    "小红书": "com.xingin.discover",
    "喜马拉雅": "com.gemd.iting",
    "得到": "com.luojilab.LuoJiFM-IOS",
    "得物": "com.siwuai.duapp",
    "起点读书": "m.qidian.QDReaderAppStore",
    "番茄小说": "com.dragon.read",
    "书旗小说": "com.shuqicenter.reader",
    "拼多多": "com.xunmeng.pinduoduo",
    "多点": "com.dmall.dmall",
    "便利蜂": "com.bianlifeng.customer.ios",
    "亿通行": "com.ruubypay.yitongxing",
    "云闪付": "com.unionpay.chsp",
    "大都会Metro": "com.DDH.SHSubway",
    "爱奇艺视频": "com.qiyi.iphone",
    "搜狐视频": "com.sohu.iPhoneVideo",
    "搜狐新闻": "com.sohu.newspaper",
    "搜狗浏览器": "com.sogou.SogouExplorerMobile",
    "虎牙": "com.yy.kiwi",
    "比心": "com.yitan.bixin",
    "转转": "com.wuba.zhuanzhuan",
    "YY": "yyvoice",
    "绿洲": "com.sina.oasis",
    "陌陌": "com.wemomo.momoappdemo1",
    "什么值得买": "com.smzdm.client.ios",
    "美团秀秀": "com.meitu.mtxx",
    "唯品会": "com.vipshop.iphone",
    "唱吧": "com.changba.ktv",
    "酷狗音乐": "com.kugou.kugou1002",
    "CSDN": "net.csdn.CsdnPlus",
    "多抓鱼": "com.duozhuyu.dejavu",
    "自如": "com.ziroom.ZiroomProject",
    "携程": "ctrip.com",
    "去哪儿旅行": "com.qunar.iphoneclient8",
    "Xmind": "net.xmind.brownieapp",
    "印象笔记": "com.yinxiang.iPhone",
    "欧陆词典": "eusoft.eudic.pro",
    "115": "com.115.personal",
    "名片全能王": "com.intsig.camcard.lite",
    "中国银行": "com.boc.BOCMBCI",
    "58同城": "com.taofang.iphone",
    # International Apps
    "Google Chrome": "com.google.chrome.ios",
    "Gmail": "com.google.Gmail",
    "Facebook": "com.facebook.Facebook",
    "Firefox": "org.mozilla.ios.Firefox",
    "Messenger": "com.facebook.Messenger",
    "Instagram": "com.burbn.instagram",
    "Starbucks": "com.starbucks.mystarbucks",
    "Luckin Coffee": "com.bjlc.luckycoffee",
    "Line": "jp.naver.line",
    "Linkedin": "com.linkedin.LinkedIn",
    "Dcard": "com.dcard.app.Dcard",
    "Youtube": "com.google.ios.youtube",
    "Spotify": "com.spotify.client",
    "Netflix": "com.netflix.Netflix",
    "Twitter": "com.atebits.Tweetie2",
    "X": "com.atebits.Tweetie2",
    "WhatsApp": "net.whatsapp.WhatsApp",
    # Apple Native Apps (Apple 原生应用)
    "Safari": "com.apple.mobilesafari",
    "App Store": "com.apple.AppStore",
    "设置": "com.apple.Preferences",
    "相机": "com.apple.camera",
    "照片": "com.apple.mobileslideshow",
    "时钟": "com.apple.mobiletimer",
    "闹钟": "com.apple.mobiletimer",
    "备忘录": "com.apple.mobilenotes",
    "提醒事项": "com.apple.reminders",
    "快捷指令": "com.apple.shortcuts",
    "天气": "com.apple.weather",
    "日历": "com.apple.mobilecal",
    "地图": "com.apple.Maps",
    "电话": "com.apple.mobilephone",
    "通讯录": "com.apple.MobileAddressBook",
    "信息": "com.apple.MobileSMS",
    "Facetime": "com.apple.facetime",
    "FaceTime": "com.apple.facetime",
    "计算器": "com.apple.calculator",
    "家庭": "com.apple.Home",
    "健康": "com.apple.Health",
    "钱包": "com.apple.Passbook",
    "股市": "com.apple.stocks",
    "图书": "com.apple.iBooks",
    "新闻": "com.apple.news",
    "视频": "com.apple.tv",
    "文件": "com.apple.DocumentsApp",
    "邮件": "com.apple.mobilemail",
    "查找": "com.apple.findmy",
    "翻译": "com.apple.Translate",
    "音乐": "com.apple.Music",
    "播客": "com.apple.podcasts",
    "库乐队": "com.apple.mobilegarageband",
    "语音备忘录": "com.apple.VoiceMemos",
    "iMovie": "com.apple.iMovie",
    "Watch": "com.apple.Bridge",
    "Apple Store": "com.apple.store.Jolly",
    "TestFlight": "com.apple.TestFlight",
    "Keynote": "com.apple.Keynote",
    "Keynote 讲演": "com.apple.Keynote",
}


def get_bundle_id(app_name: str) -> str | None:
    """
    Get the iOS bundle ID for an app name.

    Args:
        app_name: The display name of the app.

    Returns:
        The iOS bundle ID, or None if not found.
    """
    return APP_PACKAGES_IOS.get(app_name)
