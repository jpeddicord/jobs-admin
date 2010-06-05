

protected_jobs = [
    'acpid',
    'acpi-support',
    'alsa-mixer-save',
    'anacron',
    'atd',
    'brltty',
    'console-setup',
    'control-alt-delete',
    'cron',
    'cryptdisks',
    'cryptdisks-early',
    'cryptdisks-enable',
    'cryptdisks-udev',
    'dbus',
    'dmesg',
    'ecryptfs-utils-restore',
    'ecryptfs-utils-save',
    'failsafe-x',
    'fancontrol',
    'gdm',
    'hostname',
    'hwclock',
    'hwclock-save',
    'irqbalance',
    'lm-sensors',
    'module-init-tools',
    'mountall',
    'mountall-net',
    'mountall-reboot',
    'mountall-shell',
    'mounted-dev',
    'mounted-tmp',
    'mounted-varrun',
    'ondemand',
    'pcmciautils',
    'plymouth',
    'plymouth-log',
    'plymouth-splash',
    'plymouth-start',
    'plymouth-stop',
    'procps',
    'rc',
    'rcS',
    'rc-sysinit',
    'rsyslog',
    'udev',
    'udev-finish',
    'udevmonitor',
    'udevtrigger',
    'udftools',
    'unattended-upgrades',
    'upstart-udev-bridge',
    'ureadahead',
    'ureadahead-other',
]

def is_protected(jobname):
    return jobname in protected_jobs
