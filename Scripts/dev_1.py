# Verify connection

from urllib.request import urlopen


def connection_avaliable(host, host_name):
    try:
        urlopen(host, timeout=2)
        return True
    except Exception as e:
        print(host_name + " connection not avaliable")
        print(str(e))
        return False


response = connection_avaliable(host="http://192.168.1.231:8086", host_name="Influx")
print(response)
