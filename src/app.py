from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/hello/<name>')
def root(name):
    query_value = request.args.get('foo-query')
    header_value = request.headers.get('foo-header')
    return jsonify({'name': name,
                    'query': query_value,
                    'header': header_value})


@app.route('/send', methods=['POST'])
def send():
    form_value = request.form['foo-form']
    query_value = request.args.get('foo-query')
    header_value = request.headers.get('foo-header')
    return jsonify({'query': query_value,
                    'form': form_value,
                    'header': header_value})


if __name__ == '__main__':
    app.run(port=8000, debug=True)
