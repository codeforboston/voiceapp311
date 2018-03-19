class MyCityDataModel:
    """
    Represents a request from a voice platform.

    @todo: Consistent comment format that contains platform-specific terminology
    """

    def __init__(self):
        self._request_type = None
        self._request_id = None
        self._is_new_session = None
        self._session_id = None
        self._session_attributes = {}
        self._application_id = None
        self._intent_name = None
        self._output_speech = None
        self._reprompt_text = None
        self._should_end_session = None
        self._intent_variables = {}

    def __str__(self):
        return """\
        <MyCityDataModel
            request_type={},
            request_id={},
            is_new_session={},
            session_id={},
            session_attributes={},
            application_id={},
            intent_name={},
            output_speech={},
            reprompt_text={},
            should_end_session={},
            intent_variables={}
        >
        """.format(
            self._request_type,
            self._request_id,
            self._is_new_session,
            self._session_id,
            self._session_attributes,
            self._application_id,
            self._intent_name,
            self._output_speech,
            self._reprompt_text,
            self._should_end_session,
            self._intent_variables
        )

    @property
    def request_type(self):
        """The type of this request."""
        return self._request_type

    @request_type.setter
    def request_type(self, value):
        self._request_type = value

    @property
    def request_id(self):
        """The unique identifier for this request."""
        return self._request_id

    @request_id.setter
    def request_id(self, value):
        self._request_id = value

    @property
    def is_new_session(self):
        """True if this is a new session, false otherwise.."""
        return self._is_new_session

    @is_new_session.setter
    def is_new_session(self, value):
        self._is_new_session = value

    @property
    def session_id(self):
        """Unique identifier for this session."""
        return self._session_id

    @session_id.setter
    def session_id(self, value):
        self._session_id = value

    @property
    def session_attributes(self):
        """An object containing key-value pairs of session information."""
        return self._session_attributes

    @session_attributes.setter
    def session_attributes(self, value):
        self._session_attributes = value

    @property
    def application_id(self):
        """Unique identifier for this application (a.k.a. skill id)."""
        return self._application_id

    @application_id.setter
    def application_id(self, value):
        self._application_id = value

    @property
    def intent_name(self):
        """The name of the intent being handled."""
        return self._intent_name

    @intent_name.setter
    def intent_name(self, value):
        self._intent_name = value

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
