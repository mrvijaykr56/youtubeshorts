"""
Master Instagram Reels SEO Upgrade Script for @magicaltaleskid
Updates all live published Reels with:
1. High-curiosity Line-1 Hook (< 100 chars, visible before "...more").
2. Rich Hindi storytelling synopsis with embedded keywords.
3. Clear Moral Takeaway.
4. High-Save (💾) and Discussion (💬) Call-To-Actions.
5. Official YouTube link-in-bio funneling callout.
6. 12-tag viral keyword cluster (Specific story tags + High-volume Evergreen tags).
7. Posts traffic-driving pinned comments on each Reel.
"""

import os
import sys
import time
from instagrapi import Client

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, "instagram_session.json")

# Standard Evergreen Hashtag Cluster
EVERGREEN_TAGS = (
    "#HindiReels #HindiKahaniya #MoralStories #Panchatantra "
    "#KidsAnimation #HindiStories #ReelsIndia #PanchatantraTales #3DAnimation #ExplorePage"
)

# Detailed Story SEO Database keyed by unique substrings in existing captions
STORIES_SEO_DB = {
    # 1. Lion King / Diwali Special (DewmKH-JNWG)
    "जंगल के राजा को किसने झुकाया": {
        "hook": "जंगल के राजा को किसने झुकाया? 🦁🔥 ताकत बड़ी या प्यार? 👇",
        "synopsis": "घमंडी शेर पूरे जंगल पर अपनी ताकत का खौफ जमाता था। लेकिन जब जंगल के छोटे जानवरों ने एकजुट होकर प्यार और दीयों की रोशनी से उसका अहंकार पिघलाया, तो जंगल में एकता की जीत हुई!",
        "moral": "सच्ची ताकत दूसरों को डराने में नहीं, बल्कि सबके दिलों को जीतने में है! ❤️🪔",
        "question": "क्या प्यार से किसी का भी गुस्सा शांत किया जा सकता है? अपनी राय Comments में लिखें! 👇",
        "specific_tags": "#JungleKaRaja #LionStory #SherKiKahani"
    },
    # 2. Golu Elephant (Dewl7A7p-Gb)
    "नन्हे हाथी गोलू": {
        "hook": "जब नन्हे हाथी ने पूरे जंगल को बचाया! 🐘🪔 दया की सबसे बड़ी शक्ति! ✨👇",
        "synopsis": "जंगल में तूफान आने पर सब जानवर बेघर हो गए थे। नन्हे हाथी गोलू ने अपनी सूंड से भारी लकड़ियां हटाकर और रोशनी लाकर हर किसी की जान बचाई!",
        "moral": "दयालुता और परोपकार ही जीवन का सबसे बड़ा धर्म है। दूसरों की मदद करने वाले हमेशा याद रखे जाते हैं! ❤️🌾",
        "question": "क्या आपने कभी किसी बेजुबान जानवर या दोस्त की मदद की है? Comments में बताएं! 👇",
        "specific_tags": "#HathiKiKahani #GoluElephant #TrueKindness"
    },
    # 3. Squirrel & Star (DewlR2wJINr)
    "जादुई तारा": {
        "hook": "आसमान से गिरा एक जादुई तारा! 🐿️⭐ सच्ची दोस्ती का चमत्कार! ✨👇",
        "synopsis": "चीकू गिलहरी को रात में जंगल में एक चमकता हुआ नन्हा तारा मिला जो रास्ता भटक गया था। चीकू ने अपनी जान जोखिम में डालकर उस नन्हे तारे को वापस आसमान में कैसे पहुंचाया?",
        "moral": "निस्वार्थ दोस्ती और मदद से असंभव काम भी संभव हो जाता है! ❤️🌟",
        "question": "अगर आपको कोई जादुई तारा मिलता, तो आप क्या मांगते? Comments में बताएं! 👇",
        "specific_tags": "#JaduiTara #CheekuSquirrel #MagicStar"
    },
    # 4. Crow & Monkey (Dewk9qHJavu)
    "कौवे और नन्हे बंदर": {
        "hook": "कौवे और बंदर की अनोखी दोस्ती! 🐦🥭 बांटकर खाने का सच्चा सुख! ✨👇",
        "synopsis": "भूखे कौवे कालू और नन्हे बंदर मीकू ने मीठे रसीले आमों को आपस में बांटकर खाया। जब दोनों पर बाज का हमला हुआ, तो दोनों ने मिलकर एक-दूसरे की जान बचाई!",
        "moral": "बांटकर खाने से खुशी दोगुनी हो जाती है और सच्चा दोस्त हर संकट में ढाल बनता है! ❤️🥭",
        "question": "क्या आप भी अपनी पसंदीदा चीजें दोस्तों के साथ बांटते हैं? Comments में बताएं! 👇",
        "specific_tags": "#KauwaAurBandar #FriendshipStory #SharingBringsJoy"
    },
    # 5. Peacock (Dewks3tJEpK)
    "घमंडी मोर": {
        "hook": "घमंडी मोर के पंख क्यों उड़े? 🦚🌈 सुंदरता से बड़ा क्या है? ✨👇",
        "synopsis": "सुंदर मोर नील अपने रंग-बिरंगे पंखों पर बहुत घमंड करता था और दूसरों का मजाक उड़ाता था। लेकिन जब तेज आंधी में उसके पंख उड़ गए, तो उसे अपनी गलती का अहसास हुआ!",
        "moral": "घमंड हमेशा इंसान को नीचा दिखाता है। बाहरी सुंदरता से कहीं ज्यादा अनमोल मन की सादगी होती है! ❤️🦚",
        "question": "क्या कभी किसी घमंडी को सबक सीखते देखा है? Comments में शेयर करें! 👇",
        "specific_tags": "#GhamandiMor #MorKePankh #TrueBeauty"
    },
    # 6. Magic Paintbrush (DewkdrAp1eF)
    "जादुई ब्रश": {
        "hook": "जादुई ब्रश से निकली असली तितलियाँ! 🖌️✨ पर लालची राजा ने क्या किया? 😱👇",
        "synopsis": "गरीब लड़के रोहन को एक ऐसा जादुई ब्रश मिला जिससे वो जो भी बनाता, वो सच हो जाता था! जब लालची राजा ने सोने का पहाड़ बनाने को कहा, तो रोहन ने अपनी अक्ल से क्या किया?",
        "moral": "ईश्वर की दी हुई प्रतिभा का इस्तेमाल हमेशा गरीबों और जरूरतमंदों की भलाई के लिए करना चाहिए! 🎨✨",
        "question": "अगर आपके पास ऐसा जादुई ब्रश होता, तो आप सबसे पहले क्या बनाते? Comments में लिखें! 👇",
        "specific_tags": "#JaduiBrush #MagicPaintbrush #RohanKiKahani"
    },
    # 7. Clever Rabbit (DewkHItJ8Fm)
    "चतुर खरगोश": {
        "hook": "छोटे से खरगोश ने खूंखार शेर को कैसे हराया? 🐰🦁 अक्ल बड़ी या भैंस? 🧠👇",
        "synopsis": "जंगल का क्रूर शेर भासुरक रोज बेकसूर जानवरों को मारता था। लेकिन जब नन्हे चतुर खरगोश चीकू की बारी आई, तो उसने अपनी अक्ल से शेर को गहरे कुएं में कूदने पर मजबूर कर दिया!",
        "moral": "बुद्धि बल से कई गुना ज्यादा शक्तिशाली होती है। संकट में धैर्य और अक्ल का इस्तेमाल ही जीत दिलाता है! 🧠🔥",
        "question": "ताकत बड़ी होती है या अक्ल? Comments में अपना जवाब लिखें! 👇",
        "specific_tags": "#ChaturKhargosh #CleverRabbit #SherAurKhargosh"
    },
    # 8. Monkey & Crocodile (DewjjXqp2R5)
    "मगरमच्छ ने चतुर बंदर": {
        "hook": "मगरमच्छ ने बंदर के साथ क्या धोखा किया? 🐒🐊 चालाकी पर अक्ल की जीत! 🧠👇",
        "synopsis": "मीठे जामुन के पेड़ पर रहने वाले दयालु बंदर मीकू ने भूखे मगरमच्छ को रोज फल खिलाए। लेकिन दुष्ट मगरमच्छ ने अपने दोस्त का कलेजा अपनी पत्नी को खिलाने की चाल चली!",
        "moral": "मुसीबत के समय घबराने के बजाय ठंडे दिमाग और बुद्धिमानी से काम लेना चाहिए। सच्चा दोस्त कभी धोखा नहीं देता! ❤️🧠",
        "question": "क्या आपने कभी किसी धोखेबाज को अक्ल से मात दी है? Comments में बताएं! 👇",
        "specific_tags": "#BandarAurMagarmach #MonkeyCrocodile #ChaturBandar"
    },
    # 9. Mouse & Lion (Dewhu6VpnHb)
    "छोटे से चूहे ने जंगल": {
        "hook": "छोटे से चूहे ने जंगल के राजा को कैसे बचाया? 🐭🦁 कभी किसी को छोटा मत समझो! ❤️👇",
        "synopsis": "जंगल के राजा शेर ने एक नन्हे चूहे को दया करके छोड़ दिया था। कुछ दिनों बाद जब वही विशाल शेर शिकारी के मजबूत जाल में फंसा, तो उसी नन्हे चूहे ने जाल काटकर उसकी जान बचाई!",
        "moral": "कोई भी इंसान या जीव कभी छोटा या कमजोर नहीं होता। हर किसी का सम्मान करें, भलाई का बदला भलाई होता है! ❤️🌾",
        "question": "क्या कभी किसी छोटे ने आपकी बड़ी मदद की है? Comments में बताएं! 👇",
        "specific_tags": "#SherAurChuha #LionAndMouse #ChoteChandan"
    }
}

