#!/bin/bash

lock="image_uci.py"
#Start
start(){
	echo "service start..."
        su root -c "python /home/zjc/image_uci/image_uci.py &"
}

stop(){
	echo "service stop.."
	pkill -f $lock
}

status(){
	if [ -e $lock ];then
            echo "$0 service start"
        else
            echo "$0 service stop"
        fi
}

restart(){
	 stop
	 start
}

case "$1" in 
"start")
	start
	;;
"stop")
	stop
	;;
"status")
	status
	;;
"restart")
	restart
	;;
*)
	echo "$0 start|stop|status|restart|"
	;;
esac

