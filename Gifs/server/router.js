var fs = require('fs');
var path = require('path');
var cloudinary = require('cloudinary');
var Picture = require('./models/Picture');
var config = require('./config');

const perPage = config.glossary.perPage;
const mySort = {'/': {date: -1}, 'best': {like: -1}, 'random': {}};

exports.default = function(req, res){
    console.log('['+ new Date().toUTCString() +'][Server Log] - Request failed');
    res.send({ error: "Not found" });
};

exports.getOne = function(req, res){
    console.log('['+ new Date().toUTCString() +'][Server Log] - Find One request');
    Picture.findOne({_id:req.params.picture_id}, function(err, picture) {
        if (err){res.status(400).send({error: "Bad Request"});}
        else {res.json(picture);console.log('['+ new Date().toUTCString() +'][Server Log] - Find One completed');}
    });
};

exports.find = function(req, res){
    console.log('['+ new Date().toUTCString() +'][Server Log] - Find request');
    var page = 0;
    if (req.params.page_id != undefined){
        page = req.params.page_id;
    }
    var url = req.originalUrl.split('/');
    if (!isNaN(parseInt(url[1], 10)) || url[1] === ""){url = "/";}
    else {url = url[1];}

    if (mySort[url] != undefined){
        Picture.find({'validation':true})
               .limit(perPage)
               .skip(parseInt(page) * perPage)
               .sort(mySort[url])
               .exec(function(err, pictures) {
                    if (err){res.status(400).send({error: "Bad Request"});}
                    else {
                        /* For pagination */
                        Picture.find({'validation':true}).exec(function(err, results){
                            if (err){res.status(400).send({error: "Bad Request"});}
                            else {
                                if (req.originalUrl === "/random"){pictures = shuffle(pictures);}
                                    res.json(JSON.stringify(pictures) + ";" + results.length);
                                    console.log('['+ new Date().toUTCString() +'][Server Log] - Find completed');
                                }
                        });
                    }
                });
    }
};

exports.upload = function(req, res, err) {
    console.log('['+ new Date().toUTCString() +'][Server Log] - Upload request');
    if (!req.body.author){err = true;}
    if (!req.body.description){err = true;}
    if (err) {
        return res.status(400).send({error: "Code Ex522 - Error uploading file."});
    }

    var fullUrl = req.protocol + '://' + req.get('host') + req.originalUrl + "/" + req.file.filename;

    // Treatment insert
    var new_entry = {
        description: req.body.description,
        url: fullUrl,
        author: req.body.author,
        like: 0,
        like_list: "",
        date: Date.now(),
        validation: config.glossary.autoValidation
    }
    var entity = new Picture(new_entry);
    entity.save((err, new_entry) => {
        if (err) {
            res.status(400).send({error: "Code Ex524 - Error uploading file."});
        }
        else {
            console.log('['+ new Date().toUTCString() +'][Server Log] - New post successfully received');
            res.status(200).send({success: "File is uploaded"});
        }
    });

}

exports.like = function(req, res){
    console.log('['+ new Date().toUTCString() +'][Server Log] - Like request on picture id ' + req.body.id_post);

    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    if (ip.substr(0, 7) == "::ffff:") {
      ip = ip.substr(7)
    }

    if (!req.body.id_post){res.status(400).send({error: "Requete incomplete"});}
    else {
        Picture.findOne({_id:req.body.id_post}, function(err, picture) {
            var ret = true;

            if (err){
                res.status(400).send({error: "Post not found"});
            }
            else {
                if (!picture.like_list){
                    picture.like_list = ip;
                    picture.like = 1;
                }
                else {
                    var ips = picture.like_list.split(',');
                    ips.forEach((element) => {
                        if (element === ip)
                            ret = false;
                    });

                    /* Si l'ip n'est pas deja enregistré -> nouveau like */
                    if (ret !== false){
                        ips.push(ip);
                        picture.like_list = ips.toString();
                        picture.like = picture.like + 1;
                    }
                }
                if (ret === false){
                    res.status(202).send({error: "Déjà like"});
                }
                else {
                    // Save edit
                    picture.set({ like: picture.like, like_list: picture.like_list });
                    picture.save(function (err, updatedPicture) {
                        if (err) {res.status(400).send({error: "Probleme de mise à jour serveur"});}
                        else {
                            console.log('['+ new Date().toUTCString() +'][Server Log] - Like request completed on picture id ' + req.body.id_post);
                            res.status(201).send({error: "Update completed"});
                        }
                    });
                }
            }
        });
    }
}

function shuffle(array) {
  var id = array.length, tmp, rand_id;

  while (0 !== id) {
    rand_id = Math.floor(Math.random() * id);
    id--;

    tmp = array[id];
    array[id] = array[rand_id];
    array[rand_id] = tmp;
  }

  return array;
}
