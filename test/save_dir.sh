#/bin/bash
now=$(date +"%m-%d-%Y")               
ls -halt /data/logs >> log_dir_list_$now.txt
