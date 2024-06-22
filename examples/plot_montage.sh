# Plot the raw samples into a 'montage.png'

for target in "$@"
do
	echo processing $target

	# check if target exist, if not make it and copy raw files into it
	if [ ! -d $target ]; then
		mkdir $target
		cp *_"$target"_*.raw $target
	fi

	cd $target

	# convert to PNG image
	find . -name "*.raw" -exec bash -c "sox -r 48k -e signed -b 16 -c 2 --endian little {} {}.wav" \;
  	find . -name "*.raw.wav" -exec bash -c "sndfile-waveform -g 640x100 --no-rms -B 0xFFFFFFFF {} {}.png" \;
	
	# render title
	convert  -size 640x50 xc:none -box white -pointsize 20 -gravity west -draw "text 0,0 '$target:'" -font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf montage_"$target".png

	export pics=`ls *.raw.wav.png | sort -t '_'  -k3,3n | xargs echo`
	echo $pics
	export count=`echo $pics|wc -w`
	export tile=1x`echo $(($count + 1))`
	echo $tile

	# build montage
	montage -geometry 660x -tile $tile montage_"$target".png $pics montage_"$target".png 

	cd ..
done
