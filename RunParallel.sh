#!/bin/zsh
for i in data/reviews/*.json
do 
    ts -n -f sh -c "python ReviewProcess.py $i" &
done
ts -S 15

