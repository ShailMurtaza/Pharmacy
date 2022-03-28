#!/usr/bin/python
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask import Flask, render_template, request, redirect, Markup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
# from tabulate import tabulate
import new_csv
# from fpdf import FPDF
import os
import logging
from random import randint

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any random string'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
db = SQLAlchemy(app)
wd = os.path.dirname(__file__)


class Pharmacy(db.Model):
    __tablename__ = "Pharmacy"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    medicines = db.Column(db.String(100), nullable=False)
    formula = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.String(20))
    date_expiry = db.Column(db.String(20))
    details = db.Column(db.Text, default="NOT ADDED!")
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)


class Category(db.Model):
    __tablename__ = "Category"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    category = db.Column(db.String(100))


class Revenue(db.Model):
    __tablename__ = "Revenue"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    revenue = db.Column(db.Integer)
    date = db.Column(db.String(20))


##############################################
admin = Admin(app)
admin.add_view(ModelView(Pharmacy, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Revenue, db.session))
##############################################


@app.route('/', methods=['GET', 'POST'])
def index():
    medicines_list = Pharmacy.query.order_by(Pharmacy.id).all()
    check_expiry = Pharmacy.query.filter(Pharmacy.date_expiry <= date.today())
    p = []
    for i in check_expiry:
        p.append(i)
    m = []
    for i in range((len(p))):
        for x in range((len(medicines_list))):
            if p[i].id == medicines_list[x].id:
                m.append(x + 1)
                break
            else:
                continue
    expired_or_not = []
    for i in range(len(medicines_list)):
        for x in m:
            if x == i + 1:
                shail = "hacker"
                break
            else:
                shail = ""
        if shail:
            new = ("Expired")
            expired_or_not.append(new)
        else:
            new = ("Not Expired")
            expired_or_not.append(new)
    hide = {"Medicines": " ", "formula": " ", "category": " ", "date_created": " ",
            "date_expiry": " ", "status": " ", "details": " ", "actions": " ", "quantity": " ", "price": " "}
    checked_keys = []
    for i in hide:
        checked_keys.append(i)
    if request.method == 'POST':
        shail = request.form
        for i, x in shail.items():
            hide[i] = x
        f = open(wd + "\\static\\checkbox", "w")
        m = []
        for i in hide.values():
            if i != " ":
                f.write("checked" + ',')
                m.append("checked")
            else:
                f.write(" ,")
                m.append(" ")
        f.close()
        checked = dict(zip(checked_keys, m))
        return render_template('index.html', l=medicines_list, expired_or_not=expired_or_not, hide=hide, checked=checked)
    f = open(wd + "\\static\\checkbox", 'r')
    m = (f.read().split(","))
    f.close()
    m.pop()
    checked = dict(zip(checked_keys, m))
    kk = []
    for i in m:
        if i == "checked":
            kk.append("hide")
        else:
            kk.append(" ")
    hide = dict(zip(checked_keys, kk))
    return render_template('index.html', l=medicines_list, expired_or_not=expired_or_not, hide=hide, checked=checked)


@app.route('/search', methods=["POST", "GET"])
def search():
    return render_template('search.html')


@app.route('/add_data', methods=["POST", "GET"])
def add_data():
    if request.method == "POST":
        medicine_name = request.form['medicine_name'].title()
        medicine_formula = request.form['medicine_formula']
        medicine_category = request.form['medicine_category']
        medicine_manufacture_date = request.form['medicine_manufacture_date']
        medicine_expiry_date = request.form['medicine_expiry_date']
        medicine_details = request.form['medicine_details']
        medicine_quantity = request.form['medicine_quantity']
        medicine_price = request.form['medicine_price']
        if not medicine_quantity:
            medicine_quantity = 0
        if not medicine_price:
            medicine_price = 0
        add_data = Pharmacy(medicines=medicine_name, formula=medicine_formula, date_created=medicine_manufacture_date,
                            date_expiry=medicine_expiry_date, details=medicine_details, category=medicine_category, quantity=medicine_quantity, price=medicine_price)
        db.session.add(add_data)
        db.session.commit()
        return redirect('/')
    path = "add_data"
    categories = Category.query.all()
    return render_template('add_data.html', path=path, d="", cat=categories)


@app.route('/pharmacy/delete/<int:post_id>')
def post_delete(post_id):
    delete_data = Pharmacy.query.get(post_id)
    db.session.delete(delete_data)
    db.session.commit()
    return redirect('/')


