#!/usr/bin/env sh
set -e
#set -x
STOOL="suit-tool"
SRCS=`ls *.json`
for SRC in $SRCS ; do
    $STOOL create -i $SRC -o $SRC.suit
    $STOOL sign -m $SRC.suit -k keys/private_key.pem -o signed-$SRC.suit
    # $STOOL parse -m signed-$SRC.suit > signed-$SRC.txt
    # rm -f $SRC.txt

    # echo "$SRC" | sed -e "s/example\([0-9]*\).json/## Example \1:/" > $SRC.txt
    # echo "" >> $SRC.txt
    # echo "~~~" >> $SRC.txt
    # cat signed-$SRC.txt >> $SRC.txt
    # echo "~~~" >> $SRC.txt
    # echo "" >> $SRC.txt

#    if python3 -c 'import json, sys; sys.exit(0 if json.load(open(sys.argv[1])).get("severable") else 1)' $SRC ; then
#        $STOOL sever -a -m $SRC.suit -o severed-$SRC.suit
#        echo "Total size of the Envelope without COSE authentication object or Severable Elements: " `stat -c "%s" severed-$SRC.suit` >> $SRC.txt
#        echo "" >> $SRC.txt
#        echo "Envelope:">> $SRC.txt
#        echo "" >> $SRC.txt
#        echo "~~~" >> $SRC.txt
#        xxd -ps severed-$SRC.suit >> $SRC.txt
#        echo "~~~" >> $SRC.txt

#        $STOOL sever -a -m signed-$SRC.suit -o signed-severed-$SRC.suit
#        echo "Total size of the Envelope with COSE authentication object but without Severable Elements: " `stat -c "%s" signed-severed-$SRC.suit` >> $SRC.txt
#        echo "" >> $SRC.txt
#        echo "Envelope:">> $SRC.txt
#        echo "" >> $SRC.txt
#        echo "~~~" >> $SRC.txt
#        xxd -ps signed-severed-$SRC.suit >> $SRC.txt
#        echo "~~~" >> $SRC.txt


#    else
        echo "Total size of Envelope without COSE authentication object: " `stat -c "%s" $SRC.suit`
#        echo "" >> $SRC.txt
#        echo "Envelope:">> $SRC.txt
#        echo "" >> $SRC.txt
#        echo "~~~" >> $SRC.txt
#        xxd -ps $SRC.suit>> $SRC.txt
#        echo "~~~" >> $SRC.txt

#    fi
#    echo "" >> $SRC.txt
    echo "Total size of Envelope with COSE authentication object: " `stat -c "%s" signed-$SRC.suit`
#    echo "" >> $SRC.txt
#    echo "Envelope with COSE authentication object:">> $SRC.txt
#    echo "" >> $SRC.txt
#    echo "~~~" >> $SRC.txt
#    xxd -ps signed-$SRC.suit>> $SRC.txt
#    echo "~~~" >> $SRC.txt
#    echo "" >> $SRC.txt
done
