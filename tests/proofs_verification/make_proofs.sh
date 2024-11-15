#!/usr/bin/env sh
set -x
STOOL="./ethos_check.sh"
SRCS=`ls *.cpc`
rm -f proofs.txt
for SRC in $SRCS ; do
    rm -f $SRC.txt

    # Parsing the signed manifest
    echo "Verification time:" >> $SRC.txt
    set +x
    echo "~~~" >> $SRC.txt
    { time -p $STOOL $SRC; } 2> time_output.txt
    {
        read -r real_time
        read -r user_time
        read -r sys_time
    } < time_output.txt
    echo "real ${real_time#* }s" >> $SRC.txt
    echo "user ${user_time#* }s" >> $SRC.txt
    echo "sys ${sys_time#* }s" >> $SRC.txt
    set -x
    echo "~~~" >> $SRC.txt
    echo "" >> $SRC.txt 

    cat $SRC.txt >> proofs.txt
done

# Clean up temporary file
rm -f time_output.txt