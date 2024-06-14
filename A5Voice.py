#!/usr/bin/python
# 
# Script to decode the 'A5Voice' segment/packs from ASM Hydrasynth
# (c) Simon Wood, June 12, 2024 (MIT License)
#
# Reversed engineered with segment data from the Explorer FW v2.0
#
# $ md5sum a5_voice_0x01600000.bin
# 91fbb6eeca196476fe6d3a37a2668665  a5_voice_0x01600000.bin
#
# Unpacked (raw) samples can be converted to WAV
# find . -name "*.raw" -exec bash -c "sox -r 48k -e signed -b 16 -c 2 --endian little {} {}.wav" \;

# Requires:
# https://github.com/construct/construct

from construct import *

#---------------------------------------------
# Head of the A5Voice segment
HEAD = Struct(                                          # at location 0x00000000
        Const(b"\xc2\x02\x00\x00\x70\x56\x34\x12"),
        "add1_0_0" / Int32ul,
        "waveform_count" / Int32ul,

        Const(b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        Const(b"\x00\x00\x00\x00\x00\x00\x00\x00"),
)

# No idea what these are, they just count up...
COUNT = Struct(                                         # at location 0x00000020
        "count1" / Int32ul,
        Check(this.count1 != 0x88888888),
)

MAP = Struct(
        "map1" / Int32ul,
        "map2" / Int32ul,
        Check(this.map1 != 0x88888888),
)

COUNTING = Struct(                                      # at location 0x00000020
        "count" / GreedyRange(COUNT),
        Const(b"\x88\x88\x88\x88"),                     # const, or padding to address?
        "map" / GreedyRange(MAP),
)

# Crude decoding of waveform table                      # at location 0x00000b08
WAVE = Struct(
        Const(b"\x14\x8d\x00\x00\x00\x00\x00\x00"),

        "add1" / Int32ul,
        "add2" / Int32ul,
        "end" / Int32ul,

        "size" / Computed(this.end - this.add1),        # Size for each is 16K first, 16K, 8K, 4K.... 4K last
        "sample" / Pointer(this.add1, Struct(
                "data" / Bytes(this._.size),
                "uns" / Int32ul,
        )),

        Const(b"\x00\x00\xff\x7f\x80\x64\x00\x00"),
        Const(b"\x00\x64\x00\x00"),
        "wv0" / Byte, Const(b"\x7f"),                   # first in group = 129, then +1 from prev wv1
        "wv1" / Byte, Const(b"\x7f"),                   # wv1 = wv0 + 4~8, making last in group = 255
        Const(b"\x81\x7f\xff\x80\x3c\x00\x80\x00"),
        Const(b"\x00\x7f\x00\x00\x3c\x40\x2c\x00"),

        "wv2" / Int32ul,                                # low pass filter freq??
                                                        # 15616 14848 14080 13312 12544 11776 11008 10240
                                                        # 9472 8704 7936 7168 6400 5632 4864 4096 3328

        Const(b"\x20\x00\x00\x00"),
        Const(b"\xff\x7f\x00\x00\x3c\x00\x00\x00"),
        Const(b"\x00\x00\x7f\x00\x1e\x00\x00\x7f"),
        Const(b"\x00\x1f\x3c\x00\x7f\x80\x7f\x80"),
        Const(b"\x7f\x7f\x7f\x7f\x00\x7f\x00\x00"),
        Const(b"\x20\x1e\x00\x00\x00\x7f\x7f\x7f"),

        Check(this.add1 == this.add2),
)

WAVEFORM = Struct(
        "index" / Computed (this._index),
        Const(b"\x00\x00\x08\x7f"), "un0" / Int32ul,    # the values in these increase by 25 each time
        Const(b"\x08\x00\x10\x7f"), "un1" / Int32ul,    # ie un1 = un0 + 25
        Const(b"\x10\x00\x18\x7f"), "un2" / Int32ul,
        Const(b"\x18\x00\x20\x7f"), "un3" / Int32ul,
        Const(b"\x20\x00\x28\x7f"), "un4" / Int32ul,
        Const(b"\x28\x00\x30\x7f"), "un5" / Int32ul,
        Const(b"\x30\x00\x37\x7f"), "un6" / Int32ul,
        Const(b"\x37\x00\x3e\x7f"), "un7" / Int32ul,
        Const(b"\x3e\x00\x47\x7f"), "un8" / Int32ul,
        Const(b"\x47\x00\x4f\x7f"), "un9" / Int32ul,
        Const(b"\x4f\x00\x57\x7f"), "una" / Int32ul,
        Const(b"\x57\x00\x5e\x7f"), "unb" / Int32ul,
        Const(b"\x5e\x00\x65\x7f"), "unc" / Int32ul,
        Const(b"\x65\x00\x6c\x7f"), "und" / Int32ul,
        Const(b"\x6c\x00\x73\x7f"), "une" / Int32ul,
        Const(b"\x73\x00\x78\x7f"), "unf" / Int32ul,
        Const(b"\x78\x00\xff\x7f"), "ung" / Int32ul,

        "waves" / GreedyRange(WAVE),                    # or should we use 'Array(17, WAVE)'?

        Check(len_(this.waves) == 17),

        #IfThenElse(this.index == 0,
        #    Check(this.un0 == 740),
        #    Check(this.un0 == this._.waveforms[this.index-1].ung + 59)),
        Check(this.un1 == this.un0 + 25),
        Check(this.un2 == this.un1 + 25),
        Check(this.un3 == this.un2 + 25),
        Check(this.un4 == this.un3 + 25),
        Check(this.un5 == this.un4 + 25),
        Check(this.un6 == this.un5 + 25),
        Check(this.un7 == this.un6 + 25),
        Check(this.un8 == this.un7 + 25),
        Check(this.un9 == this.un8 + 25),
        Check(this.una == this.un9 + 25),
        Check(this.unb == this.una + 25),
        Check(this.unc == this.unb + 25),
        Check(this.und == this.unc + 25),
        Check(this.une == this.und + 25),
        Check(this.unf == this.une + 25),
        Check(this.ung == this.unf + 25),
)

WAVETABLE = Struct(
        "waveforms" / GreedyRange(WAVEFORM),            # or should we use 'this._.waveform_count'?

        Check(len_(this.waveforms) == this._.header.waveform_count)
)

FOOT = Struct(                                          # at location 0x015ffffc
        "add2_0_0" / Int32ul,

        Check(this._.header.add1_0_0 == this.add2_0_0),
)

# Everything bundled together
A5VOICE = Struct(
        "header" / HEAD,
        "counting" / Padded(0x00000b08 - 0x00000020, COUNTING, pattern=b"\x88"),
        "wavetable" / WAVETABLE,
        "footer" /  Pointer(0x015ffffc, FOOT)
)

A5VOICE_DAT = Struct(
        Const(b"A5Pack\x00"),
        "type" / Enum(Bytes(2),
                keyboard    = b"KB",
                desktop     = b"DR",
                explorer    = b"3M",
                delux       = b"7X",
        ),

        Const(b"\x00\x00"),
        Padded(80, Const(b"All Rights Reserved")),
        "name" / PaddedString(20, "ascii"),

        Padded(22, Const(b"A5 voice")),
        Const(b"\x60\x01"),
)

#---------------------------------------------

import os
import sys
import fnmatch

def main():
    from optparse import OptionParser
    
    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)

    parser.add_option("-d", "--dump",
        action="store_true", dest="dump",
        help="dump configuration to text")
    parser.add_option("-D", "--dumpafter",
        action="store_true", dest="dumpafter",
        help="dump configuration to text after any processing")

    parser.add_option("-W", "--waveforms",
        dest="waveforms", type=int,
        help="limit the number of waveforms to WAVEFORMS")

    parser.add_option("-u", "--unpack",
        dest="unpack",
        help="unpack raw samples to UNPACK directory")
    parser.add_option("-p", "--pack",
        dest="pack",
        help="pack PACK directory of raw samples (overwrites contents)")

    parser.add_option("-o", "--output", dest="outfile",
        help="rebuild/rewrite data to OUTFILE")

    parser.add_option("--dat",
        action="store_true", dest="dat",
        help="output in 'dat' format ready to uploaded to synth")
    parser.add_option("-n", "--name",
        dest="name", default="Hack-The-Planet!",
        help="name/version for the 'dat' pack")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("FILE not specified")

    print("Parsing '%s'" % args[0])
    infile = open(args[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if data:
        try:
            a5voice_dat = A5VOICE_DAT.parse(data)
        except:
            a5voice_dat = None

        if a5voice_dat:
            a5voice = A5VOICE.parse(data[0x87:])
        else:
            a5voice = A5VOICE.parse(data)

        if options.dump:
            print(a5voice)

        if options.waveforms:
            if options.waveforms < a5voice['header']['waveform_count']:
                print("Setting number of waveforms: %d" % options.waveforms)
                a5voice['header']['waveform_count'] = options.waveforms
                
                a5voice['wavetable']['waveforms'] = \
                    ListContainer(a5voice['wavetable']['waveforms'][0: options.waveforms])

        if options.unpack:
            path = os.path.join(os.getcwd(), options.unpack)
            if os.path.exists(path):
                sys.exit("Directory %s already exists" % path)

            os.mkdir(path)
            g = 0
            for waveform in a5voice['wavetable']['waveforms']:
                i = 0
                for wave in waveform['waves']:
                    name = "0x%8.8x_%d_%d.raw" % (wave['add1'], g, i)
                    print("Unpack: %s (0x%4.4x)" % (name, wave['sample']['uns']))

                    f = open(os.path.join(path, name), "wb")
                    f.write(wave['sample']['data'])
                    f.close()

                    i += 1
                g += 1

        if options.pack:
            path = os.path.join(os.getcwd(), options.pack)
            files = os.listdir(path)
            add = a5voice['header']['add1_0_0']

            g = 0
            for waveform in a5voice['wavetable']['waveforms']:
                for i in range(17):
                    if i < 2:
                        s = 16384
                    elif i < 3:
                        s = 8192
                    else:
                        s = 4096

                    waveform['waves'][i]['add1'] = add
                    waveform['waves'][i]['add2'] = add
                    waveform['waves'][i]['end'] = add + s

                    for name in os.listdir(path):
                        # Only update samples which match schema *_0_[0..17].raw
                        if fnmatch.fnmatch(name, "*_%d_%d.raw" % (g, i)):
                            print("Pack: %s to 0x%8.8x" % (name, add))
                            f = open(os.path.join(path, name), "rb")

                            # store raw sample for writing later
                            if f:
                                waveform['waves'][i]['sample']['data'] = f.read(s)
                                waveform['waves'][i]['sample']['uns'] = 0x0000
                                f.close()
                            break

                    # extra space between samples
                    add += s + 32
                g += 1

        if options.outfile:
            data = A5VOICE.build(a5voice)

            if len(data) > 0x01600000:
                sys.exit("Data too large for writing")

            print("Writing data to file:", options.outfile)
            outfile = open(options.outfile, "wb")
            if not outfile:
                sys.exit("Unable to open FILE for writing")

            if options.dat:
                outfile.write(A5VOICE_DAT.build({
                    "type":"explorer",
                    "name":options.name,
                }))

            outfile.write(data)
            outfile.close()

        if options.dumpafter:
            print(a5voice)


if __name__ == "__main__":
    main()

