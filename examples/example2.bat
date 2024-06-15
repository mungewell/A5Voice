echo off

REM Messing around with waveforms from:
REM https://www.adventurekid.se/akrt/waveforms/adventure-kid-waveforms/individual-folder-downloads-of-the-akwf-pack/

REM $ soxi AKWF_symetric_0001.wav
REM
REM Input File     : 'AKWF_symetric_0001.wav'
REM Channels       : 1
REM Sample Rate    : 44100
REM Precision      : 16-bit
REM Duration       : 00:00:00.01 = 600 samples = 1.02041 CDDA sectors
REM File Size      : 1.34k
REM Bit Rate       : 790k
REM Sample Encoding: 16-bit Signed Integer PCM

REM replace waveforms/samples from location 218 down...
REM within the 'factory' pack 218 is the highest with data, 219 is blank
set waveform=218

REM http://sox.sourceforge.net/
set sox="C:\Program Files (x86)\sox-14-4-2\sox.exe"
set soxp=-r 48k -e signed -b 16 -c 2 --endian little

if "%1"=="" goto end
:loop
	set target=%1

	REM export samples=`soxi -s %target%`
	%sox% --i -s %target% > temp.txt
	set /p samples=<temp.txt

	echo "processing %target% (%samples%) to %waveform%"

	REM convert to raw and reduce gain by 3dB
	%sox% %target% -r 44100 -e signed -b 16 -c 1 %target%.raw gain -3

	REM double up into two consequetive waveforms
	REM (believe ASM does to allow/alter phase angle)
	cat %target%.raw %target%.raw > temp.raw

	REM build 16k, 8k, 4k 'masters' with correct number of samples
	REM export rate=`echo "" | awk "{print (48000 * (4096 / $samples))}"`
	set /a rate= (48000 * 4096) / %samples%
	set /a rate2=%rate% / 2
	set /a rate4=%rate% / 4

	%sox% %soxp% temp.raw %target%_16k.raw rate %rate%
	%sox% %soxp% temp.raw %target%_8k.raw rate %rate2%
	%sox% %soxp% temp.raw %target%_4k.raw rate %rate4%

	REM create parts for each waveform
	REM these should be filtered, but we don't yet know how.
	%sox% %soxp% %target%_16k.raw %target%_%waveform%_0.raw
	%sox% %soxp% %target%_16k.raw %target%_%waveform%_1.raw
	%sox% %soxp% %target%_8k.raw  %target%_%waveform%_2.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_3.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_4.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_5.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_6.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_7.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_8.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_9.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_10.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_11.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_12.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_13.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_14.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_15.raw
	%sox% %soxp% %target%_4k.raw  %target%_%waveform%_16.raw

	set /a waveform=%waveform% - 1

	REM exit if too many waveforms
	if %waveform%==0 goto end

shift
if not "%~1"=="" goto loop

:end
del temp.*
