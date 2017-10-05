# Boston Data Alexa Skill

An Alexa skill to answer questions about municipal services in Boston.
Currently supports providing an address and asking for trash/recycling pick up
days.

## Installation

### Part 1: Amazon Developer
1. Go to the Amazon developers page (https://developer.amazon.com) and log in.
2. Select **Alexa** from the menu bar near the top of the page.
3. Select **Alexa Skills Kit** from the next page.
4. Select **Add a New Skill** from the upper right corner of the next page.
5. In the **Skill Information** section of the new skill fill in the following:
   * Language: **English (U.S.)**
   * Name: **Boston Data**
   * Invocation Name: **boston data**
   Leave everything else as is, click **Save** at the bottom, then **Next**.
6. You should now be in the **Interaction Model** section of the skill. Do the following:
   * In the **Intent Schema** input box, paste the contents of [intent_schema.json](docs/intent_schema.json).
   * Leave the **Custom Slot Types** section blank.
   * In the **Sample Utterances** input box, paste the contents of [sample_utterances.txt](docs/sample_utterances.txt).
   Click **Save** at the bottom and click **Next**.
7. You should now be in the **Configuration** section of the skill. Leave this
   tab open as you will enter information from your **Lambda** function here later.

### Part 2: AWS Lambda
1. Open a new tab and log in to AWS (https://aws.amazon.com)
2. Open the menu in the upper left and navigate to **Products > Computer > AWS Lambda**
3. Select **Get Started with AWS Lambda**.
4. In the upper right, click **Create function**.
5. You should now be at **Step 1, Select Blueprint**.
   Select **Author from scratch** in the upper right.
6. You should now be at **Step 2, Configure Triggers**. Click inside the
   empty dashed square and select **Alexa Skills Kit** from the menu that
   pops up, then hit **Next**.
7. You should be at **Step 3, Configure Function**.
   * Fill in the **Basic information**. I used the following:
     * Name: **BostonData**.
     * Description: *An Alexa skill allowing users to ask for information about
       municipal services in Boston.*
     * Runtime: **Python 3.6** (this won't matter because you'll upload the
       code in a .zip file).
    * Under **Lambda function code**, select **Upload a .zip file** from the
      **Code entry type** pulldown. Upload the [lambda_function.zip](./lambda_function.zip)
      archive. This .zip file contains the Python code and the external libraries
      used in it.
    * Under **Lambda function handler and role**, set the following:
      * Handler: **lambda_function.lambda_handler**.
      * Role: **Choose an existing role**
      * Existing role: **lambda_basic_execution**
      * Leave advanced settings as is.
8. In the upper right you'll see a **ARN**. Copy this and go back to the tab
   you have open from Part 1.

### Part 3: Amazon Developer
1. In the **Configuration** tab, for **Service Endpoint Type**, select
   **AWS Lambda ARN (Amazon Resource Name)**.
2. In the **Default** text field paste the ARN from Part 2.
3. Leave everything else as is.

### Part 4: Test
Once you've completed Part 3, go to the **Test** tab. Here you can run sample
voice queries using the **Service Simulator**.


## Usage

Supports three custom intents right now.
1. **My address is [your Boston address]**: Sets your address in the session.
2. **What's my address?**: Tells you the current address in the session.
3. **When is trash/garbage/recycling day?**: Tells you the trash/recycling days
   for the address in the session.

# Notes

## Alexa skill execution overview

This is basically a restatement of the guide at
[https://moduscreate.com/build-an-alexa-skill-with-python-and-aws-lambda/](https://moduscreate.com/build-an-alexa-skill-with-python-and-aws-lambda/)
with some additional clarification.

1. User issues voice command to Echo by saying, "Alexa" followed by
   a skill name and an intent. The intent may have parameters.

   In this case, something like:
   *"Alexa, ask Boston Data when is trash day?"*

   ```
   skill name : Boston Data
   intent     : find trash days
   parameters : 1 Main Street apartment 2
   ```

   We will give this intent a name, **TrashDayIntent**. You can see this in
   the intent schema.

2. Echo sends the request to the Alexa Service Platform.

   This handles the speech recognition and translates the above voice
   command to a JSON document containing the intent and any parameters.

   This JSON is sent to the skill (Boston Data in this example).

   For BostonData:

   ```
   intent    : trashday
   parameter : "1 Main Street apartment 2"
   ```

3. The skill receives the JSON.

   We're implementing the skill as an AWS Lambda, so the JSON will be
   sent to the Lambda function at the ARN associated with the skill name.

4. The Lambda contains custom code that parses the JSON to identify
   the intent and corresponding arguments (in this example, the address).

   The code then gathers data for the response. In this case that means
   a call to data.boston.gov to get the string of trash days
   associated with the provided address. Alternately this might mean
   accessing a database or session information.

   This response data is serialized in a JSON response, which is returned
   to the Alexa Service Platform. It contains the response both as text
   for Alexa to say and as text/images for the smartphone app to display.

5. The Alexa Service Platform receives the response and conveys to the
   user using text-to-speech or the app display.

## Python-specific Notes

Because the python code in Boston Data's Lambda function uses resources beyond
Python's standard libraries, it must be uploaded as a .zip file.

To generate this .zip file, we must install all of the required Python packages
in the directory that contains [our code](BostonData/lambda_function/lambda_function.py). For this project, that
directory is [BostonData/lambda_function](BostonData/lambda_function). Amazon
provides instructions on how to do so: [https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)

Once all the requisite libraries are installed, compress the contents of the
directory. The instructions note:
   >**Important**:
   >Zip the directory content, not the directory. The contents of the Zip file
   >are available as the current working directory of the Lambda function.

Recall that in Part 2 of the installation instructions we set the **Handler** to
**lambda_function.lambda_handler**. This is specifying the function that is
executed when a voice command is issued to the Alexa device. If we compress the
containing directory instead of its contents, this code is not available.




## Notes on open data sources for Boston

### https://data.boston.gov
This is the new portal for Boston's open data efforts. This site uses a tool
called CKAN, which describes itself as follows:
   >CKAN is a tool for making open data websites. (Think of a content management
   >system like WordPress - but for data, instead of pages and blog posts.)
   >It helps you manage and publish collections of data. It is used by national
   >and local governments, research institutions, and other organizations who
   >collect a lot of data.

CKAN sites are organized by datasets, which can be made available in multiple
formats. AnalyzeBoston contains 131 datasets as of this writing. Searching the
datasets for "trash" returns 4 results, including one we can use for this
project: **trash schedules by address**. The API for that dataset can be found
by following the link to the dataset and then selecting **preview**. On the
preview page there is a **DATA API** link.

Here you can find a link labelled **odata**. odata is a REST protocol for open
data. CKAN provides an odata endpoint for the **trash schedules by address**
dataset.

### https://mayors24.cityofboston.gov/open311/v2/services.json
This is the Open311 portal for the city of Boston. It requires an API key
and solely provides 311 functionality (checking the status of 311 issues or
filing new ones). At some point we'll probably want to incorporate this
type of functionality, but for the simple city service information retrieval
we're concentrating on right now, this API is not useful.

### https://data.cityofboston.gov/

**DEPRECATED**

This is the former open data portal of the city of Boston.
This API implemented the Socrata Open Data API. Socrata is a company that
provides cloud-based data visualization and analysis tools for opening
government data. **This portal is no longer being updated.**


## Miscellaneous Alexa Skill Information

### ARN (Amazon Resource Name)
From Amazon's documentation:
   >Amazon Resource Names (ARNs) uniquely identify AWS resources. We require
   >an ARN when you need to specify a resource unambiguously across all of AWS,
   >such as in IAM policies, Amazon Relational Database Service (Amazon RDS) tags,
   >and API calls.
[https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#arn-syntax-lambda](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#arn-syntax-lambda)

Our skill will be stored in an AWS Lambda function, which we can identify by its ARN.


### Slot
Slots are used for intents that require parameters. Each slot must have:
1. a name (a string describing the slot)
2. a type (this can be a type preconfigured by Amazon or a custom type)

The preconfigured slot type for a street address is described [here](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/built-in-intent-ref/slot-type-reference#postaladdress).

Information on defining a custom slot type is available [here](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/alexa-skills-kit-interaction-model-reference#custom-slot-syntax).


### Sample Utterances
Alexa needs a list of phrases that correspond to each of our skill's intents.

We provide this in the settings for our skill in the developer console (see Part 1 of installation).

The format for the list of sample utterances is

```
[intent] [phrase]
```

The phrase may contain a reference to a slot if there is one associated with
the intent it invokes. The format for this is

```
{slot_name}
```

Example of a sample utterance:

```
SetAddressIntent my address is {Address}
```

### Lambda

Our skill will invoke an Amazon Lambda function. This is where the code that
produces a response to the Alexa voice command resides.

There are several language options for this code, including Javascript
(Node.js), Java, C#, and Python(2.7 or 3.6).

Selecting Python we are provided the following template:

```python
def lambda_handler(event, context):
    # TODO implement
    return 'Hello from Lambda'
```

The event argument is the JSON received from the Alexa platform. It contains the
intent and slot information from the voice command.


Structure of the event object:
```
  session
      sessionId: [session id],
      application
          applicationId: [application id]
      attributes: {},
      user
          userId: [user id]
      new: true
  request:
      type: [request type, e.g., IntentRequest]
      requestId: [request id]
      timestamp: [timestamp]
      intent
          name: [name of the invoked intent]
          slots:
              [slot name]
                  name: [name of the slot]
                  value: [value of the slot]
      locale: "en-US"
  version: "1.0"
```
