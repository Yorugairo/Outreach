# Register (or remove) the delivery watchdog as a logon task.
#
#   .\scripts\register_watchdog.ps1            # register, start at next logon
#   .\scripts\register_watchdog.ps1 -Remove    # remove the task
#
# The task runs the watchdog module with the repo's Python. Stop a running
# instance any time with:  python -m content.video_engine.watchdog --stop

param([switch]$Remove)

$TaskName = "VideoEngineDeliveryWatchdog"

if ($Remove) {
    schtasks /Delete /TN $TaskName /F
    exit $LASTEXITCODE
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = (Get-Command python).Source
$Action = "`"$Python`" -m content.video_engine.watchdog"

schtasks /Create /TN $TaskName /SC ONLOGON /F `
    /TR "cmd /c cd /d `"$RepoRoot`" && $Action"
exit $LASTEXITCODE
