const { hashElement } = require('folder-hash');
const folderHash = require('folder-hash')
const tar = require('tar');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);
const directoryPath = args[0];
const outputDirectory = './attacks';
lastChangeTime = null;
let previousHash = null;

function hashDirectory() {
  console.log('Creating a hash over the folder '+"'"+directoryPath+"':");
  hashElement(directoryPath)
    .then(hash => {
      console.log(hash.toString());
    })
    .catch(error => {
      return console.error('hashing failed:', error);
    });

    archiveDirectory();
}  

function archiveDirectory() {  
  const outputFilePath = `${directoryPath+"_archive"}.tar`;
  tar.c({ file: outputFilePath }, [directoryPath], ['.'], (err) => {
    if (err) {
      console.error(`Error archiving directory: ${err.message}`);
      process.exit(1);
    }
    console.log(`Directory archived to ${outputFilePath}`);
  });
}

function archiveAttackDirectory() {
  console.log(`Directory ${directoryPath} has changed!`);
  const timestamp = new Date().toISOString().replace(/:/g, '-');
  const outputFile = `${directoryPath}-attack-${timestamp}.tgz`;
  const outputFilePath = path.join(outputDirectory, outputFile);

  // Check if a file has already been saved for this change
  if (lastChangeTime !== null && (new Date() - lastChangeTime) < 5000) {
    console.log('File already saved for this change');
    return;
  }

  tar.c({ file: outputFilePath, gzip: true }, [directoryPath], (err) => {
    if (err) {
      console.error(`Error archiving directory: ${err.message}`);
      process.exit(1);
    }
  });
  console.log(`Current attacked directory archived to ${outputDirectory}`);

  lastChangeTime = new Date();
}

setInterval(async () => {
  const { hash } = await folderHash.hashElement(directoryPath);
  console.log("Looking for changes...");
    if (previousHash !== null && previousHash !== hash) {
      previousHash = hash;
      archiveAttackDirectory();
      try {
        execSync('docker stop wordpress_php', { stdio: 'inherit' });
        console.log('Container stopped successfully.');
      } catch (error) {
        console.error(`Error stopping container: ${error.message}`);
        return;
      }

      try {
        execSync('docker rm wordpress_php', { stdio: 'inherit' });
        console.log('Container deleted successfully.');
      } catch (error) {
        console.error(`Error deleting container: ${error.message}`);
        return;
      }

        try {
          console.log('Deleting attacked folder.');
          fs.rmdirSync('wordpress', { recursive: true });
          console.log('Compromised folder removed succesfully!');
        } catch (error) {
          console.error(`Error removing folder: ${error.message}`);
          return;
        }

        try {
          console.log(`Extracting original folder: ${directoryPath}`);
          execSync('tar -xvf wordpress_archive.tar');
          console.log("Extraction DONE!");
        } catch (error) {
          console.error(`Error extracting folder: ${error.message}`);
          return;
        }
        
        try {
          execSync('docker run --detach --publish 80:80 --name wordpress_php --volume /home/syn4z/git_repository/Sorin-Iatco-23/Lab2/wordpress:/var/www/html apache-php', { stdio: 'inherit' });
          console.log('New container created successfully!');
        } catch (error) {
          console.error(`Error created container: ${error.message}`);
          return;
        }
        process.exit(0)
    } else if (previousHash === null) {
      previousHash = hash;
    }
}, 5000);

hashDirectory();
