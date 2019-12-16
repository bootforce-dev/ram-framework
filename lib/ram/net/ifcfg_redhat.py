from glob import iglob
from itertools import count as itercount
from itertools import groupby

from ram.osutils import FileStamp
from ram.formats import env


_NETWORKCFG = '/etc/sysconfig/network'
_NETWORKSRV = '/etc/init.d/network'
_NETWORKRUN = '/var/lock/subsys/network'
_IFCFG_ROOT = '/etc/sysconfig/network-scripts/'
_IFCFG_PATH = _IFCFG_ROOT + 'ifcfg-'
_ROUTE_PATH = _IFCFG_ROOT + 'route-'
_IFCFG_GLOB = _IFCFG_PATH + '*'


class NetworkConfiguration(object):
    DEFAULT_NETCONF = {
        'ONBOOT': 'yes',
        'BOOTPROTO': 'none',
        'PERSISTENT_DHCLIENT': 'no',
        'DEFROUTE': 'no',
        'PEERDNS': 'no',
    }
    DEFLOOP_NETCONF = {
        'ONBOOT': 'yes',
        'IPADDR': '127.0.0.1',
        'NETMASK': '255.0.0.0',
        'NETWORK': '127.0.0.0',
        'BROADCAST': '127.255.255.255',
    }

    def __init__(self, error_cb=None):
        self.error_cb = error_cb
        self.config = env.cfgopen(_NETWORKCFG, readonly=False, error_cb=self.error_cb)
        self.ifcfgs = dict()
        self.routes = dict()

    def __sort__(self, ifname):
        if self.IsLoopback(ifname):
            return ()
        else:
            return tuple(
                int("".join(data)) if flag else "".join(data)
                for flag, data in groupby(ifname, str.isdigit)
            )

    def __iter__(self):
        return iter(sorted(self.ifcfgs, key=self.__sort__))

    def _may_be_loopback(net_config_method):
        def _may_be_loopback_wrapper(self, ifname, *args, **kwargs):
            if not ifname:
                ifname = 'lo'
            return net_config_method(self, ifname, *args, **kwargs)
        return _may_be_loopback_wrapper

    def IsLoopback(self, ifname):
        return ifname == 'lo'

    @_may_be_loopback
    def DelIface(self, ifname):
        if self.IsLoopback(ifname):
            return
        if ifname == self.config['GATEWAYDEV']:
            del self.config['GATEWAYDEV']
        del self.ifcfgs[ifname]
        del self.routes[ifname]

    @_may_be_loopback
    def AddIface(self, ifname):
        self.AddIfaceFiles(ifname)
        self.ifcfgs[ifname].update(self.DEFLOOP_NETCONF if self.IsLoopback(ifname) else self.DEFAULT_NETCONF)
        self.ifcfgs[ifname]['DEVICE'] = ifname

    @_may_be_loopback
    def AddIfaceFiles(self, ifname):
        self.ifcfgs[ifname] = env.cfgopen(_IFCFG_PATH + ifname, readonly=False, error_cb=self.error_cb)
        self.routes[ifname] = env.cfgopen(_ROUTE_PATH + ifname, readonly=False, error_cb=self.error_cb)

    @_may_be_loopback
    def DelIfaceFiles(self, ifname):
        _ifcfg = env.cfgopen(_IFCFG_PATH + ifname, readonly=False, delempty=True, error_cb=self.error_cb)
        _ifcfg.clear()
        _ifcfg.sync()
        _route = env.cfgopen(_ROUTE_PATH + ifname, readonly=False, delempty=True, error_cb=self.error_cb)
        _route.clear()
        _route.sync()

    def GetIfaceDevName(self, ifname):
        return self.ifcfgs[ifname]['DEVICE'] or ifname

    @_may_be_loopback
    def SetIfaceDevName(self, ifname, devname):
        if self.IsLoopback(ifname):
            return
        self.ifcfgs[ifname]['DEVICE'] = devname

    def GetIfaceBootProto(self, ifname):
        bootproto = self.ifcfgs[ifname]['BOOTPROTO']
        if bootproto in ['dhcp', 'bootp']:
            return bootproto

        return ''

    @_may_be_loopback
    def SetIfaceBootProto(self, ifname, bootproto):
        if self.IsLoopback(ifname) or (bootproto not in ['dhcp', 'bootp']):
            self.ifcfgs[ifname]['BOOTPROTO'] = 'none'
            self.ifcfgs[ifname]['PERSISTENT_DHCLIENT'] = 'no'
        else:
            self.ifcfgs[ifname]['BOOTPROTO'] = bootproto
            self.ifcfgs[ifname]['PERSISTENT_DHCLIENT'] = 'yes'

    def GetIfaceUseDhcp(self, ifname):
        return bool(self.GetIfaceBootProto(ifname))

    @_may_be_loopback
    def SetIfaceUseDhcp(self, ifname, usedhcp):
        self.SetIfaceBootProto(ifname, "dhcp" if usedhcp else "")

    def GetIfaceEnabled(self, ifname):
        if self.IsLoopback(ifname):
            return True
        enabled = self.ifcfgs[ifname]['ONBOOT'] or 'yes'
        return not (enabled.lower() == 'no')

    @_may_be_loopback
    def SetIfaceEnabled(self, ifname, enabled):
        if self.IsLoopback(ifname):
            return
        self.ifcfgs[ifname]['ONBOOT'] = 'yes' if enabled else 'no'

    def GetIfaceIpAddress(self, ifname):
        for suffix in ['', '0']:
            if 'IPADDR' + suffix in self.ifcfgs[ifname]:
                return self.ifcfgs[ifname]['IPADDR' + suffix]
        return ''

    @_may_be_loopback
    def SetIfaceIpAddress(self, ifname, ip_addr):
        self.ifcfgs[ifname]['IPADDR'] = ip_addr
        if 'IPADDR0' in self.ifcfgs[ifname]:
            del self.ifcfgs[ifname]['IPADDR0']

    def GetIfaceIpNetmask(self, ifname):
        for suffix in ['', '0']:
            if 'NETMASK' + suffix in self.ifcfgs[ifname]:
                return self.ifcfgs[ifname]['NETMASK' + suffix]
        return ''

    @_may_be_loopback
    def SetIfaceIpNetmask(self, ifname, netmask):
        self.ifcfgs[ifname]['NETMASK'] = netmask
        if 'NETMASK0' in self.ifcfgs[ifname]:
            del self.ifcfgs[ifname]['NETMASK0']

    def GetPeerDnsDevice(self):
        iflist = []
        for ifover in list(self):
            if not self.GetIfacePeerDns(ifover):
                continue
            elif self.IsLoopback(ifover):
                continue
            else:
                iflist += [ifover]

        return ' '.join(iflist)

    @_may_be_loopback
    def SetPeerDnsDevice(self, ifname):
        iflist = ifname.split()
        for ifover in list(self):
            if not ifover in iflist:
                self.SetIfacePeerDns(ifover, False)

        for ifover in iflist:
            self.SetIfacePeerDns(ifover, True)

    def GetIfacePeerDns(self, ifname):
        _value = self.ifcfgs[ifname]['PEERDNS'] or 'yes'
        return not (_value == 'no')

    @_may_be_loopback
    def SetIfacePeerDns(self, ifname, peerdns):
        self.ifcfgs[ifname]['PEERDNS'] = 'yes' if peerdns else 'no'

    @_may_be_loopback
    def GetIfacePrimaryDns(self, ifname):
        return self.ifcfgs[ifname]['DNS1']

    @_may_be_loopback
    def GetIfaceSecondaryDns(self, ifname):
        return self.ifcfgs[ifname]['DNS2']

    @_may_be_loopback
    def SetIfacePrimaryDns(self, ifname, srvaddr):
        self.ifcfgs[ifname]['DNS1'] = srvaddr

    @_may_be_loopback
    def SetIfaceSecondaryDns(self, ifname, srvaddr):
        self.ifcfgs[ifname]['DNS2'] = srvaddr

    @_may_be_loopback
    def GetIfaceSearchList(self, ifname):
        return self.ifcfgs[ifname]['DOMAIN']

    @_may_be_loopback
    def SetIfaceSearchList(self, ifname, domlist):
        self.ifcfgs[ifname]['DOMAIN'] = domlist

    def GetGatewayDevice(self):
        ifname = self.config['GATEWAYDEV']
        iflist = []
        for ifover in list(self) if not ifname else [ifname]:
            _value = self.ifcfgs[ifover]['DEFROUTE'] or 'yes'

            if _value == 'no':
                continue
            elif self.IsLoopback(ifover):
                continue
            else:
                iflist += [ifover]

        return ' '.join(iflist)

    @_may_be_loopback
    def SetGatewayDevice(self, ifname):
        iflist = ifname.split()
        for ifover in list(self):
            if not ifover in iflist:
                self.ifcfgs[ifover]['DEFROUTE'] = 'no'

        for ifover in iflist:
            self.ifcfgs[ifname]['DEFROUTE'] = 'yes'

        if self.IsLoopback(ifname) or len(iflist) != 1:
            self.config['GATEWAYDEV'] = ''
        else:
            self.config['GATEWAYDEV'] = ifname

    def GetIfaceIpGateway(self, ifname):
        return self.ifcfgs[ifname]['GATEWAY'] or self.config['GATEWAY']

    @_may_be_loopback
    def SetIfaceIpGateway(self, ifname, gateway):
        self.config['GATEWAY'] = ''
        self.ifcfgs[ifname]['GATEWAY'] = gateway

    def GetIfaceGwIgnored(self, ifname):
        _value = self.ifcfgs[ifname]['DHCLIENT_IGNORE_GATEWAY'] or 'no'
        return _value == 'yes'

    @_may_be_loopback
    def SetIfaceGwIgnored(self, ifname, ignored):
        self.ifcfgs[ifname]['DHCLIENT_IGNORE_GATEWAY'] = 'yes' if ignored else 'no'

    def GetIfaceStaticRoutes(self, ifname):
        rtlist = []
        for i in itercount():
            address = self.routes[ifname]['ADDRESS%u' % i]
            if not address:
                break
            netmask = self.routes[ifname]['NETMASK%u' % i]
            if not netmask:
                continue
            gateway = self.routes[ifname]['GATEWAY%u' % i]
            rtlist += [(address, netmask, gateway)]
        return rtlist

    @_may_be_loopback
    def SetIfaceStaticRoutes(self, ifname, rtlist):
        self.routes[ifname].clear()
        for i, (address, netmask, gateway) in enumerate(rtlist):
            self.routes[ifname]['ADDRESS%u' % i] = address
            self.routes[ifname]['NETMASK%u' % i] = netmask
            self.routes[ifname]['GATEWAY%u' % i] = gateway

    def GetHostname(self):
        return self.config['HOSTNAME'] or self.config['DHCP_HOSTNAME']

    def SetHostname(self, hostname):
        self.config['HOSTNAME'] = hostname
        self.config['DHCP_HOSTNAME'] = hostname

    def GetIfaceProperty(self, ifname, prop):
        return self.ifcfgs[ifname][prop]

    @_may_be_loopback
    def SetIfaceProperty(self, ifname, prop, value):
        self.ifcfgs[ifname][prop] = value


