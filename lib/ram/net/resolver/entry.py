#!/usr/bin/python

import ram.context
import ram.widgets


with ram.context(__name__):
    from ..utils import ValidateDomainList, ValidateEmptyOrIpV4
    from ..network.utils import ListPeerDnsDevices

from ram.widgets import *


def SwitchPeerDnsDevice(config, delta):
    devices = ListPeerDnsDevices(config['ifconfig'])
    current = config['resolver']['peerdns'] or "no"
    options = ["no"] + devices[:]

    propose = options[(options.index(current) + delta) % len(options)]

    config['resolver']['peerdns'] = propose if propose in devices else ""


def SelectPeerDnsDevice(config, ensure=False):
    devices = ListPeerDnsDevices(config['ifconfig'])
    current = config['resolver']['peerdns'] or "no"
    options = ["no"] + devices[:]

    if current not in options:
        if not ram.widgets.AskViaButtons(
            "Incorrect DNS over DHCP",
            "WARNING: Current DHCP interface for obtaining DNS `%s`\n"
            "is not available or configured at the moment.\n\n"
            "What would you like to do with DNS over DHCP?\n" % current,
            "Select device ...", "Keep `%s`" % current
        ):
            return
    elif ensure:
        return

    propose = ram.widgets.SingleChoice("Obtain DNS addresses over DHCP?", "", options, current=current)
    if propose == current:
        return

    config['resolver']['peerdns'] = propose if propose in devices else ""


def EditIfaceDnsServers(config, edit_servers=True):
    resolv = config['resolver']
    current = resolv['peerdns']

    if current and not ram.widgets.AskViaButtons(
        "Use static configuration?",
        "Current interface to obtain DNS configuration via DHCP:\n\n\t%s\n\n"
        "Would you like to use static configuration?\n" % current
    ):
        return

    resolv['peerdns'] = ""

    if not edit_servers:
        return

    domains, pri_dns, sec_dns = ram.widgets.RunEntry(
        "Interface DNS configuration",
        "Specify domain search list, primary and secondary DNS addresses.",
        [
            ("Search list", resolv['domains'], ValidateDomainList),
            ("Primary", resolv['pri_dns'], ValidateEmptyOrIpV4),
            ("Secondary", resolv['sec_dns'], ValidateEmptyOrIpV4),
        ]
    )

    if not pri_dns and sec_dns:
        pri_dns, sec_dns = sec_dns, pri_dns

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
        EditIfaceDnsServers(config)

    def __EditSecondaryDnsServer(action):
        EditIfaceDnsServers(config)

    def __EditDomainSearchList(action):
        EditIfaceDnsServers(config)

    if not resolv['pri_dns'] and resolv['sec_dns']:
        resolv['pri_dns'], resolv['sec_dns'] = resolv['sec_dns'], resolv['pri_dns']

    def __MkDnsConfigurationMenu():
        domains = "dhcp" if resolv['peerdns'] else resolv['domains']
        pri_dns = "dhcp" if resolv['peerdns'] else resolv['pri_dns']
        sec_dns = "dhcp" if resolv['peerdns'] else resolv['sec_dns']
        peerdns = resolv['peerdns'] if resolv['peerdns'] else "no"

        return [
            ("%-16s < %6s >" % ("Use DHCP:", peerdns.center(6)), __SelectPeerDnsDevice),
            ("", 1),
            ("%-16s %s" % ("Search list:", domains), __EditDomainSearchList),
            ("%-16s %-15s" % ("Primary DNS:", pri_dns), __EditPrimaryDnsServer),
            ("%-16s %-15s" % ("Secondary DNS:", sec_dns), __EditSecondaryDnsServer),
        ]

    SelectPeerDnsDevice(config, ensure=True)

    ram.widgets.RunMenu(
        "Select Action - Resolver",
        __MkDnsConfigurationMenu,
        itemExit=wizard,
        doAction=True
    )


def ModifyPeerDnsDevice(config, propose, show_confirm=True):
    current = config['resolver']['peerdns']
    _ifconf = config['ifconfig'][propose]

    if not current == propose and show_confirm:
        if not _ifconf:
            return ram.widgets.ShowError(
                propose,
                "Device is not found!",
            )

        if not _ifconf['hw_addr']:
            warning = "WARNING: Device is not found!\n\n"
        elif not _ifconf['enabled']:
            warning = "WARNING: Device is not enabled!\n\n"
        elif not _ifconf['usedhcp']:
            warning = "WARNING: Device is not using DHCP!\n\n"
        else:
            warning = ""

        if not current or not config['ifconfig'][current]:
            if not ram.widgets.AskViaButtons(
                "Use dynamic configuration?",
                "Current DNS configuration is static.\n\n"
                "Proposed interface to obtain DNS configuration via DHCP:\n\n\t%s\n\n"
                "%s"
                "Would you like to continue?" % (
                    propose, warning
                )
            ):
                return
        else:
            if not ram.widgets.AskViaButtons(
                "Change device to obtain DNS addresses?",
                "Current interface to obtain DNS configuration via DHCP:\n\n\t%s\n\n"
                "Proposed interface to obtain DNS configuration via DHCP:\n\n\t%s\n\n"
                "%s"
                "Would you like to continue?" % (
                    current, propose, warning
                )
            ):
                return

    config['resolver']['peerdns'] = propose
