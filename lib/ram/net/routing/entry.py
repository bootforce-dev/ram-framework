#!/usr/bin/python

import ram.context
import ram.widgets


with ram.context(__name__):
    from ..utils import ValidateEmptyOrIpV4, ValidateIpV4
    from ..network.utils import ListEnabledDevices


def SwitchGatewayDevice(config, delta):
    ifaces = ListEnabledDevices(config['ifconfig'])
    current = config['routing']['default'] or "no"
    options = ["no"] + ifaces[:]

    ifname = options[(options.index(current) + delta) % len(options)]

    config['routing']['default'] = ifname if ifname in ifaces else ""


def SelectGatewayDevice(config, ensure=False):
    ifaces = ListEnabledDevices(config['ifconfig'])
    current = config['routing']['default'] or "no"
    options = ["no"] + ifaces[:]

    if current not in options:
        if not ram.widgets.AskViaButtons(
            "Incorrect gateway device",
            "Current interface for default route `%s`\n"
            "is not available or enabled at the moment.\n\n"
            "What would you like to do with gateway device?\n" % current,
            "Select device ...", "Keep `%s`" % current
        ):
            return
    elif ensure:
        return

    ifname = ram.widgets.SingleChoice("Select gateway device", "", options, current=current)
    if ifname == current:
        return

    config['routing']['default'] = ifname if ifname in ifaces else ""


def EditGatewayAddress(config, ifname):
    ifconf = config['ifconfig'][ifname]

    if ifconf['usedhcp'] and ram.widgets.AskViaButtons(
        "Use static configuration?",
        "Interface `%s` is configured to obtain gateway address via DHCP protocol.\n\n"
        "Would you like to use static gateway address?\n" % ifname,
        "Continue with DHCP", "Set gateway ..."
    ):
        ifconf['ignored'] = "_"
    else:
        gateway, = ram.widgets.RunEntry(
            "Interface gateway configuration",
            "Specify IP address of the gateway for the interface `%s`." % ifname,
            [
                ("Gateway", ifconf['gateway'], ValidateEmptyOrIpV4),
            ],
        )
        ifconf['gateway'] = gateway
        ifconf['ignored'] = ""


def RoutesConfigurationMenu(config, wizard):

    def __SelectGatewayDevice(action):
        if action == ram.widgets.ACTION_SET:
            SelectGatewayDevice(config)
        elif action == ram.widgets.ACTION_INC:
            SwitchGatewayDevice(config, +1)
        elif action == ram.widgets.ACTION_DEC:
            SwitchGatewayDevice(config, -1)

    def __EditGatewayAddress(action):
        if not config['routing']['default']:
            SelectGatewayDevice(config)
        if config['routing']['default']:
            EditGatewayAddress(config, config['routing']['default'])

    def __MkRoutesConfigurationMenu():
        default = config['routing']['default']

        usedhcp = config['ifconfig'][default]['usedhcp'] if default else ""
        ignored = config['ifconfig'][default]['ignored'] if default else ""
        gateway = config['ifconfig'][default]['gateway'] if default else ""

        if usedhcp and (ignored or not gateway):
            gateway = "dhcp"

        default = default if default else "no"

        return [
            ("%-16s" % ("Default route:"), 0),
            ("%-16s < %6s >" % ("  Interface:", default.center(6)), __SelectGatewayDevice),
            ("%-16s %-15s" % ("  Gateway:", gateway), __EditGatewayAddress),
        ]

    SelectGatewayDevice(config, ensure=True)

    ram.widgets.RunMenu(
        "Select Action - Routing",
        __MkRoutesConfigurationMenu,
        current=__SelectGatewayDevice,
        itemExit=wizard,
        doAction=True
    )


def RemoveGatewayDevice(config):
    ifaces = ListEnabledDevices(config['ifconfig'])
    current = config['routing']['default']

    if current in ifaces and not ram.widgets.AskViaButtons(
        "Remove device to use as default gateway?",
        "Current default route interface:\n\n\t%s\n\n"
        "Would you like to reset default route interface?" % current
    ):
        return

    config['routing']['default'] = ""


def ModifyGatewayDevice(config, ifname):
    ifaces = ListEnabledDevices(config['ifconfig'])
    current = config['routing']['default']

    if not ifname in ifaces:
        return ram.widgets.ShowError(
            ifname,
            "No suitable device found on the machine.",
        )

    if current == ifname:
        return

    if not current and not ram.widgets.AskViaButtons(
        "Change device to use as default gateway?",
        "Current default route interface is not set.\n\n"
        "Would you like to set default route interface:\n\n\t%s\n\n?" % ifname
    ):
        return

    if current in ifaces and not ram.widgets.AskViaButtons(
        "Change device to use as default gateway?",
        "Current default route interface:\n\n\t%s\n\n"
        "Would you like to set default route interface:\n\n\t%s\n\n?" % (
            current, ifname
        )
    ):
        return

    config['routing']['default'] = ifname
    EditGatewayAddress(config, config['routing']['default'])
