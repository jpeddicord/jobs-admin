
# workaround for services that don't provide very friendly descriptions
_alt_descriptions = {
    'apport': _('Crash Reporting'),
    'avahi-daemon': _("Service Discovery"),
    'bluetooth': _("Bluetooth"),
    'cups': _("Printing"),
    'kerneloops': _("Kernel Crash Handler"),
    'networking': _("Manual Networking"),
    'pulseaudio': _("PulseAudio"),
}

# these services should not be managed by us
_protected_jobs = [
    'acpid',
    'acpi-support',
    'alsa-mixer-save',
    'anacron',
    'apparmor',
    'atd',
    'binfmt-support',
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
    'dns-clean',
    'ecryptfs-utils-restore',
    'ecryptfs-utils-save',
    'failsafe-x',
    'fancontrol',
    'gdm',
    'grub-common',
    'halt',
    'hostname',
    'hwclock',
    'hwclock-save',
    'irqbalance',
    'killprocs',
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
    'pppd-dns',
    'procps',
    'rc',
    'rc.local',
    'rcS',
    'rc-sysinit',
    'reboot',
    'rsyslog',
    'sendsigs',
    'single',
    'sudo',
    'udev',
    'udev-finish',
    'udevmonitor',
    'udevtrigger',
    'udftools',
    'umountfs',
    'umountnfs.sh',
    'umountroot',
    'unattended-upgrades',
    'upstart-udev-bridge',
    'urandom',
    'ureadahead',
    'ureadahead-other',
    'x11-common',
]

def is_protected(jobname):
    return jobname in _protected_jobs

def alt_description(jobname):
    if jobname in _alt_descriptions:
        return _alt_descriptions[jobname]
    else:
        return None