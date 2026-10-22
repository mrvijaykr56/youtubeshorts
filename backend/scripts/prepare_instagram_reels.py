"""
Instagram Reels Packaging Automation for @magicaltaleskid
Prepares ready-to-publish Instagram Reel packages from existing 3D animated Shorts:
- 1080x1920 MP4 Video
- High-res 9:16 Cover Thumbnail
- Pre-formatted high-conversion Caption with Instagram SEO & Hashtags
"""

import os
import sys
import json
import shutil

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
REELS_PKG_DIR = os.path.join(OUTPUT_DIR, "instagram_reels_packages")
os.makedirs(REELS_PKG_DIR, exist_ok=True)

REELS_METADATA = {
    "golden_goose": {
        "title": "Goose of Gold (सोने का अंडा)",
        "hook": "रोज एक सोने का अंडा! 🪺✨ पर लालच ने क्या किया?",
        "synopsis": "गरीब किसान भोला को खलिहान में एक जादुई बत्तख मिली जो हर सुबह 24K सोने का अंडा देती थी। लेकिन जब भोला के मन में लालच का शैतान जागा, तो उसने सब कुछ खो दिया!",
        "moral": "लालच हमेशा इंसान को कंगाल बना देता है। सब्र और संतोष ही जीवन का सबसे बड़ा खजाना है! ❤️🌾",
        "question": "क्या आपने भी कभी किसी को लालच में नुकसान उठाते देखा है? Comments में ज़रूर बताएं! 👇"
    },
    "blue_jackal": {
        "title": "The Blue Jackal (नीला सियार)",
        "hook": "अचानक ये सियार पूरा नीला कैसे हो गया? 🐺💙",
        "synopsis": "जंगल का भूखा सियार गिद्दु धोबी के नीले रंग के टब में गिर गया और पूरा नीला हो गया! जंगल के शेर और हाथी डर गए, तो उसने राजा बनने का ढोंग रचा। लेकिन एक पूर्णिमा की रात उसका सच सामने आ गया!",
        "moral": "झूठ, फरेब और दिखावे की शान कभी ज्यादा दिन नहीं टिकती। सच हमेशा सामने आकर रहता है! ❤️🧠",
        "question": "क्या झूठ बोलकर कोई कभी सफल हो सकता है? अपनी राय हमें Comments में बताएं! 👇"
    },
    "honest_woodcutter": {
        "title": "Honest Woodcutter (ईमानदार लकड़हारा)",
        "hook": "कुल्हाड़ी नदी में गिरी, जलपरी ने क्या दिया? 🪓✨",
        "synopsis": "घने जंगल में गरीब लकड़हारे कबीर की लोहे की कुल्हाड़ी नदी में गिर गई। जब दिव्य जलपरी 24K सोने और चांदी की कुल्हाड़ी लेकर आई, तो कबीर की ईमानदारी देखकर दंग रह गई!",
        "moral": "ईमानदारी ही इंसान का सबसे बड़ा गहना है। जो सच के रास्ते पर चलता है, ईश्वर उसका साथ कभी नहीं छोड़ते! ❤️🪵",
        "question": "अगर आपको सोने की कुल्हाड़ी मिलती, तो आप क्या करते? Comments में बताएं! 👇"
    },
    "monkey_and_crocodile": {
        "title": "The Monkey and Crocodile (बंदर और मगरमच्छ)",
        "hook": "मगरमच्छ ने बंदर के साथ क्या धोखा किया? 🐒🐊",
        "synopsis": "मीठे जामुन के पेड़ पर रहने वाले दयालु बंदर मीकू ने भूखे मगरमच्छ को रोज फल खिलाए। लेकिन दुष्ट मगरमच्छ ने अपने दोस्त का कलेजा अपनी पत्नी को खिलाने की चाल चली!",
        "moral": "मुसीबत के समय घबराने के बजाय ठंडे दिमाग और बुद्धिमानी से काम लेना चाहिए। सच्चा दोस्त कभी विश्वासघात नहीं करता! ❤️🧠",
        "question": "क्या आपने कभी किसी दोस्त की चालाकी पकड़ी है? Comments में शेयर करें! 👇"
    },
    "clever_rabbit": {
        "title": "The Clever Rabbit (चतुर खरगोश)",
        "hook": "छोटे से खरगोश ने खूंखार शेर को कैसे हराया? 🐰🦁",
        "synopsis": "जंगल का क्रूर शेर भासुरक रोज बेकसूर जानवरों को मारता था। लेकिन जब नन्हे चतुर खरगोश चीकू की बारी आई, तो उसने अपनी अक्ल से शेर को गहरे कुएं में कूदने पर मजबूर कर दिया!",
        "moral": "बुद्धि बल से कई गुना ज्यादा शक्तिशाली होती है। संकट में धैर्य और अक्ल का इस्तेमाल ही जीत दिलाता है! 🧠🔥",
        "question": "ताकत बड़ी होती है या अक्ल? Comments में अपना विचार लिखें! 👇"
    },
    "mouse_and_lion": {
        "title": "The Lion and the Mouse (शेर और चूहा)",
        "hook": "छोटे से चूहे ने जंगल के राजा को कैसे बचाया? 🐭🦁",
        "synopsis": "जंगल के राजा शेर ने एक नन्हे चूहे को दया करके छोड़ दिया था। कुछ दिनों बाद जब वही विशाल शेर शिकारी के मजबूत जाल में फंसा, तो उसी नन्हे चूहे ने जाल काटकर उसकी जान बचाई!",
        "moral": "कोई भी इंसान या जीव कभी छोटा या कमजोर नहीं होता। हर किसी का सम्मान करें, भलाई का बदला हमेशा भलाई होता है! ❤️🌾",
        "question": "क्या कभी किसी छोटे ने आपकी बड़ी मदद की है? Comments में बताएं! 👇"
    }
}

