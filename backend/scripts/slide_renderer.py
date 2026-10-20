import os
import sys
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(font_type="sans-bold", size=60):
    """
    Returns an ImageFont instance matching the requested profile.
    Searches system font folders dynamically with robust default fallbacks.
    """
    font_candidates = {
        "sans-bold": [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            r"C:\Windows\Fonts\seguiemj.ttf", # Emoji support
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttf"
        ],
        "sans-regular": [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttf"
        ],
        "sans-italic": [
            r"C:\Windows\Fonts\ariali.ttf",
            r"C:\Windows\Fonts\calibrii.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
            "/System/Library/Fonts/Helvetica.ttf"
        ],
        "serif-bold": [
            r"C:\Windows\Fonts\timesbd.ttf",
            r"C:\Windows\Fonts\georgiab.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/System/Library/Fonts/Times.dfont"
        ],
        "serif-regular": [
            r"C:\Windows\Fonts\times.ttf",
            r"C:\Windows\Fonts\georgia.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/System/Library/Fonts/Times.dfont"
        ],
        "serif-italic": [
            r"C:\Windows\Fonts\timesi.ttf",
            r"C:\Windows\Fonts\georgiai.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
            "/System/Library/Fonts/Times.dfont"
        ],
        "mono": [
            r"C:\Windows\Fonts\consola.ttf",
            r"C:\Windows\Fonts\cour.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/System/Library/Fonts/Courier.ttf"
        ]
    }
    
    candidates = font_candidates.get(font_type, font_candidates["sans-regular"])
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
                
    # Direct Pillow default fallback if no files match
    return ImageFont.load_default()


