# -------------------//// Note input pdf should contain text less than 2000 characters////-------------------#

# Environment variables
import os

# for saving file locally in server
from werkzeug.utils import secure_filename

# Flask App
from flask import Flask, render_template, redirect, url_for, request, send_from_directory

# Api request
import requests

# PDF to Text imports
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
    pdf_resource_manager = PDFResourceManager()
    laparams = LAParams()
    stringio = io.StringIO()

    text = TextConverter(pdf_resource_manager, stringio, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(pdf_resource_manager, text)

    # Process each page contained in the document.
    for page in PDFPage.get_pages(data):
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
    with open("static/files/output.mp3", "wb") as out:
        out.write(response.content)
        print('Audio content written to file "output.mp3"')


@app.route('/', methods=["GET", "POST"])
def index():
    saved = request.args.get("saved")
    if saved is None:
        saved = ""
    if request.method == "POST":
        data = request.files["file"]
        # print(data)
        # print(type(data))

        data.save(secure_filename(data.filename))
        print('file uploaded successfully')

        pdf_to_text(data)
        # print(datas)
        print(" Pdf converted to string")

        text_mp3()
        saved = "(Output) Mp3 file downloaded"

        file_name = data.filename.replace(" ", "_")
        os.remove(file_name)
        return redirect(url_for("download"))
        # render_template("index.html", saved=saved)
    return render_template("index.html")


@app.route('/download')
def download():
    return send_from_directory(directory='static/files', path="output.mp3", as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True)
