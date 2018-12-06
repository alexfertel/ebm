#!/usr/bin/env python3.6
import array
import config
import fcntl
import socket

import struct


def cut(body: str, size: int = config.MESSAGE_LENGTH) -> list:
    length = len(body)
    if size > length:
        val = ''
        result = []
        for i in range(length):
            if i % size == 0:
                result.append(val)
                val = ''
            else:
                val += body[i] if i != length else body[i]
        return result
    else:
        return [body]


def inbetween(a, b, c):
    """
    Is c between a and b
    :param a: int
    :param b: int
    :param c: int
    :return: bool
    """
    a = a % config.SIZE
    b = b % config.SIZE
    c = c % config.SIZE
    if a < b:
        return a <= c <= b
    return a <= c or c <= b


def all_interfaces():
    max_possible = 128  # arbitrary. raise if needed.
    _bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', b'\0' * _bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', _bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()
    lst = []
    for i in range(0, outbytes, 40):
        name = namestr[i:i + 16].split(b'\0', 1)[0]
        ip = namestr[i + 20:i + 24]
        lst.append((name.decode(), format_ip(ip)))
    return lst


def format_ip(addr):
    return str(addr[0]) + '.' + \
           str(addr[1]) + '.' + \
           str(addr[2]) + '.' + \
           str(addr[3])


def is_connected():
    ifaces = all_interfaces()
    connected = []

    i = 0
    for ifname, ip in ifaces:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])
            s.bind((ip, 13131))
            connected.append(ifname)
            print(f"{ifname} is connected")
        except Exception as e:
            print(f"{e}")
            print(f"{ifname} is not connected")
        i += 1

    return connected


# import socket
# import array
# import struct
# import fcntl

def get_local_interfaces():
    """ Returns a dictionary of name:ip key value pairs. """

    # Max possible bytes for interface result.  Will truncate if more than 4096 characters to describe interfaces.
    MAX_BYTES = 4096

    # We're going to make a blank byte array to operate on.  This is our fill char.
    FILL_CHAR = b'\0'

    # Command defined in ioctl.h for the system operation for get iface list
    # Defined at https://code.woboq.org/qt5/include/bits/ioctls.h.html under
    # /* Socket configuration controls. */ section.
    SIOCGIFCONF = 0x8912

    # Make a dgram socket to use as our file descriptor that we'll operate on.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Make a byte array with our fill character.
    names = array.array('B', MAX_BYTES * FILL_CHAR)

    # Get the address of our names byte array for use in our struct.
    names_address, names_length = names.buffer_info()

    # Create a mutable byte buffer to store the data in
    mutable_byte_buffer = struct.pack('iL', MAX_BYTES, names_address)

    # mutate our mutable_byte_buffer with the results of get_iface_list.
    # NOTE: mutated_byte_buffer is just a reference to mutable_byte_buffer - for the sake of clarity we've defined them as
    # separate variables, however they are the same address space - that's how fcntl.ioctl() works since the mutate_flag=True
    # by default.
    mutated_byte_buffer = fcntl.ioctl(sock.fileno(), SIOCGIFCONF, mutable_byte_buffer)

    # Get our max_bytes of our mutated byte buffer that points to the names variable address space.
    max_bytes_out, names_address_out = struct.unpack('iL', mutated_byte_buffer)

    # Convert names to a bytes array - keep in mind we've mutated the names array, so now our bytes out should represent
    # the bytes results of the get iface list ioctl command.
    namestr = names.tostring()

    namestr[:max_bytes_out]

    bytes_out = namestr[:max_bytes_out]

    # Each entry is 40 bytes long.  The first 16 bytes are the name string.
    # the 20-24th bytes are IP address octet strings in byte form - one for each byte.
    # Don't know what 17-19 are, or bytes 25:40.
    ip_dict = {}
    for i in range(0, max_bytes_out, 40):
        name = namestr[i: i + 16].split(FILL_CHAR, 1)[0]
        name = name.decode('utf-8')
        ip_bytes = namestr[i + 20:i + 24]
        full_addr = []
        for netaddr in ip_bytes:
            if isinstance(netaddr, int):
                full_addr.append(str(netaddr))
            elif isinstance(netaddr, str):
                full_addr.append(str(ord(netaddr)))
        ip_dict[name] = '.'.join(full_addr)

    return ip_dict


if __name__ == '__main__':
    # ifs = all_interfaces()
    # print(ifs)
    # for i in ifs:
    #     print("%12s   %s" % (i[0], format_ip(i[1])))
    # print(is_connected())
    print(get_local_interfaces())
