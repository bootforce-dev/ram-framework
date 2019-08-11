#!/usr/bin/python

def ListPresentDevices(config):
    return list(sorted(
        ifname for ifname in config
        if not config[ifname]['defconf']
    ))
