import ram.context
import ram.widgets


with ram.context(__name__):
    from ..utils import ValidateDomainList, ValidateEmptyOrIpV4
    from .utils import ListPeerDnsDevices
    from .utils import ProbePeerDnsDevice
    from .utils import CheckPeerDnsDevice

from ram.widgets import *


def SwitchPeerDnsDevice(config, delta):
    devices = ListPeerDnsDevices(config['ifconfig'])
    ifname_ = config['resolver']['peerdns']
    options = [""] + sorted(devices)

    config['resolver']['peerdns'] = options[
        (options.index(ifname_) + delta) % len(options)
    ]


def SelectPeerDnsDevice(config):
    devices = ListPeerDnsDevices(config['ifconfig'])
    ifname_ = config['resolver']['peerdns']

    options = [
        ("no", "")
    ] + [
        (_ + (" *" if devices[_] else ""), _) for _ in sorted(devices)
    ]

    config['resolver']['peerdns'] = ram.widgets.SingleChoice(
        "Obtain DNS addresses over DHCP?",
        "",
        options,
        current=ifname_
    )


def EnsurePeerDnsDevice(config):
    ifname_ = config['resolver']['peerdns']

    if ifname_:
        iserror_, warning_ = CheckPeerDnsDevice(config['ifconfig'], ifname_)

        if not warning_:
            pass
        elif ram.widgets.AskViaButtons(
            "Continue with device to obtain DNS addresses?",
            "Current interface to obtain DNS configuration:\n\n"
            "  %s\n\n"
            "  %s\n\n"
            "Would you like to select another device?\n" % (
                ifname_, warning_
            ),
            "Select device ...", "Keep `%s`" % ifname_
        ):
            SelectPeerDnsDevice(config)
        elif iserror_:
            return False

    return True


def EditIfaceDnsServers(config):
    resolv = config['resolver']

    domains, pri_dns, sec_dns = ram.widgets.RunEntry(
        "Interface DNS configuration",
        "Specify domain search list, primary and secondary DNS addresses.",
        [
            ("Search list", resolv['domains'], ValidateDomainList),
            ("Primary", resolv['pri_dns'], ValidateEmptyOrIpV4),
            ("Secondary", resolv['sec_dns'], ValidateEmptyOrIpV4),
        ]
    )

    resolv['domains'] = domains
    resolv['pri_dns'] = pri_dns
    resolv['sec_dns'] = sec_dns


def RunDnsConfigurationMenu(config, wizard):
    resolv = config['resolver']

    def __SelectPeerDnsDevice(action):
        if action == ram.widgets.ACTION_SET:
            SelectPeerDnsDevice(config)
        elif action == ram.widgets.ACTION_INC:
            SwitchPeerDnsDevice(config, +1)
        elif action == ram.widgets.ACTION_DEC:
            SwitchPeerDnsDevice(config, -1)

    def __EditPrimaryDnsServer(action):
        RemovePeerDnsDevice(config, edit_address=True)

    def __EditSecondaryDnsServer(action):
        RemovePeerDnsDevice(config, edit_address=True)

    def __EditDomainSearchList(action):
        RemovePeerDnsDevice(config, edit_address=True)

    def __MkDnsConfigurationMenu():
        peerdns = resolv['peerdns']

        if not peerdns:
            domains = resolv['domains']
            pri_dns = resolv['pri_dns']
            sec_dns = resolv['sec_dns']

            peerdns = "no"
            warning = ""
        else:
            domains = "dhcp"
            pri_dns = "dhcp"
            sec_dns = "dhcp"

            iserror, warning = CheckPeerDnsDevice(config['ifconfig'], peerdns)

        return [
            ("%-16s < %6s >" % ("Use DHCP:", peerdns.center(6)), __SelectPeerDnsDevice),
            ("", 1),
            ("%-16s %s" % ("Search list:", domains), __EditDomainSearchList),
            ("%-16s %-15s" % ("Primary DNS:", pri_dns), __EditPrimaryDnsServer),
            ("%-16s %-15s" % ("Secondary DNS:", sec_dns), __EditSecondaryDnsServer),
            ("", 2),
            ("%-32s" % warning, 3),
        ]

    if not EnsurePeerDnsDevice(config):
        return

    ram.widgets.RunMenu(
        "Select Action - Resolver",
        __MkDnsConfigurationMenu,
        itemExit=wizard,
        doAction=True
    )


def RemovePeerDnsDevice(config, show_confirm=True, edit_address=False):
    ifname_ = config['resolver']['peerdns']

    if show_confirm:
        if ifname_:
            iserror_, warning_ = CheckPeerDnsDevice(config['ifconfig'], ifname_)

            if not ram.widgets.AskViaButtons(
                "Use static configuration?",
                "Current interface to obtain DNS configuration:\n\n"
                "  %s\n\n"
                "  %s\n\n"
                "Proposed to use static DNS confiruation.\n\n"
                "Would you like to continue?\n" % (
                    ifname_, warning_
                )
            ):
                return

    config['resolver']['peerdns'] = ""

    if edit_address:
        EditIfaceDnsServers(config)


def ModifyPeerDnsDevice(config, ifname, show_confirm=True):
    ifname_ = config['resolver']['peerdns']
    ifconf = config['ifconfig'][ifname]

    if show_confirm:
        iserror, warning = ProbePeerDnsDevice(ifconf)

        if ifname_ == ifname:
            if not warning:
                pass
            elif not ram.widgets.AskViaButtons(
                "Continue with device to obtain DNS addresses?",
                "Current interface to obtain DNS configuration:\n\n"
                "  %s\n\n"
                "  %s\n\n"
                "Would you like to keep using device?\n" % (
                    ifname, warning
                ),
                "Keep", "Reset"
            ):
                ifname = ""
            elif iserror:
                return
        elif iserror:
            return ram.widgets.ShowError(ifname, warning)
        elif not ifname_:
            if not ram.widgets.AskViaButtons(
                "Use dynamic configuration?",
                "Current DNS configuration is static.\n\n"
                "Proposed interface to obtain DNS configuration:\n\n"
                "  %s\n\n"
                "  %s\n\n"
                "Would you like to continue?" % (
                    ifname, warning
                )
            ):
                return
        else:
            iserror_, warning_ = ProbePeerDnsDevice(config['ifconfig'], ifname_)

            if not ram.widgets.AskViaButtons(
                "Change device to obtain DNS addresses?",
                "Current interface to obtain DNS configuration:\n\n"
                "  %s\n\n"
                "  %s\n\n"
                "Proposed interface to obtain DNS configuration:\n\n"
                "  %s\n\n"
                "  %s\n\n"
                "Would you like to continue?" % (
                    ifname_, warning_, ifname, warning
                )
            ):
                return

    config['resolver']['peerdns'] = ifname


def CompatPeerDnsConfig(config):
    # multiple non-lo peer dns devices
    # non-lo devices with static dnses

    peerdns = []
    confdns = []

    for ifname in config['ifconfig']:
        ifconf = config['ifconfig'][ifname]

        if ifconf['domains'] or ifconf['pri_dns'] or ifconf['sec_dns']:
            confdns += [ifname]

        if ifconf['peerdns']:
            peerdns += [ifname]

    if not confdns and not peerdns[1:]:
        return True
    elif not ram.widgets.AskViaButtons(
        "Ambiguous DNS configuration",
        "Current configuration of DNS is ambiguous\n\n"
        "Would you like to reset DNS configuration?",
        "Select device ...", "Go back",
    ):
        return False

    return True
