import sys

from waitress import serve

from flask import Flask, render_template, redirect, request, jsonify

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TooManyRequests, TranscriptsDisabled, NoTranscriptAvailable

from summarizer import summarize_text

from pdf_handler import pdf2text

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField

from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'files'


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload")


def unicodetoascii(text):
    TEXT = (text.
            replace('\\xe2\\x80\\x99', "'").
            replace('\\xc3\\xa9', 'e').
            replace('\\xe2\\x80\\x90', '-').
            replace('\\xe2\\x80\\x91', '-').
            replace('\\xe2\\x80\\x92', '-').
            replace('\\xe2\\x80\\x93', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x98', "'").
            replace('\\xe2\\x80\\x9b', "'").
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9d', '"').
            replace('\\xe2\\x80\\x9e', '"').
            replace('\\xe2\\x80\\x9f', '"').
            replace('\\xe2\\x80\\xa6', '...').
            replace('\\xe2\\x80\\xb2', "'").
            replace('\\xe2\\x80\\xb3', "'").
            replace('\\xe2\\x80\\xb4', "'").
            replace('\\xe2\\x80\\xb5', "'").
            replace('\\xe2\\x80\\xb6', "'").
            replace('\\xe2\\x80\\xb7', "'").
            replace('\\xe2\\x81\\xba', "+").
            replace('\\xe2\\x81\\xbb', "-").
            replace('\\xe2\\x81\\xbc', "=").
            replace('\\xe2\\x81\\xbd', "(").
            replace('\\xe2\\x81\\xbe', ")"))
    return TEXT

# Function to get transcript using video ID
def get_yt_video_id(id):
    transcript = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
    transcript_text = ''

    for text in transcript:
        transcript_text += text['text']

    transcript_text = unicodetoascii(transcript_text)

    summary = summarize_text(transcript_text)

    return summary
    # chunks = text_processing(transcript_text)
    # summary = summarize_text(chunks)
    # return summary


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        if request.form['submit_button'] == 'YT TRANSCRIPT SUMMARIZER':
            return redirect('yt')
        elif request.form['submit_button'] == 'PDF SUMMARIZER':
            return redirect('pdf')

    return render_template("root.html")


@app.route("/yt", methods=["GET", "POST"])
def yt_landing_page():
    if request.method == "POST":
        url = str(request.form.get("url"))
        if url:
            try:
                if '=' in url:
                    video_id = str(url.split("=")[1])
                else:
                    video_id = str(url.split("/")[3])
                text = get_yt_video_id(video_id)
                return render_template("result.html", text_here=text)


                # Catching Exceptions

            except VideoUnavailable:
                return jsonify(success=False, message="VideoUnavailable: The video is no longer available.",
                               response=None), 400

            except TooManyRequests:
                return jsonify(success=False, message="TooManyRequests: YouTube is receiving too many requests from "
                                                      "this IP."" Wait until the ban on server has been lifted.",
                               response=None), 500

            except TranscriptsDisabled:
                return jsonify(success=False, message="TranscriptsDisabled: Subtitles are disabled for this video.",
                               response=None), 400

            except NoTranscriptAvailable:
                return jsonify(success=False, message="NoTranscriptAvailable: No transcripts are available for this "
                                                      "video.",
                               response=None), 400

            except NoTranscriptFound:
                return jsonify(success=False, message="NoTranscriptAvailable: No transcripts were found.",
                               response=None), 400

            except Exception as e:
                # Prevent server error by returning this message to all other un-expected errors.
                print(e)
                sys.stdout.flush()

                return jsonify(success=False,
                               message="Some error occurred."
                                       " Contact the administrator if it is happening too frequently.",
                               response=None), 500

    return render_template("yt.html")


@app.route("/pdf", methods=["GET", "POST"])
def pdf_text_try():
    form = UploadFileForm()

    if form.validate_on_submit():
        file = form.file.data  # First grab the file
        text = pdf2text(file)
        text = unicodetoascii(text)
        summary = summarize_text(text)
        return render_template('result.html', text_here=str(summary))
        # file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
        #                        secure_filename(file.filename)))  # Then save the file
        # return "File has been uploaded."

    return render_template('pdf.html', form=form)


# @app.route("/result", methods=["GET","POST"])
# def show_result(summary):
#    return render_template('result.html', textHere = str(summary))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
