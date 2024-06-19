
# modified implementation of 'TCP' checksum

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16) 

def checksum(msg, init=0x01):
    l = len(msg)
    out = bytearray(msg)

    # preset checksum
    out[8] = 0x00
    out[9] = init

    s = 0
    if l & 1:
        out += b"\x00"

    '''
    # Method 1
    # fails with
    # b"\x02\x06\x08\x00\x93\x7d\x00\x00\xfe\xff\x56\x3a\x16\x41\xf6\x01\x00\x00",
    for i in range(0,l,2):
        s = s +((out[i]<<8)+(out[i+1])) # Big Endian
    s = s + (s >>16)
    '''
    # Method 2
    for i in range(0,l,2):
        w = (out[i]<<8)+out[i+1]        # Big Endian
        s = carry_around_add(s, w)

    # embed new checksum
    out[8] = ~s & 0xff
    out[9] = (~s >> 8) & 0xff

    return bytes(out[:l])

#---------------------------------------------

import usb
import argparse
from sys import exit, platform
import struct

def main():
    from optparse import OptionParser
    
    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)

    parser.add_option("-a", "--add",
        dest="add", type=int, default=0x40200000,
        help="force the add of the segment to be read")
    parser.add_option("-s", "--size",
        dest="size", type=int,
        help="force the size of the segment to be read")

    parser.add_option("-v", "--verbose",
        action="store_true", dest="verbose",
        help="be verbose, hexdump data")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("output FILE not specified")

    hydra = usb.core.find(idVendor=0x0a67, idProduct=0x8e00)

    if not hydra:
        exit("Could not locate HydraSynth")

    reattach = bytearray(hydra[0].bNumInterfaces)
    if platform == "linux" or platform == "linux2":
        for configuration in hydra:
            for interface in configuration:
                ifnum = interface.bInterfaceNumber
                reattach[ifnum] = True
                if not hydra.is_kernel_driver_active(ifnum):
                    reattach[ifnum] = False
                    continue
                try:
                    #print "Detach %s: %s\n" % (hydra, ifnum)
                    hydra.detach_kernel_driver(ifnum)
                except (usb.core.USBError, ep):
                    pass

    hydra.set_configuration()
    cfg = hydra.get_active_configuration()

    if options.verbose:
        print(cfg)

    ifnum = cfg[(0,0)].bInterfaceNumber
    alternate_settting = usb.control.get_interface(hydra, ifnum)
    intf = usb.util.find_descriptor(cfg, bInterfaceNumber = ifnum,
            bAlternateSetting = alternate_settting)

    ep = usb.util.find_descriptor(intf,custom_match = \
            lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)

    rp = usb.util.find_descriptor(intf,custom_match = \
            lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN)

    if ep:
        print("Writing data to file:", args[0])
        outfile = open(args[0], "wb")
        if not outfile:
            print("Unable to open FILE for writing")

        init = 1
        seq = 0x0002
        add = options.add
        todo = 0x01600000       # default, changed later

        reset = 2
        while todo > 0:
            if reset > 0:
                #ep.write(b"\x01\x03\x03\x00\x00\x00\x00\x00\x86\x38\x62\x79\x65")
                ep.write(checksum(b"\x01\x03\x03\x00\x00\x00\x00\x00CSbye"))

                try:
                    data = rp.read(64)
                except (usb.core.USBError, ep):
                    pass

                #ep.write(b"\x02\x00\x05\x00\x01\x00\x00\x00\x2c\xb4\x68\x65\x6c\x6c\x6f")
                ep.write(checksum(b"\x02\x00\x05\x00\x01\x00\x00\x00CShello"))

                try:
                    data = rp.read(64)
                except (usb.core.USBError, ep):
                    pass

                if data and options.verbose:
                    print(bytes(data[10:]).decode("ascii"))

                if reset == 2:
                    # auto-magically determine segment size
                    if not options.size:
                        options.size = 0x01600000

                    todo = options.size

                reset = 0

                while todo > 0:
                    #ep.write(b"\x02\x06\x08\x00\x02\x00\x00\x00\xb6\xdd\x00\x00\x20\x40\xf6\x01\x00\x00")
                    ep.write(checksum(b"\x02\x06\x08\x00"+struct.pack("<l", seq)+b"CS" \
                            +struct.pack("<l", add)+struct.pack("<l", 502), init))

                    # trying to read 512 bytes through 64 byte port...
                    for i in range(8):
                        if i == 0 and options.verbose:
                            print("0x%8.8x : " % add, end='')

                        try:
                            data = rp.read(64)
                        except usb.core.USBTimeoutError:
                            if options.verbose:
                                print()
                            print("Timeout at 0x%8.8x -> Toggling 'init'" % add)
                            init = (init + 1) & 1
                            reset = 1
                            break
                        except (usb.core.USBError, ep):
                            pass

                        if data:
                            if options.verbose:
                                print(".", end="")

                            if i == 0:
                                # crop protocol from output
                                out = data[10:]
                            else:
                                out = data

                            if todo > 0:
                                if todo > len(out):
                                    outfile.write(out)
                                    todo -= len(out)
                                else:
                                    outfile.write(out[:todo])
                                    todo = 0

                    if reset == 0:
                        # update counters
                        seq += 1
                        add += 0x01f6
                        if options.verbose:
                            print("")
                    else:
                        break

        outfile.close()

        #ep.write(b"\x02\x03\x03\x00\x0b\x00\x00\x00\x82\x28\x62\x79\x65")
        ep.write(checksum(b"\x02\x03\x03\x00"+struct.pack("<l", seq)+b"CSbye"))

        try:
            data = rp.read(64)
        except (usb.core.USBError, ep):
            pass

        if data:
            if options.verbose:
                print(bytes(data[10:]).decode("ascii"))


    # Clean up, and re-attach endpoints if they were previous attached
    usb.util.dispose_resources(hydra)

    for configuration in hydra:
        for interface in configuration:
            ifnum = interface.bInterfaceNumber
            if (reattach[ifnum]):
                    hydra.attach_kernel_driver(ifnum)


if __name__ == "__main__":
    main()

