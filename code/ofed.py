# driver 관리 (설치 되어 있는 버전 확인)
# ofed_info -n

# service 관리 (서비스 On 상태 확인, 서비스 실행 시도 -> On 상태 확인) (설치 유무 확인은 어렵?)
# opensmd (by OFED)
# openibd (by OFED)
# nv_peer_mem  (by nvidia_peer_memory)

import subprocess

class IbDriver():
    def __init__(self):
        self.ofed_version = self.get_ofed_version()

    def get_ofed_version(self):
        try:
            ofed_version = subprocess.check_output(["ofed_info -n"], shell=True, stderr=subprocess.STDOUT).decode("utf-8").replace("\n", "")
        except subprocess.CalledProcessError as e:
            # raise Exception("OFED Version get error. OFED installed ?")
            return None
        return ofed_version

    def is_ofed_installed(self):
        if self.ofed_version is not None:
            return True
        else:
            return False

SERVICE_STATUS_ACTIVE = "active"
SERVICE_OPENSMD = "opensmd"
SERVICE_OPENIBD = "openibd"
SERVICE_NV_PEER_MEM = "nv_peer_mem"

class IbService():

    def __init__(self):
        pass    
    
    def _get_service_status(self, service: str):
        """
            Args:
                service (str) : openibd, opensmd, nv_peer_mem ...
        """
        try:
            service_status_log = subprocess.check_output(["service {} status".format(service)], shell=True, stderr=subprocess.STDOUT).decode("utf-8").split()
            status_index = service_status_log.index("Active:") + 1

            service_status = service_status_log[status_index]
        except subprocess.CalledProcessError as e:
            try:
                service_status_log = e.output.decode("utf-8").split()
                status_index = service_status_log.index("Active:") + 1
                service_status = service_status_log[status_index]
            except ValueError as ve:
                service_status = "N/A"

        return service_status

    def get_opensmd_service_status(self):
        return self._get_service_status(service="opensmd")

    def get_openibd_service_status(self):
        return self._get_service_status(service="openibd")

    def get_nv_peer_mem_service_status(self):
        return self._get_service_status(service="nv_peer_mem")

    def get_all_service_status(self):
        opensmd_status = self.get_opensmd_service_status()
        openibd_status = self.get_openibd_service_status()
        nv_peer_mem_status = self.get_nv_peer_mem_service_status()
        
        return opensmd_status, openibd_status, nv_peer_mem_status

    def is_ib_service_status_ok(self):

        opensmd_status, openibd_status, nv_peer_mem_status = self.get_all_service_status()

        if opensmd_status == openibd_status == nv_peer_mem_status == SERVICE_STATUS_ACTIVE:
            status_ok = True
        else:
            status_ok = False

        return status_ok

    def print_status(self, opensmd_status: list, openibd_status: list, nv_peer_mem_status: list, is_ok: list):
        form = "|%-15s|%20s|"
        base_line = form % ("-"*15,"-"*20)
        print(base_line)
        print(form % ("service", "status"))
        print(base_line)
        print(form % ("opensmd", " -> ".join(opensmd_status)))
        print(form % ("openibd", " -> ".join(openibd_status)))
        print(form % ("nv_peer_mem", " -> ".join(nv_peer_mem_status)))
        print(base_line)

        print("Service OK : {}".format(" -> ".join(is_ok)))

    def _start_service(self, service: str):
        """
            Args:
                service (str) : openibd, opensmd, nv_peer_mem ...
        """
        try:
            stop_message = subprocess.check_output(["service {} stop".format(service)], shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            print("Stop Error ", e.output.decode("utf-8"))

        try:
            start_message = subprocess.check_output(["service {} start".format(service)], shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            print("Start Error", e.output.decode("utf-8"))

        return True

    def start_opensmd_service(self):
        self._start_service(service=SERVICE_OPENSMD)

    def start_openibd_service(self):
        self._start_service(service=SERVICE_OPENIBD)

    def start_nv_peer_mem_service(self):
        self._start_service(service=SERVICE_NV_PEER_MEM)
        
    def start_all_service(self):

        old_opensmd_status, old_openibd_status, old_nv_peer_mem_status = self.get_all_service_status()
        old_status_ok = str(self.is_ib_service_status_ok())

        self.start_opensmd_service()
        self.start_openibd_service()
        self.start_nv_peer_mem_service()

        new_opensmd_status, new_openibd_status, new_nv_peer_mem_status = self.get_all_service_status()
        new_status_ok = str(self.is_ib_service_status_ok())

        self.print_status(opensmd_status=[old_opensmd_status, new_opensmd_status], 
                        openibd_status=[old_openibd_status, new_openibd_status], 
                        nv_peer_mem_status=[old_nv_peer_mem_status, new_nv_peer_mem_status], is_ok=[old_status_ok, new_status_ok])
        ## Check
        self.is_ib_service_status_ok()

