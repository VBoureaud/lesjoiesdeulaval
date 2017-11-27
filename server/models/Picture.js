var mongoose = require('mongoose');

var pictureSchema = new mongoose.Schema({
    id: {type:String},
    description: {type:String},
    url: {type:String},
    like: {type:Number},
    like_list: {type:String},
    date: {type:Date},
    author: {type:String},
    validation: {type:Boolean}
});

module.exports = mongoose.model('Picture', pictureSchema);