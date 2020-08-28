# Spelling Bee
This is a spelling bee application created for the Amazon Echo device using Alexa Skills Kit. The Amazon Echo device interacts with users through
voice commands. When a user wishes to play spelling bee, the Echo will ask user for spelling difficulties. After choosing a difficulty the user
will be provided a new word. The following are commands available to users: repeat, skip, define, give example, finish game. The commands
allow users to Echo to repeat the word, skip the current word, give definition of the current word, give an example of usage of current word, or to end the game
respectively.

## Installation
To develop for the Amazon Echo, we need to use the Amazon Web Services Lambda service. In AWS console, select Lambda and create new lambda function.
Upload the python file in your new lambda service. Note: The Lambda service for Alexa Skills Kit is only available in N.Virgina region, so make sure you are pointing to "US East (N. Virginia)" region. Once the Lambda service is created, go to Alexa Skills Kit to create a new skill. In The ASK configuration, link your endpoint to the Lambda ARN of the new lambda service you just created. And in the ASK Interaction Model, upload the Intent Schema and Sample Utterances appropriately. The Intent Schema defines the blueprint of your intent, and the Sample Utterances give possible phrasings of commands the users can say.

