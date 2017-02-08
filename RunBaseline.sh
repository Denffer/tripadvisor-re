#!/bin/zsh
for i in data/line/norm_vectors200/*.txt
do 
    python Baseline.py $i
    #ts -n -f sh -c "python Baseline.py $i" &
done
#ts -S 15


