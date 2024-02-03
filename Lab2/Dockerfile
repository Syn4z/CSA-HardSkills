FROM php:apache
# install the PHP extensions we need
RUN apt-get update && apt-get upgrade -y && apt-get install -y libpng-dev libjpeg-dev && rm -rf /var/lib/apt/lists/* \
 && docker-php-ext-configure gd --with-jpeg=/usr \
 && docker-php-ext-install gd mysqli opcache
# set recommended PHP.ini settings
# see https://secure.php.net/manual/en/opcache.installation.php
RUN { \
  echo 'opcache.memory_consumption=128'; \
  echo 'opcache.interned_strings_buffer=8'; \
  echo 'opcache.max_accelerated_files=4000'; \
  echo 'opcache.revalidate_freq=2'; \
  echo 'opcache.fast_shutdown=1'; \
  echo 'opcache.enable_cli=1'; \
    } > /usr/local/etc/php/conf.d/opcache-recommended.ini
RUN a2enmod rewrite expires
CMD /usr/sbin/apache2ctl -D FOREGROUND