def IfConfigTest(ifname):
    if ifname.endswith(('~', '.bak', '.old', '.orig', '.rpmnew', '.rpmorig', '.rpmsave')):
        return False
    elif ifname == 'lo' or ifname.endswith(('-range')) or ':' in ifname:
        return False
    else:
        return True


def IfConfigList():
    return ['lo'] + filter(
        IfConfigTest,
        map(
            lambda _: _[len(_IFCFG_PATH):],
            iglob(_IFCFG_GLOB)
        )
    )


def QueryNetworkConfiguration(error_cb=None):
    netconf = NetworkConfiguration(error_cb=error_cb)

    for ifname in IfConfigList():
        if ifname not in netconf.ifcfgs:
            netconf.AddIfaceFiles(ifname)
        else:
            raise RuntimeError('Interface configuration already exists: `%s`.' % ifname)

    return netconf


def NetworkConfigurationStamp():
    tstamp = max([FileStamp(_NETWORKCFG), FileStamp(_IFCFG_ROOT)])

    for ifname in IfConfigList():
        ifcfg = _IFCFG_PATH + ifname
        route = _ROUTE_PATH + ifname
        tstamp = max([tstamp, FileStamp(ifcfg), FileStamp(route)])

    return tstamp


def NetworkServiceRunInEffect():
    return FileStamp(_NETWORKRUN)


def StoreNetworkConfiguration(netconf):
    if not netconf.config and not netconf.ifcfgs:
        raise RuntimeError('Attempting to store empty configuration')

    for ifname in IfConfigList():
        if ifname not in netconf.ifcfgs:
            netconf.DelIfaceFiles(ifname)

    for ifname in netconf.ifcfgs:
        netconf.ifcfgs[ifname].sync()
        netconf.routes[ifname].sync()

    netconf.config.sync()


if __name__ == '__main__':
    from sys import stderr, argv

    def dump_to_stderr(file, lnum, emsg):
        print >> stderr, "File %s: Line %s: %s" % (file, lnum, emsg)

    if argv[1:]:
        for filename in argv[1:]:
            result = env.cfgopen(filename, error_cb=dump_to_stderr)
            print "%s: %s" % (filename, result)
    else:
        netconf = QueryNetworkConfiguration(error_cb=dump_to_stderr)
        print netconf.config
        print netconf.ifcfgs
        print netconf.routes
