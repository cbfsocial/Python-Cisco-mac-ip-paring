import paramiko

ip = [all device's ip]
usr = ""
pwd = ""


def hostname_parser(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=usr, password=pwd, look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = client.exec_command('sh run | i hostname')
    return stdout.readlines()[0].replace('hostname ', '').replace('\r\n', '')


def arp_line_parser(line):
    spl = list(filter(lambda s: s != '', line.split(' ')))
    return spl[1], spl[3]


def arp_parser(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=usr, password=pwd, look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = client.exec_command('show arp')
    lines = stdout.readlines()[4:]
    return list(map(arp_line_parser, lines))


def line_parser(line):
    return line.split('    ')[1], line.split('     ')[-1].replace('\r\n', '')


def port_parser(host, port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=usr, password=pwd, look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = client.exec_command("show mac address-table int Fa0/" + str(port))
    lines = stdout.readlines()
    if len(lines) > 5:
        return list(map(line_parser, lines[5:-1]))
    client.close()


arp_table = arp_parser('CORE IP where all arp collected')
for host in ip:
    hostname = hostname_parser(host)
    f = open("hostname_done.txt", 'a')
    for port in range(1, 49):
        parsed = port_parser(host, port)
        if parsed is not None:
            for parsed_elem in parsed:
                arp = list(filter(lambda a: a[1] == parsed_elem[0], arp_table))
                if len(arp) > 0:
                    f.write(hostname + ',' + parsed_elem[1] + ',' + parsed_elem[0] + ',' + arp[0][0] + '\n')
    f.close()
