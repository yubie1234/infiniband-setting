import time
from ib_info_parser import AllInfiniband

class VFsSetting():

    def __init__(self, interface_name):
        self.infiniband = AllInfiniband().get_infiniband(interface_name=interface_name)
        pass


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

        time_base = str(time.time()) # 1673870377.4855864
        time_base_guid_list = []
        for i in range(5):
            time_base_guid_list.append(time_base[i:i+2])
        return time_base_guid_list


    def set_vf_guid(self, vf_id):
        """
            echo ${TIME_GUID[0]}:${TIME_GUID[1]}:${TIME_GUID[2]}:${TIME_GUID[3]}:${TIME_GUID[4]}:${GUID[5]}:${GUID[6]}:$i > /sys/class/infiniband/mlx5_0/device/sriov/$i/node
            echo ${TIME_GUID[0]}:${TIME_GUID[1]}:${TIME_GUID[2]}:${TIME_GUID[3]}:${TIME_GUID[4]}:${GUID[5]}:${GUID[6]}:$i > /sys/class/infiniband/mlx5_0/device/sriov/$i/port
        """

        port_path = "/sys/class/infiniband/mlx5_0/device/sriov/{vf_id}/port".format(vf_id=vf_id) # infiniband.path + /sriov/{vf_id}/port
        node_path = "/sys/class/infiniband/mlx5_0/device/sriov/{vf_id}/node".format(vf_id=vf_id) # infiniband.path + /sriov/{vf_id}/node

        guid = ":".join(self.generate_datetime_base_guid() + [self.infiniband.node_guid[-4:-2], self.infiniband.node_guid[-2:], "{0:02d}".format(vf_id)]) # 16:67:73:38:87:b3:86
        print(guid) 

print(VFsSetting("ibs9").set_vf_guid(1))