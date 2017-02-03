#!/bin/zsh
for i in data/line/norm_vectors200/*.txt 
do
    python Methodology.py $i 0
    #for j in $(seq -0.5 0.25 0.5)
    #do 
        #python Methodology.py $i $j
        #ts -n -f sh -c "python Methodology.py $i $j" &
    #done
done
#ts -S 10


