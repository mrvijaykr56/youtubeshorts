Add-Type -AssemblyName PresentationCore, PresentationFramework, WindowsBase, System.Xaml

$source = @'
using System;
using System.IO;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Globalization;

public class FestivePollGenerator {
    public static void GenerateSquare1x1(string outputPath) {
        int W = 1080;
        int H = 1080;
        var rtb = new RenderTargetBitmap(W, H, 96, 96, PixelFormats.Pbgra32);
        var visual = new DrawingVisual();

        using (var dc = visual.RenderOpen()) {
            // 1. Royal Festive Background Gradient (Midnight Indigo to Deep Royal Purple)
            var bgGradient = new LinearGradientBrush(
                Color.FromRgb(15, 8, 30),
                Color.FromRgb(40, 15, 55),
                new Point(0, 0),
                new Point(0, 1)
            );
            dc.DrawRectangle(bgGradient, null, new Rect(0, 0, W, H));

            // Outer Golden Border
            var borderPen = new Pen(new SolidColorBrush(Color.FromArgb(160, 255, 215, 0)), 4);
            dc.DrawRoundedRectangle(null, borderPen, new Rect(25, 25, W - 50, H - 50), 20, 20);

            var fontNirmala = new FontFamily("Nirmala UI");
            var ci = CultureInfo.GetCultureInfo("hi-IN");

            // 2. Top Festive Badge
            var badgePen = new Pen(new SolidColorBrush(Color.FromRgb(255, 180, 0)), 1.5);
            var badgeBrush = new SolidColorBrush(Color.FromArgb(90, 80, 20, 120));
            dc.DrawRoundedRectangle(badgeBrush, badgePen, new Rect((W - 540) / 2.0, 45, 540, 48), 24, 24);

            var badgeTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var badgeFt = new FormattedText("🪔 FESTIVE SPECIAL COMMUNITY POLL ✨", ci, FlowDirection.LeftToRight, badgeTf, 22, new SolidColorBrush(Color.FromRgb(255, 220, 100)), 1.25);
            badgeFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(badgeFt, new Point(W / 2.0, 56));

            // 3. Main Question Header
            var titleTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var titleFt = new FormattedText("इस बार दीपावली और छठ पूजा पर आपके घर\nसबसे पसंदीदा पकवान कौन सा बनता है?", ci, FlowDirection.LeftToRight, titleTf, 36, new SolidColorBrush(Color.FromRgb(255, 255, 255)), 1.25);
            titleFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(titleFt, new Point(W / 2.0, 115));

            var subTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Normal, FontStretches.Normal);
            var subFt = new FormattedText("अपनी पसंद को VOTE करें (Comments में 1, 2, 3 या 4 लिखें) 👇", ci, FlowDirection.LeftToRight, subTf, 24, new SolidColorBrush(Color.FromRgb(255, 210, 120)), 1.25);
            subFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(subFt, new Point(W / 2.0, 220));

            // 4. 4 Poll Options (Cards Layout: 2 rows of 2)
            int cardW = 460;
            int cardH = 280;
            int startX = 60;
            int gapX = 40;
            int startY = 275;
            int gapY = 35;

            var options = new[] {
                new { Num = "1", Title = "ठेकुआ (Thekua) 🌾", Desc = "छठ महापर्व का सबसे पावन व स्वादिष्ट महाप्रसाद", Col = startX, Row = startY, Accent = Color.FromRgb(255, 140, 0) },
                new { Num = "2", Title = "काजू कतली (Kaju Katli) 🍬", Desc = "दीपावली की सबसे लोकप्रिय व शाही मिठाई", Col = startX + cardW + gapX, Row = startY, Accent = Color.FromRgb(220, 20, 60) },
                new { Num = "3", Title = "बेसन के लड्डू (Besan Laddu) 🟡", Desc = "शुद्ध देसी घी के दानेदार व पारंपरिक लड्डू", Col = startX, Row = startY + cardH + gapY, Accent = Color.FromRgb(255, 190, 0) },
                new { Num = "4", Title = "मावे की गुजिया (Mawa Gujiya) 🥟", Desc = "दीपावली की खास कुरकुरी व मीठी पारंपरिक गुजिया", Col = startX + cardW + gapX, Row = startY + cardH + gapY, Accent = Color.FromRgb(50, 205, 50) }
            };

            foreach (var opt in options) {
                // Card Background (Frosted Glassmorphism with colored glow)
                var cardBg = new LinearGradientBrush(
                    Color.FromArgb(170, 30, 20, 50),
                    Color.FromArgb(210, 45, 25, 75),
                    new Point(0, 0),
                    new Point(1, 1)
                );
                var cardPen = new Pen(new SolidColorBrush(Color.FromArgb(120, opt.Accent.R, opt.Accent.G, opt.Accent.B)), 2.5);
                dc.DrawRoundedRectangle(cardBg, cardPen, new Rect(opt.Col, opt.Row, cardW, cardH), 18, 18);

                // Option Number Badge Circle
                var circleBrush = new SolidColorBrush(opt.Accent);
                dc.DrawEllipse(circleBrush, null, new Point(opt.Col + 55, opt.Row + 55), 32, 32);

                var numTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
                var numFt = new FormattedText(opt.Num, ci, FlowDirection.LeftToRight, numTf, 32, Brushes.White, 1.25);
                numFt.TextAlignment = TextAlignment.Center;
                dc.DrawText(numFt, new Point(opt.Col + 55, opt.Row + 35));

                // Option Title
                var optTitleTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
                var optTitleFt = new FormattedText(opt.Title, ci, FlowDirection.LeftToRight, optTitleTf, 28, new SolidColorBrush(Color.FromRgb(255, 235, 180)), 1.25);
                dc.DrawText(optTitleFt, new Point(opt.Col + 105, opt.Row + 40));

                // Divider Line
                var divPen = new Pen(new SolidColorBrush(Color.FromArgb(60, 255, 255, 255)), 1);
                dc.DrawLine(divPen, new Point(opt.Col + 30, opt.Row + 105), new Point(opt.Col + cardW - 30, opt.Row + 105));

                // Description text
                var descTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Normal, FontStretches.Normal);
                var descFt = new FormattedText(opt.Desc, ci, FlowDirection.LeftToRight, descTf, 21, new SolidColorBrush(Color.FromRgb(220, 220, 240)), 1.25);
                descFt.MaxTextWidth = cardW - 60;
                descFt.TextAlignment = TextAlignment.Left;
                dc.DrawText(descFt, new Point(opt.Col + 30, opt.Row + 125));

                // Interactive 'Vote' Pill Button inside card
                var votePillBrush = new SolidColorBrush(Color.FromArgb(140, opt.Accent.R, opt.Accent.G, opt.Accent.B));
                dc.DrawRoundedRectangle(votePillBrush, null, new Rect(opt.Col + 30, opt.Row + cardH - 65, cardW - 60, 42), 21, 21);
                var voteTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
                var voteFt = new FormattedText("VOTE FOR OPTION " + opt.Num, ci, FlowDirection.LeftToRight, voteTf, 18, Brushes.White, 1.25);
                voteFt.TextAlignment = TextAlignment.Center;
                dc.DrawText(voteFt, new Point(opt.Col + (cardW / 2.0), opt.Row + cardH - 55));
            }

