from infiniband import AllInfiniband
aib = AllInfiniband()

for ib in aib.infiniband_list:
    print(ib.__dict__)
    if len(ib.vf_list) > 0:
        for vf in ib.vf_list:
            print("\t",vf.__dict__)