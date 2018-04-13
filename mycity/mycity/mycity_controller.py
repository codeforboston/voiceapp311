"""
Controller for mycity voice app.

This class handles all voice requests.
"""

from __future__ import print_function
from mycity.mycity_data_model import MyCityDataModel
from mycity.mycity_response_data_model import MyCityResponseDataModel
from .intents.user_address_intent import set_address_in_session, \
    get_address_from_session, request_user_address_response
from .intents.trash_intent import get_trash_day_info
from .intents.unhandled_intent import unhandled_intent
from .intents.snow_parking_intent import get_snow_emergency_parking_intent
from .intents.get_alerts_intent import get_alerts_intent
from .intents import intent_constants


class MyCityController:
    """
    Handles requests for the MyCity voice app.


    @type mcr: MyCityDataModel
    @param mcr: Request from platform as a MyCityRequestModel object
    """
    LOG_CLASS = '\n\n[class: MyCityController]'

    def __init__(self, mycity_request):
        """
        Construct the controller.

        @type mycity_request: MyCityDataModel
        @param mycity_request: Request from platform as a MyCityRequestModel object
        """
        self._mycity_request = mycity_request
        self._mycity_response = MyCityResponseDataModel()
    def execute_request(self):
        """
        Route the incoming request based on type (LaunchRequest, IntentRequest,
        etc.) The JSON body of the request is provided in the event parameter.
        """
        print(
            self.LOG_CLASS,
            '[method: main]',
            'MyCityDataModel received:\n',
            str(self._mycity_request)
        )

        # TODO: This section should be generalized for all platforms if possible
        """
        Uncomment this if statement and populate with your skill's application ID 
        to prevent someone else from configuring a skill that sends requests to 
        this function.
        """
        # if (mcd.application_id !=
        #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
        #     raise ValueError("Invalid Application ID")

        if self._mycity_request.is_new_session:
            self.on_session_started()

        if self._mycity_request.request_type == "LaunchRequest":
            return self.on_launch()
        elif self._mycity_request.request_type == "IntentRequest":
            return self.on_intent()
        elif self._mycity_request.request_type == "SessionEndedRequest":
            return self.on_session_ended()

    def on_session_started(self):
        """
        Called when the session starts.
        """
        print(
            MyCityController.LOG_CLASS,
            '[method: on_session_started]',
            '[requestId: ' + str(self._mycity_request.request_id) + ']',
            '[sessionId: ' + str(self._mycity_request.session_id) + ']'
        )

    def on_launch(self):
        """
        Called when the user launches the skill without specifying what
        they want.
        """
        print(
            MyCityController.LOG_CLASS,
            '[method: on_launch]',
            '[requestId: ' + str(self._mycity_request.request_id) + ']',
            '[sessionId: ' + str(self._mycity_request.session_id) + ']'
        )
        # Dispatch to your skill's launch
        return self.get_welcome_response()

    def on_intent(self):
        """
        If the event type is "request" and the request type is "IntentRequest",
        this function is called to execute the logic associated with the
        provided intent and build a response.
        """
        mycity_request  = self._mycity_request
        mycity_response  = self._mycity_response
        print(
            self.LOG_CLASS,
            '[method: on_intent]',
            '[intent: ' + mycity_request.intent_name + ']',
            'MyCityDataModel received:',
            mycity_request
        )

        # Check if the user is setting the address. This is special cased
        # since they may have been prompted for this info from another intent
        if mycity_request.intent_name == "SetAddressIntent":
            set_address_in_session(mycity_request)

            if intent_constants.ADDRESS_PROMPTED_FROM_INTENT \
                    in mycity_request.session_attributes:
                # User was prompted for address from another intent.
                # Set our current intent to be that original intent now that
                # we have set the address.
                mycity_request.intent_name = mycity_request.session_attributes[intent_constants.ADDRESS_PROMPTED_FROM_INTENT]
                print("Address set after calling another intent. Redirecting "
                      "intent to {}".format(mycity_request.intent_name))
                # Delete the session key indicating this intent was called
                # from another intent.
                del mycity_request.session_attributes[intent_constants.ADDRESS_PROMPTED_FROM_INTENT]
            else:
                return get_address_from_session(mycity_request, mycity_response)

        # session_attributes = session.get("attributes", {})
        if mycity_request.intent_name == "GetAddressIntent":
            return get_address_from_session(mycity_request, mycity_response)
        elif mycity_request.intent_name == "TrashDayIntent":
            return request_user_address_response(mycity_request, mycity_response) \
                if intent_constants.CURRENT_ADDRESS_KEY \
                not in mycity_request.session_attributes \
                else get_trash_day_info(mycity_request, mycity_response)
        elif mycity_request.intent_name == "SnowParkingIntent":
            return request_user_address_response(mycity_request, mycity_response) \
                if intent_constants.CURRENT_ADDRESS_KEY \
                not in mycity_request.session_attributes \
                else get_snow_emergency_parking_intent(mycity_request, mycity_response)
        elif mycity_request.intent_name == "GetAlertsIntent":
            return get_alerts_intent(mycity_request, mycity_response)
        elif mycity_request.intent_name == "AMAZON.HelpIntent":
            return self.get_welcome_response()
        elif mycity_request.intent_name == "AMAZON.StopIntent" or \
                mycity_request.intent_name == "AMAZON.CancelIntent":
            return self.handle_session_end_request()
        elif mycity_request.intent_name == "UnhandledIntent":
            return unhandled_intent(mycity_request, mycity_response)
        else:
            raise ValueError("Invalid intent")

    def on_session_ended(self):
        """
        Called when the user ends the session.
        Is not called when the skill returns should_end_session=true
        """
        print(
            self.LOG_CLASS,
            '[method: on_session_ended]',
            'MyCityDataModel received:',
            str(self._mycity_request)
        )
        return self._mycity_response
        # add cleanup logic here

    def get_welcome_response(self):
        """
        If we wanted to initialize the session to have some attributes we could
        add those here.
        """
        print(
            self.LOG_CLASS,
            '[method: get_welcome_response]'
        )
        self._mycity_response.session_attributes = self._mycity_request.session_attributes
        self._mycity_response.card_title = "Welcome"
        self._mycity_response.output_speech = \
            "Welcome to the Boston Public Services skill. How can I help you? "

        # If the user either does not reply to the welcome message or says
        # something that is not understood, they will be prompted again with
        # this text.
        self._mycity_response.reprompt_text = \
            "For example, you can tell me your address by saying, " \
            "\"my address is\" followed by your address."
        self._mycity_response.should_end_session = False
        return self._mycity_response

    def handle_session_end_request(self):
        self._mycity_response.session_attributes = self._mycity_request.session_attributes
        self._mycity_response.card_title = "Boston Public Services - Thanks"
        self._mycity_response.output_speech = \
            "Thank you for using the Boston Public Services skill. " \
            "See you next time!"
        self._mycity_response.should_end_session = True
        return self._mycity_response
