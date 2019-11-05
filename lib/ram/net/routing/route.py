import ram.widgets


# NOT USED

def __FormatLnRoute(ifname, address, netmask, gateway):
    lnroute = "net %-15s mask %-15s" % (address, netmask)
    lnroute += " via %-15s" % (gateway or '')
    lnroute += " dev %s" % ifname
    return lnroute


def EditStaticRoute(config, rttable, idx):
    if 0 <= idx < len(rttable):
        ifname, (address, netmask, gateway), rtitem = rttable[idx]
    else:
        ifname, (address, netmask, gateway), rtitem = None, ('', '', ''), None

    address, netmask, gateway = ram.widgets.AskEntries(
        "Static route configuration",
        "Specify IP address and netmask of destination with gateway address.",
        [
            ("Address:", address),
            ("Netmask:", netmask),
            ("Gateway:", gateway)
        ],
        "Ok"
    )

    invalid_text = \
        ValidateIpV4("Address", address) + \
        ValidateIpV4("Netmask", netmask) + \
        ValidateIpV4("Gateway", gateway, True)

    if invalid_text:
        return ram.widgets.ShowError(
            "Input address isn't valid",
            invalid_text,
            "Ok"
        )

    gwdevs = [gwname for gwname in config if not config.IsLoopback(gwname)]
    ifname = ram.widgets.SingleChoice("Select interface to set route via", gwdevs, ifname)
    rtdata = address, netmask, gateway

    if rtitem:
        rttext, rtfunc = rtitem
        rttable[idx] = ifname, rtdata, (__FormatLnRoute(ifname, *rtdata), rtfunc)
    else:
        def __EditStaticRoute(idx=len(rttable)):
            EditStaticRoute(config, rttable, idx)
        rttable.append((ifname, rtdata, (__FormatLnRoute(ifname, *rtdata), __EditStaticRoute)))


def DelStaticRoutes(config, rttable):
    options = [(rtitem[0], idx, False) for idx, (ifname, rtdata, rtitem) in enumerate(rttable) if rtitem]
    if options:
        options = ram.widgets.AskCheckboxes("Select routes to delete", "", options, "Delete", "Cancel")
        for idx, checked in options:
            if checked:
                rttable[idx] = ifname, rtdata, None


def StaticRoutesMenu(config):
    rttable = []

    def __NewStaticRoute():
        EditStaticRoute(config, rttable, idx=len(rttable))

    def __RmStaticRoutes():
        DelStaticRoutes(config, rttable)

    idx = 0
    for ifname in config:
        _routes = config.GetIfaceStaticRoutes(ifname)
        for i, rtdata in enumerate(_routes):
            def __EditStaticRoute(idx=i):
                EditStaticRoute(config, rttable, idx)
            rttable.append((ifname, rtdata, (__FormatLnRoute(ifname, *rtdata), __EditStaticRoute)))
            idx += 1

    current = None
    while True:
        options = []
        for ifname, rtdata, rtitem in rttable:
            if rtitem:
                options.append(rtitem)

        if options:
            options.append(("", 0))
        options.append(("New route ...", __NewStaticRoute))
        options.append(("Delete routes ...", __RmStaticRoutes))
        options.append(("%20s" % "", 1))
        options.append(("Go back ...", None))

        watched, current = ram.widgets.RunMenu("Select Action - Routes", options, current, oneshot=True)
        if not watched and not current:
            break

    for ifname in config:
        _routes = [rtdata for ifgate, rtdata, rtitem in rttable if rtitem and ifname == ifgate]
        config.SetIfaceStaticRoutes(ifname, _routes)
