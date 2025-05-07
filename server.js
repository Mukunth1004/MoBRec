const https = require('https');
const fs = require('fs');
const express = require('express');

const app = express();

// Read SSL certificate files
const options = {
  key: fs.readFileSync('private-key.pem'),
  cert: fs.readFileSync('certificate.pem'),
};

// Route to handle the authorization callback (you can add other routes as necessary)
app.get('/', (req, res) => {
  res.send('Server is running on HTTPS!');
});

// Start the HTTPS server
https.createServer(options, app).listen(3000, () => {
  console.log('Server is running at https://localhost:3000');
});
