param()

$ErrorActionPreference = "Continue"
$base = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$repoItem = Get-Item -LiteralPath $base
for ($i = 0; $i -lt 7; $i++) { $repoItem = $repoItem.Parent }
$repo = $repoItem.FullName
$build = Join-Path $base "build-review"
$project = Join-Path $repo "content/video_engine/projects/systems-and-blowups/normal-for-which-bridge"
$logs = Join-Path $base "logs"
New-Item -ItemType Directory -Path $logs -Force | Out-Null

$runs = New-Object 'System.Collections.Generic.List[string]'

function Invoke-Logged {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    $log = Join-Path $logs "$Name.log"
    $meta = Join-Path $logs "$Name.command.txt"
    $display = "python " + ($Arguments -join " ")
    @("cwd=$repo", "command=$display") | Set-Content -LiteralPath $meta -Encoding utf8
    Push-Location -LiteralPath $repo
    try {
        & python @Arguments 1> $log 2>&1
        $exit = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    Add-Content -LiteralPath $meta -Value "exit_code=$exit" -Encoding utf8
    $runs.Add("$Name`t$exit`tlogs/$Name.log`tlogs/$Name.command.txt")
    return $exit
}

$null = Invoke-Logged -Name "01-probe-gate" -Arguments @(
    "content/video_engine/scripts/probe.py", $build, "--gate", "--timeline", "bridge-short.timeline.json"
)
$null = Invoke-Logged -Name "02-motion-gate" -Arguments @(
    "content/video_engine/scripts/gate_motion_density.py", $build, "--timeline", "bridge-short.timeline.json"
)
$null = Invoke-Logged -Name "03-floor-gate" -Arguments @(
    "content/video_engine/scripts/gate_one_shot_floor.py", $build, "--project", $project,
    "--timeline", "bridge-short.timeline.json"
)
$null = Invoke-Logged -Name "04-self-watch" -Arguments @(
    "content/video_engine/scripts/self_watch.py", $build, "--project", $project,
    "--script", "SCRIPT-SHORT", "--short", "--step", "2", "--tile", "360",
    "--timeline", "bridge-short.timeline.json"
)

"name`texit_code`tstdout_stderr_log`texact_command" | Set-Content -LiteralPath (Join-Path $base "RUN-SUMMARY.tsv") -Encoding utf8
$runs | Add-Content -LiteralPath (Join-Path $base "RUN-SUMMARY.tsv") -Encoding utf8

function Add-HashRow {
    param([string]$Label, [string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $hashRows.Add("$Label`tMISSING`t0`t-")
        return
    }
    $item = Get-Item -LiteralPath $Path
    $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    $rel = $item.FullName.Substring($repo.Length + 1).Replace("\", "/")
    $hashRows.Add("$Label`t$rel`t$($item.Length)`t$sha")
}

$hashRows = New-Object 'System.Collections.Generic.List[string]'
"label`trelative_path`tbytes`tsha256" | Set-Content -LiteralPath (Join-Path $base "HASHES.tsv") -Encoding utf8
Add-HashRow "source-script" (Join-Path $project "build_short.py")
Add-HashRow "source-narration" (Join-Path $project "SCRIPT-SHORT-VO.txt")
Add-HashRow "take-chirp-mp3" (Join-Path $project "vo-short/audio/scene_1.mp3")
Add-HashRow "take-chirp-words" (Join-Path $project "vo-short/audio/scene_1.words.json")
Add-HashRow "take-kokoro-mp3" (Join-Path $project "vo-short/audio/scene_kokoro.mp3")
Add-HashRow "take-kokoro-words" (Join-Path $project "vo-short/audio/scene_kokoro.words.json")
Add-HashRow "source-build-engine" (Join-Path $project "build-review/scene-evidence-engine.mjs")
Add-HashRow "baseline-build-engine" (Join-Path $build "scene-evidence-engine.mjs")
Add-HashRow "baseline-compiled-timeline" (Join-Path $build "bridge-short.timeline.json")
Add-HashRow "baseline-word-timeline" (Join-Path $build "timeline.json")
Add-HashRow "baseline-player" (Join-Path $build "player.html")
Add-HashRow "baseline-assets" (Join-Path $build "assets.json")
Add-HashRow "baseline-audio" (Join-Path $build "audio/episode.mp3")
$hashRows | Add-Content -LiteralPath (Join-Path $base "HASHES.tsv") -Encoding utf8

function Rel([string]$Path) {
    return (Get-Item -LiteralPath $Path).FullName.Substring($repo.Length + 1).Replace("\", "/")
}
function GateResult([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return "MISSING" }
    $text = Get-Content -Raw -LiteralPath $Path
    $m = [regex]::Match($text, "RESULT:\s*([^\r\n]+)")
    if ($m.Success) { return $m.Groups[1].Value.Trim() }
    $m = [regex]::Match($text, "VERDICT:\s*([^\r\n]+)")
    if ($m.Success) { return $m.Groups[1].Value.Trim() }
    return "NO RESULT LINE"
}

$compiled = Get-Content -Raw -LiteralPath (Join-Path $build "bridge-short.timeline.json") | ConvertFrom-Json
$wordTl = Get-Content -Raw -LiteralPath (Join-Path $build "timeline.json") | ConvertFrom-Json
$sceneList = @($compiled.scenes)
$dockCount = (@($sceneList | ForEach-Object { @($_.docks) })).Count
$speciesCount = (@($sceneList | ForEach-Object { @($_.species) })).Count
$compiledCount = @($compiled.captions).Count
$sentenceCount = @($wordTl.sentences).Count
$motionReport = Join-Path $build "GATES-MOTION.md"
$motionLog = Join-Path $logs "02-motion-gate.log"
$floorLog = Join-Path $logs "03-floor-gate.log"
$selfWatchLog = Join-Path $logs "04-self-watch.log"
$motionFresh = GateResult $motionLog
$floorFresh = GateResult $floorLog
$selfWatchFresh = GateResult $selfWatchLog
$comparison = @(
    "# Baseline comparison",
    "",
    "Chosen gate target: build-review copied to baseline/build-review/.",
    "Older comparison: review-v1 (read-only; never rebuilt).",
    "",
    "| measure | review-v1 | build-review source | baseline after gates |",
    "|---|---:|---:|---:|",
    "| compiled timeline SHA-256 | a0d4c505a26ce49a12220af9e4ccdc66614cb9ea669706b3ad2f26567ae802d9 | 19a9ec48ba13e862a0aaf3781ec7a6e9024abc4cf34aa3c10ed8e45073d8db99 | $((Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $build "bridge-short.timeline.json")).Hash.ToLowerInvariant()) |",
    "| runtime (s) | 56.904014 | 56.904014 | $($wordTl.runtime_s) |",
    "| compiled scenes | 6 | 6 | $($sceneList.Count) |",
    "| caption pages | 39 | 39 | $compiledCount |",
    "| docks | 0 | 0 | $dockCount |",
    "| targeted species | 8 | 8 | $speciesCount |",
    "| narration sentences | 19 | 19 | $sentenceCount |",
    "| motion result | 0 FAIL / 1 WARN / 18 PASS / 1 JUDGE / 5 INFO | 0 FAIL / 1 WARN / 18 PASS / 1 JUDGE / 5 INFO | $motionFresh |",
    "| floor result | not measured under E96 (predates) | current floor expected to judge | $floorFresh |",
    "| self-watch result | TODO after historical report | TODO after historical report | $selfWatchFresh |",
    "",
    "The baseline's complete gate output is in build-review/GATES-MOTION.md and",
    "the complete floor/self-watch stdout and stderr are in logs/ with exact",
    "commands and exit codes in RUN-SUMMARY.tsv."
)
$comparison | Set-Content -LiteralPath (Join-Path $base "BASELINE-COMPARISON.md") -Encoding utf8

Write-Output "baseline=$base"
Get-Content -LiteralPath (Join-Path $base "RUN-SUMMARY.tsv")
