# opensm
import subprocess
from .infiniband import AllInfiniband

class IPoIB():
    def __init__(self, interface_name, ib_ip):
        self.infiniband = AllInfiniband().get_infiniband(interface_name=interface_name)
        self.ib_ip = ib_ip

    def set_opensm(self, node_guid):
        """ form change
        08c0:eb03:00e4:b23e 
        ->
        0x08c0eb0300e4b23e
        """
        def form_change(node_guid):
            new_node_guid = "0x{}".format(node_guid.replace(":", ""))
            return new_node_guid

        node_guid = form_change(node_guid)

        result = subprocess.check_output(["opensm -g {node_guid} --daemon".format(node_guid=node_guid)], shell=True, stderr=subprocess.STDOUT)
        print(result)

    def set_ip(self, interface_name, ib_ip):
        result = subprocess.check_output(["ifconfig {interface_name} {ib_ip}".format(interface_name=interface_name, ib_ip=ib_ip)], shell=True, stderr=subprocess.STDOUT)
        print(result)

    def set_ipoib(self):

        self.set_opensm(node_guid=self.infiniband.node_guid)
        self.set_ipoib(interface_name=self.infiniband.interface_name, ib_ip=self.ib_ip)