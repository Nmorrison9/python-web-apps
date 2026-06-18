from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import pgeocode

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        email      = request.form.get('email')
        subject    = request.form.get('subject')
        message    = request.form.get('message')

        msg = Message(
            subject=f"Wood Works Contact: {subject}",
            recipients=[os.environ.get('MAIL_USERNAME')],
            body=f"From: {first_name} {last_name} <{email}>\n\n{message}",
            reply_to=email
        )
        try:
            mail.send(msg)
            flash('Your message was sent successfully!', 'success')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/check-zipcode')
def check_zipcode():
    user_zip = request.args.get('zipcode', '').strip()
    business_zip = os.environ.get('BUSINESS_ZIPCODE', '44417')

    dist = pgeocode.GeoDistance('us')
    distance = dist.query_postal_code(business_zip, user_zip)

    if distance != distance:  # NaN check
        return jsonify({'error': 'Invalid postcode. Please try a valid US zip code.'})

    miles = float(distance) * 0.621371
    in_range = bool(miles <= 100)

    return jsonify({
        'in_range': in_range,
        'miles': round(miles, 1)
    })

if __name__ == '__main__':
    app.run(debug=True)