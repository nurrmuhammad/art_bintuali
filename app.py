import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = 'static/uploads'
GALLERY_FILE = 'data/gallery.json'

CATEGORIES = ["art_colligrafiya", "dekorativniy", "naqqoshlik"]

# === TELEGRAM BOT SOZLAMALARI ===
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
# @userinfobot orqali olingan yoki guruh uchun -100... ko‘rinishida
def send_telegram_order(name, phone, desc):
    text = (
        f"🖼 <b>Yangi buyurtma!</b>\n"
        f"<b>Ism:</b> {name}\n"
        f"<b>Telefon:</b> {phone}\n"
        f"<b>Izoh:</b> {desc}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    print("==== TELEGRAMGA YUBORILAYAPTI ====")
    print("URL:", url)
    print("DATA:", data)
    r = requests.post(url, data=data)
    print("==== TELEGRAM JAVOB ====")
    print(r.status_code)
    print(r.text)
    return r

def load_gallery():
    if not os.path.exists(GALLERY_FILE):
        return []
    with open(GALLERY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_gallery(gallery):
    with open(GALLERY_FILE, 'w', encoding='utf-8') as f:
        json.dump(gallery, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    gallery = load_gallery()
    cat = request.args.get('cat')
    categories = CATEGORIES
    if cat and cat in categories:
        filtered_gallery = [g for g in gallery if g.get('category') == cat]
    else:
        filtered_gallery = gallery
    return render_template('gallery.html', gallery=filtered_gallery, categories=categories, cat=cat)

@app.route('/detail/<int:id>')
def detail(id):
    gallery = load_gallery()
    art = gallery[id]
    return render_template('detail.html', art=art)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        desc = request.form['desc']
        # TELEGRAMGA YUBORISH
        resp = send_telegram_order(name, phone, desc)
        if resp.status_code == 200:
            flash('Buyurtmangiz muvaffaqiyatli yuborildi!', 'success')
        else:
            flash('Telegramga yuborishda xatolik: ' + resp.text, 'danger')
        return redirect(url_for('order'))
    return render_template('order.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    gallery = load_gallery()
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        desc = request.form['desc']
        category = request.form['category']
        if file and file.filename:
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            gallery.append({'filename': filename, 'title': title, 'desc': desc, 'category': category})
            save_gallery(gallery)
            flash('Rasm muvaffaqiyatli yuklandi!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Rasm fayli tanlanmadi!', 'danger')
    categories = CATEGORIES
    return render_template('admin.html', gallery=gallery, categories=categories)

@app.route('/admin/delete/<int:id>')
def delete(id):
    gallery = load_gallery()
    art = gallery.pop(id)
    file_path = os.path.join(UPLOAD_FOLDER, art['filename'])
    if os.path.exists(file_path):
        os.remove(file_path)
    save_gallery(gallery)
    flash('Rasm o‘chirildi!', 'warning')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)
