mysql -uroot -p3n1th@rm0N -e "drop schema voyagesapi_old;"
mysql -uroot -p3n1th@rm0N -e "create database voyagesapi_old;"
mysql -uroot -p3n1th@rm0N voyagesapi_old < ../data/voyagesapi_old.sql

mysql -uroot -p3n1th@rm0N -e "drop schema voyagesapi_new;"
mysql -uroot -p3n1th@rm0N -e "create database voyagesapi_new;"
mysql -uroot -p3n1th@rm0N voyagesapi_new < ../data/voyagesapi_new.sql