@app.route('/pharmacy/update/<int:post_id>', methods=['GET', 'POST'])
def post_update(post_id):
    update_data = Pharmacy.query.get(post_id)
    if request.method == 'POST':
        update_data.medicines = request.form['medicine_name'].title()
        update_data.formula = request.form['medicine_formula']
        update_data.category = request.form['medicine_category']
        update_data.date_created = request.form['medicine_manufacture_date']
        update_data.date_expiry = request.form['medicine_expiry_date']
        update_data.details = request.form['medicine_details']
        update_data.quantity = request.form['medicine_quantity']
        update_data.price = request.form['medicine_price']
        if not update_data.quantity:
            update_data.quantity = 0
        if not update_data.price:
            update_data.price = 0
        db.session.commit()
        return redirect('/')
    path = ''
    d = {"medicines": update_data.medicines, "formula": update_data.formula, "created": update_data.date_created,
         "expiry": update_data.date_expiry, "details": update_data.details, "category": update_data.category, "quantity": update_data.quantity, "price": update_data.price}
    categories = Category.query.all()
    return render_template('add_data.html', update_data=update_data, path=path, d=d, cat=categories)


@app.route('/category', methods=["POST", "GET"])
def category():
    if request.method == "POST":
        medicine_category = request.form['medicine_category'].title()
        add_category = Category(category=medicine_category)
        db.session.add(add_category)
        db.session.commit()
        return redirect('/category')
    categories = Category.query.all()
    return render_template('category.html', l=categories)


@app.route('/category/delete/<int:post_id>')
def category_delete(post_id):
    delete_data = Category.query.get(post_id)
    db.session.delete(delete_data)
    db.session.commit()
    return redirect('/category')


@app.route('/category/update/<int:post_id>', methods=['POST'])
def category_update(post_id):
    update_data = Category.query.get(post_id)
    update_data.category = request.form['medicine_category'].title()
    db.session.commit()
    return redirect("/category")


def display_bill_table():
    data = new_csv.csv_file_reader(wd + "\\static\\bills\\bill.csv")
    # data.pop(0)
    # table = "<table class=table><tr><th class=table>{0[0][0]}</th><th>{0[0][1]}</th><th>{0[0][2]}</th></tr>".format(
    #     data)
    table = "<table class=table1><tr class=table1><th class=table1>Medicines</th><th class=table1>Discount</th><th class=table1>Quantity</th><th class=table1>Price</th></tr>"
    try:
        for i in data[1:]:
            table = table + \
                "<tr class=table1><td class=table1>{s[0]}</td><td class=table1>{s[1]}</td><td class=table1>{s[2]}</td><td class=table1>{s[3]}</td></tr>".format(
                    s=i)
    except:
        pass
    table += "</table>"
    return Markup(table)


@app.route('/initialize_billing')
def initialize_billing():
    f = open(wd + "\\static\\bills\\bill.csv", "w")
    f.close()
    return redirect("/billing")


def advance_billing(mode, medi_name, discount, price, quantity, customer_name=""):
    if mode == "w":
        f = open(wd + "\\static\\bills\\bill.csv", "r")
        data = f.read()
        f.close()
        f = open(wd + "\\static\\bills\\bill.csv", mode)
        f.write(customer_name + "\n")
        f.write(data)
    else:
        f = open(wd + "\\static\\bills\\bill.csv", mode)
    """
    if len(medi_name) >= 15:
        l = []
        for i in medi_name:
            l.append(i)
        for i in range((len(medi_name)/15)+1):
            try:
                l.insert(i*15, ",,\n")
            except:
                continue
        l.pop(0)
        new_medi_name = "".join(l)
    else:
        new_medi_name = medi_name
    """
    new_medi_name = medi_name
    f.write(new_medi_name + "," + discount + "," + quantity + "," + price + "\n")
    f.close()


def csv_reader():
    f = open(wd + "\\static\\bills\\bill.csv")
    data = f.read()
    f.close()
    return data


def billing_part():
    table = display_bill_table()
    data = csv_reader()
    medi_names = Pharmacy.query.all()
    return (table, data, medi_names)


def del_pdf():
    path = wd + "\\static\\bills\\"
    all_list = os.listdir(path)
    pdf_list = [pdf for pdf in all_list if pdf.endswith(".pdf")]
    for i in pdf_list:
        remove = (os.path.join(path, i))
        os.remove(remove)


@app.route('/billing', methods=['GET', 'POST'])
def billing():
    del_pdf()
    table = billing_part()[0]
    data = billing_part()[1]
    medi_names = billing_part()[2]
    if request.method == 'POST':
        try:
            customer_name = request.form['Customer Name'].title()
        except(KeyError):
            customer_name = ""
        medi_data = request.form['Name'].split(" | ")
        medi_name = medi_data[0].title()
        discount = (request.form['Discount'] + "%")
        medi_quantity = int(medi_data[1])
        price = medi_data[2]
        quantity = int(request.form['Quantity'])

        update_data = Pharmacy.query.filter(
            Pharmacy.quantity == medi_quantity, Pharmacy.medicines == medi_name).first()
        update_data.quantity = (medi_quantity - quantity)
        db.session.commit()

        # if medi_name and str(price) and str(quantity) and not customer_name:
        if not customer_name:
            advance_billing("a", medi_name, discount, str(price), str(quantity))
            table = billing_part()[0]
            data = billing_part()[1]
            medi_names = billing_part()[2]
            return render_template("billing.html", table=table, data=data, medi_names=medi_names)
        # elif medi_name and str(price) and str(quantity) and customer_name:
        else:
            advance_billing("w", medi_name, discount, str(price), str(quantity), customer_name)
            table = billing_part()[0]
            data = billing_part()[1]
            medi_names = billing_part()[2]
            return render_template("billing.html", table=table, data=data, medi_names=medi_names)
    return render_template("billing.html", table=table, data=data, disable="not disable", medi_names=medi_names)