            // 5. Bottom Channel Branding Bar
            var footerTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var footerFt = new FormattedText("🔔 @MagicalTalesKidz | 3D Hindi Kahaniya & Festive Specials", ci, FlowDirection.LeftToRight, footerTf, 23, new SolidColorBrush(Color.FromRgb(255, 215, 0)), 1.25);
            footerFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(footerFt, new Point(W / 2.0, H - 70));
        }

        rtb.Render(visual);

        var encoder = new JpegBitmapEncoder();
        encoder.QualityLevel = 96;
        encoder.Frames.Add(BitmapFrame.Create(rtb));

        var dir = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir)) {
            Directory.CreateDirectory(dir);
        }

        using (var fs = new FileStream(outputPath, FileMode.Create, FileAccess.Write)) {
            encoder.Save(fs);
        }
        Console.WriteLine("[FestivePollGenerator] Successfully created 1080x1080 festive poll graphic at: " + outputPath);
    }
}
'@

Add-Type -TypeDefinition $source -ReferencedAssemblies PresentationCore, PresentationFramework, WindowsBase, System.Xaml

$outputPath = "D:\WorkSpace\MyVideoWorkspace\backend\output\festive_poll_assets\festive_poll_1080x1080.jpg"
[FestivePollGenerator]::GenerateSquare1x1($outputPath)
