#!/bin/zsh
for i in data/line/vectors200/Bangkok.txt 
do
    for j in $(seq 1 10)
    do 
        ts -n -f sh -c "python Distance.py $i $j" &
    done
done
ts -S 10


