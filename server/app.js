//Main file
var bodyParser = require('body-parser');
var express = require('express');
var path = require('path');
var mongoose = require('mongoose');
var multer = require('multer');
var handler = require('./router');
var config = require('./config');

/* Gestion picture upload */
var storage = multer.diskStorage({
    destination: function (req, file, cb){
        cb(null, 'uploads/')
    },
    filename: function (req, file, cb){
        if (!file.originalname.match(/\.(gif)$/) || file.mimetype !== "image/gif"){
            var err = new Error();
            err.code = 'filetype';
            return cb(err);
        }
        cb(null, Date.now() + ".gif");
    }
});
var upload = multer({ storage: storage,
                      limits:
                      { fileSize: config.glossary.maxFileSize }
                    }).single('picture');

/* Connection DB et recuperation schema */
mongoose.Promise = global.Promise;
mongoose.connect(config.glossary.mongodbUrl, {    useMongoClient: true });
var Picture = require('./models/Picture');

var app = express();

app.set('port', (process.env.PORT || config.glossary.port));

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  res.header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE");
  next();
});

/* For display image uploads on server */
app.use('/upload', express.static(__dirname + '/uploads'));

var router = express.Router();
router.get('/', handler.find);
router.get('/best', handler.find);
router.get('/best/:page_id', handler.find);
router.get('/random', handler.find);
router.get('/picture/:picture_id', handler.getOne);
router.get('/:page_id', handler.find);
router.post('/like', handler.like);
router.post('/upload', function (req, res) {
  upload(req, res, function (err) {
    handler.upload(req, res, err);
  })
});
app.use('/', router);

app.listen(app.get('port'), function () {
  console.log("Started LesJoiesDeUlaval Server at " + app.get('port'));
});