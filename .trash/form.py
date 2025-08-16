from flask import Flask, render_template, request, redirect, url_for
import json
import os
import math
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
DATA_FILE = 'data.json'
ITEMS_PER_PAGE = 5

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def form():
    data = load_data()

    if request.method == 'POST':
        question = request.form['question']
        keywords = request.form['keywords'].split(',')
        answer = request.form['answer']
        edit_index = request.form.get('edit_index')

        new_entry = {
            "question": question.strip(),
            "keywords": [k.strip() for k in keywords],
            "answer": answer.strip()
        }

        if edit_index != "":
            data[int(edit_index)] = new_entry
        else:
            data.append(new_entry)

        save_data(data)
        return redirect(url_for('form'))

    # Pagination
    page = int(request.args.get('page', 1))
    reversed_data = list(reversed(data))
    total_pages = math.ceil(len(reversed_data) / ITEMS_PER_PAGE)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_data = reversed_data[start:end]

    return render_template('form.html',
                           data=page_data,
                           full_data=reversed_data,
                           page=page,
                           total_pages=total_pages)

@app.route('/edit/<int:index>')
def edit(index):
    data = load_data()

    if 0 <= index < len(data):
        entry = data[index]
        reversed_data = list(reversed(data))
        total_pages = math.ceil(len(reversed_data) / ITEMS_PER_PAGE)
        page_data = reversed_data[:ITEMS_PER_PAGE]

        return render_template('form.html',
                               data=page_data,
                               full_data=reversed_data,
                               edit_entry=entry,
                               edit_index=index,
                               page=1,
                               total_pages=total_pages)
    else:
        return redirect(url_for('form'))

@app.route('/delete/<int:index>')
def delete(index):
    data = load_data()
    if 0 <= index < len(data):
        data.pop(index)
        save_data(data)
    return redirect(url_for('form'))

@app.route('/import_excel', methods=['GET', 'POST'])
def import_excel():
    if request.method == 'POST':
        file = request.files['excel_file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_excel(filepath)

            new_data = []
            for _, row in df.iterrows():
                question = str(row.get('question', '')).strip()
                answer = str(row.get('answer', '')).strip()
                keywords = [kw.strip() for kw in str(row.get('keywords', '')).split(',')]

                if question and answer:
                    new_data.append({
                        "question": question,
                        "keywords": keywords,
                        "answer": answer
                    })

            existing_data = load_data()
            existing_data.extend(new_data)
            save_data(existing_data)

            return redirect(url_for('form'))

    return render_template('import_excel.html')


if __name__ == '__main__':
    app.run(debug=True)
