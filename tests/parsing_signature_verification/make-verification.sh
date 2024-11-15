#!/usr/bin/env sh
set -x
STOOL="python3 ../bin/suit-tool"
SRCS=`ls *.json`
rm -f examples.txt
for SRC in $SRCS ; do
    rm -f $SRC.txt

    # Parsing the signed manifest
    echo "Parsing time:" >> $SRC.txt 
    set +x
    echo "~~~" >> $SRC.txt
    { time -p $STOOL parse -m signed-$SRC.suit > signed-$SRC.txt; } 2> time_output.txt
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
    echo "Parsing output:" >> $SRC.txt
    echo "~~~" >> $SRC.txt
    cat signed-$SRC.txt >> $SRC.txt
    echo "~~~" >> $SRC.txt
    echo "" >> $SRC.txt

    # Verifying the signed manifest
    echo "~~~" >> $SRC.txt
    set +x
    echo "Verifying time:" >> $SRC.txt
    { time -p $STOOL verify -m $SRC.suit -s signed-$SRC.suit -k ../public_key.pem > verified-$SRC.txt; } 2> time_output.txt
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
    echo "Verifying output:" >> $SRC.txt
    echo "~~~" >> $SRC.txt
    cat verified-$SRC.txt >> $SRC.txt
    echo "~~~" >> $SRC.txt
    echo "" >> $SRC.txt

    if python3 -c 'import json, sys; sys.exit(0 if json.load(open(sys.argv[1])).get("severable") else 1)' $SRC ; then
        $STOOL sever -a -m $SRC.suit -o severed-$SRC.suit
        echo "Total size of the Envelope without COSE authentication object or Severable Elements: " `stat -f "%z" severed-$SRC.suit` >> $SRC.txt
        echo "" >> $SRC.txt
        echo "Envelope:" >> $SRC.txt
        echo "" >> $SRC.txt
        echo "~~~" >> $SRC.txt
        xxd -ps severed-$SRC.suit >> $SRC.txt
        echo "~~~" >> $SRC.txt

        $STOOL sever -a -m signed-$SRC.suit -o signed-severed-$SRC.suit
        echo "Total size of the Envelope with COSE authentication object but without Severable Elements: " `stat -f "%z" signed-severed-$SRC.suit` >> $SRC.txt
        echo "" >> $SRC.txt
        echo "Envelope:" >> $SRC.txt
        echo "" >> $SRC.txt
        echo "~~~" >> $SRC.txt
        xxd -ps signed-severed-$SRC.suit >> $SRC.txt
        echo "~~~" >> $SRC.txt
    else
        echo "Total size of Envelope without COSE authentication object: " `stat -f "%z" $SRC.suit` >> $SRC.txt
        echo "" >> $SRC.txt
        echo "Envelope:" >> $SRC.txt
        echo "" >> $SRC.txt
        echo "~~~" >> $SRC.txt
        xxd -ps $SRC.suit >> $SRC.txt
        echo "~~~" >> $SRC.txt
    fi
    echo "" >> $SRC.txt
    echo "Total size of Envelope with COSE authentication object: " `stat -f "%z" signed-$SRC.suit` >> $SRC.txt
    echo "" >> $SRC.txt
    echo "Envelope with COSE authentication object:" >> $SRC.txt
    echo "" >> $SRC.txt
    echo "~~~" >> $SRC.txt
    xxd -ps signed-$SRC.suit >> $SRC.txt
    echo "~~~" >> $SRC.txt
    echo "" >> $SRC.txt
    cat $SRC.txt >> examples.txt
done

# Clean up temporary file
rm -f time_output.txt