'use strict';
var Alexa = require("alexa-sdk");

exports.handler = function(event, context, callback) {
    var alexa = Alexa.handler(event, context);
    alexa.registerHandlers(handlers);
    alexa.execute();
};

var handlers = {
    'LaunchRequest': function () {
        this.emit('SayHello');
    },
    'HelloWorldIntent': function () {
        this.emit('SayHello')
    },
    'TrashPickUpIntent' : function () {
        this.emit('trashPickUp');
    },
    'SayHello': function () {
        this.emit(':tell', 'Hello there!');
    }, 
    'TrashPickUp': function () {
        //add functionality here
    }
};

