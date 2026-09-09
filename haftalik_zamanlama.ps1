# LeadRadar — haftalik otomatik calistirma kurulumu
# Orijinal n8n akisindaki "her pazartesi 09:00" cron tetikleyicisinin Windows karsiligi.
# Bu betigi BIR KEZ calistirin; Gorev Zamanlayici'da gorev olusturur.

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = "LeadRadar Lead Avcisi"
$command = "py `"$projectDir\run.py`""

schtasks /Create /F /SC WEEKLY /D MON /ST 09:00 /TN $taskName /TR "cmd /c cd /d `"$projectDir`" && $command"

Write-Host ""
Write-Host "Gorev olusturuldu: '$taskName' (her pazartesi 09:00)."
Write-Host "Kaldirmak icin: schtasks /Delete /TN `"$taskName`" /F"
