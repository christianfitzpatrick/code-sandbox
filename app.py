'''
Simple Flask API wrapper for code execution logic

Pointing your browser at '/' renders a simple static page for uploading code
Extremely barebones; just used as a front-end for demonstration purposes

Most testing was done via cURL
'''

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from runtime_utils import DockerRunJob, DockerBuildJob, COMPILERS, RUNTIMES, HOST_DIR

app = Flask(__name__)


@app.route('/')
def index():
    ''' render static file upload page '''
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    ''' save, run, and return code execution results '''
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(f'{HOST_DIR}/{filename}')

    filetype = filename.split('.')[-1]

    if filetype in RUNTIMES:
        job = DockerRunJob(uploaded_file.filename)
        out = job.run()
    elif filetype in COMPILERS:
        job = DockerBuildJob(uploaded_file.filename)
        out = job.build_and_run()

    return out
    #  return render_template('output.html', output=out)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
