uwsgi --stop /webproject/my-blog/project-master.pid
echo "已关闭uwsgi，重启中"
sleep 2
uwsgi --ini /webproject/my-blog/back/depend_manage/uwsgi.ini 
echo "重启完成"
