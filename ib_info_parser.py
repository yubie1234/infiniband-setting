import subprocess
import os

SRIOV_PF = "PF"
SRIOV_VF = "VF"

class AllInfiniband():

    def __init__(self):
        self.infiniband_list = []

        for path in self.get_infiniband_devices_path():
            self.infiniband_list.append(Infiniband(path=path))


    def get_infiniband_devices_path(self):
        path_list = subprocess.check_output('find /sys/devices -name infiniband | sort', shell=True, stderr=subprocess.STDOUT).decode("utf-8").split()
        for i, path in enumerate(path_list): 
            path_list[i] = path.replace("infiniband", "")

        return path_list

class Infiniband:

    def __init__(self, path):
        self.interface_name = self.get_interface_name(path=path)
        self.mlx_name = self.get_mlx_name(path=path)
        self.sriov_func = self.get_sriov_func(path=path)
        self.num_of_vf = self.get_num_of_vf(path=path)


    def get_interface_name(self, path):
        interface_name = os.listdir(path+"/net/")[-1]
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

    def get_num_of_vf(self, path):
        # PF - 0 ~ N
        # VF - 0
        if os.path.isdir(path+"/sriov/"):
            return len(os.listdir(path+"/sriov/"))
        else :
            return 0




