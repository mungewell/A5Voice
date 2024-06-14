# render a sine

export soxp="-r 48k -e signed -b 16 -c 2 --endian little"

export target=sine
export waveform=1

# create waveform using parameters to get 2 waves, 4096 samples
sox -V -r 4096 -n -b 32 -c 1 sine.wav synth 1 sin 2 vol -6.53dB
sox sine.wav -r 4096 -e signed -b 16 -c 2 --endian little $target"_16k.raw"

# build 8k and 4k 'masters'
#sox $soxp $target"_16k.raw" -r 24k $target"_8k.raw"
#sox $soxp $target"_16k.raw" -r 12k $target"_4k.raw"
python3 ../decimate_raw.py -d 2 $target"_16k.raw" -o $target"_8k.raw"
python3 ../decimate_raw.py -d 4 $target"_16k.raw" -o $target"_4k.raw"

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

