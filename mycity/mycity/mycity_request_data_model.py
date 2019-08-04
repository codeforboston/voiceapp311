"""
Data Model for structuring requests to the skill implementation
"""
import json


class MyCityRequestDataModel:
    """
    Represents a request from a voice platform.
    
    Standard way requests are structured so they may be acted upon by
    the skill implementation.

    @todo: Consistent comment format that contains platform-specific terminology
        
    Note:
        The property methods below get and set attribute values.
    """

    def __init__(self):
        self._request_type = None
        self._request_id = None
        self._is_new_session = None
        self._session_id = None
        self._session_attributes = {}
        self._application_id = None
        self._intent_name = None
        self._intent_variables = {}
        self._device_id = None
        self._api_access_token = None
        self._has_geolocation = None
        self._geolocation_permission = None
        self._geolocation_coordinates = None

    def __str__(self):
        return """\
        <MyCityRequestDataModel
            request_type={},
            request_id={},
            is_new_session={},
            session_id={},
            session_attributes={},
            application_id={},
            intent_name={},
            intent_variables={},
            device_id={},
            api_access_token={},
            has_geolocation={},
            geolocation_permission={},
            geolocation_coordinates={}
        >
        """.format(
            self._request_type,
            self._request_id,
            self._is_new_session,
            self._session_id,
            self._session_attributes,
            self._application_id,
            self._intent_name,
            self._intent_variables,
            self._device_id,
            self._api_access_token,
            self._has_geolocation,
            self._geolocation_permission,
            self._geolocation_coordinates
        )

    def get_logger_string(self):
        """
        Cloudwatch will group multiline log strings if they use return
        character instead of the newline character.

        :return: The string representation of this object with \r instead of \n
        """
        return self.__str__().replace('\n', '\r')

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
    def device_id(self):
        """
        An id to identify which device Alexa is utlizing for the service
        """
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        self._device_id = value

    @property
    def api_access_token(self):
        """
        the token which is neccessary to acquire access to a user's personal information
        """
        return self._api_access_token

    @api_access_token.setter
    def api_access_token(self, value):
        self._api_access_token = value

    @property
    def device_has_geolocation(self):
        """
        Returns if the user's device has geolocation services
        """
        return self._has_geolocation

    @device_has_geolocation.setter
    def device_has_geolocation(self, value: bool):
        self._has_geolocation = value
    
    @property
    def geolocation_permission(self):
        """
        Returns if this device has geolocation permission
        """
        if not self._has_geolocation:
            return False
        return self._geolocation_permission

    @geolocation_permission.setter
    def geolocation_permission(self, value: bool):
        self._geolocation_permission = value

    @property
    def geolocation_coordinates(self):
        return self._geolocation_coordinates

    @geolocation_coordinates.setter
    def geolocation_coordinates(self, value: dict):
        self._geolocation_coordinates = value
    