import mycity.test.intent_base_case as base_case


#########################################
# TestCase class for open_spaces_intent #
#########################################


class GetOpenSpacesTestCase(base_case.IntentBaseCase):

    __test__ = True
    
    intent_to_test = "GetOpenSpacesIntent"
    returns_reprompt_text = False


