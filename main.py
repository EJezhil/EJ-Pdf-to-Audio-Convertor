# -------------------//// Note input pdf should contain text less than 2000 characters////-------------------#


# Environment variables
import os
import tkinter

# Flask App
from flask import Flask, render_template, redirect, url_for, request

# Api request
import requests

# PDF to Text imports
from tkinter import filedialog
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io

datas = None


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')

# Convert PDF to text
def pdf_to_text(data):
    global datas
    fp = open(data, 'rb')
    pdf_resource_manager = PDFResourceManager()
    laparams = LAParams()
    stringio = io.StringIO()

    text = TextConverter(pdf_resource_manager, stringio, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(pdf_resource_manager, text)

    # Process each page contained in the document.
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        datas = stringio.getvalue()



def text_mp3():
    global datas
    # Send the converted text from pdf to API to generate voice (mp3)file
    url = "https://api.play.ht/api/v2/tts/stream"

    payload = {
        "text": datas,
        "voice": "s3://mockingbird-prod/abigail_vo_6661b91f-4012-44e3-ad12-589fbdee9948/voices/speaker/manifest.json",
        "output_format": "mp3"
    }
    headers = {
        "accept": "audio/mpeg",
        "content-type": "application/json",
        "AUTHORIZATION": os.environ.get("API_KEY"),
        "X-USER-ID": os.environ.get("USER_ID")
    }

    response = requests.post(url, json=payload, headers=headers)
    # print(response.text)
    print(" Text converted into mp3 data")

    # store this response content in mp3 file
    with open("output.mp3", "wb") as out:
        out.write(response.content)
        print('Audio content written to file "output.mp3"')


@app.route('/', methods=["GET", "POST"])
def index():
    saved = request.args.get("saved")
    if saved is None:
        saved = ""
    if request.method == "POST":
        tk = tkinter.Tk()
        print("clicked")
        data = filedialog.askopenfilename()
        pdf_to_text(data)
        # print(datas)
        print(" Pdf converted to string")

        text_mp3()
        saved = "Mp3 file downloaded"
        redirect(url_for("index",saved=saved))
    return render_template("index.html",saved=saved)


if __name__ == "__main__":
    app.run(debug=True)
