from flask import Flask, render_template, request
from utils import generate_chapter_summaries

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    summaries = []
    if request.method == 'POST':
        url = request.form['book_url']
        try:
            summaries = generate_chapter_summaries(url)
        except Exception as e:
            print(f"Error: {e}")
    return render_template('index.html', summaries=summaries)

if __name__ == '__main__':
    app.run(debug=True)