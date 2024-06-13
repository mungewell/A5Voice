# Inital test to see if the waveforms can be altered, by cloning the first Waveform "Sine"
# into the second position - overwriting the "Triangle".
#
# NOTE: All tests at user's own risk, we have not confirmed that anything done here is safe!

# unpack the first waveform
rm -r just_one
python3 A5Voice.py -W 1 -u just_one a5_voice_0x01600000.bin 

# rename them so samples are going to be packed as the second waveform...
md5sum just_one/*_0_*.raw
find just_one/ -name *.raw -exec bash -c 'mv {} `echo {} | sed -e "s/_0_/_1_/"`' \;

# pack into a new sound pack - all 220 waveforms
python3 A5Voice.py -o messed_with.bin -p just_one a5_voice_0x01600000.bin 

# unpack first and second waveforms to test
rm -r messed_with/
python3 A5Voice.py -W 2 -u messed_with messed_with.bin

# check...
md5sum messed_with/*_0_*.raw
md5sum messed_with/*_1_*.raw
