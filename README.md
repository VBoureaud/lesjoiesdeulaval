# Les joies de ULaval

Express your feelings of life on the Laval university campus through humorous gif.
This project is the result of a personal challenge on a weekend.
[http://lesjoiesdeulaval.be](http://lesjoiesdeulaval.be)


## Architecture

Client side is programmed in ReactJS.
The server is a NodeJS server that offers an API to communicate with the client.

When you send a new post with the client, you upload a picture to the server who is saved in the folder "uploads/"

## Deployment

First of all, you need to have a mongodb server on your machine.
After that, you will have to install the dependencies before to can start.

```bash
$ cd client/
$ npm install
```

```bash
$ cd server/
$ npm install
```

Last step, check the "client/config.js" and the "server/config.js"

client :
```
export const config = {
    apiUrl: "http://127.0.0.1:5000", // Here, you can edit the server address if you need to
    clientUrl: "http://127.0.0.1:3000" // Here, you can edit the client address if you need to
    perPage: 5, // How many post would you like to see on your page ? You have to edit with the same value in the config server file
    monthNames: ["Jan", "Feb", "Mar", "Avr", "Mai", "Jun", // Month named for French langage
  "Jui", "Aoû", "Sep", "Oct", "Nov", "Dec"],
};
```

server:

```
var glossary = {
    mongodbUrl: "mongodb://localhost:27017/GifParty", // Here, you can edit the mongodb address if you need to
    port: 5000, // Here, you can edit the port of your server
    maxFileSize: 7340032, // Choose the max size accepted to upload
    perPage: 5, // How many post would you like to see on your page ? You have to edit with the same value in the config client file
    autoValidation: true // If true, when you send new post the validation is automatic.
};
```

Next, you just have to start your server

```bash
$ cd client/
$ npm start
```

```bash
$ cd server/
$ npm start
```

Enjoy

## Project's directories

```
.
├── client
│   ├── package.json
│   ├── public
│   │   ├── index.html
│   │   └── manifest.json
│   ├── src
│   │   ├── Components
│   │   │   ├── Add.js
│   │   │   ├── App.js
│   │   │   ├── Picture.js
│   │   │   └── Pictures.js
│   │   ├── config.js
│   │   ├── Css
│   │   │   └── App.css
│   │   ├── Img
│   │   │   └── eclipse.svg
│   │   ├── index.js
│   │   └── style
│   │       └── App.css
├── README.md
├── server
│   ├── app.js
│   ├── config.js
│   ├── models
│   │   └── Picture.js
│   ├── package.json
│   ├── router.js
│   └── uploads
│       └── index.html

```