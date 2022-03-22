#!/bin/bash

. ${HOME}/.bashrc

#host=$USER
host="$(hostname -s)"
ip=$(grep "^$host IP " /usr/global/bin/regress.params | awk '{print $3}')
echo "name: $host"

#ip=${HTTP_IP}

cd ~/ws/gash/regressstatus
if [ ! -h /$host/status ]
then
    ln -s ~/ws/gash/regressstatus /$host/status
fi
if [ -h ~/ws/gash/regressstatus/regressstatus ]
then
    rm -vf ~/ws/gash/regressstatus/regressstatus
fi
chmod 755 *.*
chmod 777 cgi_scripts/pause
chmod 755 cgi_scripts/*.cgi
chmod 777 tree_nodes.js
chmod 777 tree_nodes2.js
chmod 777 tree_format2.js
chmod 777 latest
chmod 777 left.html

cp images/favicon.ico /$host/results/
chmod 777 /$host/results/index.html
echo \<meta http-equiv=\"refresh\" content=\"0 \; url=http://$ip/status/result.php\"\> > /$host/results/index.html      
cp jobs_index.php /$host/jobs/

rm index.html
cd -
