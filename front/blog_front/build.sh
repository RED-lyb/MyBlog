cd /webproject/my-blog/front/blog_front
npm run build
rm -rf /usr/share/nginx/html/dist/
cp -r /webproject/my-blog/front/blog_front/dist/ /usr/share/nginx/html/
