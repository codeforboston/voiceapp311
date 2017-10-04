'use strict';
const Alexa = require('alexa-sdk');
const https = require('https');

<<<<<<< HEAD
//=========================================================================================================================================
//TODO: The items below this comment need your attention.
//=========================================================================================================================================

//Replace with your app ID (OPTIONAL).  You can find this value at the top of your skill's page on http://developer.amazon.com.
//Make sure to enclose your value in quotes, like this: const APP_ID = 'amzn1.ask.skill.bb4045e6-b3e8-4133-b650-72923c5980f1';
const APP_ID = undefined;

const SKILL_NAME = 'Boston Info';
const GET_FACT_MESSAGE = "Here you go: ";
const HELP_MESSAGE = 'You can say tell me a Boston 311 information, or, you can say exit... What can I help you with?';
const HELP_REPROMPT = 'What can I help you with?';
const STOP_MESSAGE = 'Goodbye!';

//=========================================================================================================================================
//TODO: Replace this data with your own.  You can find translations of this data at http://github.com/alexa/skill-sample-node-js-fact/data
//=========================================================================================================================================
const data = [
  "Trash pick up days in Boston are Tuesday and Thursday"
];

//=========================================================================================================================================
//Editing anything below this line might break your skill.
//=========================================================================================================================================

const handlers = {
    'LaunchRequest': function () {
        this.emit('GetBostonInfo');
    },
    'GetNewFactIntent': function () {

        //Get data for Tash PickUp and Recycling
        // https.get('https://data.boston.gov/api/action/datastore_search?resource_id=fee8ee07-b8b5-4ee5-b540-5162590ba5c1&q={"Address": "1 Charles St S PH1-A"}', (res) => {
        //     console.log('statusCode:', res.statusCode);
        //     console.log('headers:', res.headers);
        //   var TrashPickUp="Trash Pick up on ";
        //   var Recycling="Recycling on ";
        //   var AlexaTell="For Address "
        //
        //   //Get Response and parse String for Alexa
        //     res.on('data', (d) => {
        //       var apiResponse = JSON.parse(d);
        //       AlexaTell = AlexaTell + apiResponse["result"]["records"][0]["Address"] +
        //       TrashPickUp + temapiResponsep["result"]["records"][0]["Trash"] +
        //       Recycling + apiResponse["result"]["records"][0]["Recycling"];
        //     });
        //
        //   }).on('error', (e) => {
        //     console.error(e);
        //   });

        const factArr = data;
        const factIndex = Math.floor(Math.random() * factArr.length);
        const randomFact = factArr[factIndex];
        const speechOutput = GET_FACT_MESSAGE + randomFact;

        // this.response.cardRenderer(SKILL_NAME, randomFact);

        this.response.cardRenderer(SKILL_NAME, randomFact);

        this.response.speak(speechOutput);
        this.emit(':responseReady');
    },
    'AMAZON.HelpIntent': function () {
        const speechOutput = HELP_MESSAGE;
        const reprompt = HELP_REPROMPT;

        this.response.speak(speechOutput).listen(reprompt);
        this.emit(':responseReady');
=======

var handlers = {
    'LaunchRequest': function () {
        this.emit('SayHello');
>>>>>>> b4c4fc3f49041ffdb491352891a64e0f45f03ede
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

