#!/usr/bin/python

def ListGatewayDevices(config):
    return list(sorted(
        ifname for ifname in config
        if not config[ifname]['defconf']
        and config[ifname]['hw_addr']
        and config[ifname]['enabled']
    ))

def CheckGatewayDevice(_ifconf):
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
