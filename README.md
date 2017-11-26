# ruthgrace.github.io

I got the website template from [Start Bootstrap](http://startbootstrap.com/) - [Freelancer](http://startbootstrap.com/template-overviews/freelancer/)

## Install instructions:

```
node install
```

To compile, run

```
gulp
```

Note that the CSS is done with Less, so edit the files in the less folder (instead of trying to change the CSS directly), and don't forget to recompile.

## Production setup

Symlink the nginx config to /etc/nginx/sites-available and /etc/nginx/sites-enabled, and symlink the sysctl .service config to /etc/systemd/system/. Make sure that the www-data user is in the right groups to be able to make the socket file in the directory pulled from git. Make sure that /var/log/ruthgracewong is accessible by the www-data user.

If everything looks like its working fine when you run it manually but doesn't work under sysctl, you can try running it as the www-data user:

```
sudo -u www-data python wsgi.py
```

## Maintenance

To renew your SSL cert:

```
certbot certonly --force-renewal -a webroot -w /var/www/ruthgrace -d www.ruthgracewong.com -w /var/www/ruthgrace -d ruthgracewong.com
```
