$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$files = Get-ChildItem -LiteralPath (Join-Path $root 'ref') -File |
    Where-Object { $_.Name -like 'IMG_20211023*.jpg' -or $_.Name -eq 'pra.jpg' } |
    Sort-Object Name
$output = Join-Path $PSScriptRoot 'reference-contact-sheets'
New-Item -ItemType Directory -Force -Path $output | Out-Null

$cols = 4
$rows = 4
$cellW = 360
$cellH = 250
$labelH = 28
$font = [System.Drawing.Font]::new('Arial', 12, [System.Drawing.FontStyle]::Bold)
$labelBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
$background = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(26, 26, 26))

for ($page = 0; $page * ($cols * $rows) -lt $files.Count; $page++) {
    $bitmap = [System.Drawing.Bitmap]::new($cols * $cellW, $rows * ($cellH + $labelH))
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.FillRectangle($background, 0, 0, $bitmap.Width, $bitmap.Height)
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    for ($slot = 0; $slot -lt $cols * $rows; $slot++) {
        $index = $page * ($cols * $rows) + $slot
        if ($index -ge $files.Count) { break }
        $col = $slot % $cols
        $row = [math]::Floor($slot / $cols)
        $image = [System.Drawing.Image]::FromFile($files[$index].FullName)
        try {
            $scale = [math]::Min($cellW / $image.Width, $cellH / $image.Height)
            $width = [int]($image.Width * $scale)
            $height = [int]($image.Height * $scale)
            $x = $col * $cellW + [int](($cellW - $width) / 2)
            $y = $row * ($cellH + $labelH) + [int](($cellH - $height) / 2)
            $graphics.DrawImage($image, $x, $y, $width, $height)
            $graphics.DrawString($files[$index].Name, $font, $labelBrush, $col * $cellW + 4, $row * ($cellH + $labelH) + $cellH + 4)
        } finally {
            $image.Dispose()
        }
    }
    $path = Join-Path $output ('contact-{0:D2}.jpg' -f ($page + 1))
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Jpeg)
    $graphics.Dispose()
    $bitmap.Dispose()
}

$font.Dispose()
$labelBrush.Dispose()
$background.Dispose()
Write-Output "Created $([math]::Ceiling($files.Count / 16.0)) contact sheets from $($files.Count) references."
