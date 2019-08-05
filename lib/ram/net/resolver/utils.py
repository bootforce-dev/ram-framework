#!/usr/bin/python

def IterPeerDnsDevices(config):
    for ifname in config:
        iserror, warning = CheckPeerDnsDevice(config[ifname])
        if iserror:
            continue
        else:
            yield (ifname, warning)

def ListPeerDnsDevices(config):
    return dict(IterPeerDnsDevices(config))

def CheckPeerDnsDevice(_ifconf):
    if not _ifconf or _ifconf['defconf']:
        return True, "ERROR: Device is not configured!"

    if not _ifconf['hw_addr']:
        return False, "WARNING: Device is not found!"
    elif not _ifconf['enabled']:
        return False, "WARNING: Device is not enabled!"
    elif not _ifconf['usedhcp']:
        return False, "WARNING: Device not using DHCP!"
    else:
        return False, ""
