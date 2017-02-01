#!/bin/zsh
dir1="data/line/vectors2/"

if [ ! -d "$dir1" ]
then
    echo "Creating directory:\033[1m" $dir1 "\033[0m"
    mkdir $dir1
fi

for i in data/line/norm_vectors200/*.txt
do
	ts -n -f sh -c "python LowerDimension.py $i" & 
done
ts -S 8


