# ZoomMyLife

Requirements: Need to have flutter installed and be able to run 'flutter run'
If you do not have flutter installed, use [install flutter ](https://docs.flutter.dev/get-started/install) to install flutter

1. Clone the project, using the following command: 'git clone https://github.com/divyeshbommana/ZoomMyLife.git'

2. Go into the folder 'zoom_my_life'. Add the API_KEYS.yml file here

3. Install all requirements using the following command: 'pip install -r requirements.txt'

Note: This might take a long time, up to 5 minutes. 
This will be based on the packages already present in your system

4. You will need to have two terminals in '../ZoomMyLife/zoom_my_life'

Note: If in ZoomMyLife folder, use 'cd zoom_my_life' to get into 'zoom_my_life' folder

5. In one of the terminal, set up the RAG server by running the following command: 'python ./RAG.py'

Note: This will retrieve a document, load it in, split it into chunks with overlap, 
embed these chunks, create a retriever to get 3 closest documents, define two pipelines, 
and finally gets the LLM model. Therefore, running this might take some time. 

Luckily, we will only need to run this once, for the duration of application running.
When '* Running on http://127.0.0.1:5000', is displayed, the server is up and running

DO NOT CLOSE THIS WINDOW/TERMINAL, closing will force you to set up server once again

6. After the server is set up, use the second terminal to run the following command: 'flutter run'

Note: You may use windows or any other browser options provided. 

# Application

After application is running, you may interact with the LLM using the text box and pressing enter (on screen or keyboard)

Ex. 'What are the planets?'

For the LLM to perform as a medical assistant, you will need to enter some health data using the '+' button
And enter your health data

Now you may ask the LLM to give you some suggestions

Ex. 'Give me some health suggestions'

Note: Currently the data will be stored in the documents folder as 'userData.csv'.
So even after you close the application and server, you will not need to re-enter data

# Limitations/Future Work

* Currently the csv is stored in the way that new data is appended at the bottom of csv file and the LLM is told that later
* entries are the most latest. But this isn't enough and LLM could make mistakes

* Need to add gender and create regex limitations on text-entry fields when adding health data.

* The document used, only contains 15 pages. The 450 page document is present in folder, but is not used due to time complexities

* The LLM used is only 'llama-3.1-8b-instant' as using a larger model with a CPU-only device made it near impossible.

* Need to experiment with different prompts and embedding models
