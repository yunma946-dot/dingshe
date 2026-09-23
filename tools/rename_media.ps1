$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$photosRoot = Join-Path $projectRoot "photos"
$imageExtensions = @(".jpg", ".jpeg", ".png", ".webp", ".avif")

if (-not (Test-Path -LiteralPath $photosRoot -PathType Container)) {
    throw "The photos folder was not found: $photosRoot"
}

$folders = @(Get-ChildItem -LiteralPath $photosRoot -Directory | Sort-Object Name)
$plan = @()
$skipped = @()
$ready = 0

foreach ($folder in $folders) {
    $images = @(
        Get-ChildItem -LiteralPath $folder.FullName -File |
        Where-Object {
            $imageExtensions -contains $_.Extension.ToLowerInvariant() -and
            $_.Name -notmatch '^\d{2}-(480|800)\.webp$'
        } |
        Sort-Object Name
    )
    $videos = @(
        Get-ChildItem -LiteralPath $folder.FullName -File |
        Where-Object { $_.Extension.ToLowerInvariant() -eq ".mp4" } |
        Sort-Object Name
    )

    if ($images.Count -eq 0 -and $videos.Count -eq 0) {
        continue
    }
    if ($images.Count -gt 3) {
        $skipped += "$($folder.Name): more than 3 images"
        continue
    }
    if ($videos.Count -gt 1) {
        $skipped += "$($folder.Name): more than 1 MP4 video"
        continue
    }

    $folderPlan = @()
    for ($index = 0; $index -lt $images.Count; $index++) {
        $newName = ("{0:D2}{1}" -f ($index + 1), $images[$index].Extension.ToLowerInvariant())
        if ($images[$index].Name -cne $newName) {
            $folderPlan += [pscustomobject]@{
                Folder = $folder.FullName
                OldName = $images[$index].Name
                NewName = $newName
                Source = $images[$index].FullName
            }
        }
    }
    if ($videos.Count -eq 1 -and $videos[0].Name -cne "profile.mp4") {
        $folderPlan += [pscustomobject]@{
            Folder = $folder.FullName
            OldName = $videos[0].Name
            NewName = "profile.mp4"
            Source = $videos[0].FullName
        }
    }

    if ($folderPlan.Count -eq 0) {
        $ready++
    } else {
        $plan += $folderPlan
    }
}

if ($plan.Count -gt 0) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $logPath = Join-Path $projectRoot "media-rename-log-$timestamp.csv"
    $plan | Select-Object Folder, OldName, NewName | Export-Csv -LiteralPath $logPath -NoTypeInformation -Encoding UTF8

    foreach ($item in $plan) {
        $extension = [System.IO.Path]::GetExtension($item.OldName)
        $temporaryName = ".dingshe-rename-$([guid]::NewGuid().ToString('N'))$extension"
        Rename-Item -LiteralPath $item.Source -NewName $temporaryName
        $item | Add-Member -NotePropertyName TemporaryPath -NotePropertyValue (Join-Path $item.Folder $temporaryName)
    }

    foreach ($item in $plan) {
        $target = Join-Path $item.Folder $item.NewName
        if (Test-Path -LiteralPath $target) {
            throw "Target already exists: $target"
        }
        Rename-Item -LiteralPath $item.TemporaryPath -NewName $item.NewName
    }

    Write-Host "Renamed $($plan.Count) files."
    Write-Host "Rename log: $logPath"
} else {
    Write-Host "No files needed renaming."
}

if ($ready -gt 0) {
    Write-Host "$ready folders were already correctly named."
}
if ($skipped.Count -gt 0) {
    Write-Host ""
    Write-Host "Skipped folders:" -ForegroundColor Yellow
    foreach ($message in $skipped) {
        Write-Host "- $message" -ForegroundColor Yellow
    }
}
