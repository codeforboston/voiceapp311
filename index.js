/* eslint-disable  func-names */
/* eslint quote-props: ["error", "consistent"]*/
/**
 * This sample demonstrates a simple skill built with the Amazon Alexa Skills
 * nodejs skill development kit.
 * This sample supports multiple lauguages. (en-US, en-GB, de-DE).
 * The Intent Schema, Custom Slots and Sample Utterances for this skill, as well
 * as testing instructions are located at https://github.com/alexa/skill-sample-nodejs-fact
 **/

'use strict';
const Alexa = require('alexa-sdk');
const https = require('https');

//=========================================================================================================================================
//TODO: The items below this comment need your attention.
//=========================================================================================================================================

//Replace with your app ID (OPTIONAL).  You can find this value at the top of your skill's page on http://developer.amazon.com.
//Make sure to enclose your value in quotes, like this: const APP_ID = 'amzn1.ask.skill.bb4045e6-b3e8-4133-b650-72923c5980f1';
const APP_ID = undefined;

const SKILL_NAME = 'Boston Info';
const GET_FACT_MESSAGE = "Here's your fact: ";
const HELP_MESSAGE = 'You can say tell me a space fact, or, you can say exit... What can I help you with?';
const HELP_REPROMPT = 'What can I help you with?';
const STOP_MESSAGE = 'Goodbye!';

//=========================================================================================================================================
//TODO: Replace this data with your own.  You can find translations of this data at http://github.com/alexa/skill-sample-node-js-fact/data
//=========================================================================================================================================
const data = [
  "NEVER!",
  "Maybe by Boston 2030?",
];

//=========================================================================================================================================
//Editing anything below this line might break your skill.
//=========================================================================================================================================

const handlers = {
    'LaunchRequest': function () {
        this.emit('GetNewFactIntent');
    },
    'GetNewFactIntent': function () {

        //Get data for Tash PickUp and Recycling
        https.get('https://data.boston.gov/api/action/datastore_search?resource_id=fee8ee07-b8b5-4ee5-b540-5162590ba5c1&q={"Address": "1 Charles St S PH1-A"}', (res) => {
            console.log('statusCode:', res.statusCode);
            console.log('headers:', res.headers);
          var TrashPickUp="Trash Pick up on ";
          var Recycling="Recycling on ";
          var AlexaTell="For Address "

          //Get Response and parse String for Alexa
            res.on('data', (d) => {
              var apiResponse = JSON.parse(d);
              AlexaTell = AlexaTell + apiResponse["result"]["records"][0]["Address"] + 
              TrashPickUp + temapiResponsep["result"]["records"][0]["Trash"] +
              Recycling + apiResponse["result"]["records"][0]["Recycling"];
            });
          
          }).on('error', (e) => {
            console.error(e);
          });

        const factArr = data;
        const factIndex = Math.floor(Math.random() * factArr.length);
        const randomFact = factArr[factIndex];
        const speechOutput = GET_FACT_MESSAGE + randomFact;

        // this.response.cardRenderer(SKILL_NAME, randomFact);

        this.response.cardRenderer(SKILL_NAME, AlexaTell);
        
        this.response.speak(speechOutput);
        this.emit(':responseReady');
    },
    'AMAZON.HelpIntent': function () {
        const speechOutput = HELP_MESSAGE;
        const reprompt = HELP_REPROMPT;

        this.response.speak(speechOutput).listen(reprompt);
        this.emit(':responseReady');
    },
    'AMAZON.CancelIntent': function () {
        this.response.speak(STOP_MESSAGE);
        this.emit(':responseReady');
    },
    'AMAZON.StopIntent': function () {
        this.response.speak(STOP_MESSAGE);
        this.emit(':responseReady');
    },
};

exports.handler = function (event, context, callback) {
    const alexa = Alexa.handler(event, context, callback);
    alexa.APP_ID = APP_ID;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
