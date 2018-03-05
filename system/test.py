import nmap


target_mac = '78:88:6d:26:24:12'

nm = nmap.PortScanner()

nm.scan(hosts='192.168.178.0/24', arguments='-sP')

host_list = nm.all_hosts()
print(host_list)
for host in host_list:
   print(nm[host])
   if  'mac' in nm[host]['addresses']:
      print(host+' : '+nm[host]['addresses']['mac'])
      if target_mac == nm[host]['addresses']['mac']:
         print('Target Found')
