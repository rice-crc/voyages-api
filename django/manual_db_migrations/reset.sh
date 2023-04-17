mysql -uroot -pPASSWORD -e "drop schema voyagesapi_old;"
mysql -uroot -pPASSWORD -e "create database voyagesapi_old;"
mysql -uroot -pPASSWORD voyagesapi_old < ../data/voyagesapi_old.sql

mysql -uroot -pPASSWORD -e "drop schema voyagesapi_new;"
mysql -uroot -pPASSWORD -e "create database voyagesapi_new;"
mysql -uroot -pPASSWORD voyagesapi_new < ../data/voyagesapi_new.sql
