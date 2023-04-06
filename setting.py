#!/usr/bin/python3
# 제공 기능 목록
# 1. 모든 Infiniband 설정 정보 조회 --ib-all
# 2. 지정한 Interface Infiniband 설정 정보 조회 --ib-pf-all, --ib-vf-all, --ib-select ib0
# 3. MST SRIOV 활성화 상태 정보 조회 --mst-status, --mst-status-all-config
# 4. MST SRIOV 활성화 및 NUM VF 개수 설정 --mst-setting --mst-sriov-en 0|1 --mst-numvfs NUM(>0)
# 5. VF NUM VF 생성 --vf-setting --vf-root ib0 --vf-numvfs NUM(>0) OPTIONAL --vf-guid-set --vf-debug
from code import AllInfiniband, Mst, VFsSetting, IbDriver, IbService

def custom_bool(int_):
    if int_ is None:
        return None
    if int(int_) == 0:
        return False
    else:
        return True

import pprint
import argparse
parser = argparse.ArgumentParser(description="For Infiniband Setting.")
parser.add_argument('--check-all', action='store_true', help='Show All setting status.')

parser.add_argument('--ib-all', action='store_true', help='Show All Infiniband interface info.')
parser.add_argument('--ib-pf-all', action='store_true', help='Show All pf Infiniband interface info.')
parser.add_argument('--ib-vf-all', action='store_true', help='Show All vf Infiniband interface info.')
parser.add_argument('--ib-select', type=str, help='Show select Infiniband interface info. (ib0, ibs9 ...)')

parser.add_argument('--mst-status', action='store_true', help='Show Mst setting status, sriov avaliable.')
parser.add_argument('--mst-status-all-config', action='store_true', help='Show Mst all config setting.')
parser.add_argument('--mst-setting', action='store_true', help='For Mst sriov en, numvfs.')
parser.add_argument('--mst-sriov-en', type=custom_bool, help='For Mst sriov en. 0(False) | 1(True)')
parser.add_argument('--mst-numvfs', type=int, help='For Mst numvfs. numvfs >= 0')

parser.add_argument('--vf-setting', action='store_true', help="VF Setting.")
parser.add_argument('--vf-root', type=str, help="VF root (PF) interface name")
parser.add_argument('--vf-numvfs', type=int, help='For vf numvfs. numvfs >= 0')
parser.add_argument('--vf-guid-set', action='store_true', help='For vf node,port guid')
parser.add_argument('--vf-debug', action='store_true', help='For showing vf setting result.')

args = parser.parse_args()

def show_ib_all():
    for infiniband in AllInfiniband().infiniband_list:
        pprint.pprint(infiniband.__dict__)

def show_ib_pf_all():
    for infiniband in AllInfiniband().get_pf_infiniband():
        pprint.pprint(infiniband.__dict__)

def show_ib_vf_all():
    for infiniband in AllInfiniband().get_vf_infiniband():
        pprint.pprint(infiniband.__dict__)

def show_ib_select(interface_name):
    pprint.pprint(AllInfiniband().get_infiniband(interface_name=interface_name).__dict__)


def check_all_print():
    EMPTY_GUID = "0000:0000:0000:0000"

    form = "|{0:^25}|{1:^20}|{2:^20}|"
    check_form = "|{0:<25}|{1:^20}|{2:^20}|"
    base = form.format("-"*25, "-"*20, "-"*20)
    head = form.format("Check List", "Result", "Status")
    print(base)
    print(head)
    print(base)
    check_list = []
    try:
        mst = Mst(error_raise=False)
    except Exception as e:
        raise e
        pass
    
    all_infiniband = AllInfiniband()
    pf_infiniband_list = all_infiniband.get_pf_infiniband()

    
    

    check_list.append(check_form.format("OFED INSTALLED", str(IbDriver().is_ofed_installed()), ""))
    check_list.append(check_form.format("OFED VERSION", str(IbDriver().ofed_version), ""))
    check_list.append(check_form.format("OFED RELATED SERVICE ", str(IbService().is_ib_service_status_ok()), ""))
    interface = "{} - ({})".format(len(pf_infiniband_list), ",".join([ pf.interface_name for pf in pf_infiniband_list ]))
    check_list.append(check_form.format("IB Interface", interface, ""))
    check_list.append(check_form.format("MST SRIOV ENABLE", mst.mst_sriov_en, ""))
    check_list.append(check_form.format("MST NUMVFS", mst.mst_numvfs, ""))

    # PF 마다 존재
    for pf_infiniband in pf_infiniband_list:
        check_list.append(check_form.format("VF NUM", "{}/{}".format(pf_infiniband.numvfs, pf_infiniband.totalvfs), ""))
        check_list.append(check_form.format("VF GUID NOT EMPTY", str(pf_infiniband.is_vf_guid_not_empty()), ""))
    for check in check_list:
        print(check)
    print(base)
    # print("OFED INSTALLED ? ", IbDriver().is_ofed_installed())
    # print(IbService().is_ib_service_status_ok())
    # print("OFED INSTALLED ") # True
    # print("OFED SERVICE") # Active
    # print("IB NUM OF PF") # 1 이상
    # print("MST SRIOV ENABLE ") # On
    # print("MST NUMVFS ") # 1 이상
    # print("VF SETTING ") # VF 존재, GUID OK
                    





if __name__ == "__main__":

    if args.check_all:
        # ofed installed check
        # ofed service check
        # ib exist check
        # mfs sriov enable check
        # mfs setting check
        # vf setting check
        check_all_print()

    if args.ib_all:
        show_ib_all()
    elif args.ib_pf_all:
        show_ib_pf_all()
    elif args.ib_vf_all:
        show_ib_vf_all()
    elif args.ib_select:
        show_ib_select(interface_name=args.ib_select)



    if args.mst_status:
        mst = Mst()
        print("%-20s %2s %-10s" % ("MST SRIOV AVALAIABLE", "", mst.is_sriov_avaliable()))
        print("%-20s %2s %-10s" % ("MST SRIOV_EN", "", mst.mst_sriov_en))
        print("%-20s %2s %-10s" % ("MST NUM_OF_VFS ", "", mst.mst_numvfs))

        if args.mst_status_all_config:
            print("MST CONFIG")
            for query in mst.mst_query:
                print(query)

    elif args.mst_setting:
        mst = Mst()
        print(args.mst_sriov_en)
        print(args.mst_numvfs)
        mst.set_mst_for_sriov(sriov_en=args.mst_sriov_en, numvfs=args.mst_numvfs)


    if args.vf_setting:

        mst = Mst()
        if mst.is_sriov_avaliable() == False:
            raise Exception("SRIOV Unavaliable. Please run this command first. --mst-setting --mst_sriov_en 1 --mst_numvfs NUM(>0)")


        vfs = VFsSetting(args.vf_root)
        print("%-20s" % ("Created VF status"), vfs.create_vfs(numvfs=args.vf_numvfs, vf_guid_create=args.vf_guid_set, debug=args.vf_debug))
        print("%-20s" % ("VF Root (PF)"), args.vf_root)
        print("%-20s" % ("NUM of VF"), args.vf_numvfs)