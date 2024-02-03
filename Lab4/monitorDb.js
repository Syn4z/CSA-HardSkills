const mysql = require('mysql');
const MySQLEvents = require('@rodrigogs/mysql-events');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

let i = 0;
const DELAY_MS = 10000;
let attack = false;
let isInstanceRunning = false;

const program = async () => {
  let connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password123',
  });

  let instance = new MySQLEvents(connection, {
    startAtEnd: true,
    excludedSchemas: {
      mysql: true,
    },
  });

  setInterval(async () => {
    if (attack) {
      try {
        instance.stop();
        execSync('docker stop wordpress_db', { stdio: 'inherit' });
        console.log('Container stopped successfully.');
      } catch (error) {
        console.error(`Error stopping container: ${error.message}`);
        return;
      }

      try {
        execSync('docker rm wordpress_db', { stdio: 'inherit' });
        console.log('Container deleted successfully.');
      } catch (error) {
        console.error(`Error deleting container: ${error.message}`);
        return;
      }

      try {
        execSync('docker run --detach --name wordpress_db --publish 3306:3306 --volume /home/syn4z/git_repository/Sorin-Iatco-23/Lab4/db:/docker-entrypoint-initdb.d -e MYSQL_DATABASE="wordpress_db" -e MYSQL_USER=sorin -e MYSQL_PASSWORD=password123 -e MYSQL_ROOT_PASSWORD=password123 mysql:latest', { stdio: 'inherit' });
        console.log('New container created successfully!');
      } catch (error) {
        console.error(`Error created container: ${error.message}`);
        return;
      }

      let isInstanceRunning = false;
      
      if (!isInstanceRunning) {
        try {
          await instance.start();
          isInstanceRunning = true; 
          console.log('Instance started successfully!');
        } catch (error) {
          console.error(`Error starting instance: ${error.message}`);
          return;
        }
      }
    }
    attack = false;
    if (fs.existsSync(`./db-attack/attack${i}`)) {
      i++;
    }
    console.log("Looking for changes")
    if (!isInstanceRunning) { 
      await instance.start();
    }
  }, DELAY_MS);

  instance.addTrigger({
    name: 'TEST',
    expression: '*',
    statement: MySQLEvents.STATEMENTS.ALL,
    onEvent: (event) => {
      console.log("Change detected!");
      console.log(event);
      
      const fileName = 'db-attack-' + new Date().toISOString() + '.txt';
      const outputDirectory = `./db-attack/attack${i}`;
      if (!fs.existsSync(outputDirectory)) {
          fs.mkdirSync(outputDirectory);
      }
      const filePath = path.join(outputDirectory, fileName);
      fs.writeFile(filePath, JSON.stringify(event), function (err) {
        if (err) return console.log(err);
      });

      const dumpsql = `docker exec wordpress_db sh -c 'exec mysqldump --all-databases -uroot -ppassword123' > "/home/syn4z/git_repository/Sorin-Iatco-23/Lab4/db-attack/wordpress.sql"`;
      execSync(dumpsql, { stdio: 'inherit' });

      attack = true;
    }
  });
  
  instance.on(MySQLEvents.EVENTS.CONNECTION_ERROR, console.error);
  instance.on(MySQLEvents.EVENTS.ZONGJI_ERROR, console.error);
};

program()
  .then(() => console.log('Waiting for database events...'))
  .catch(console.error);