def draw_wrapped_text(draw, text, font, fill_color, x, y, max_width, line_spacing=1.3):
    """
    Helper to wrap text to fit within a maximum width and draw it.
    Returns the ending Y coordinate so items can be stacked sequentially.
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        # Use getlength if available (Pillow 10+), otherwise fall back to draw.textbbox
        try:
            w = font.getlength(test_line)
        except AttributeError:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            
        if w > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []
                
    if current_line:
        lines.append(" ".join(current_line))
        
    current_y = y
    # Retrieve line height metrics
    try:
        bbox = draw.textbbox((0, 0), "Aj", font=font)
        line_h = int((bbox[3] - bbox[1]) * line_spacing)
    except AttributeError:
        line_h = int(65 * line_spacing)
        
    for line in lines:
        draw.text((x, current_y), line, fill=fill_color, font=font)
        current_y += line_h
        
    return current_y


from html.parser import HTMLParser
import html

class HTMLStyledTextParser(HTMLParser):
    def __init__(self, default_color):
        super().__init__()
        self.tokens = []
        self.is_bold = False
        self.is_italic = False
        self.is_underline = False
        self.current_color = default_color
        self.default_color = default_color
        self.is_bullet = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ("b", "strong"):
            self.is_bold = True
        elif tag in ("i", "em"):
            self.is_italic = True
        elif tag in ("u",):
            self.is_underline = True
        elif tag == "li":
            self.is_bullet = True
            # Add bullet point indicator token
            self.tokens.append({
                "text": "•",
                "bold": True,
                "italic": False,
                "underline": False,
                "color": self.current_color,
                "is_bullet": True
            })
            # Add a non-breaking space
            self.tokens.append({
                "text": "  ",
                "bold": False,
                "italic": False,
                "underline": False,
                "color": self.current_color
            })
        elif tag in ("p", "br", "div"):
            # Add newline token
            self.tokens.append({
                "text": "\n",
                "bold": False,
                "italic": False,
                "underline": False,
                "color": self.current_color
            })
        elif tag in ("span", "font"):
            if "color" in attrs_dict:
                color_hex = attrs_dict["color"].strip().lstrip("#")
                try:
                    self.current_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                except Exception:
                    pass
            elif "style" in attrs_dict:
                style_str = attrs_dict["style"]
                if "color:" in style_str:
                    try:
                        color_hex = style_str.split("color:", 1)[1].split(";", 1)[0].strip().lstrip("#")
                        self.current_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                    except Exception:
                        pass

    def handle_endtag(self, tag):
        if tag in ("b", "strong"):
            self.is_bold = False
        elif tag in ("i", "em"):
            self.is_italic = False
        elif tag in ("u",):
            self.is_underline = False
        elif tag in ("li", "p", "div"):
            self.is_bullet = False
            self.tokens.append({
                "text": "\n",
                "bold": False,
                "italic": False,
                "underline": False,
                "color": self.current_color
            })
        elif tag in ("span", "font"):
            self.current_color = self.default_color

    def handle_data(self, data):
        # Decode any standard HTML entities
        clean_data = html.unescape(data)
        # Split by spaces but preserve them as separate tokens for wrapping
        words = re.split(r'(\s+)', clean_data)
        for w in words:
            if not w:
                continue
            self.tokens.append({
                "text": w,
                "bold": self.is_bold,
                "italic": self.is_italic,
                "underline": self.is_underline,
                "color": self.current_color
            })


def draw_styled_html(draw, html_text, x_start, y_start, max_width, font_family="sans", default_size=60, default_color=(28,27,26), default_line_height=80, alignment="left"):
    """
    Renders fully formatted HTML text with inline styles onto Pillow canvas.
    Handles word wrapping, paragraph alignments, list bullets, bold, italic, and underline tags.
    """
    # 1. Parse HTML into style tokens
    parser = HTMLStyledTextParser(default_color)
    try:
        parser.feed(html_text)
        tokens = parser.tokens
    except Exception as e:
        print(f"[slide_renderer] HTML parse failed: {e}. Falling back to plain text.", flush=True)
        # Fallback to plain text wrapping
        font = get_font(f"{font_family}-regular", default_size)
        return draw_wrapped_text(draw, html_text, font, default_color, x_start, y_start, max_width)

    # 2. Pre-load style fonts
    fonts = {
        "regular": get_font(f"{font_family}-regular", default_size),
        "bold": get_font(f"{font_family}-bold", default_size),
        "italic": get_font(f"{font_family}-italic", default_size),
        # Fallback for bold+italic
        "bold_italic": get_font(f"{font_family}-bold", default_size)
    }

    # 3. Group tokens into lines based on max_width
    lines = []
    current_line = []
    current_width = 0
    
    for token in tokens:
        text = token["text"]
        if text == "\n":
            lines.append(current_line)
            current_line = []
            current_width = 0
            continue
            
        font_key = "regular"
        if token.get("bold") and token.get("italic"):
            font_key = "bold_italic"
        elif token.get("bold"):
            font_key = "bold"
        elif token.get("italic"):
            font_key = "italic"
            
        font = fonts.get(font_key) or fonts.get("regular")
        
        # Measure size
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
        except AttributeError:
            w = draw.textsize(text, font=font)[0]
            
        if current_width + w > max_width and text.strip() and not token.get("is_bullet"):
            # Wrap
            lines.append(current_line)
            current_line = [token]
            current_width = w
        else:
            current_line.append(token)
            current_width += w
            
    if current_line:
        lines.append(current_line)
        
    # 4. Render lines on the canvas
    y = y_start
    for line in lines:
        if not line or (len(line) == 1 and line[0]["text"].strip() == ""):
            y += default_line_height // 2
            continue
            
        # Calculate total line width for custom alignments
        total_line_w = 0
        line_tokens_with_fonts = []
        for token in line:
            font_key = "regular"
            if token.get("bold"): font_key = "bold"
            elif token.get("italic"): font_key = "italic"
            font = fonts.get(font_key) or fonts.get("regular")
            
            try:
                bbox = draw.textbbox((0, 0), token["text"], font=font)
                w = bbox[2] - bbox[0]
            except AttributeError:
                w = draw.textsize(token["text"], font=font)[0]
            total_line_w += w
            line_tokens_with_fonts.append((token, font, w))
            
        # Compute horizontal alignment offset
        if alignment == "center":
            x = x_start + (max_width - total_line_w) // 2
        elif alignment == "right":
            x = x_start + (max_width - total_line_w)
        else:
            x = x_start
            
        # Draw tokens sequentially
        for token, font, w in line_tokens_with_fonts:
            # Underline handling
            draw.text((x, y), token["text"], fill=token["color"], font=font)
            if token.get("underline"):
                try:
                    bbox = draw.textbbox((x, y), token["text"], font=font)
                    line_y = bbox[3] + 4
                except AttributeError:
                    line_y = y + default_size + 4
                draw.line([(x, line_y), (x + w, line_y)], fill=token["color"], width=3)
            x += w
            
        y += default_line_height
        
    return y


def draw_bold_bullet(draw, title, desc, font_bold, font_reg, color_bold, color_reg, x, y, max_width):
    """
    Renders an elegant textbook-style bullet point.
    Draws the dot indicator, the bold title prefix (e.g. 'Easy to Learn & Read: '),
    and then wraps and draws the regular-weight description text next to it.
    """
    dot = "•  "
    try:
        dot_w = font_bold.getlength(dot)
    except AttributeError:
        dot_w = len(dot) * 25
    draw.text((x, y), dot, fill=color_bold, font=font_bold)
    
    full_title = f"{title}: "
    combined_text = f"{full_title}{desc}"
    
    # Wrap combined text using the regular font
    words = combined_text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        try:
            w = font_reg.getlength(test_line)
        except AttributeError:
            bbox = draw.textbbox((0, 0), test_line, font=font_reg)
            w = bbox[2] - bbox[0]
        if w > max_width - dot_w:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
        
    try:
        bbox_reg = draw.textbbox((0, 0), "Aj", font=font_reg)
        line_h = int((bbox_reg[3] - bbox_reg[1]) * 1.35)
    except AttributeError:
        line_h = int(55 * 1.35)
        
    current_y = y
    first_line = True
    for line in lines:
        line_x = x + dot_w if first_line else x + dot_w + 20
        
        if first_line and line.startswith(full_title):
            # Draw the bold title prefix
            draw.text((line_x, current_y), full_title, fill=color_bold, font=font_bold)
            try:
                prefix_w = font_bold.getlength(full_title)
            except AttributeError:
                prefix_w = len(full_title) * 32
            remaining_text = line[len(full_title):]
            draw.text((line_x + prefix_w, current_y), remaining_text, fill=color_reg, font=font_reg)
        else:
            draw.text((line_x, current_y), line, fill=color_reg, font=font_reg)
            
        current_y += line_h
        first_line = False
        
    return current_y


def draw_slide_gradient(width, height):
    """
    Creates a premium linear background gradient spanning from slate-black (#090A0E)
    to a modern deep space purple (#161424).
    """
    img = Image.new("RGB", (width, height), color=(9, 10, 14))
    draw = ImageDraw.Draw(img)
    
    start_color = (9, 10, 14)       # Deep slate black
    end_color = (25, 20, 42)        # Cosmic deep purple
    
    for y in range(height):
        # Linear interpolation
        ratio = y / float(height)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    return img


def add_dot_grid(img, spacing=150):
    """
    Overlays a subtle, elegant high-tech dot grid pattern to make the background
    look like an architect's canvas or a premium whiteboard.
    Spaced and sized elegantly for native 4K Ultra HD.
    """
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    dot_color = (255, 255, 255, 16)  # Slightly more distinct transparent white
    # Since drawing thousands of dots is fast, cover the whole canvas
    for x in range(spacing, width, spacing):
        for y in range(spacing, height, spacing):
            # Draw a beautiful crisp 5x5 dot
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=dot_color)


def render_slide(
    scene_data: dict,
    output_path: str,
    width: int = 2160,
    height: int = 3840,
    illustration_path: str = None
):
    """
    Core slide layout engine.
    Renders a vertical 9:16 slide card combining:
      - Deep Slate Gradient with tech dot grid overlay.
      - Glassmorphic rounded container card with neon outer outline.
      - Sleek Step label pill (e.g. 'STEP 1') in top-left.
      - Bold educational Title.
      - Custom bullets list (with checkmark icons).
      - EITHER a macOS mockup code terminal box OR a beautifully formatted
        graphic panel containing the generated Pollinations image.
    """
    # 1. Base Gradient Canvas (Completely clean and minimalist without tech dot grid lines)
    bg_color_hex = scene_data.get("bg_color", "").strip()
    if bg_color_hex and bg_color_hex.startswith("#"):
        try:
            hex_clean = bg_color_hex.lstrip("#")
            bg_color_rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
            img = Image.new("RGB", (width, height), color=bg_color_rgb)
        except Exception:
            img = draw_slide_gradient(width, height)
    else:
        img = draw_slide_gradient(width, height)
    
    # Create transparency layer for glassmorphic overlay card
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # 2. Main Center Card coordinates
    margin_x = 120
    card_top = 280
    card_bottom = height - 280
    card_width = width - (2 * margin_x)
    
    # Draw semi-transparent dark grey card background (#121420 with 86% opacity)
    card_color = (18, 20, 32, 220) 
    card_r = 70  # Corner radius
    
    # Draw rounded rectangle container (completely clean and borderless, removing all outer cyan neon border lines)
    draw_overlay.rounded_rectangle(
        [margin_x, card_top, width - margin_x, card_bottom],
        radius=card_r,
        fill=card_color
    )
    
    # Composite the overlay onto the base image
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # Simple Q&A Layout Handlers (Textbook Style Layout)
    layout_type = scene_data.get("layout_type", "")
    if layout_type == "simple_qa":
        # Get selected brand/art style template - support forced slide preset override!
        brand_style = str(scene_data.get("slide_style", scene_data.get("art_style", "cinematic"))).lower().strip()
        
        # Define 5 premium educational slide brand palettes matching the selected preset
        PALETTES = {
            "cyberpunk": {
                "bg": (9, 7, 15),              # Deep midnight neon black
                "charcoal": (255, 0, 127),      # Hot neon pink for title/bold
                "grey": (0, 240, 255),          # Vibrant ice cyan for descriptions
                "divider": (59, 28, 95)         # Neon purple divider
            },
            "pixar": {
                "bg": (250, 249, 246),          # Soft clean white
                "charcoal": (225, 91, 50),      # Cozy bright coral/orange
                "grey": (59, 72, 86),           # Modern slate blue/grey
                "divider": (245, 220, 208)      # Soft peach divider
            },
            "anime": {
                "bg": (10, 17, 40),             # Deep tranquil navy blue
                "charcoal": (226, 177, 60),     # Radiant golden amber
                "grey": (209, 213, 219),        # Soft silver grey
                "divider": (27, 42, 87)         # Deep cobalt divider
            },
            "oil_painting": {
                "bg": (18, 18, 18),             # Sophisticated dark charcoal grey
                "charcoal": (212, 175, 55),     # Classic imperial metallic gold
                "grey": (250, 240, 230),        # Warm linen ivory
                "divider": (45, 45, 42)         # Deep bronze divider
            },
            "cinematic": {
                "bg": (249, 246, 240),          # Warm book cream page
                "charcoal": (28, 27, 26),       # Deep dark charcoal brown
                "grey": (74, 69, 63),           # Elegant charcoal grey
                "divider": (228, 224, 213)      # Warm beige divider
            }
        }
        
        # Select palette or fallback to cinematic
        palette = PALETTES.get(brand_style)
        if not palette:
            if "paint" in brand_style:
                palette = PALETTES["oil_painting"]
            elif "cyber" in brand_style:
                palette = PALETTES["cyberpunk"]
            elif "pixar" in brand_style or "3d" in brand_style:
                palette = PALETTES["pixar"]
            elif "anime" in brand_style:
                palette = PALETTES["anime"]
            else:
                palette = PALETTES["cinematic"]
                
        bg_color = palette["bg"]
        color_charcoal = palette["charcoal"]
        color_grey = palette["grey"]
        color_divider = palette["divider"]
        
        # Check for slide-specific background color override!
        bg_color_override = scene_data.get("bg_color", "").strip()
        if bg_color_override and bg_color_override.startswith("#"):
            try:
                hex_clean = bg_color_override.lstrip("#")
                bg_color_rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                bg_color = bg_color_rgb
            except Exception:
                pass
                
        # Check for slide heading & text color override!
        font_color_override = scene_data.get("font_color", "").strip()
        if font_color_override and font_color_override.startswith("#"):
            try:
                hex_clean = font_color_override.lstrip("#")
                color_override_rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                color_charcoal = color_override_rgb
                color_grey = color_override_rgb
            except Exception:
                pass
        
        # 1. Re-initialize canvas to solid brand style background
        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        margin_left = 140
        max_text_width = width - (2 * margin_left)
        
        # Get custom typography overrides or default to standard
        font_family = str(scene_data.get("font_family", "sans")).strip().lower()
        if font_family not in ("sans", "serif", "mono"):
            font_family = "sans"
            
        font_size_summary = int(scene_data.get("font_size", 72))
        alignment = str(scene_data.get("alignment", "left")).strip().lower()
        if alignment not in ("left", "center", "right"):
            alignment = "left"
            
        line_height_factor = float(scene_data.get("line_height", 1.35))
        line_spacing_pixels = int(font_size_summary * line_height_factor)
        
        # 2. Draw high-level summary paragraph at the top using the HTML compiler
        summary_text = scene_data.get("summary", scene_data.get("narration", ""))
        summary_y = 380
        
        summary_bottom = draw_styled_html(
            draw,
            html_text=summary_text,
            x_start=margin_left,
            y_start=summary_y,
            max_width=max_text_width,
            font_family=font_family,
            default_size=font_size_summary,
            default_color=color_charcoal,
            default_line_height=line_spacing_pixels,
            alignment=alignment
        )
        
        # 3. Draw horizontal dividing line
        divider_y = summary_bottom + 80
        draw.line(
            [(margin_left, divider_y), (width - margin_left, divider_y)],
            fill=color_divider,
            width=6
        )
        
        # 4. Draw section title with key emoji
        section_title = scene_data.get("section_title", "🔑 Key Features").strip()
        font_size_section = 80
        section_y = divider_y + 110
        
        section_bottom = draw_styled_html(
            draw,
            html_text=section_title,
            x_start=margin_left,
            y_start=section_y,
            max_width=max_text_width,
            font_family=font_family,
            default_size=font_size_section,
            default_color=color_charcoal,
            default_line_height=int(font_size_section * 1.3),
            alignment=alignment
        )
        
        # 5. Draw the elegant list of bullet points
        bullets = scene_data.get("bullets", [])
        bullet_y = section_bottom + 80
        bullet_spacing = 90
        
        for bullet in bullets:
            if isinstance(bullet, dict):
                title = bullet.get("title", "").strip()
                desc = bullet.get("description", "").strip()
                bullet_str = f"<b>{title}:</b> {desc}" if desc else title
            else:
                bullet_str = bullet.strip()
                
            if not bullet_str:
                continue
                
            # Automatically wrap plain bullets inside list items
            if not bullet_str.startswith("<li"):
                bullet_str = f"<li>{bullet_str}</li>"
                
            bullet_bottom = draw_styled_html(
                draw,
                html_text=bullet_str,
                x_start=margin_left,
                y_start=bullet_y,
                max_width=max_text_width,
                font_family=font_family,
                default_size=58,
                default_color=color_grey,
                default_line_height=78,
                alignment="left"
            )
            bullet_y = bullet_bottom + 30
            
        # Save finished slide frame as pixel-perfect lossless JPEG
        img.save(output_path, "JPEG", quality=100, subsampling=0)
        print(f"[slide_renderer] [OK] Rendered Textbook Style Lossless 4K Q&A slide saved to: {output_path}", flush=True)
        return

    # 3. Step Badge Pill in Top-Left
    step_label = scene_data.get("step_title", "INTRO").upper()
    font_badge = get_font("sans-bold", 56)
    badge_x = margin_x + 60
    badge_y = card_top + 60
    
    # Render pill background
    badge_padding_x = 50
    badge_padding_y = 24
    # Determine text box size
    try:
        badge_box = draw.textbbox((0, 0), step_label, font=font_badge)
        text_w = badge_box[2] - badge_box[0]
        text_h = badge_box[3] - badge_box[1]
    except AttributeError:
        text_w = len(step_label) * 36
        text_h = 56
        
    badge_r = 30
    draw.rounded_rectangle(
        [
            badge_x - badge_padding_x,
            badge_y - badge_padding_y,
            badge_x + text_w + badge_padding_x,
            badge_y + text_h + badge_padding_y
        ],
        radius=badge_r,
        fill=(0, 255, 255, 30), # 12% opacity cyan fill
        outline=(0, 255, 255, 180),
        width=4
    )
    # Draw badge text in vibrant cyan (#00FFFF)
    draw.text((badge_x, badge_y - 2), step_label, fill=(0, 255, 255), font=font_badge)
    
    # 4. Slide Bold Title
    slide_title = scene_data.get("slide_title", "Step Details").strip()
    font_title = get_font("sans-bold", 110)
    title_x = margin_x + 60
    title_y = badge_y + text_h + 80
    
    # Draw elegant white title with high legibility wrapping
    title_bottom = draw_wrapped_text(
        draw,
        slide_title,
        font=font_title,
        fill_color=(255, 255, 255),
        x=title_x,
        y=title_y,
        max_width=card_width - 120,
        line_spacing=1.2
    )
    
    # Draw subtle dividing line below title (upgraded to 6px)
    divider_y = title_bottom + 40
    draw.line(
        [(title_x, divider_y), (width - title_x, divider_y)],
        fill=(50, 60, 85),
        width=6
    )
    

    # 5. Bullet Points List
    bullets = scene_data.get("bullets", [])
    font_bullet = get_font("sans-regular", 68)
    bullet_y = divider_y + 70
    
    for b_idx, bullet in enumerate(bullets):
        if not bullet.strip():
            continue
        
        # Render a gorgeous, glowing cyan/mint circle badge for the bullet dot
        bullet_dot_x = title_x + 15
        bullet_dot_y = bullet_y + 24
        bullet_dot_r = 16
        
        # Draw soft glowing bullet dot outer core
        draw.ellipse(
            [
                bullet_dot_x - bullet_dot_r,
                bullet_dot_y - bullet_dot_r,
                bullet_dot_x + bullet_dot_r,
                bullet_dot_y + bullet_dot_r
            ],
            fill=(0, 255, 180) # Mint neon
        )
        
        # Wrap and draw bullet text
        bullet_text_x = bullet_dot_x + 55
        bullet_bottom = draw_wrapped_text(
            draw,
            bullet,
            font=font_bullet,
            fill_color=(230, 235, 245),
            x=bullet_text_x,
            y=bullet_y,
            max_width=card_width - 180,
            line_spacing=1.35
        )
        # Advance vertically for next bullet
        bullet_y = bullet_bottom + 50
        
    # 6. Bottom Asset Block Layout (macOS Code Box OR Generated Graphic Card)
    code_snippet = scene_data.get("code_snippet", "").strip()
    
    asset_top = card_bottom - 1100  # Give asset block ~1000px height
    asset_bottom = card_bottom - 80
    asset_left = margin_x + 60
    asset_right = width - margin_x - 60
    asset_width = asset_right - asset_left
    asset_height = asset_bottom - asset_top
    
    if code_snippet:
        # Layout Option A: Renders a macOS-style Developer Code Editor Card
        # Draw Editor dark container (#0A0B10) with upgraded border stroke
        draw.rounded_rectangle(
            [asset_left, asset_top, asset_right, asset_bottom],
            radius=35,
            fill=(10, 11, 16),
            outline=(45, 50, 70),
            width=4
        )
        
        # Draw macOS window controls top header bar
        dot_r = 16
        dot_start_x = asset_left + 60
        dot_y = asset_top + 60
        dot_spacing = 42
        
        # Red
        draw.ellipse([dot_start_x - dot_r, dot_y - dot_r, dot_start_x + dot_r, dot_y + dot_r], fill=(255, 95, 86))
        # Yellow
        draw.ellipse([dot_start_x + dot_spacing - dot_r, dot_y - dot_r, dot_start_x + dot_spacing + dot_r, dot_y + dot_r], fill=(255, 189, 46))
        # Green
        draw.ellipse([dot_start_x + (2 * dot_spacing) - dot_r, dot_y - dot_r, dot_start_x + (2 * dot_spacing) + dot_r, dot_y + dot_r], fill=(39, 201, 63))
        
        # Draw subtle Editor tab title, e.g. "script.py"
        font_tab = get_font("mono", 44)
        draw.text((dot_start_x + 150, dot_y - 25), "tutorial.py", fill=(100, 115, 140), font=font_tab)
        
        # Draw code text inside editor starting below the header (scaled up for high-legibility CS code display)
        code_font = get_font("mono", 64)
        code_text_x = asset_left + 60
        code_text_y = dot_y + 80
        
        # Render code lines with bright glowing color highlights (mint/cyan theme)
        lines = code_snippet.split("\n")
        line_spacing_h = 88
        
        # Regex-based syntax highlighter for elite textbook mockup code displays
        # Matches comments, double/single quoted strings, keywords, builtins, numbers, and other characters/spaces
        code_regex = re.compile(
            r'(?P<comment>#.*)|'
            r'(?P<string>"[^"]*"|\'[^\']*\')|'
            r'\b(?P<keyword>def|class|import|from|return|if|else|elif|for|in|while|try|except|with|as|lambda|pass|yield|and|or|not|is)\b|'
            r'\b(?P<builtin>print|len|int|str|float|list|dict|set|tuple|range|self)\b|'
            r'\b(?P<number>\d+)\b|'
            r'(?P<other>[^\s#"\']+|\s+)'
        )
        
        for line_idx, line in enumerate(lines):
            if line_idx > 10:  # Prevent overflow
                break
                
            # Render line token-by-token with appropriate aesthetic colors
            current_x = code_text_x
            display_line = line.strip()
            
            for match in code_regex.finditer(display_line):
                token = match.group(0)
                if match.group("comment"):
                    color = (100, 115, 140)      # Deep Slate Gray for comments
                elif match.group("string"):
                    color = (255, 180, 110)      # Soft Peach/Orange for strings
                elif match.group("keyword"):
                    color = (255, 95, 162)       # Hot Pink for keywords
                elif match.group("builtin"):
                    color = (0, 240, 255)        # Cyber Cyan for builtins
                elif match.group("number"):
                    color = (255, 215, 0)        # Bright Gold for numbers
                else:
                    color = (0, 255, 180)        # Crisp Mint Green for variables, symbols, and operators
                    
                draw.text((current_x, code_text_y), token, fill=color, font=code_font)
                try:
                    current_x += code_font.getlength(token)
                except AttributeError:
                    # Fallback for older Pillow versions lacking getlength
                    bbox = draw.textbbox((0, 0), token, font=code_font)
                    current_x += (bbox[2] - bbox[0])
                    
            code_text_y += line_spacing_h
            
    elif illustration_path and os.path.exists(illustration_path):
        # Layout Option B: Renders an Illustration Graphic Card
        # Pastes the generated Pollinations image inside a beautiful centered capsule box
        try:
            # Load illustration
            illus = Image.open(illustration_path)
            
            # Rescale illustration to fit inside slide asset region
            # Maintain aspect ratio to avoid distortion, then crop to fill the asset region neatly
            illus_w, illus_h = illus.size
            
            # Determine scale factor to fill the asset rectangle
            scale_f = max(asset_width / float(illus_w), asset_height / float(illus_h))
            new_w = int(illus_w * scale_f)
            new_h = int(illus_h * scale_f)
            
            # Resize
            illus_resized = illus.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Crop to exact bounds
            crop_x = (new_w - asset_width) // 2
            crop_y = (new_h - asset_height) // 2
            illus_cropped = illus_resized.crop((crop_x, crop_y, crop_x + asset_width, crop_y + asset_height))
            
            # Create a rounded mask to round the edges of the pasted image beautifully
            mask = Image.new("L", (asset_width, asset_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, asset_width, asset_height], radius=45, fill=255)
            
            # Paste illustration onto slide frame
            img.paste(illus_cropped, (asset_left, asset_top), mask)
            
            # Borderless illustration capsule
            pass
        except Exception as e:
            print(f"[slide_renderer] Failed to paste slide illustration: {e}", flush=True)
            
    else:
        # Layout Option C: Typographical Fallback Box if no code/image
        # Draw a clean high-legibility motivational/takeaway tip box
        draw.rounded_rectangle(
            [asset_left, asset_top, asset_right, asset_bottom],
            radius=35,
            fill=(25, 30, 50, 40), # Highly transparent slate card
            outline=(50, 60, 85),
            width=3
        )
        
        # Center quote mark icon
        font_quote = get_font("sans-bold", 140)
        draw.text((asset_left + 60, asset_top + 80), "💡", fill=(255, 200, 0), font=font_quote)
        
        # Add a prominent educational reminder summary
        font_tip = get_font("sans-regular", 64)
        draw_wrapped_text(
            draw,
            "Remember: clear visual steps and deliberate pacing make your lessons unforgettable. Double-check your code to verify it compiles perfectly!",
            font=font_tip,
            fill_color=(150, 165, 190),
            x=asset_left + 240,
            y=asset_top + 110,
            max_width=asset_width - 300,
            line_spacing=1.35
        )
        
    # Save finished slide frame as pixel-perfect lossless JPEG
    # Disabling lossy chroma subsampling (subsampling=0) and setting quality=100
    # preserves vector-sharp text edges on dark slate canvas with absolute zero artifacts!
    img.save(output_path, "JPEG", quality=100, subsampling=0)
    print(f"[slide_renderer] [OK] Rendered Lossless 4K slide frame saved to: {output_path}", flush=True)

