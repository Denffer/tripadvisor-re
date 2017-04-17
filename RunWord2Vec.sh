#!/bin/zsh
for i in data/corpora/*.txt
do 
    ts -n -f sh -c "python Word2Vec.py $i" &
done
ts -S 5


