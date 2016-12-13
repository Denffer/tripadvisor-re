#!/bin/zsh
for i in data/corpora/*.txt
do 
    ts -n -f sh -c "python Glove.py -w 3 --min-count 5 $i" &
done
ts -S 15


