#!/usr/bin/python

def ListPeerDnsDevices(config):
    return list(sorted(
        ifname for ifname in config
        if not config[ifname]['defconf']
        and config[ifname]['hw_addr']
        and config[ifname]['enabled']
        and config[ifname]['usedhcp']
    ))

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
