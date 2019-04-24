"""
Data Model for structuring responses from the skill implementation

"""

import logging

logger = logging.getLogger(__name__)


class MyCityResponseDataModel:

    """
    Represents a response to a voice platform.

    Standard way of structuring responses from the skill implementation.

    @todo: Consistent comment format that contains platform-specific terminology

    Note:
        The property methods below get and set attribute values.
    """

    def __init__(self):
        self._session_attributes = {}
        self._card_title = None
        self._output_speech = None
        self._reprompt_text = None
        self._should_end_session = None
        self._intent_variables = {}
        self._dialog_directive = None
        self._slot_to_elicit = None

    def __str__(self):
        return """\
        <MyCityResponseDataModel
            session_attributes={},
            card_title={},
            output_speech={},
            reprompt_text={},
            should_end_session={},
            intent_variables={}
            dialog_directive={}
            slot_to_elicit={}
        >
        """.format(
            self._session_attributes,
            self._card_title,
            self._output_speech,
            self._reprompt_text,
            self._should_end_session,
            self._intent_variables,
            self._dialog_directive,
            self._slot_to_elicit
        )

    def get_logger_string(self):
        """
        Cloudwatch will group multiline log strings if they use return
        character instead of the newline character.

        :return: The string representation of this object with \r instead of \n
        """
        return self.__str__().replace('\n', '\r')

    @property
    def session_attributes(self):
        """An object containing key-value pairs of session information."""
        return self._session_attributes

    @session_attributes.setter
    def session_attributes(self, value):
        self._session_attributes = value

    @property
    def card_title(self):
        """An object containing the title of the card that will be shown."""
        return self._card_title

    @card_title.setter
    def card_title(self, value):
        self._card_title = value

    @property
    def output_speech(self):
        """The script for Alexa's response to the request."""
        return self._output_speech

    @output_speech.setter
    def output_speech(self, value):
        self._output_speech = value

    @property
    def reprompt_text(self):
        """
        The script for Alexa's response in the case that the user needs to
        be reprompted.
        """
        return self._reprompt_text

    @reprompt_text.setter
    def reprompt_text(self, value):
        self._reprompt_text = value

    @property
    def should_end_session(self):
        """
        Boolean indicating whether the session should end after this response
        is received by the platform.
        """
        return self._should_end_session

    @should_end_session.setter
    def should_end_session(self, value):
        self._should_end_session = value

    @property
    def intent_variables(self):
        """
        An object containing key-value pairs representing the variables
        captured in the user's input.

        On the Alexa platform, these are called "slots".
        """
        return self._intent_variables

    @intent_variables.setter
    def intent_variables(self, value):
        self._intent_variables = value

    @property
    def dialog_directive(self):
        """
        String indicating the voice platform should modify the course of the
        dialog with the user in some way.

        In the case of "Dialog.Delegate", this signals that the Alexa platform
        should "take charge" of this response to the user according to the
        intent's dialog model.(usually involves prompting the user to
        confirm / provide a required slot filling value with a valid utterance,
        which is needed to fulfill the intent)
        """
        return self._dialog_directive

    @dialog_directive.setter
    def dialog_directive(self, value):
        valid_directives = [
            "Delegate",  # Delegate dialog decision to platform
            "ElicitSlotTrash",  # Ask for address for trash
            "ElicitSlotZipCode"  # Ask for users zip code
        ]

        if value not in valid_directives:
            logging.error("Error: {} is not a valid directive".format(value))
            return

        if value == "Delegate":
            self._dialog_directive = {'type': 'Dialog.Delegate'}
        elif value == "ElicitSlotTrash":
            self._dialog_directive = {
                    'type': 'Dialog.ElicitSlot',
                    'slotToElicit': 'Address'
                    }
        elif value == "ElicitSlotZipCode":
            self._dialog_directive = {
                'type': 'Dialog.ElicitSlot',
                'slotToElicit': 'Zipcode'
            }