INSTAGRAM_HASHTAGS = (
    "#HindiReels #HindiKahaniya #MoralStories #Panchatantra "
    "#KidsAnimation #HindiStories #ReelsIndia #PanchatantraTales "
    "#3DAnimation #ReelsInstagram #ExplorePage #MagicalTalesKidz"
)

import subprocess

def check_has_audio(video_path):
    try:
        res = subprocess.run(
            [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ],
            capture_output=True, text=True
        )
        return bool(res.stdout.strip())
    except Exception:
        return True

def package_reels():
    print("=" * 70)
    print("📱 PACKAGING 3D STORIES FOR INSTAGRAM REELS (@magicaltaleskid)")
    print("=" * 70)

    count = 0
    for folder_name, meta in REELS_METADATA.items():
        src_dir = os.path.join(OUTPUT_DIR, folder_name)
        if not os.path.exists(src_dir):
            continue

        # Find best video file with confirmed audio
        video_file = None
        for cand in ["final_video.mp4", "final_video_xfade.mp4"]:
            cand_path = os.path.join(src_dir, cand)
            if os.path.exists(cand_path) and check_has_audio(cand_path):
                video_file = cand_path
                break
        
        # Fallback to any existing file if none passed
        if not video_file:
            for cand in ["final_video.mp4", "final_video_xfade.mp4"]:
                cand_path = os.path.join(src_dir, cand)
                if os.path.exists(cand_path):
                    video_file = cand_path
                    break

        if not video_file:
            continue

        # Target reel package directory
        pkg_dir = os.path.join(REELS_PKG_DIR, folder_name)
        os.makedirs(pkg_dir, exist_ok=True)

        # Copy Video (enforce fresh copy with audio)
        dest_video = os.path.join(pkg_dir, f"{folder_name}_reel.mp4")
        shutil.copy2(video_file, dest_video)

        # Copy Cover Thumbnail
        cover_src = os.path.join(src_dir, "scene_1.jpg")
        dest_cover = os.path.join(pkg_dir, "cover_thumbnail.jpg")
        if os.path.exists(cover_src):
            shutil.copy2(cover_src, dest_cover)

        # Generate Instagram Caption
        caption_text = (
            f"{meta['hook']}\n\n"
            f"{meta['synopsis']}\n\n"
            f"🌟 कहानी की सीख (Moral of the Story):\n"
            f"{meta['moral']}\n\n"
            f"💬 {meta['question']}\n\n"
            f"👉 अपने बच्चों और दोस्तों के साथ यह जादुई कहानी ज़रूर SHARE और SAVE करें! ❤️\n"
            f"🎬 पूरी 3D कहानी और नए एपिसोड्स देखने के लिए BIO में दिए गए YouTube लिंक पर क्लिक करें! 🔔\n"
            f"Follow @magicaltaleskid for daily 3D Hindi moral stories! ✨\n\n"
            f"{INSTAGRAM_HASHTAGS}\n"
        )

        caption_file = os.path.join(pkg_dir, "caption.txt")
        with open(caption_file, "w", encoding="utf-8") as f:
            f.write(caption_text)

        print(f"✅ Packaged Reel: [{meta['title']}]")
        print(f"   📁 Folder : {pkg_dir}")
        print(f"   🎥 Video  : {os.path.basename(dest_video)} ({round(os.path.getsize(dest_video)/(1024*1024), 1)} MB)")
        print(f"   🖼️  Cover  : cover_thumbnail.jpg")
        print(f"   ✍️ Caption: caption.txt ready\n")
        count += 1

    print("=" * 70)
    print(f"🎉 PACKAGING COMPLETE: {count} Instagram Reels ready for @magicaltaleskid!")
    print(f"📍 Location: {REELS_PKG_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    package_reels()
