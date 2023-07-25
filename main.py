from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from langchain.llms import OpenAI
import random

app = Flask(__name__)

chat = OpenAI(model_name="gpt-4", temperature=.5, arbitrary_types_allowed=True)


@app.route('/')
def index():
	return render_template('index.html')


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
	shrunk_resume = chat(prompt)
	job_description = request.form.get('job_description')
	print("Original Job Description: " + job_description[:10])
	prompt = "You are going to be passed a job description. You should make it as short as possible while still keeping the relevant information. Be Brief. \n\n Job Description: %s" % job_description
	shrunk_job_description = chat(prompt)
	prompt = "Please act as an HR professional and create the perfect resume. This resume should be a tweaked version of the current resume so it is applicable to the job description. Think about the similarities between the resume, and job description and how previous experiences can be applied. Business and job title should not change. The resume should include details and be properly formatted.The resume must include contact information, relevant skills and tweaked to fit the job description, previous experience tweaked to fit the job descirption, and education.\n CURRENT RESUME: %s \n JOB DESCRIPTION: %s" % (
	 shrunk_resume, shrunk_job_description)
	PerfectResume = chat(prompt)
	pResume = PerfectResume
	print("Resume Generated")
	newFile = open("GeneratedResumes/" + str(random.randint(0, 1000)) + ".txt",
	               "w")
	newFile.write(pResume)
	newFile.close()
	return str(pResume)


def shrinkText(text):
	prompt = "You are going to be passed a piece of text. You should make it as short as possible while still keeping the relevant information.\n\n Text: %s" % text
	shrunk_text = chat(prompt)
	return shrunk_text


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
