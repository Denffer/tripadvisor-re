#!/bin/zsh
for i in data/corpora/*.txt
do 
    ts -n -f sh -c "python Glove.py -w 5 $i" &
done
ts -S 10


