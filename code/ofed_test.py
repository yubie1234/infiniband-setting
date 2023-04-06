from ofed import IbDriver, IbService


print("OFED INSTALLED ? ", IbDriver().is_ofed_installed())
print(IbService().is_ib_service_status_ok())
print(IbService().start_all_service())