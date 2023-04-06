import subprocess
import os

SRIOV_PF = "PF"
SRIOV_VF = "VF"

class AllInfiniband():

    def __init__(self):
        self.infiniband_list = []

        for path in self.get_infiniband_devices_path():
            try:
                infiniband = Infiniband(path=path)
            except Exception as e:
                raise e
                continue
                
            self.infiniband_list.append(infiniband)


    def get_infiniband_devices_path(self):
        path_list = subprocess.check_output('find /sys/devices -name infiniband | sort', shell=True, stderr=subprocess.STDOUT).decode("utf-8").split()
        """
            /sys/devices/pci0000:16/0000:16:02.0/0000:17:00.0/infiniband
            /sys/devices/pci0000:16/0000:16:02.0/0000:17:00.1/infiniband
            /sys/devices/pci0000:16/0000:16:02.0/0000:17:00.2/infiniband
        """
        for i, path in enumerate(path_list): 
            path_list[i] = path.replace("infiniband", "")

        if len(path_list) == 0:
            raise Exception("Infiniband Not Found.")

        return path_list

    def get_infiniband(self, interface_name):
        for infiniband in self.infiniband_list:
            if infiniband.interface_name == interface_name:
                return infiniband

        raise Exception("Not Found {} Infiniband Device.".format(interface_name))

    def get_pf_infiniband(self):
        infiniband_list = []
        for infiniband in self.infiniband_list:
            if infiniband.sriov_func == SRIOV_PF:
                infiniband_list.append(infiniband)

        return infiniband_list

    def get_vf_infiniband(self):
        infiniband_list = []
        for infiniband in self.infiniband_list:
            if infiniband.sriov_func == SRIOV_VF:
                infiniband_list.append(infiniband)

        return infiniband_list
EMPTY_GUID = "0000:0000:0000:0000"
class Infiniband:

    def __init__(self, path):
        self.path = path
        self.interface_name = self.get_interface_name(path=path)
        self.mlx_name = self.get_mlx_name(path=path)
        self.sriov_func = self.get_sriov_func(path=path)
        self.numvfs = self.get_numvfs(path=path) if self.sriov_func == SRIOV_PF else 0
        self.totalvfs = self.get_totalvfs(path=path) if self.sriov_func == SRIOV_PF else 0

        self.node_guid = self.get_node_guid(path=path)

        # PF인 경우 해당 PF가 가지고 있는 VF들
        if self.sriov_func == SRIOV_PF:
            self.vf_list = self.get_vf_list(path=path)
        else:
            self.vf_list = []

    def get_interface_name(self, path):
        try:
            interface_name = os.listdir(path+"/net/")[-1]
        except IndexError as ie:
            # raise Exception("Infiniband interface name empty.")
            return None
        except FileNotFoundError as fe:
            return None
        return interface_name


    def get_mlx_name(self, path):
        mlx_name = os.listdir(path+"/infiniband/")[-1]
        return mlx_name

    def get_sriov_func(self, path):
        # PF / VF
        if os.path.isdir(path+"/sriov/"):
            return SRIOV_PF
        else :
            return SRIOV_VF

    def get_numvfs(self, path):
        # 실제 활성화 되어 있는 vf 개수 sriov_numvfs
        # PF - 0 ~ N
        # VF - 0
        item = "/sriov_numvfs"
        try:
            with open(path + item, "r") as f:
                numvfs = f.read().replace("\n", "")
        except FileNotFoundError as fne:
            numvfs = 0

        return int(numvfs)

    def get_totalvfs(self, path):
        # 활성화 할 수 있는 총 vf 개수 sriov_totalvfs
        # + /sriov_totalvfs
        item = "/sriov_totalvfs"

        try:
            with open(path + item, "r") as f:
                totalvfs = f.read().replace("\n", "")
        except FileNotFoundError as fne:
            totalvfs = 0

        return int(totalvfs)

    def get_node_guid(self, path):
        item = "/infiniband/{mlx_name}/node_guid".format(mlx_name=self.mlx_name)
        with open(path + item, "r") as f:
            node_guid = f.read().replace("\n", "")
        return node_guid

    def get_vf_list(self, path):
        vf_list = []
        for item in sorted(os.listdir(path)):
            if item.find("virtfn") == 0 and os.path.islink(path + item):
                vf_list.append(Infiniband(os.path.realpath(path + item)))

        return vf_list

    def is_vf_guid_not_empty(self):
        # PF 이면서 VF 1개 이상일 때 GUID 값이 0000으로 구성되어 있는지 아닌지 확인

        for vf in self.vf_list:
            if vf.node_guid == EMPTY_GUID:
                return False
        
        return True