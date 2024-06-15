# A5Voice
HydraSynth util to replace/alter the Waveforms in the 'A5Voice' segment.

*Note*: ASM does not endorse this project. The project does not disassemble proprietary code, or share copyrighted materials. Reversed engineered information may be risky to your device/keyboard - no warranties on broken equipment.

## Usage:
The `A5Voice.py` script can `--unpack` existing waveforms and `--pack` new ones from/to the data in the 'A5Voice' segment of memory on the device.

Process with be updated as we find out more, but is basically:

- Use ASM dev tool to retrieve 'A5Voice' segment from keyboard
- Use our Python script to '--unpack/--pack' waveforms as needed
- Use ASM dev tool to pack into a '.dat' file
- Use normal ASM updater to load to keyboard

At present this has only been tested on the HydraSynth Explorer, although the other keyboards may use the same schema/data structures.

Example video of using the results on an Explorer:
https://youtu.be/WxSYWyxl-5s

Check the 'examples' directory for a few examples showing how to generate/process your '.wav' files into the required format.
