def IterGatewayDevices(config):
    for ifname in config:
        iserror, warning = ProbeGatewayDevice(config[ifname])
        if iserror:
            continue
        else:
            yield (ifname, warning)

def ListGatewayDevices(config):
    return dict(IterGatewayDevices(config))

def ProbeGatewayDevice(_ifconf):
    if not _ifconf or _ifconf['defconf']:
        return True, "ERROR: Device is not configured!"

    if not _ifconf['hw_addr']:
        return False, "WARNING: Device is not found!"
    elif not _ifconf['enabled']:
        return False, "WARNING: Device is not enabled!"
    else:
        return False, ""

def ShownGatewayIpAddr(_ifconf):
    if _ifconf['usedhcp'] and (_ifconf['ignored'] or not _ifconf['gateway']):
        return "dhcp"
    else:
        return _ifconf['gateway']
