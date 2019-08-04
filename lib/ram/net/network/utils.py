#!/usr/bin/python

def ListPeerDnsDevices(config):
    return list(sorted(
        ifname for ifname in config
        if config[ifname]['enabled']
        and config[ifname]['usedhcp']
    ))