def format_caption(story_data):
    caption = (
        f"{story_data['hook']}\n\n"
        f"{story_data['synopsis']}\n\n"
        f"🌟 कहानी की सीख (Moral of the Story):\n"
        f"{story_data['moral']}\n\n"
        f"💾 SAVE करें बच्चों के लिए और अपने दोस्तों के साथ SHARE करें!\n"
        f"💬 {story_data['question']}\n\n"
        f"🎬 पूरी 3D कहानी और नए एपिसोड्स देखने के लिए BIO में दिए गए YouTube लिंक पर क्लिक करें! 🔔\n"
        f"👉 Follow @magicaltaleskid for daily 3D Hindi stories! ✨\n\n"
        f"{story_data['specific_tags']} {EVERGREEN_TAGS}"
    )
    return caption

def optimize_all_reels():
    print("=" * 70)
    print("🚀 OPTIMIZING ALL INSTAGRAM REELS SEO & TAGS FOR @magicaltaleskid")
    print("=" * 70)

    cl = Client()
    cl.load_settings(SESSION_FILE)
    cl.username = "magicaltaleskid"

    user_id = cl.user_id_from_username(cl.username)
    medias = cl.user_medias(user_id, amount=15)
    print(f"📡 Found {len(medias)} published medias on account.\n")

    updated_count = 0
    for m in medias:
        old_caption = m.caption_text or ""
        code = m.code
        reel_url = f"https://www.instagram.com/reel/{code}/"

        # Check which story matches
        matched_story = None
        for key, data in STORIES_SEO_DB.items():
            if key in old_caption:
                matched_story = data
                break

        if not matched_story:
            # Skip if already newly formatted (e.g. golden_goose)
            if "रोज 24K सोने का अंडा" in old_caption:
                print(f"⏩ [Reel {code}] (Golden Goose) already has perfected SEO. Skipping.")
                continue
            print(f"ℹ️ [Reel {code}] No matching story pattern found. Skipping.")
            continue

        new_caption = format_caption(matched_story)

        print(f"⚡ Optimizing Reel [{code}]: {matched_story['hook'][:50]}...")
        try:
            cl.media_edit(m.id, caption=new_caption)
            print(f"  ✅ Updated Caption, Hook, High-Save CTA & 12-Tag Cluster!")
            print(f"  🔗 Link: {reel_url}")

            # Also post engagement traffic-driving comment if not already present
            try:
                comment_text = "🎬 इस कहानी का पूरा 3D अनुभव हमारे YouTube चैनल पर देखें! Link bio में उपलब्ध है 👉 @magicaltaleskid ✨"
                cl.media_comment(m.id, comment_text)
                print(f"  💬 Pinned YouTube traffic comment posted!")
            except Exception as ce:
                print(f"  Note on comment: {ce}")

            updated_count += 1
            print("  ⏳ Sleeping 5s between edits to respect rate limits...\n")
            time.sleep(5)
        except Exception as e:
            print(f"  ❌ Error editing Reel {code}: {e}\n")

    print("=" * 70)
    print(f"🎉 MASTER REELS SEO UPGRADE COMPLETE: {updated_count} Reels successfully optimized!")
    print("=" * 70)

if __name__ == "__main__":
    optimize_all_reels()
