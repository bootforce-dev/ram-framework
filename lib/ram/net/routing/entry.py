#!/usr/bin/python

import ram.context
import ram.widgets


with ram.context(__name__):
    from ..utils import ValidateEmptyOrIpV4, ValidateIpV4
    from .utils import ListGatewayDevices
    from .utils import CheckGatewayDevice
    from .utils import ShownGatewayIpAddr


def SwitchGatewayDevice(config, delta):
    devices = ListGatewayDevices(config['ifconfig'])
    current = config['routing']['default']
    options = [""] + sorted(devices)

    config['routing']['default'] = options[
        (options.index(current) + delta) % len(options)
    ]


def SelectGatewayDevice(config):
    devices = ListGatewayDevices(config['ifconfig'])
    current = config['routing']['default']

    options = [
        ("no", "")
    ] + [
        (_ + (" *" if devices[_] else ""), _) for _ in sorted(devices)
    ]

    config['routing']['default'] = ram.widgets.SingleChoice(
        "Select gateway device",
        "",
        options,
        current=current
    )


def EnsureGatewayDevice(config):
    current = config['routing']['default']

    if current:
        _ifconf = config['ifconfig'][current]
        iserror, warning = CheckGatewayDevice(_ifconf)

        if warning:
            if ram.widgets.AskViaButtons(
                "Continue with device to use as default gateway?",
                "Current default route interface:\n\n\t%s\n\n"
                "%s\n\n"
                "Would you like to select another device?\n" % (
                    current, warning
                ),
                "Select device ...", "Keep `%s`" % current
            ):
                SelectGatewayDevice(config)
            elif iserror:
                return False

    return True


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

        if not default:
            default = "no"
            gateway = ""
            warning = ""
        else:
            _ifconf = config['ifconfig'][default]
            gateway = ShownGatewayIpAddr(_ifconf)
            iserror, warning = CheckGatewayDevice(_ifconf)

        return [
            ("%-16s" % ("Default route:"), 0),
            ("%-16s < %6s >" % ("  Interface:", default.center(6)), __SelectGatewayDevice),
            ("%-16s %-15s" % ("  Gateway:", gateway), __EditGatewayAddress),
            ("", 1),
            ("%-32s" % warning, 2),
        ]

    if not EnsureGatewayDevice(config):
        return

    ram.widgets.RunMenu(
        "Select Action - Routing",
        __MkRoutesConfigurationMenu,
        current=__SelectGatewayDevice,
        itemExit=wizard,
        doAction=True
    )


def RemoveGatewayDevice(config, show_confirm=True):
    current = config['routing']['default']

    if current and show_confirm:
        if config['ifconfig'][current]:
            if not ram.widgets.AskViaButtons(
                "Remove device to use as default gateway?",
                "Current default route interface:\n\n\t%s\n\n"
                "Would you like to reset default route interface?" % current
            ):
                return

    config['routing']['default'] = ""


def ModifyGatewayDevice(config, propose, show_confirm=True, edit_address=False):
    current = config['routing']['default']
    _ifconf = config['ifconfig'][propose]

    if show_confirm:
        iserror, warning = CheckGatewayDevice(_ifconf)
        if current == propose and warning:
            if not ram.widgets.AskViaButtons(
                "Continue with device to use as default gateway?",
                "Current default route interface:\n\n\t%s\n\n"
                "%s\n\n"
                "Would you like to keep using device?\n" % (
                    current, warning
                ),
                "Keep", "Reset"
            ):
                propose = ""
            elif iserror:
                return
        elif iserror:
            return ram.widgets.ShowError(propose, warning)
        elif not current:
            if not ram.widgets.AskViaButtons(
                "Change device to use as default gateway?",
                "Current default route interface is not set.\n\n"
                "Proposed default route interface:\n\n\t%s\n\n"
                "%s\n\n"
                "Would you like to continue?" % (
                    propose, warning
                )
            ):
                return
        else:
            if not ram.widgets.AskViaButtons(
                "Change device to use as default gateway?",
                "Current default route interface:\n\n\t%s\n\n"
                "Proposed default route interface:\n\n\t%s\n\n"
                "%s\n\n"
                "Would you like to continue?" % (
                    current, propose, warning
                )
            ):
                return

    config['routing']['default'] = propose

    if propose and edit_address:
        EditGatewayAddress(config, config['routing']['default'])
