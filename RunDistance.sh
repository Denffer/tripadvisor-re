#!/bin/zsh
for i in data/line/vectors200/New_York_City.txt 
do
    for j in $(seq 0.0 0.1 1)
    do 
        python Distance.py $i $j
        #ts -n -f sh -c "python Distance.py $i $j" &
    done
done
#ts -S 10


