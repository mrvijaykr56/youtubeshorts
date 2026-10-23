Add-Type -AssemblyName PresentationCore, PresentationFramework, WindowsBase, System.Xaml

$source = @'
using System;
using System.IO;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Globalization;

public class PollImageGenerator {
    private static BitmapImage LoadBitmap(string path) {
        var bmp = new BitmapImage();
        bmp.BeginInit();
        bmp.CacheOption = BitmapCacheOption.OnLoad;
        bmp.UriSource = new Uri(Path.GetFullPath(path));
        bmp.EndInit();
        return bmp;
    }

    public static void GenerateSquare1x1(string assetDir, string outputPath) {
        int W = 1080;
        int H = 1080;
        var rtb = new RenderTargetBitmap(W, H, 96, 96, PixelFormats.Pbgra32);
        var visual = new DrawingVisual();

        using (var dc = visual.RenderOpen()) {
            // Dark gradient background
            var gradient = new LinearGradientBrush(
                Color.FromRgb(15, 12, 28),
                Color.FromRgb(32, 24, 60),
                new Point(0, 0),
                new Point(0, 1)
            );
            dc.DrawRectangle(gradient, null, new Rect(0, 0, W, H));

            var fontNirmala = new FontFamily("Nirmala UI");
            var ci = CultureInfo.GetCultureInfo("hi-IN");

            // Header Title
            var titleTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var titleFt = new FormattedText("अगली 3D कहानी कौन सी देखना चाहते हैं? 🎬✨", ci, FlowDirection.LeftToRight, titleTf, 38, new SolidColorBrush(Color.FromRgb(255, 215, 0)), 1.25);
            titleFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(titleFt, new Point(W / 2.0, 35));

            var subTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Normal, FontStretches.Normal);
            var subFt = new FormattedText("अपनी पसंदीदा कहानी को VOTE करें (1, 2, 3 या 4) 👇", ci, FlowDirection.LeftToRight, subTf, 26, new SolidColorBrush(Color.FromRgb(210, 210, 235)), 1.25);
            subFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(subFt, new Point(W / 2.0, 88));

            // Grid items: 350x350
            int imgSize = 350;
            int gapX = 40;
            int startX = (W - (imgSize * 2 + gapX)) / 2; // 170
            int startY = 145;
            int rowGap = 70; // gap for label

            var items = new[] {
                new { File = "poll_option_1_thirsty_crow.jpg", Label = "1. प्यासा कौवा (Clever Crow)", X = startX, Y = startY, Num = "1" },
                new { File = "poll_option_2_tortoise_hare.jpg", Label = "2. कछुआ और खरगोश (The Race)", X = startX + imgSize + gapX, Y = startY, Num = "2" },
                new { File = "poll_option_3_greedy_dog.jpg", Label = "3. लालची कुत्ता (Greedy Dog)", X = startX, Y = startY + imgSize + rowGap, Num = "3" },
                new { File = "poll_option_4_friends_bear.jpg", Label = "4. दो दोस्त और भालू (True Friend)", X = startX + imgSize + gapX, Y = startY + imgSize + rowGap, Num = "4" }
            };

            var goldPen = new Pen(new SolidColorBrush(Color.FromRgb(255, 215, 0)), 3);
            var badgeBrush = new SolidColorBrush(Color.FromRgb(255, 45, 85));
            var badgeTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.ExtraBold, FontStretches.Normal);
            var labelTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);

            foreach (var item in items) {
                string fullPath = Path.Combine(assetDir, item.File);
                var img = LoadBitmap(fullPath);

                // Draw gold border & image
                dc.DrawRoundedRectangle(null, goldPen, new Rect(item.X - 2, item.Y - 2, imgSize + 4, imgSize + 4), 16, 16);
                dc.DrawImage(img, new Rect(item.X, item.Y, imgSize, imgSize));

                // Number badge
                dc.DrawRoundedRectangle(badgeBrush, null, new Rect(item.X + 10, item.Y + 10, 48, 48), 10, 10);
                var badgeFt = new FormattedText(item.Num, ci, FlowDirection.LeftToRight, badgeTf, 30, Brushes.White, 1.25);
                badgeFt.TextAlignment = TextAlignment.Center;
                dc.DrawText(badgeFt, new Point(item.X + 34, item.Y + 15));

                // Hindi + English Label below image
                var labelFt = new FormattedText(item.Label, ci, FlowDirection.LeftToRight, labelTf, 25, Brushes.White, 1.25);
                labelFt.TextAlignment = TextAlignment.Center;
                dc.DrawText(labelFt, new Point(item.X + imgSize / 2.0, item.Y + imgSize + 14));
            }

            // Bottom CTA Pill
            int ctaY = 985;
            dc.DrawRoundedRectangle(badgeBrush, null, new Rect(140, ctaY, W - 280, 60), 30, 30);
            var ctaTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var ctaFt = new FormattedText("COMMENT में 1, 2, 3 या 4 लिखकर VOTE करें! 👇", ci, FlowDirection.LeftToRight, ctaTf, 26, Brushes.White, 1.25);
            ctaFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(ctaFt, new Point(W / 2.0, ctaY + 13));
        }

        rtb.Render(visual);
        var enc = new JpegBitmapEncoder { QualityLevel = 95 };
        enc.Frames.Add(BitmapFrame.Create(rtb));
        using (var fs = File.Create(outputPath)) {
            enc.Save(fs);
        }
    }

    public static void GenerateStory9x16(string assetDir, string outputPath) {
        int W = 1080;
        int H = 1920;
        var rtb = new RenderTargetBitmap(W, H, 96, 96, PixelFormats.Pbgra32);
        var visual = new DrawingVisual();

        using (var dc = visual.RenderOpen()) {
            var gradient = new LinearGradientBrush(
                Color.FromRgb(15, 12, 28),
                Color.FromRgb(36, 26, 68),
                new Point(0, 0),
                new Point(0, 1)
            );
            dc.DrawRectangle(gradient, null, new Rect(0, 0, W, H));

            var fontNirmala = new FontFamily("Nirmala UI");
            var ci = CultureInfo.GetCultureInfo("hi-IN");

            // Header Title
            var titleTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var titleFt = new FormattedText("VOTE FOR NEXT 3D STORY!", ci, FlowDirection.LeftToRight, titleTf, 48, new SolidColorBrush(Color.FromRgb(255, 215, 0)), 1.25);
            titleFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(titleFt, new Point(W / 2.0, 90));

            var subFt = new FormattedText("अगली जादुई कहानी कौन सी देखना चाहते हैं? 🎬✨", ci, FlowDirection.LeftToRight, titleTf, 38, Brushes.White, 1.25);
            subFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(subFt, new Point(W / 2.0, 160));

            var sub2Ft = new FormattedText("Choose your favorite story (1, 2, 3 or 4) 👇", ci, FlowDirection.LeftToRight, titleTf, 28, new SolidColorBrush(Color.FromRgb(210, 210, 235)), 1.25);
            sub2Ft.TextAlignment = TextAlignment.Center;
            dc.DrawText(sub2Ft, new Point(W / 2.0, 218));

            // Grid items: 450x450
            int imgSize = 450;
            int gapX = 40;
            int startX = (W - (imgSize * 2 + gapX)) / 2; // 70
            int startY = 300;
            int rowGap = 90;

            var items = new[] {
                new { File = "poll_option_1_thirsty_crow.jpg", Label = "1. प्यासा कौवा (Clever Crow)", X = startX, Y = startY, Num = "1" },
                new { File = "poll_option_2_tortoise_hare.jpg", Label = "2. कछुआ खरगोश (The Race)", X = startX + imgSize + gapX, Y = startY, Num = "2" },
                new { File = "poll_option_3_greedy_dog.jpg", Label = "3. लालची कुत्ता (Greedy Dog)", X = startX, Y = startY + imgSize + rowGap, Num = "3" },
                new { File = "poll_option_4_friends_bear.jpg", Label = "4. दोस्त और भालू (True Friend)", X = startX + imgSize + gapX, Y = startY + imgSize + rowGap, Num = "4" }
            };

            var goldPen = new Pen(new SolidColorBrush(Color.FromRgb(255, 215, 0)), 4);
            var badgeBrush = new SolidColorBrush(Color.FromRgb(255, 45, 85));
            var badgeTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.ExtraBold, FontStretches.Normal);
            var labelTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);

            foreach (var item in items) {
                string fullPath = Path.Combine(assetDir, item.File);
                var img = LoadBitmap(fullPath);

                dc.DrawRoundedRectangle(null, goldPen, new Rect(item.X - 3, item.Y - 3, imgSize + 6, imgSize + 6), 20, 20);
                dc.DrawImage(img, new Rect(item.X, item.Y, imgSize, imgSize));

                // Badge
                dc.DrawRoundedRectangle(badgeBrush, null, new Rect(item.X + 14, item.Y + 14, 56, 56), 12, 12);
                var badgeFt = new FormattedText(item.Num, ci, FlowDirection.LeftToRight, badgeTf, 36, Brushes.White, 1.25);
                badgeFt.TextAlignment = TextAlignment.Center;
                dc.DrawText(badgeFt, new Point(item.X + 42, item.Y + 20));

                // Label
                var labelFt = new FormattedText(item.Label, ci, FlowDirection.LeftToRight, labelTf, 32, Brushes.White, 1.25);
                labelFt.TextAlignment = TextAlignment.Center;
                dc.DrawText(labelFt, new Point(item.X + imgSize / 2.0, item.Y + imgSize + 18));
            }

            // Bottom CTA Pill
            int ctaY = 1620;
            dc.DrawRoundedRectangle(badgeBrush, null, new Rect(80, ctaY, W - 160, 85), 42, 42);
            var ctaTf = new Typeface(fontNirmala, FontStyles.Normal, FontWeights.Bold, FontStretches.Normal);
            var ctaFt = new FormattedText("COMMENT में 1, 2, 3 या 4 लिखकर VOTE करें! 👇", ci, FlowDirection.LeftToRight, ctaTf, 36, Brushes.White, 1.25);
            ctaFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(ctaFt, new Point(W / 2.0, ctaY + 20));

            var handleFt = new FormattedText("@magicaltaleskid | 3D Hindi Kahaniya", ci, FlowDirection.LeftToRight, titleTf, 26, new SolidColorBrush(Color.FromRgb(180, 180, 210)), 1.25);
            handleFt.TextAlignment = TextAlignment.Center;
            dc.DrawText(handleFt, new Point(W / 2.0, 1740));
        }

        rtb.Render(visual);
        var enc = new JpegBitmapEncoder { QualityLevel = 95 };
        enc.Frames.Add(BitmapFrame.Create(rtb));
        using (var fs = File.Create(outputPath)) {
            enc.Save(fs);
        }
    }
}
'@

Add-Type -TypeDefinition $source -ReferencedAssemblies PresentationCore, PresentationFramework, WindowsBase, System.Xaml

$pollDir = "d:\WorkSpace\YTShorts\backend\output\community_poll_assets\upcoming_story_poll"
$outDir = "d:\WorkSpace\YTShorts\backend\output\community_poll_assets\instagram_poll"

# 1. Generate 1:1 Square Instagram Feed Graphic
$squareOut = Join-Path $outDir "instagram_poll_1080x1080.jpg"
[PollImageGenerator]::GenerateSquare1x1($pollDir, $squareOut)
Write-Host "✅ Generated 1:1 Square Feed Graphic: $squareOut"

# 2. Generate 9:16 Story Graphic
$storyOut = Join-Path $outDir "instagram_story_poll_1080x1920.jpg"
[PollImageGenerator]::GenerateStory9x16($pollDir, $storyOut)
Write-Host "✅ Generated 9:16 Story Graphic: $storyOut"
