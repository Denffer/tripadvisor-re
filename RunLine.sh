
dir1="./data/line/vectors200/"
dir2="./data/line/norm_vectors200/"

if [ ! -d "$dir1" ]
then
    echo "Creating directory:\033[1m" $dir1 "\033[0m"
    mkdir $dir1
fi

if [ ! -d "$dir2" ]
then
    echo "Creating directory:\033[1m" $dir2 "\033[0m"
    mkdir $dir2
fi
    
for i in data/line/cooccur/Istanbul.txt
do
    echo "Running Line (first-order) on:\033[1m" $i "\033[0m"
    filename=$(echo $i | cut -d'/' -f 4)
    echo $filename
    #./Line/line -train $i -output data/line/vectors200/$filename -size 200 -order 1 -negative 30 -samples 300 -threads 5
    ./Line/normalize -input data/line/vectors200/$filename -output data/line/norm_vectors200/$filename -binary 0
    echo "-------------------------------------------"
done    

