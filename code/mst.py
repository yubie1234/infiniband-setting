#!/bin/bash
"""
mst start

mst status

MST_DEVICE=$(mst status | grep /dev | awk '{print $1}')

MST_SRIOV_EN=$(mlxconfig -d $MST_DEVICE q | grep SRIOV_EN | awk '{print $2}') # True(1) or False(0)

MST_NUM_OF_VFS=$(mlxconfig -d $MST_DEVICE q | grep NUM_OF_VFS | awk '{print $2}')

NUM_OF_GPU=$(nvidia-smi -q -x | grep "gpu id" | wc -l)

NEED_NUM_OF_VFS=$(($NUM_OF_GPU + 1))

if [ "$MST_SRIOV_EN" == "True(1)" ] && [ "$MST_NUM_OF_VFS" == "$NEED_NUM_OF_VFS" ]
then
    echo "SKIP SRIOV_EN NUM_OF_VFS SET "
    echo "RUN mst_after.sh"
else
    mlxconfig -d $MST_DEVICE set SRIOV_EN=1 NUM_OF_VFS=$NEED_NUM_OF_VFS
fi
"""
import subprocess
class BinaryNotExistError(Exception):
    pass

class BinaryNotWorkingError(Exception):
    pass
 

MST_TRUE = "True(1)"
MST_FALSE = "False(0)"

class Mst:
    def __init__(self):
        self._system_check() # binary exist check

        self.mst_device = self.get_mst_device()
        self.mst_query = self.get_mst_query(mst_device=self.mst_device)

        # Query 관련
        self.mst_sriov_en = self.get_mst_sriov_en()
        self.mst_numvfs = self.get_mst_numvfs()

    def _system_check(self):
        try:
            subprocess.check_output(["which mst && which mlxconfig"], shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as se:
            raise BinaryNotExistError("[mst | mlxconfig] not exist. check ofed installed.")
        # If mst or mlxconfig not 

    def get_mst_device(self):
        try:
            # mst status | grep /dev | awk '{print $1}'
            mst_status = subprocess.check_output(["mst status "], shell=True, stderr=subprocess.STDOUT).decode("utf-8").split()
            for line in mst_status:
                if "/dev/mst" in line:
                    return line
        except subprocess.CalledProcessError as scpe:
            raise BinaryNotWorkingError("mst not working. \n returncode [{}]. \n output [{}]".format(scpe.returncode, scpe.stdout.decode("utf-8")))
        
        raise Exception("mst device not found.")

    def get_mst_query(self, mst_device):
        try:
            mst_query = subprocess.check_output(["mlxconfig -d {MST_DEVICE} q".format(MST_DEVICE=mst_device)], shell=True, stderr=subprocess.STDOUT).decode("utf-8").split("\n")
        except subprocess.CalledProcessError as scpe:
            raise BinaryNotWorkingError("mlxconfig not working. \n returncode [{}]. \n output [{}]".format(scpe.returncode, scpe.stdout.decode("utf-8")))
        return mst_query

    def get_mst_value_by_key(self, key):
        for query in self.mst_query:
            if " {key} ".format(key=key) in query:
                return query.split()[-1]

        raise Exception("{key} KEY Not Found.".format(key))

    def get_mst_sriov_en(self):
        return self.get_mst_value_by_key(key="SRIOV_EN")

    def get_mst_sriov_en_set_command(self, sriov_en: bool):
        command = " SRIOV_EN={} ".format(str(sriov_en))
        return command

        # sriov_en = 1 if sriov_en == True else 0
        # sriov_en_setting = subprocess.check_output(["echo y | mlxconfig -d {MST_DEVICE} set SRIOV_EN={SRIOV_EN}".format(MST_DEVICE=self.mst_device, SRIOV_EN=sriov_en)], shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        # print(sriov_en_setting)


    def get_mst_numvfs(self):
        # sriov_numvfs = subprocess.check_output(["mlxconfig -d {MST_DEVICE} q | grep NUM_OF_VFS | awk '{{print $2}}'".format(MST_DEVICE=mst_device)], shell=True, stderr=subprocess.STDOUT).decode("utf-8").replace("\n","")
        # return sriov_numvfs
        return int(self.get_mst_value_by_key(key="NUM_OF_VFS"))

    def get_mst_numvfs_set_command(self, numvfs: int):
        command = " NUM_OF_VFS={} ".format(numvfs)
        return command
        
        # numvfs_setting = subprocess.check_output(["echo y | mlxconfig -d {MST_DEVICE} set NUM_OF_VFS={NEED_NUM_OF_VFS}".format(MST_DEVICE=self.mst_device, NEED_NUM_OF_VFS=numvfs)], shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        # print(numvfs_setting)

    def set_mst_for_sriov(self, sriov_en: bool=None, numvfs: int=None):

        if sriov_en is None and numvfs is None:
            raise Exception("Setting Value Empty.")

        if self.is_same_config(sriov_en=sriov_en, numvfs=numvfs):
            print("Same Setting Skip.")
            return True

        set_command = ""
        if sriov_en is not None:
            set_command += self.get_mst_sriov_en_set_command(sriov_en=sriov_en)

        if numvfs is not None:
            set_command += self.get_mst_numvfs_set_command(numvfs=numvfs)

        
        mst_setting = subprocess.check_output(["echo y | mlxconfig -d {MST_DEVICE} set {SET_COMMAND}".format(MST_DEVICE=self.mst_device, SET_COMMAND=set_command)], shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        print(mst_setting)
    #
    def is_sriov_avaliable(self):
        is_avaliable = True
        if self.mst_sriov_en == MST_FALSE:
            # SRIOV EN ?
            print("[Warn] Need to set SRIOV_EN=1. Current SRIOV_EN={}".format(self.mst_sriov_en))
            is_avaliable = False

        if self.mst_numvfs == 0:
            # NUMVFS more than 0 ?
            print("[Warn] Need to set NEED_NUM_OF_VFS=(More than 1). Current NUM_OF_VFS={}".format(self.mst_numvfs))
            is_avaliable = False
        return is_avaliable

    def is_same_config(self, sriov_en, numvfs):
        if sriov_en is None:
            sriov_en = self.mst_sriov_en
        else:
            sriov_en = MST_TRUE if sriov_en == True else MST_FALSE 

        if numvfs is None:
            numvfs = self.mst_numvfs

        # print(sriov_en, self.mst_sriov_en, numvfs, self.mst_numvfs)

        if sriov_en == self.mst_sriov_en and numvfs == self.mst_numvfs:
            return True
        else:
            return False