@app.route('/update_bill', methods=["POST", 'GET'])
def update_bill():
    try:
        l = []
        data = request.form['data'].replace('\r', "")
        check_data = new_csv.csv_data_reader(data)
        check_data.pop(0)
        for i in check_data:
            l.append(len(i))
        for i in (l):
            if i != 4:
                return "An error has been occured<br><a href='/billing'>GO BACK!</a>"
        with open(wd + "\\static\\bills\\bill.csv", "w") as f:
            f.write(data)
    except:
        pass
    table = display_bill_table()
    data = csv_reader()
    medi_names = Pharmacy.query.all()
    return render_template('billing.html', table=table, data=data, medi_names=medi_names)


@app.route('/display/bill')
def display_bill_text():
    total = []
    discount = []
    date_time = datetime.now()
    with open(wd + '\\static\\bills\\bill_starter.txt', 'r') as f:
        bill_starter = Markup(f.read())
    with open(wd + '\\static\\bills\\bill_ender.txt', 'r') as f:
        bill_ender = Markup(f.read())
    raw_bill = new_csv.csv_file_reader(wd + "\\static\\bills\\bill.csv")
    # bill.pop(1)
    for i in raw_bill[1:]:
        price = int(i[2]) * int(i[3])
        total.append(price)
        discount_per = int(i[1].replace("%", ""))
        discount.append(price - (discount_per * price) / 100)
    total = sum(total)
    discount = sum(discount)
    return render_template('bill.html', bill=raw_bill, date_time=date_time, bill_starter=bill_starter, bill_ender=bill_ender, total=total, discount=discount)


def create_pdf(bill):
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times")
    pdf.multi_cell(100, 5, txt=bill)
    pdf.output("\\static/bills/bill.pdf")
    """
    global name_num
    while True:
        with open(wd + '\\static\\bills\\pdf_make_name', "r") as f:
            name_num_before = f.read()
            name_num = (str(randint(0, 999999999)) + ".pdf")
            if not name_num_before == name_num:
                break
    with open(wd + '\\static\\bills\\pdf_make_name', "w") as f:
        f.write(name_num)
    f = open(wd + "\\static\\bills\\pdf_make_command", "r")
    pdf_make_command = ('"' + wd + '\\' + f.read().replace("\n", "") + name_num)
    f.close()
    # pdf_make = ("wkhtmltopdf " + str(address) + " \\static/bills/bill.pdf")
    os.system(pdf_make_command)
    # os.system("xpdf \\static/bills/bill.pdf")


@app.route('/done_billing')
def done_billing():
    bill = Markup(display_bill_text())
    create_pdf(bill)
    # fpdf.multi_cell(w: float, h: float, txt: str, border = 0, align: str = 'J', fill: bool = False)
    return render_template('done_billing.html', bill=bill, name_num=name_num)


@app.route('/bill_editor', methods=['GET', 'POST'])
def bill_editor():
    """
    header = ('Medicines', 'Quantity', 'Price')
    table = [['Example', 1, 100], ['-----------', '-----------', '-----------'], ['Example', 2, 100]]
    bill_preveiw = ("CUSTOMER NAME  ::::::  Customer Name\nDate And Time 2000-01-01 12:00:00.0000\n" +
                    (tabulate(table, headers=header, tablefmt="pretty")) + "\nTOTAL ===================  300")
    """
    if request.method == 'POST':
        bill_starter = request.form['bill_starter']
        bill_ender = request.form['bill_ender'].encode("utf-8")
        # return bill_ender
        with open(wd + '\\static\\bills\\bill_starter.txt', 'w') as f:
            f.write(bill_starter)
        with open(wd + '\\static\\bills\\bill_ender.txt', 'w') as f:
            f.write(bill_ender)
        return redirect('/bill_editor')
    with open(wd + '\\static\\bills\\bill_starter.txt', 'r') as f:
        bill_starter = Markup(f.read())
    with open(wd + '\\static\\bills\\bill_ender.txt', 'r') as f:
        bill_ender = Markup(f.read().decode('utf-8'))
    # bill_preveiw = (bill_starter + bill_preveiw + '\n' + bill_ender + '\nCREATED BY SHAIL')
    # return bill_ender
    return render_template('bill_editor.html', bill_starter=bill_starter, bill_ender=bill_ender)


@app.route('/close')
def close():
    os.system("taskkill /F /pid " + str(os.getpid()))


if __name__ == '__main__':
    app.run(debug=True)
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=8080)
