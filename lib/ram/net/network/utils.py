#!/usr/bin/python

def ListPeerDnsDevices(config):
    return list(sorted(
        ifname for ifname in config
        if not config[ifname]['defconf']
        and config[ifname]['hw_addr']
        and config[ifname]['enabled']
        and config[ifname]['usedhcp']
    ))

def ListGatewayDevices(config):
    return list(sorted(
        ifname for ifname in config
        if not config[ifname]['defconf']
        and config[ifname]['hw_addr']
        and config[ifname]['enabled']
    ))

def ListPresentDevices(config):
    return list(sorted(
        ifname for ifname in config
        if not config[ifname]['defconf']
    ))
