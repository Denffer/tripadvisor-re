#!/bin/zsh
for i in data/line/norm_vectors200/*.txt
do 
    ts -n -f sh -c "python LowerDimension.py $i" &
done
ts -S 10


