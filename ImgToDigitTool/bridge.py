from flask import Flask, request, jsonify
from flask_cors import CORS
from googleAPI import detect_text_uri

app = Flask(__name__)
CORS(app)

@app.route('/detect-text', methods=['POST'])
def handle_detect_text():
    data = request.get_json()
    image_url = data.get('imageUrl')
    if not image_url:
        return jsonify({'error': 'Missing imageUrl'}), 400

    try:
        text_description = detect_text_uri(image_url)  # 调用文字识别函数
        return jsonify({'result': text_description}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
