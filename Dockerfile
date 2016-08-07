FROM grahamdumpleton/mod-wsgi-docker:python-3.4-onbuild

# setup a log directory for our application user
RUN mkdir /var/log/warn
RUN chown -R www-data:www-data /var/log/warn
RUN chmod -R 7777 /var/log/warn

CMD [ "warn.wsgi" ]