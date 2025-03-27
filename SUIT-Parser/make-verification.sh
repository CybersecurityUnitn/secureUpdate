#!/usr/bin/env sh
set -x
STOOL="./out/secure_update validate-manifest"
SRCS=`ls *.json.suit`

for SRC in $SRCS ; do
    rm -f time-$SRC.txt
    rm -f out-$SRC.txt

    # Parsing and verify the signature of the manifest
    echo "Parsing and signature verification time:" >> time-$SRC.txt 
    set +x
    echo "~~~" >> time-$SRC.txt
    #{ time -p $STOOL $SRC > out-$SRC.txt; } 2> time_output.txt
    { time -p sh -c "$STOOL $SRC > /dev/null 2> /dev/null"; } 2> time_output.txt
    {
        read -r real_time
        read -r user_time
        read -r sys_time
    } < time_output.txt
    echo "real ${real_time#* }s" >> time-$SRC.txt
    echo "user ${user_time#* }s" >> time-$SRC.txt
    echo "sys ${sys_time#* }s" >> time-$SRC.txt
    set -x
    echo "~~~" >> time-$SRC.txt

    # Execute memory measurement 
    # command time -v ./cli/cli --dry-run signed-example5.json.suit
    set +x
    echo "Parsing and signature verification memory usage:" >> time-$SRC.txt 
    echo "~~~" >> time-$SRC.txt
    #{ command time -v $STOOL $SRC > out-$SRC.txt; } 2>> time-$SRC.txt
    { command time -v sh -c "$STOOL $SRC > /dev/null 2> /dev/null"; } 2>> time-$SRC.txt
    set -x
    echo "~~~" >> time-$SRC.txt

done

# Clean up temporary file
rm -f time_output.txt