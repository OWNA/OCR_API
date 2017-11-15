classes=('photo' 'scan')
for class in "${classes[@]}"
do
for counter in {0..115}
do
./abbyy/run.py images/C/${class}-${counter}.jpg data/processed/C/${class}-${counter}-p1.txt -txt -p textExtraction
./abbyy/run.py images/C/${class}-${counter}.jpg data/processed/C/${class}-${counter}-p1.xml -xmlForCorrectedImage -p textExtraction
./abbyy/run.py images/C/${class}-${counter}.jpg data/processed/C/${class}-${counter}-p1-original.xml -xml -p textExtraction
done
done

classes=("A" "B" "C" "D" "E")
for class in "${classes[@]}"
do
for counter in {1..75}
do
./abbyy/run.py images/B/${class}/${counter}${class}.jpg data/processed/B/${counter}${class}-p1.txt -txt -p textExtraction
./abbyy/run.py images/B/${class}/${counter}${class}.jpg data/processed/B/${counter}${class}-p1.xml -xmlForCorrectedImage -p textExtraction
./abbyy/run.py images/B/${class}/${counter}${class}.jpg data/processed/B/${counter}${class}-p1-original.xml -xml -p textExtraction
done
done
