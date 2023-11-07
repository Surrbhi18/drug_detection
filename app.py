from flask import Flask, send_file, request, jsonify
from PIL import Image
import pytesseract
import io
import pandas as pd

app = Flask(__name__)

# Read the list of medications from the CSV file
master_list_df = pd.read_csv('Master_list.csv')
medications = master_list_df['drug'].str.lower().tolist()

# Read the list of medications and diseases from the final CSV file
final_list_df = pd.read_csv('final.csv')
final_list = final_list_df.groupby('drug')['disease'].apply(set).to_dict()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    file = request.files['file']
    img = Image.open(io.BytesIO(file.read()))
    extracted_text = pytesseract.image_to_string(img).lower()  # Convert extracted text to lowercase

    found_words = list(set(word for word in medications if word in extracted_text))
    found_diseases = {word: list(final_list.get(word, [])) for word in found_words}

    # Remove duplicate diseases for each word
    for word in found_diseases:
        found_diseases[word] = list(set(found_diseases[word]))

    return jsonify({'extracted_text': extracted_text, 'found_words': found_words, 'found_diseases': found_diseases})

if __name__ == '__main__':
    app.run()
