"""Constants used across Alexa intents"""

# The key used for the current address in session attributes
CURRENT_ADDRESS_KEY = "currentAddress"

# When an intent that requires an address is invoked without a known address,
# we redirect to get the user's address. This constant is the key whose value is
# the name of the intent where the need for an address originated.
ADDRESS_PROMPTED_FROM_INTENT = "addressPromptedFromIntent"
