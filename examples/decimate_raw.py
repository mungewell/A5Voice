# script to process raw files

import numpy as np
import struct

def main():
    from optparse import OptionParser
    
    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)

    parser.add_option("-v", "--values",
        action="store_true", dest="values",
        help="print out the values of samples")
    parser.add_option("-d", "--decimate",
        dest="decimate", type=int, default=1,
        help="decimate the samples by a factor of DECIMATE")
    parser.add_option("-m", "--median",
        action="store_true", dest="median",
        help="use median, rather than mean")
    parser.add_option("-o", "--output", dest="outfile",
        help="rebuild/rewrite data to OUTFILE")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("FILE not specified")

    values = []
    infile = open(args[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        while True:
            data = infile.read(4)
            if (len(data)) == 0:
                break
            values.append(struct.unpack("<hh", data))
    infile.close()

    outfile = None
    if options.outfile:
        outfile = open(options.outfile, "wb")

    i = 0
    d = options.decimate
    v = []
    for value in values:
        i += 1
        d -= 1
        v.append(value)
        if d <= 0:
            a = np.array(v, dtype=int)
            if options.median:
                out = a.median(axis=0)
            else:
                out = a.mean(axis=0)

            if options.values:
                print(i, out)#, v)
            if outfile:
                outfile.write(struct.pack("<hh", int(out[0]), int(out[1])))

            d = options.decimate
            v = []

    if outfile:
        outfile.close()


if __name__ == "__main__":
    main()

