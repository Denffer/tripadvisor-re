#!/bin/zsh
for i in data/reranked_reviews/*.json
do 
    python ReviewProcess.py $i
    #ts -n -f sh -c "python ReviewProcess.py $i" &
done
#ts -S 15

