# Exercise 6: Put the Honeypot in a Separate Bridge Network

## Create a Docker Network

Creating a dedicated network for our honeypot helps us avoid the need to update the IP of the database server each time it changes.

Parameters:
  - [Subnet for network](https://docs.docker.com/engine/reference/commandline/network_create/): 172.26.160.1/16
  - IP Range: 172.26.161.1/24. The difference between IP Range and Subnet is that an IP range is a set of IP addresses that can be used by devices on a network, while a subnet is a smaller network within a larger network.
  - Gateway: 172.26.161.2. The gateway is basically protocol converter, facilitating compatibility between two protocols.

```
docker network create --driver bridge --subnet 172.26.160.1/16 --ip-range=172.26.161.1/24 --gateway=172.26.161.2 wordpress_bridge
```

## Connect the WordPress Server to the Network

We can use a new name for the wordpress container, like `wordpress_php_new`.

To use the same name, we must first stop the old container, `docker stop wordpress_php`, and rename it, so it is not lost: `docker rename wordpress_php wordpress_php_old`.

```
docker run --detach --name wordpress_php_new --network wordpress_bridge --ip 172.26.161.11 --publish 80:80 --volume /home/syn4z/git_repository/Sorin-Iatco-23/Lab2/wordpress:/var/www/html apache-php
```

This time, the `docker run` is different, because we are specifying the network for the container and specify the ip address. And that is because we are creating a docker bridge network.

## Connect The MySQL Server to the Network

```
docker run --detach --name wordpress_db_new --network wordpress_bridge --ip 172.26.161.12 --publish 3306:3306 --volume /home/syn4z/git_repository/Sorin-Iatco-23/Lab4/db:/docker-entrypoint-initdb.d -e MYSQL_DATABASE="wordpress_db" -e MYSQL_USER=sorin -e MYSQL_PASSWORD=password123 -e MYSQL_ROOT_PASSWORD=password123 mysql:latest
```

## Check that the network sees the containers

Run `docker network inspect wordpress_bridge` on the newly created network:

```
[
    {
        "Name": "wordpress_bridge",
        "Id": "2b911adef62d7266990994c3b23adefc1a33a6a5b28fe332c452ea27ad3384f5",
        "Created": "2023-05-04T08:06:48.790299228Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.26.160.1/16",
                    "IPRange": "172.26.161.1/24",
                    "Gateway": "172.26.161.2"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "5ae603a193410ce19c86b1e5f4152e9462ab194cf0066f0b29e0054616b03543": {
                "Name": "wordpress_php_new",
                "EndpointID": "81e496acf9801a967745502ea00428cf178ea3930ffdcc9aabb02233feac3966",
                "MacAddress": "02:42:ac:1a:a1:0b",
                "IPv4Address": "172.26.161.11/16",
                "IPv6Address": ""
            },
            "c3b82a98928470a383e7bb0afab6df35a0074e05c72d368e90b96ca3148a5eec": {
                "Name": "wordpress_db_new",
                "EndpointID": "a601c34a30ab014c86079550286de9299dda1a596a1836657de0a58e82c7ab46",
                "MacAddress": "02:42:ac:1a:a1:0c",
                "IPv4Address": "172.26.161.12/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {}
    }
]
```

## Run WordPress

1. Update the `wp-config.php`.

```
...
define( 'DB_NAME', 'wordpress_db' );

/** Database username */
define( 'DB_USER', 'sorin' );

/** Database password */
define( 'DB_PASSWORD', 'password123' );

/** Database hostname */
define( 'DB_HOST', 'wordpress_db_new' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );
...
```

2. Launch the `wordpress_php_new` container and check that it listens for requests.

```
HTTP/1.1 200 OK
Date: Thu, 04 May 2023 08:12:24 GMT
Server: Apache/2.4.56 (Debian)
X-Powered-By: PHP/8.2.4
X-Robots-Tag: noindex
Link: <http://172.26.160.1/wp-json/>; rel="https://api.w.org/"
X-Content-Type-Options: nosniff
Access-Control-Expose-Headers: X-WP-Total, X-WP-TotalPages, Link
Access-Control-Allow-Headers: Authorization, X-WP-Nonce, Content-Disposition, Content-MD5, Content-Type
Expires: Wed, 11 Jan 1984 05:00:00 GMT
Cache-Control: no-cache, must-revalidate, max-age=0
Allow: GET
Connection: close
Transfer-Encoding: chunked
Content-Type: application/json; charset=UTF-8
...
```