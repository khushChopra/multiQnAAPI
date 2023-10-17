from flask import Flask, request, send_file
from zania import AnsweringWizard
from uuid import uuid4
import os
import tempfile
import json
OPEN_API_KEY = os.environ.get("OPEN_API_KEY")
FILE_STORE_LOCATION = "temp"

app = Flask(__name__)

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

@app.route("/", methods=["POST"])
def process_files():
    # Check if the POST request contains two files with the names "questions" and "document"
    if "questions" not in request.files or "document" not in request.files:
        return "Two files must be provided.", 400

    questions = request.files["questions"]
    document = request.files["document"]

    # Check if the files have valid extensions
    allowed_extensions = {'json', 'pdf'} 
    if not questions.filename.lower().endswith(tuple(allowed_extensions)) or \
            not document.filename.lower().endswith(tuple(allowed_extensions)):
        return 'Invalid file format. Supported formats: json, pdf', 400
    
    # Same them in temp folder to process
    ensure_directory_exists(FILE_STORE_LOCATION)
    questions_file_name = os.path.join(FILE_STORE_LOCATION, str(uuid4())+questions.filename)
    document_file_name = os.path.join(FILE_STORE_LOCATION, str(uuid4())+document.filename)
    questions.save(questions_file_name)
    document.save(document_file_name)

    # Generate answers and save it in a temp file
    res = AnsweringWizard(document_file_name, questions_file_name, OPEN_API_KEY).get_answers()
    os.remove(questions_file_name)
    os.remove(document_file_name)
    temp = tempfile.TemporaryFile()
    temp.write(json.dumps({"result": res}).encode())
    temp.seek(0)
    return send_file(temp, as_attachment=True, download_name='data.json')

if __name__ == '__main__':
    app.run(debug=True, port=8000)


