'use strict';
const Alexa = require('alexa-sdk');
const https = require('https');


var handlers = {
    'LaunchRequest': function () {
        this.emit('SayHello');
    },
    'HelloWorldIntent': function () {
        this.emit('SayHello')
    },
    'TrashPickUpIntent' : function () {
        console.log("inside trash pick up intent");
        this.emit('TrashPickUp');
    },
    'SayHello': function () {
        console.log("testing here");
        this.emit(':tell', 'Hello there!');
    }, 
    'TrashPickUp': function () {
        var TrashPickUp="Trash Pick up on ";
        var Recycling="Recycling on ";
        var AlexaTell="For Address ";
        var output ="";
        var myRequest = "test";
        console.log("inside trash function");
        httpsGet(myRequest,  (apiResponse) => {
            console.log("sent     : " + myRequest);
            console.log("received : " + apiResponse);
            // var apiResponse = JSON.parse(output);
            output = AlexaTell + apiResponse["result"]["records"][0]["Address"] + 
            TrashPickUp + apiResponse["result"]["records"][0]["Trash"] +
            Recycling + apiResponse["result"]["records"][0]["Recycling"];
            console.log("regular output:" + output);
            console.log("stringify:" + JSON.stringify(output));

            this.response.speak(output);
            this.emit(':responseReady');

        });
    }
};

exports.handler = function(event, context, callback) {
    var alexa = Alexa.handler(event, context);
    alexa.registerHandlers(handlers);
    alexa.execute();
};

function httpsGet(myData, callback) {
        console.log("inside this httpsGet");
    
        // GET is a web service request that is fully defined by a URL string
        // Try GET in your browser:
        // https://cp6gckjt97.execute-api.us-east-1.amazonaws.com/prod/stateresource?usstate=New%20Jersey
    
    
        // Update these options with the details of the web service you would like to call
    
        var req = https.get('https://data.boston.gov/api/action/datastore_search?resource_id=fee8ee07-b8b5-4ee5-b540-5162590ba5c1&q={"Address":"866 Huntington ave"}', res => {
            res.setEncoding('utf8');
            var returnData = "";
            console.log("inside request");
    
            res.on('data', chunk => {
                returnData = returnData + chunk;
                console.log("chunk:" + chunk)
            });

            res.on('error', err => {
                console.log(err);
                console.log("so many errors");
            });
    
            res.on('end', () => {
                // we have now received the raw return data in the returnData variable.
                // We can see it in the log output via:
                // console.log(JSON.stringify(returnData))
                // we may need to parse through it to extract the needed data
    
                var pop = JSON.parse(returnData);
                console.log("in end");
                console.log(pop);
    
                callback(pop);  // this will execute whatever function the caller defined, with one argument
    
            });
    
        });
        console.log("request about to hit");
        req.end();
    }

