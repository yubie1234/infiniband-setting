from vf import VFsSetting

def test_interface_normal():
    vfs = VFsSetting("ibs9")
    print(vfs.create_vfs(10))
    print(vfs._debug())

def test_interface_normal_no_guid():
    vfs = VFsSetting("ibs9")
    print(vfs.create_vfs(20, False, True))
    print(vfs._debug())


def test_interface_notfound():
    vfs = VFsSetting("aaaa")
    print(vfs.create_vfs(10))
    print(vfs._debug())

def test_interface_vf():
    vfs = VFsSetting("ibs9v0")
    print(vfs.create_vfs(10))
    print(vfs._debug())


test_interface_normal_no_guid()