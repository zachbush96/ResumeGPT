##ToDo
#Implement LamgChain
#Use LangChain streaming, and stream the LLM output to the user using websockets

#import os
from flask import Flask, render_template, request
#import openai
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
from langchain.llms import OpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
import random
#from langchain.chat_models import ChatOpenAI as OpenAI

#Eventually Remove this, it should be pulled from Langchain
#openai.api_key = os.environ['openAI-API-Key']

app = Flask(__name__)
# Create a SocketIO instance and link it to the app
socketio = SocketIO(app)


#Custom Callback handler that emits the tokens via a socket
class StreamingSocketIOCallbackHandlerFinal(BaseCallbackHandler):

	def __init__(self, socketio):
		self.socketio = socketio

	def on_llm_new_token(self, token: str, **kwargs) -> None:
		self.socketio.emit('token', token)

class StreamingSocketIOCallbackHandlerSHResume(BaseCallbackHandler):

	def __init__(self, socketio):
		self.socketio = socketio

	def on_llm_new_token(self, token: str, **kwargs) -> None:
		self.socketio.emit('shrunkResume', token)

class StreamingSocketIOCallbackHandlerSHJob(BaseCallbackHandler):

	def __init__(self, socketio):
		self.socketio = socketio

	def on_llm_new_token(self, token: str, **kwargs) -> None:
		self.socketio.emit('shrunkJob', token)


#chat = OpenAI(streaming=True,callbacks=[StreamingSocketIOCallbackHandler(socketio)],temperature=.5)
chat = OpenAI(model_name="gpt-4", temperature=.5)

streamingShrunkResume = OpenAI(
 streaming=True,
 callbacks=[StreamingSocketIOCallbackHandlerSHResume(socketio)],
 temperature=.8)

streamingJobDescription = OpenAI(
 streaming=True,
 callbacks=[StreamingSocketIOCallbackHandlerSHJob(socketio)],
 temperature=.8)

streamingChat = OpenAI(
 streaming=True,
 callbacks=[StreamingSocketIOCallbackHandlerFinal(socketio)],
 temperature=.9)


#Return the main page
@app.route('/')
def index():
	return render_template('index.html')


@socketio.on('connect')
def connect():
	print('Client connected')


@socketio.on('disconnect')
def disconnect():
	print('Client disconnected')


#Reads information from the POST'ed form
#Returns text with "The perfect Resume"
@app.route('/process', methods=['POST'])
def process():
	try:
		resume = request.files.get('resume').read().decode('utf-8')
		print("User uploaded txt file")
		R = open("Uploaded_Resumes/" + str(random.randint(0, 10000)) + ".txt", "w")
		R.write(resume)
		R.close()
	except:
		pass
	try:
		resume = request.form.get('resume_text')
		print("User pasted resume")
		R = open("Uploaded_Resumes/" + str(random.randint(0, 10000)) + ".txt", "w")
		R.write(resume)
		R.close()
	except:
		return "No Resume Uploaded"

	prompt = "You are going to be passed a users resume. You should make it as short as possible while still keeping the relevant information. \n\n Resume: %s" % resume
	shrunk_resume = streamingShrunkResume(prompt)

	job_description = request.form.get('job_description')
	print("Original Job Description: " + job_description[:10])
	prompt = "You are going to be passed a job description. You should make it as short as possible while still keeping the relevant information. Be Brief. \n\n Job Description: %s" % job_description
	#print(prompt)
	#shrunk_job_description = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":prompt}])
	shrunk_job_description = streamingJobDescription(prompt)

	prompt = "Please act as an HR professional and create the perfect resume. This resume should be a tweaked version of the current resume so it is applicable to the job description. Think about the similarities between the resume, and job description and how previous experiences can be applied. Business and job title should not change. The resume should include details and be properly formatted.The resume must include contact information, relevant skills and tweaked to fit the job description, previous experience tweaked to fit the job descirption, and education.\n CURRENT RESUME: %s \n JOB DESCRIPTION: %s" % (
	 shrunk_resume, shrunk_job_description)
	PerfectResume = streamingChat(prompt)
	pResume = PerfectResume
	print("Resume Generated")
	newFile = open("GeneratedResumes/" + str(random.randint(0, 1000)) + ".txt",
	               "w")
	newFile.write(pResume)
	newFile.close()
	return str(pResume)


def shrinkText(text):
	#Make an API call to ChatGPT-3.5 to shrink the pass text and return the shrunk text
	prompt = "You are going to be passed a piece of text. You should make it as short as possible while still keeping the relevant information.\n\n Text: %s" % text
	#shrunk_text = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{ "role": "user", "content": prompt}])
	shrunk_text = chat(prompt)
	return shrunk_text

@socketio.on('getLLMText')
def getLLMText():
	pass


#Start the server, continuously listen to requests on all interfaces 0.0.0.0
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
