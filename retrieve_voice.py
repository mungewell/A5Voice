

# modified implementation of 'TCP' checksum

def checksum(msg):
    l = len(msg)
    out = bytearray(msg)

    # preset checksum
    out[8] = 0x00
    out[9] = 0x01

    s = 0
    if l & 1:
        out += b"\x00"

    for i in range(0,l,2):
        s = s +((out[i]<<8)+(out[i+1]))
    s = s + (s >>16)

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
        #ep.write(b"\x01\x03\x03\x00\x00\x00\x00\x00\x86\x38\x62\x79\x65")
        ep.write(checksum(b"\x01\x03\x03\x00\x00\x00\x00\x00CSbye"))

        try:
            data = rp.read(64)
        except (usb.core.USBError, ep):
            pass

        # hello
        #ep.write(b"\x02\x00\x05\x00\x01\x00\x00\x00\x2c\xb4\x68\x65\x6c\x6c\x6f")
        ep.write(checksum(b"\x02\x00\x05\x00\x01\x00\x00\x00CShello"))

        try:
            data = rp.read(64)
        except (usb.core.USBError, ep):
            pass

        if data:
            if options.verbose:
                print(bytes(data[10:]).decode("ascii"))

            # auto-magically determine segment size
            if not options.size:
                #options.size = 0x01600000
                print("Forcing short read as Checksum() needs fixing...")
                options.size = 1506

            print("Writing data to file:", args[0])
            outfile = open(args[0], "wb")
            if not outfile:
                print("Unable to open FILE for writing")
            else:
                seq = 2
                add = 0x40200000
                todo = options.size

                while todo > 0:
                    #ep.write(b"\x02\x06\x08\x00\x02\x00\x00\x00\xb6\xdd\x00\x00\x20\x40\xf6\x01\x00\x00")
                    ep.write(checksum(b"\x02\x06\x08\x00"+struct.pack("<l", seq)+b"CS" \
                            +struct.pack("<l", add)+struct.pack("<l", 502)))

                    # trying to read 512 bytes through 64 byte port...
                    for i in range(8):
                        try:
                            data = rp.read(64)
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
    
                    # update counters
                    add += 502
                    seq += 1

                    if options.verbose:
                        print("")

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

