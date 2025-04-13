from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

def caesar_cipher(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            shifted = ord(char) + shift
            if char.islower():
                if shifted > ord('z'):
                    shifted -= 26
                elif shifted < ord('a'):
                    shifted += 26
            else:
                if shifted > ord('Z'):
                    shifted -= 26
                elif shifted < ord('A'):
                    shifted += 26
            result += chr(shifted)
        else:
            result += char
    return result

@app.route('/cipher', methods=['POST'])
def cipher():
    data = request.get_json()
    original_text = data.get('text', '')
    ciphered_text = caesar_cipher(original_text)
    return jsonify({'original': original_text, 'ciphered': ciphered_text})

if __name__ == '__main__':
    app.run(debug=True)