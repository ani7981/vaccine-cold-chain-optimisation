$ErrorActionPreference = 'SilentlyContinue'
Write-Output "VaxKavach WSL Keepalive Daemon Started."
while ($true) {
    try {
        $status = wsl -d FedoraLinux-42 -u root -- podman ps --filter "name=vaxkavach_db" --format "{{.Status}}" 2>$null
        if ($status -notlike "*Up*") {
            wsl -d FedoraLinux-42 -u root -- podman --cgroup-manager=cgroupfs start vaxkavach_db 2>$null
        }
    } catch {}
    Start-Sleep -Seconds 5
}
