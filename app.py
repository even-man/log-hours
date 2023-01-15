from flask import Flask, render_template, request, redirect, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import datetime
from decimal import Decimal


# from logging.config import dictConfig

# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })



app = Flask(__name__)

db_name = 'data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.app_context().push()

class shifts(db.Model):
    shift_number = db.Column(db.Integer, primary_key = True, nullable=False)
    shift_date = db.Column(db.DateTime, nullable = False)
    shift_hours = db.Column(db.Float, nullable = False)
    shift_earned = db.Column(db.Float, nullable = False)

    def __repr__(self) -> str:
        return '<Name %r>' % self.id

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    shiftList = shifts.query.order_by(shifts.shift_date)

    totalHours = 0
    totalEarned = 0
    totalShifts = 0

    print(shiftList)

    for shift in shiftList:
        totalHours += shift.shift_hours
        totalEarned += shift.shift_earned
        totalShifts += 1

    averageEarned = totalEarned / totalShifts
    averageEarned = '{:.2f}'.format(averageEarned)

    return render_template('index.html', shiftList=shiftList, totalHours=totalHours, totalEarned=totalEarned, totalShifts=totalShifts, averageEarned=averageEarned)

@app.route('/log-hours/', methods=['GET', 'POST'])
def log():

    if request.method == 'POST':

        shift_date = datetime.datetime.strptime(request.form.get('shiftDate'), r'%Y-%m-%d')
        shift_hours = float(request.form.get('shiftHours'))
        shift_earned = shift_hours * float(request.form.get('toplevelWages'))

        new_shift = shifts( shift_date=shift_date, shift_hours=shift_hours, shift_earned=shift_earned)
        app.logger.info(new_shift.shift_number)

        try:
            db.session.add(new_shift)
            db.session.commit()
            # flash('success')
            return redirect('/log-hours')

        except:
            return 'error adding data'

    if request.method == 'GET':
        return render_template('log.html')

@app.route('/delete/<int:code>')
def delete(code):
    item = shifts.query.filter_by(shift_number=code).first()

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/')
    except:
        return 'error deleting'

@app.route('/update/<int:code>', methods=['GET', 'POST'])
def update(code):

    shift = shifts.query.filter_by(shift_number = code).first()

    if request.method == 'POST':
        shift.shift_date = datetime.datetime.strptime(request.form.get('shiftDate'), r'%Y-%m-%d')
        shift.shift_hours = float(request.form.get('shiftHours'))
        shift.shift_earned = shift.shift_hours * float(request.form.get('toplevelWages'))

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'error updating item'


    if request.method == 'GET':
        return render_template('update.html', shift=shift)

if __name__ == "__main__":
    app.run(debug=True)
