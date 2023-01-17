import time
import subprocess
from .infiniband import AllInfiniband, SRIOV_VF


class VFsSetting():

    def __init__(self, interface_name):
        self.infiniband = AllInfiniband().get_infiniband(interface_name=interface_name)

        if self.infiniband.sriov_func == SRIOV_VF: 
            raise Exception("This Interface is VF.")

        self._time = str(time.time())


    def generate_datetime_base_guid(self):
        """
        TIME_BASE_GUID=$(date +%s)
        echo $TIME_BASE_GUID
        TIME_GUID=()
        TIME_GUID[0]=$(echo $TIME_BASE_GUID | cut -c 1-2)
        TIME_GUID[1]=$(echo $TIME_BASE_GUID | cut -c 3-4)
        TIME_GUID[2]=$(echo $TIME_BASE_GUID | cut -c 5-6)
        TIME_GUID[3]=$(echo $TIME_BASE_GUID | cut -c 7-8)
        TIME_GUID[4]=$(echo $TIME_BASE_GUID | cut -c 9-10)
        """

        time_base = self._time # 1673870377.4855864
        time_base_guid_list = []
        for i in range(5):
            time_base_guid_list.append(time_base[i:i+2])
        return time_base_guid_list


    def set_vf_guid(self, vf_id):
        """
            echo ${TIME_GUID[0]}:${TIME_GUID[1]}:${TIME_GUID[2]}:${TIME_GUID[3]}:${TIME_GUID[4]}:${GUID[5]}:${GUID[6]}:$i > /sys/class/infiniband/mlx5_0/device/sriov/$i/node
            echo ${TIME_GUID[0]}:${TIME_GUID[1]}:${TIME_GUID[2]}:${TIME_GUID[3]}:${TIME_GUID[4]}:${GUID[5]}:${GUID[6]}:$i > /sys/class/infiniband/mlx5_0/device/sriov/$i/port
        """
        def write_guid(path, guid):
            with open(path, "w") as f:
                f.write(guid)

        port_path = self.infiniband.path + "/sriov/{vf_id}/port".format(vf_id=vf_id)
        node_path = self.infiniband.path + "/sriov/{vf_id}/node".format(vf_id=vf_id) 

        guid = ":".join(self.generate_datetime_base_guid() + [self.infiniband.node_guid[-4:-2], self.infiniband.node_guid[-2:], "{0:02d}".format(vf_id)]) # 16:67:73:38:87:b3:86

        write_guid(path=port_path, guid=guid)
        write_guid(path=node_path, guid=guid)

    def set_numvfs(self, numvfs):

        numvfs_path = self.infiniband.path + "/sriov_numvfs"
        with open(numvfs_path, "w") as f:
            f.write(str(numvfs))

    def create_vfs(self, numvfs, vf_guid_create=True, debug=False):
        if numvfs is None:
            raise Exception("Numvfs must be int. Not a {}".format(type(numvfs)))

        self.set_numvfs(numvfs=0) ## init
        self.set_numvfs(numvfs=numvfs) 

        if vf_guid_create:
            for i in range(numvfs):
                self.set_vf_guid(vf_id=i)

        if debug:
            self._debug()

        return True

    def _debug(self):

        print(subprocess.check_output(["ibdev2netdev -v"], shell=True).decode("utf-8"))
        print(subprocess.check_output(["lspci | grep Mellanox"], shell=True).decode("utf-8"))
        print(subprocess.check_output(["ip -a link show | grep ib"], shell=True).decode("utf-8"))
        print(subprocess.check_output(["ibstat | grep GUID"], shell=True).decode("utf-8"))

