import network

def start_access_point(local_ip="192.168.4.1", essid=None, password=None):
    wifi_interface = network.WLAN(network.AP_IF)
    if essid is None:
        essid = "test"

    wifi_interface.active(False)
    wifi_interface.ifconfig((local_ip, "255.255.255.0", local_ip, local_ip))

    if password:
        wifi_interface.config(essid=essid, security=3, password=password)
    else:
        wifi_interface.config(essid=essid, security=0)

    wifi_interface.active(True)
    print(f"Access point started with ESSID '{essid}' at IP {local_ip}")