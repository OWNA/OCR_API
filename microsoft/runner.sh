classes=('photo' 'scan')
for class in "${classes[@]}"
do
for counter in {0..115}
do
./microsoft/process.py images/C/${class}-${counter}.jpg data/processed/C/${class}-${counter}-microsoft.json
done
done

classes=("A" "B" "C" "D" "E" "F")
for class in "${classes[@]}"
do
for counter in {1..75}
do
./microsoft/process.py images/B/${class}/${counter}${class}.jpg data/processed/B/${counter}${class}-microsoft.json
done
done
