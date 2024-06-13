# Messing around with waveforms from:
# https://www.adventurekid.se/akrt/waveforms/adventure-kid-waveforms/individual-folder-downloads-of-the-akwf-pack/

# $ soxi AKWF_symetric_0001.wav
#
# Input File     : 'AKWF_symetric_0001.wav'
# Channels       : 1
# Sample Rate    : 44100
# Precision      : 16-bit
# Duration       : 00:00:00.01 = 600 samples = 1.02041 CDDA sectors
# File Size      : 1.34k
# Bit Rate       : 790k
# Sample Encoding: 16-bit Signed Integer PCM

# replace waveforms/samples from location 218 down...
# within the 'factory' pack 218 is the highest with data, 219 is blank
export waveform=218

export soxp="-r 48k -e signed -b 16 -c 2 --endian little"

for target in "$@"
do
	echo processing $target to $waveform

	# convert to raw and reduce gain by 3dB
	sox $target $soxp $target".raw" gain -3

	# double up into two consequetive waveforms
	# (believe ASM does to allow/alter phase angle)
	cat $target".raw" $target".raw" > temp.raw

	# build 16k, 8k, 4k 'masters' with correct number of samples
	sox $soxp temp.raw $target"_8k.raw" rate 75271.056661562
	sox $soxp temp.raw $target"_4k.raw" rate 37635.528330781
	sox $soxp temp.raw $target"_16k.raw" rate 150542.113323124

	# create parts for each waveform
	# these should be filtered, but we don't yet know how.
	sox $soxp $target"_16k.raw" $target"_"$waveform"_0.raw"
	sox $soxp $target"_16k.raw" $target"_"$waveform"_1.raw"
	sox $soxp $target"_8k.raw"  $target"_"$waveform"_2.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_3.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_4.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_5.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_6.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_7.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_8.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_9.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_10.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_11.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_12.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_13.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_14.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_15.raw"
	sox $soxp $target"_4k.raw"  $target"_"$waveform"_16.raw"

	waveform=$((waveform-1))

	# exit if too many waveforms
	if [ $waveform == 0 ] ; then
		exit
	fi
done
