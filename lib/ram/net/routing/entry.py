#!/usr/bin/python

import ram.context
import ram.widgets


with ram.context(__name__):
    from net.utils import ValidateEmptyOrIpV4, ValidateIpV4


def SwitchGatewayDevice(config, delta):
    ifaces = config['ifaces'].split()
    current = config['default'] if config['default'] else "no"
    options = ["no"] + ifaces[:]

    ifname = options[(options.index(current) + delta) % len(options)]

    config['default'] = ifname if ifname in ifaces else ""


def SelectGatewayDevice(config, ensure=False):
    ifaces = config['ifaces'].split()
    current = config['default'] if config['default'] else "no"
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

    config['default'] = ifname if ifname in ifaces else ""


def EditGatewayAddress(config):
    ifname = config['default']

    if config[ifname]['usedhcp'] and ram.widgets.AskViaButtons(
        "Use static configuration?",
        "Interface `%s` is configured to obtain gateway address via DHCP protocol.\n\n"
        "Would you like to use static gateway address?\n" % ifname,
        "Continue with DHCP", "Set gateway ..."
    ):
        config[ifname]['ignored'] = "_"
    else:
        gateway, = ram.widgets.RunEntry(
            "Interface gateway configuration",
            "Specify IP address of the gateway for the interface `%s`." % ifname,
            [
                ("Gateway", config[ifname]['gateway'], ValidateEmptyOrIpV4),
            ],
        )
        config[ifname]['gateway'] = gateway
        config[ifname]['ignored'] = ""


def RoutesConfigurationMenu(config, wizard):

    def __SelectGatewayDevice(action):
        if action == ram.widgets.ACTION_SET:
            SelectGatewayDevice(config)
        elif action == ram.widgets.ACTION_INC:
            SwitchGatewayDevice(config, +1)
        elif action == ram.widgets.ACTION_DEC:
            SwitchGatewayDevice(config, -1)

    def __EditGatewayAddress(action):
        if not config['default']:
            SelectGatewayDevice(config)
        if config['default']:
            EditGatewayAddress(config)

    def __MkRoutesConfigurationMenu():
        default = config['default']
        usedhcp = config[default]['usedhcp'] if default else ""
        ignored = config[default]['ignored'] if default else ""
        gateway = config[default]['gateway'] if default else ""

        if usedhcp and (ignored or not gateway):
            gateway = "dhcp"

        default = config['default'] if default else "no"

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
    ifaces = config['ifaces'].split()
    current = config['default']

    if current in ifaces and not ram.widgets.AskViaButtons(
        "Remove device to use as default gateway?",
        "Current default route interface:\n\n\t%s\n\n"
        "Would you like to reset default route interface?" % current
    ):
        return

    config['default'] = ""


def ModifyGatewayDevice(config, ifname):
    ifaces = config['ifaces'].split()
    current = config['default']

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

    config['default'] = ifname
    EditGatewayAddress(config)
