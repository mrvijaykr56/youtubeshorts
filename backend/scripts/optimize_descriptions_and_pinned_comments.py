"""
Master Optimization Script: Upgrades Descriptions & Engagement Comments across all 17 YouTube Videos & Instagram Reels.
"""

import os
import sys
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())

youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

PLAYLIST_ID = "PLJE6ifX-QD0A"
PLAYLIST_URL = f"https://www.youtube.com/playlist?list={PLAYLIST_ID}"
SUB_URL = "https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"

SHARED_TAGS = [
    "MagicalTalesKidz", "Hindi Kahaniya", "moral stories in hindi",
    "panchatantra stories", "kids moral stories", "3d animated stories",
    "hindi cartoon", "bal kahaniya", "bedtime stories in hindi",
    "fairy tales in hindi", "jadui kahaniya", "hindi animated tales",
    "hindi stories for kids", "hindi story cartoon", "stories for kids",
    "panchatantra tales in hindi", "shorts", "yt shorts",
    "हिंदी कहानियां", "पंचतंत्र की कहानियां", "नैतिक कहानियां", "हिंदी कार्टून"
]

ALL_VIDEOS = {
    "yQQlvP0MtG8": {
        "title": "कौवे ने एक घूंट पानी के लिए क्या कमाल किया? 🦅💧 The Thirsty Crow | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["thirsty crow story", "pyasa kauwa", "the thirsty crow", "chatur kauwa", "panchatantra pyasa kauwa", "akalmandi ki kahani"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #ThirstyCrow #PyasaKauwa #3DAnimation #HindiCartoon #BalKahani",
        "story_body": "भीषण गर्मी में प्यास से तड़पते कालू कौवे को एक घड़े में थोड़ा सा पानी दिखा। लेकिन चोंच पानी तक नहीं पहुंच पा रही थी! देखिए कैसे अपनी सूझबूझ और कंकड़ डालकर उसने अपनी प्यास बुझाई!",
        "moral": "मुसीबत में हिम्मत नहीं हारनी चाहिए। मेहनत और सूझबूझ से नामुमकिन काम भी मुमकिन हो जाता है! ❤️💡",
        "comment_q": "💡 क्या आपने कभी किसी मुश्किल समस्या का अनोखा हल निकाला है? हमें Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "RQsyj6r_980": {
        "title": "रोज एक सोने का अंडा! पर लालच ने क्या किया? 🪺✨ Goose of Gold | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["golden goose story", "sone ka anda", "lalchi kisan", "the goose of gold", "sone ke ande dene wali murgi", "lalach buri bala hai"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #GoldenGoose #SoneKaAnda #3DAnimation #HindiCartoon #BalKahani",
        "story_body": "गरीब किसान भोला को खलिहान में एक जादुई बत्तख मिली जो हर सुबह 24K सोने का अंडा देती थी। लेकिन जब भोला के मन में लालच का शैतान जागा, तो उसने सब कुछ खो दिया!",
        "moral": "लालच हमेशा इंसान को कंगाल बना देता है। सब्र और संतोष ही जीवन का सबसे बड़ा खजाना है! ❤️🌾",
        "comment_q": "🪺 अगर आपको रोज़ एक सोने का अंडा मिलता, तो आप सबसे पहले क्या करते? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "1d8fNhpscXY": {
        "title": "अचानक ये सियार पूरा नीला कैसे हो गया? 🐺💙 The Blue Jackal | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["blue jackal story", "neela siyar ki kahani", "the blue jackal", "chatur siyar", "neela gidad", "panchatantra blue jackal"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #BlueJackal #NeelaSiyar #3DAnimation #HindiCartoon #KidsStories",
        "story_body": "जंगल का भूखा सियार गिद्दु धोबी के नीले रंग के टब में गिर गया और पूरा नीला हो गया! जंगल के शेर और हाथी डर गए, तो उसने राजा बनने का ढोंग रचा। लेकिन एक पूर्णिमा की रात उसका सच सामने आ गया!",
        "moral": "झूठ, फरेब और दिखावे की शान कभी ज्यादा दिन नहीं टिकती। सच हमेशा सामने आकर रहता है! ❤️🧠",
        "comment_q": "🐺 क्या झूठ बोलकर कोई हमेशा के लिए बच सकता है? अपनी राय Comments में लिखें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "Wio6lrQKrjA": {
        "title": "कुल्हाड़ी नदी में गिरी, जलपरी ने क्या दिया? 🪓✨ Honest Woodcutter | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["honest woodcutter story", "sone ki kulhadi", "imandar lakadhara", "the golden axe", "jalpari aur lakadhara", "honesty is the best policy"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #HonestWoodcutter #SoneKiKulhadi #3DAnimation #HindiCartoon #BalKahani",
        "story_body": "घने जंगल में गरीब लकड़हारे कबीर की लोहे की कुल्हाड़ी नदी में गिर गई। जब दिव्य जलपरी 24K सोने और चांदी की कुल्हाड़ी लेकर आई, तो कबीर की ईमानदारी देखकर दंग रह गई!",
        "moral": "सच्ची ईमानदारी दुनिया की सबसे बड़ी दौलत है। जो सच के रास्ते पर चलता है, उसे जीवन में अनमोल खुशियां मिलती हैं! ❤️💎",
        "comment_q": "🪓 अगर जलपरी आपको सोने की कुल्हाड़ी देती, तो क्या आप सच बोलते? हमें बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "wsaNFDsKSM8": {
        "title": "मगरमच्छ ने बंदर के साथ क्या धोखा किया? 🐒🐊 The Monkey & The Crocodile | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["monkey and crocodile story", "bandar aur magarmach", "the clever monkey", "panchatantra bandar aur magarmach", "ramu bandar", "chatur bandar"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #MonkeyAndCrocodile #BandarAurMagarmach #3DAnimation #HindiCartoon",
        "story_body": "नदी किनारे जामुन के पेड़ पर रहने वाले चतुर रामू बंदर को लालची मगरमच्छ ने बीच नदी में धोखा दिया! लेकिन संकट के समय रामू ने अपनी बुद्धि से जान कैसे बचाई?",
        "moral": "मुसीबत के समय कभी घबराना नहीं चाहिए। शांत दिमाग और चतुराई से हर बड़े खतरे को मात दी जा सकती है! ❤️🧠",
        "comment_q": "🐒 संकट के समय रामू बंदर की चतुराई आपको कैसी लगी? Comments में लिखें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "HEVzgJuGzyE": {
        "title": "चतुर खरगोश ने घमंडी शेर को कैसे हराया? 🐰🦁 The Clever Rabbit & The Lion | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["clever rabbit and lion", "chatur khargosh aur sher", "the clever rabbit", "sher aur khargosh", "buddhiman khargosh", "lion in the well"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #CleverRabbit #ChaturKhargosh #3DAnimation #HindiStories #BalKahani",
        "story_body": "जब घमंडी राजा बब्बर शेर ने जंगल में खौफ फैलाया, तो नन्हे चींटू खरगोश ने अपनी अक्ल से शेर को गहरे कुएं में गिरा दिया!",
        "moral": "सच्ची अक्ल और हिम्मत हमेशा भारी शारीरिक ताकत से जीतती है। समझदारी से हर मुश्किल आसान हो जाती है! ❤️🧠",
        "comment_q": "🧠 अक्ल बड़ी या भैंस? इस कहानी से आपने क्या सीखा? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "WNNNbeNU_o4": {
        "title": "छोटे से चूहे ने जंगल के राजा को कैसे बचाया? 🐭🦁 The Mouse & The Lion | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["the mouse and the lion", "chatur chuha aur sher", "sher aur chuha", "the lion and the mouse", "panchatantra mouse lion", "chota chuha"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #MouseAndLion #ChuhaAurSher #3DAnimation #HindiCartoon #KidsAnimation",
        "story_body": "शिकारी के लोहे के मजबूत जाल में फंसे विशाल शेर को एक नन्हे चूहे चीकू ने अपने तेज दांतों से काटकर आजाद कर दिया!",
        "moral": "कोई भी दोस्त छोटा या कमजोर नहीं होता। किया गया उपकार और दया कभी व्यर्थ नहीं जाती! ❤️🤝",
        "comment_q": "🐭 क्या कभी किसी छोटे दोस्त ने आपकी बड़ी मदद की है? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "cKAR_Y-g0Gw": {
        "title": "जादुई ब्रश से निकली असली तितलियाँ! 🖌️✨ Rohan's Magic Paintbrush | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["magic paintbrush story", "jadui brush ki kahani", "the magic paintbrush", "rohan magic brush", "jadui kahaniya hindi", "magical tales"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #MagicPaintbrush #JaduiBrush #3DAnimation #KidsCartoon #HindiFairyTales #BedtimeStories",
        "story_body": "नन्हे रोहन को मिला एक जादुई बांस का ब्रश! जैसे ही उसने कागज़ पर तितली बनाई, वह सचमुच उड़ने लगी। लेकिन जब लालची जमींदार ने ब्रश छीना, तो क्या हुआ?",
        "moral": "सच्ची कला और प्रतिभा दूसरों के चेहरे पर मुस्कान लाने के लिए होती है, लालच के लिए नहीं! ❤️✨",
        "comment_q": "🎨 अगर आपको जादुई ब्रश मिले तो आप सबसे पहले क्या बनाएंगे? Comments में लिखें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "cN6k6lu0-Mc": {
        "title": "घमंडी मोर के पंख क्यों उड़े? 🦚🌈 The Secret of True Beauty | Bal Kahani #Shorts",
        "specific_tags": ["ghamandi mor ki kahani", "the proud peacock", "neel peacock", "mor ke pankh", "kids moral stories hindi", "panchatantra peacock"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #ProudPeacock #GhamandiMor #3DAnimation #HindiStories #BalKahani",
        "story_body": "नील मोर को अपने सुंदर पंखों पर बहुत घमंड था। लेकिन जब बारिश के तूफान में जंगल के नन्हे पक्षी फंसे, तो उसने दूसरों की मदद करना सीखा!",
        "moral": "सच्ची सुंदरता बाहरी रूप-रंग में नहीं, दूसरों की मदद करने वाले दयालु दिल में है! ❤️🌈",
        "comment_q": "🦚 बाहरी सुंदरता से बढ़कर क्या होता है? अपनी राय Comments में साझा करें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "JNMuCm6b8xg": {
        "title": "कौवे और बंदर की अनोखी दोस्ती! 🐦🥭 Sharing Brings Joy | 3D Cartoon Hindi #Shorts",
        "specific_tags": ["kalu kauwa", "bandar aur kauwa", "sharing is caring story", "crow and monkey", "3d cartoon hindi", "kids hindi kahani"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #CrowAndMonkey #KauwaAurBandar #3DAnimation #HindiStories #KidsCartoons",
        "story_body": "कालू कौवा और मीकू बंदर पहले एक मीठे आम के लिए लड़ते थे, लेकिन जब उन्होंने मिलकर बांटकर खाना शुरू किया, तो उनकी पक्की दोस्ती हो गई!",
        "moral": "लड़ाई और गुस्से से कुछ हासिल नहीं होता। मिलकर बांटकर खाने में ही सबसे बड़ा आनंद है! ❤️🥭",
        "comment_q": "🥭 क्या आप भी दोस्तों के साथ चीजें शेयर करते हैं? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "OHny_kUkjAw": {
        "title": "आसमान से गिरा एक जादुई तारा! 🐿️⭐ Cheeku's Magic Wish | Hindi Kids Story #Shorts",
        "specific_tags": ["cheeku gilahari", "jadui tara story", "falling star kids story", "cheeku squirrel", "hindi bedtime story", "kids 3d animation"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #CheekuSquirrel #JaduiTara #3DAnimation #BedtimeStories #KidsHindiStories",
        "story_body": "आसमान से टूटा हुआ एक चमकीला तारा चीकू गिलहरी के हाथ लगा। चीकू ने उस तारे से अपनी ख्वाहिश मांगने के बजाय जंगल के अंधेरे को दूर किया!",
        "moral": "खुशियां अपने पास छुपाने से नहीं, अंधेरे में दूसरों का रास्ता रोशन करने से बढ़ती हैं! ❤️⭐",
        "comment_q": "⭐ अगर टूटता तारा मिले तो आपकी पहली विश क्या होगी? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "mR2eWSWiZoE": {
        "title": "जब छोटे हाथी ने पूरे जंगल को बचाया! 🐘🪔 True Kindness Wins | 3D Hindi Kahani #Shorts",
        "specific_tags": ["golu hathi", "baby elephant story", "diwali elephant story", "chota hathi", "kindness stories for kids", "hindi animation cartoon"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #BabyElephant #GoluHathi #3DAnimation #KidsCartoon #HindiKahani",
        "story_body": "नन्हे गोलू हाथी ने दिवाली की रात अपनी इकलौती जलती हुई दिया एक ठिठुरते हुए नन्हे खरगोश को दे दी। देखिए उसकी इस निस्वार्थ दया का क्या फल मिला!",
        "moral": "निस्वार्थ सेवा और दया ही दुनिया की सबसे बड़ी रोशनी है! ❤️🪔",
        "comment_q": "🐘 गोलू हाथी की दयालुता आपको कैसी लगी? Comments में लिखें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "OQGNGYqde3c": {
        "title": "जंगल के राजा को किसने झुकाया? 🦁🔥 Power vs Love | Panchatantra Moral Story #Shorts",
        "specific_tags": ["sheru the lion", "lion king moral story", "jungle ka raja sher", "power vs love", "panchatantra sher ki kahani", "hindi cartoon animation"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #SheruLion #JungleKaRaja #3DAnimation #HindiCartoon",
        "story_body": "जंगल के राजा शेरू को अपनी ताकत पर घमंड था। लेकिन जब एक नन्हे जानवर के प्यार ने उसे बचाया, तो उसे समझ आया कि असली राजा कौन होता है!",
        "moral": "सच्चा राजा ताकत और डर से नहीं, प्यार और न्याय से दिलों पर राज करता है! ❤️👑",
        "comment_q": "🦁 ताकत बड़ी या प्यार? आपको क्या लगता है? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "cuaCG-6B-1M": {
        "title": "लालिची बंदर को मिली जादुई सीख! 🐒✨ Never Be Greedy | Hindi Kahaniya #Shorts",
        "specific_tags": ["miku bandar", "lalchi bandar", "never be greedy story", "miku monkey laddoo", "panchatantra monkey story", "kids animated kahani"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #MikuMonkey #LalchiBandar #3DAnimation #HindiStories #BalKahani",
        "story_body": "मीकू बंदर को मिला एक जादुई कटोरा जो मीठे लड्डुओं से भरा था। उसने किसी को लड्डू नहीं दिए, लेकिन लालच का क्या भयानक नतीजा हुआ?",
        "moral": "अकेले खाने में कभी तृप्ति नहीं मिलती, दोस्तों के साथ बांटकर खाने में ही सच्चा सुख है! ❤️🐒",
        "comment_q": "🐒 क्या आपने कभी किसी लालची का नुकसान होते देखा है? Comments में लिखें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "HYHK9AW6tA8": {
        "title": "नन्ही चींटी ने शिकारी का तीर कैसे रोका? 🐜🕊️ The Ant & The Dove | 3D Hindi Kahaniya #Shorts",
        "specific_tags": ["chiti aur kabootar ki kahani", "the ant and the dove", "ant and dove story", "chiti aur kabootar", "panchatantra ant dove", "hindi moral stories for children"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #Panchatantra #AntAndDove #ChitiAurKabootar #3DAnimation #HindiStories #BalKahani",
        "story_body": "एक नन्ही चींटी पानी में बह रही थी, जब दयालु कबूतर ने पत्ता गिराकर उसकी जान बचाई। फिर जब शिकारी ने कबूतर पर तीर ताना, तो चींटी ने शिकारी के पैर पर काटकर कबूतर की जान बचाई!",
        "moral": "एक छोटी सी नेकी कभी बेकार नहीं जाती। जो दूसरों का भला करता है, भगवान हमेशा उसका साथ देते हैं! ❤️🤝",
        "comment_q": "🐜 चींटी और कबूतर की सच्ची दोस्ती से आपने क्या सीखा? Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "_CJgao4mtTc": {
        "title": "आसमान से बात करने वाला जादुई तारा! ⭐✨ Twinkle & The Wish Star | Hindi Kids Story #Shorts",
        "specific_tags": ["jadui tara story", "twinkle star hindi", "whisper star", "space story hindi", "kids bedtime story", "hindi animated fairy tale"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #KidsAnimation #JaduiTara #WishStar #3DAnimation #BedtimeStories #BalKahani",
        "story_body": "आसमान के सबसे प्यारे नन्हे तारे ट्विंकल को मिला एक जादुई व्हिस्पर स्टार जो बच्चों की दिल की सच्ची दुआएं पूरी करता है!",
        "moral": "दूसरों के सपनों को पूरा करने में मदद करना ही सबसे बड़ी खुशी है! 💖✨",
        "comment_q": "✨ आपको यह जादुई कहानी कैसी लगी? अपनी राय Comments में जरूर दें! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    },
    "QDUQdph0D9U": {
        "title": "आसमान की सबसे तेज जादुई रेस! 🚀⭐ The Starry Race | 3D Animated Hindi Cartoon #Shorts",
        "specific_tags": ["starry race story", "space cartoon hindi", "twinkle and zip", "kids race cartoon", "friendship moral story", "hindi 3d cartoon"],
        "hashtags": "#Shorts #HindiKahaniya #MoralStories #KidsAnimation #StarryRace #3DAnimation #HindiCartoon #BalKahani",
        "story_body": "टूटते तारे ज़िप ने ट्विंकल को अंतरिक्ष की सबसे तेज जादुई रेस की चुनौती दी! लेकिन जब ज़िप मुसीबत में फंसा, तो ट्विंकल ने अपनी जीत छोड़कर उसे बचाया!",
        "moral": "अकेले जीतने से कहीं ज्यादा महान और सच्चा दोस्त की मदद करना है! ❤️🚀",
        "comment_q": "🚀 जीत बड़ी या सच्ची दोस्ती? हमें Comments में बताएं! 👇\n🎬 पूरी 3D कहानियां देखें: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n🔔 सब्सक्राइब करें: https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"
    }
}

def update_descriptions_and_comments():
    print("=" * 75)
    print("🚀 OPTIMIZING DESCRIPTIONS, TAGS & PINNED COMMENTS FOR ALL 17 VIDEOS")
    print("=" * 75)

    success_desc = 0
    success_comments = 0

    for vid_id, data in ALL_VIDEOS.items():
        print(f"\n▶ Video [{vid_id}]: {data['title'][:55]}...")
        try:
            # 1. Update Video Metadata (Description, Tags, Category, COPPA)
            v_res = youtube.videos().list(part="snippet,status", id=vid_id).execute()
            if v_res.get("items"):
                v_item = v_res["items"][0]
                snippet = v_item["snippet"]
                status = v_item["status"]

                snippet["title"] = data["title"]
                snippet["categoryId"] = "1"

                # Tag Assembly (max 380 chars)
                all_raw_tags = list(dict.fromkeys(data["specific_tags"] + SHARED_TAGS))
                safe_tags = []
                cur_chars = 0
                for tag in all_raw_tags:
                    cleaned = tag.strip()
                    extra = len(cleaned) + (1 if safe_tags else 0)
                    if cur_chars + extra <= 380:
                        safe_tags.append(cleaned)
                        cur_chars += extra
                    else:
                        break
                snippet["tags"] = safe_tags

                # Infobells-Style Description
                snippet["description"] = (
                    f"{data['hashtags']}\n\n"
                    f"{data['story_body']}\n\n"
                    f"🌟 कहानी की सीख (Moral of the Story):\n"
                    f"{data['moral']}\n\n"
                    f"🎬 Watch All 3D Hindi Stories in Official Playlist:\n"
                    f"{PLAYLIST_URL}\n\n"
                    f"🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:\n"
                    f"{SUB_URL}\n\n"
                    f"{data['hashtags']}\n"
                )

                status["selfDeclaredMadeForKids"] = False

                youtube.videos().update(
                    part="snippet,status",
                    body={"id": vid_id, "snippet": snippet, "status": status}
                ).execute()
                print("  ✅ Upgraded Description & SEO Tags successfully!")
                success_desc += 1

            # 2. Check & Post Engagement Comment
            comment_text = data["comment_q"]
            try:
                # Check existing comments
                c_res = youtube.commentThreads().list(
                    part="snippet",
                    videoId=vid_id,
                    maxResults=20
                ).execute()

                already_commented = False
                for item in c_res.get("items", []):
                    top_c = item["snippet"]["topLevelComment"]["snippet"]
                    if "MagicalTalesKidz" in top_c.get("authorDisplayName", "") or "कहानियां देखें" in top_c.get("textOriginal", ""):
                        already_commented = True
                        break

                if not already_commented:
                    youtube.commentThreads().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "videoId": vid_id,
                                "topLevelComment": {
                                    "snippet": {
                                        "textOriginal": comment_text
                                    }
                                }
                            }
                        }
                    ).execute()
                    print("  💬 Inserted Official Engagement Magnet Comment!")
                    success_comments += 1
                else:
                    print("  ℹ️ Official engagement comment already present.")
            except Exception as ce:
                print(f"  ⚠️ Comment insertion note: {ce}")

            time.sleep(0.5)

        except Exception as e:
            print(f"  ❌ Error on {vid_id}: {e}")

    print("\n" + "=" * 75)
    print(f"🎉 COMPLETED: {success_desc}/{len(ALL_VIDEOS)} Descriptions Updated | {success_comments} New Comments Posted!")
    print("=" * 75)

if __name__ == "__main__":
    update_descriptions_and_comments()
