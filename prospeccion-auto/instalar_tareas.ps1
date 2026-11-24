# Registers the weekly prospecting tasks in Windows Task Scheduler.
# Run once from PowerShell:  .\instalar_tareas.ps1
# Requires the venv at C:\Users\kineb\.venvs\mkf-prospeccion (see ESTADO.md).
$py = 'C:\Users\kineb\.venvs\mkf-prospeccion\Scripts\python.exe'
$d  = $PSScriptRoot

$tasks = @(
    @{ Name = 'MKF_Prospeccion_Centros';   Script = 'prospecting_semanal.py'; Day = 'Monday'  },
    @{ Name = 'MKF_Alianzas_Estrategicas'; Script = 'alianzas_semanal.py';    Day = 'Tuesday' }
)

foreach ($t in $tasks) {
    $action   = New-ScheduledTaskAction -Execute $py -Argument "`"$d\$($t.Script)`"" -WorkingDirectory $d
    $trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $t.Day -At 8:00
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    Register-ScheduledTask -TaskName $t.Name -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
}

Get-ScheduledTask -TaskName 'MKF_*' | ForEach-Object {
    "{0} | {1} | next: {2}" -f $_.TaskName, $_.State, (Get-ScheduledTaskInfo $_).NextRunTime
}
