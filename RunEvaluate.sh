#!/bin/zsh
for i in data/ranking/*
do 
    python Evaluate.py $i
    #ts -n -f sh -c "python Evaluate.py $i" &
done
#ts -S 15


