from infiniband import AllInfiniband
aib = AllInfiniband()

print([ ib.__dict__ for ib in aib.infiniband_list ] )