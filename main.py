from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os, uuid
from werkzeug.utils import secure_filename
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)

app.secret_key = '\x7f\xb0D\xfd}(\x1aP\xedt\xa5r^\xda\xa7tf\x1f\xf2V\x93\xf2n\x96'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lms'

mysql = MySQL(app)

def update_fine():
        cur = mysql.connection.cursor()
        cur.execute('select M_Id from borrow')
        l1=cur.fetchall()
        for j in l1:
            print(j[0])
            cur.execute(
                'select due_date from book inner join borrow on book.book_id= borrow.book_id where borrow.M_Id=%s',
                ([j[0]]))
            list1 = cur.fetchall()
            sum = 0
            for i in list1:
                mdate1 = date.today()
                rdate1 = i[0]
                delta = (mdate1 - rdate1).days
                print(delta)
                if delta > 30:
                    sum = sum + (delta - 30) * 10
            cur.execute('update lib_member set unpaid_fines=%s where M_Id=%s', (sum, j[0]))
        mysql.connection.commit()
        cur.close()

@app.route("/", methods=['GET', 'POST'])
def home():
    update_fine()
    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        isbn = request.form['isbn']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if title == "" and author == "" and category == "" and isbn == "":
            cur.execute(
                'SELECT ISBN, title, author, year_of_publication, category, image FROM book')
            result = cur.fetchall()

        elif title != "":
            if author == "" and category == "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s', [title])
                result = cur.fetchall()
            elif author == "" and category == "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and isbn = %s' ,
                    ([title], [isbn]))
                result = cur.fetchall()
            elif author == "" and category != "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and category = %s' ,
                    ([title], [category]))
                result = cur.fetchall()
            elif author == "" and category != "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and category = %s and isbn = %s' ,
                    ([title], [category], [isbn]))
                result = cur.fetchall()
            elif author != "" and category == "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and author = %s' ,
                    ([title], [author]))
                result = cur.fetchall()
            elif author != "" and category == "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and author = %s and isbn = %s',
                    ([title], [author],[isbn]))
                result = cur.fetchall()
            elif author != "" and category != "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and author = %s and category= %s',
                    ([title], [author], [category]))
                result = cur.fetchall()
            elif author != "" and category != "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where title = % s and author = %s and category = %s and isbn = %s',
                    ([title], [author], [category], [isbn]))
                result = cur.fetchall()

        elif title == "" and author!="":
            if category == "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where author = %s',
                    ([author]))
                result = cur.fetchall()
            elif category == "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where author = %s and isbn = %s',
                    ([author], [isbn]))
                result = cur.fetchall()
            elif category != "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where author = %s and category = %s',
                    ([author], [category]))
                result = cur.fetchall()
            elif category != "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where author = %s and category = %s and isbn = %s',
                     ([author], [category], [isbn]))
                result = cur.fetchall()

        elif title == "" and author == "":
            if category == "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where isbn = %s',
                     ([isbn]))
                result = cur.fetchall()
            elif category != "" and isbn == "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where category = %s',
                    ([category]))
                result = cur.fetchall()
            elif category != "" and isbn != "":
                cur.execute(
                    'SELECT ISBN, title, author, year_of_publication, category, image FROM book where category = %s and isbn = %s',
                    ([category], [isbn]))
                result = cur.fetchall()

        mysql.connection.commit()
        cur.close()
        if result:
            if 'loggedin' in session:

                return render_template('index.html', detail=result, msg="Result for the search",
                                       username=session['username'], email = session['email1'])
            else:
                return render_template('index.html', detail=result, msg="Result for the search", username="", email="")
        else:
            if 'loggedin' in session:

                return render_template('index.html', detail="No records found", username=session['username'], email = session['email1'])
            else:
                return render_template('index.html', detail="No records found", username="", email="")
    else:
        if 'loggedin' in session:

            return render_template('index.html', username=session['username'], email=session['email1'])
        else:
            return render_template('index.html', username="", email="")



@app.route("/update_profile/", methods=['GET', 'POST'])
def update_profile():
    update_fine()
    msg = ''
    if 'loggedin' in session:

        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            email = request.form['email']
            address = request.form['address']
            cpassword = request.form['cpassword']
            if len(name) > 0 and len(password) > 0 and len(email) > 0 and len(address) > 0 and len(cpassword) > 0:
                if (email[:3] == 'lib' and email[-11:] == "@iiti.ac.in"):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT * FROM librarian WHERE email = % s', (email,))
                    account = cursor.fetchone()
                    if account and account['email']!=session['email1']:
                        msg = 'Account already exists with this email!'
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Invalid email address !'
                    elif not name or not password or not email or not address or not cpassword or not address:
                        msg = 'Please fill out the form !'
                    elif cpassword != password:
                        msg = 'Confirm password does not match with password !'
                    else:
                        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        cursor.execute('update librarian set lib_password=%s where L_Id=%s',(hashed,[session['id'], ]))
                        if session['email1']!=email:
                            session['email1']=email
                            cursor.execute('update librarian set email=%s where L_Id=%s',(email,[session['id'], ]))
                        if session['username']!=name:
                            session['username']=name
                            cursor.execute('update librarian set lib_name=%s where L_Id=%s', (name,[session['id'], ]))
                        if session['address']!=address:
                            session['address']=address
                            cursor.execute('update librarian set address=%s where L_Id=%s', (address,[session['id'], ]))
                        mysql.connection.commit()
                        cursor.close()
                        msg = 'Your profile has been successfully updated !'
                elif (email[-11:] == "@iiti.ac.in"):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT * FROM lib_member WHERE email = % s', (email,))
                    account = cursor.fetchone()
                    if account and account['email']!=session['email1']:
                        msg = 'Account already exists with this email!'
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Invalid email address !'
                    elif not name or not password or not email or not address or not cpassword or not address:
                        msg = 'Please fill out the form !'
                    elif cpassword != password:
                        msg = 'Confirm password does not match with password !'
                    else:
                        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        cursor.execute('update lib_member set member_password=%s where M_Id=%s', (hashed,[session['id'], ]))
                        if session['email1'] != email:
                            session['email1'] = email
                            cursor.execute('update lib_member set email=%s where M_Id=%s', (email,[session['id'], ]))
                        if session['username'] != name:
                            session['username'] = name
                            cursor.execute('update lib_member set member_name=%s where M_Id=%s', (name,[session['id'], ]))
                        if session['address'] != address:
                            session['address'] = address
                            cursor.execute('update lib_member set address=%s where M_Id=%s', (address,[session['id'], ]))
                        mysql.connection.commit()
                        cursor.close()
                        msg = 'Your profile has been successfully updated !'
                else:
                    msg = 'Invalid email address, not a member of institute !'
            else:
                msg = 'Please fill out the form !'
        return render_template('update_profile.html', username=session['username'],msg=msg,email=session['email1'],address=session['address'])
    else:
        return redirect(url_for('login'))

@app.route("/login/", methods=['GET', 'POST'])
def login():
    update_fine()
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if len(email) > 0 and len(password) > 0:
            if (email[:3]=='lib'):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM librarian WHERE email = %s', (email,))
                account = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                if account and bcrypt.checkpw(password.encode('utf-8'), account['lib_password'].encode('utf-8')):
                    session['loggedin'] = True
                    session['id'] = account['L_Id']
                    session['username'] = account['lib_name']
                    session['email1'] = account['email']
                    session['address'] = account['address']
                    return redirect(url_for('lib_dashboard'))
                else:
                  msg = 'Incorrect email/password!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM lib_member WHERE email = %s', (email,))
                account = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                if account and bcrypt.checkpw(password.encode('utf-8'), account['member_password'].encode('utf-8')):
                    session['loggedin'] = True
                    session['id'] = account['M_Id']
                    session['username'] = account['member_name']
                    session['email1'] = account['email']
                    session['address'] = account['address']
                    return redirect(url_for('user_dashboard'))
                else:
                  msg = 'Incorrect email/password!'
        else:
            msg = ' Please fill the entries !'
    return render_template('login.html', msg=msg)

@app.route('/login/logout')
def logout():
    update_fine()
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email1', None)
    session.pop('address', None)

    return redirect(url_for('login'))

@app.route("/register/", methods=['GET', 'POST'])
def register():
    update_fine()
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']
        cpassword = request.form['cpassword']
        if len(name) > 0 and len(password) > 0 and len(email) > 0 and len(address) > 0 and len(cpassword) > 0:
            if (email[:3] == 'lib' and email[-11:]=="@iiti.ac.in"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM librarian WHERE email = % s', (email,))
                account = cursor.fetchone()
                if account:
                    msg = 'Account already exists with this email!'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address !'
                elif not name or not password or not email or not address or not cpassword or not address:
                    msg = 'Please fill out the form !'
                elif cpassword != password:
                    msg = 'Confirm password does not match with password !'
                else:
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute('INSERT INTO librarian VALUES (NULL, % s, % s, % s,% s)',
                                   ( name, hashed, address,email,))
                    mysql.connection.commit()
                    cursor.close()
                    msg = 'You have successfully registered !'
            elif (email[-11:]=="@iiti.ac.in"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM lib_member WHERE email = % s', (email,))
                account = cursor.fetchone()
                if account:
                    msg = 'Account already exists with this email!'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address !'
                elif not name or not password or not email or not address or not cpassword or not address:
                    msg = 'Please fill out the form !'
                elif cpassword != password:
                    msg = 'Confirm password does not match with password !'
                else:
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute('INSERT INTO lib_member VALUES (NULL, % s, % s, % s,% s, %s)',
                                   (hashed, name, address, 0, email,))
                    mysql.connection.commit()
                    cursor.close()
                    msg = 'You have successfully registered !'
            else:
                msg = 'Invalid email address, not a member of institute !'
        else:
            msg = 'Please fill out the form !'

    return render_template('register.html', msg=msg)


@app.route("/lib_dashboard/")
def lib_dashboard():
    update_fine()
    if 'loggedin' in session:

        return render_template('lib_dashboard.html', username=session['username'], email=session['email1'])
    return redirect(url_for('login'))

@app.route("/user_dashboard/")
def user_dashboard():
    update_fine()
    if 'loggedin' in session:

        return render_template('user_dashboard.html', username=session['username'], email=session['email1'])
    return redirect(url_for('login'))


@app.route("/remove_book/", methods=['GET', 'POST'])
def remove_book():
    update_fine()
    msg = ''
    if request.method == 'POST':
        book_id = request.form['book_id']
        isbn = request.form['isbn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select shelf_Id,count from book where book_id = %s', ([book_id]))
        a = cursor.fetchone()
        cursor.execute('select capacity from shelf where shelf_Id = %s', (a['shelf_Id'],))
        c = cursor.fetchone()
        if 1 <= int(a['count']):
            if int(a['count'])-1==0:
                cursor.execute('update shelf set shelf_status = %s where shelf_Id = %s',
                                    ('available', a['shelf_Id'],))
            cursor.execute('delete from book where book_id = %s', ([book_id]), )
            cursor.execute('update shelf set capacity = %s where shelf_Id = %s', (int(c['capacity'])+1,a['shelf_Id'], ))
            cursor.execute('update book set count = %s where ISBN = %s', (int(a['count']) - 1,[isbn], ))
            msg= 'Book removed successfully.'
        else:
            msg = 'Cannot remove books.'
        mysql.connection.commit()
        cursor.close()

    if 'loggedin' in session:

        email = session['email1']
        if email[:3] == 'lib':
            return render_template('remove_book.html', username=session['username'], msg=msg, email=session['email1'])
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route("/registeredusers/")
def registeredusers():
    update_fine()
    if 'loggedin' in session:

        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM lib_member")
        if resultValue > 0:
            userDetails = cur.fetchall()
            cur.execute('select M_Id2 from follower_following where M_Id1= %s',([session['id']],))
            list=cur.fetchall()
            l=[]
            for i in list:
                l.append(i[0])

            mysql.connection.commit()
            cur.close()
            return render_template('registeredusers.html', userDetails=userDetails, l =l, username=session['username'],
                                   email=session['email1'])
        else:
            return render_template('registeredusers.html', username="", email="")
    else:
        return render_template('login.html', username="", email="")




@app.route("/add_book/", methods=['GET', 'POST'])
def add_book():
    update_fine()
    msg = ''
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        year = request.form['year']
        category = request.form['category']
        file = request.files['file']
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)
        allowed_extensions = {'.jpg', '.png', '.jpeg'}
        if extension[1] in allowed_extensions:
            f_name = str(uuid.uuid4()) + str(extension[1])
            app.config['UPLOAD_FOLDER'] = 'static/Uploads'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor1.execute('select shelf_Id,capacity from shelf where capacity <> %s', (0,))
            s1 = cursor1.fetchone()
            print(s1)
            if s1:
                    p= cursor1.execute('select count from book where ISBN= %s limit 1',[isbn])
                    cursor1.execute('INSERT INTO book VALUES (NULL,%s, % s, % s, % s,% s,% s,% s,%s,%s,% s)',
                                (isbn, title, author, year, s1['shelf_Id'], p,0,category,'on shelf',f_name))
                    cursor1.execute('update shelf set capacity = %s where shelf_Id = %s', (s1['capacity']-1,s1['shelf_Id'],))
                    cursor1.execute('update book set count = %s where ISBN = %s',
                                    (p+1, [isbn],))
                    if p+1==75:
                        cursor1.execute('update shelf set shelf_status = %s where shelf_Id = %s',
                                    ('no space', s1['shelf_Id'],))
                    msg = 'Book added successfully'
            else:
                    msg = 'Cannot add books overflow.'
            mysql.connection.commit()
            cursor1.close()
        else:
            msg = 'Upload image in jpg/png/jpeg format only!'
    if 'loggedin' in session:

        email = session['email1']
        if email[:3] == 'lib':
            return render_template('add_book.html', username=session['username'], msg=msg, email=session['email1'])
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route("/books/", methods=['GET', 'POST'])
def books():
    update_fine()
    msg = ''
    cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor1.execute('select * from book ')
    details = cursor1.fetchall()
    mysql.connection.commit()
    cursor1.close()
    if 'loggedin' in session:

        return render_template('books.html', username=session['username'], msg=msg, detail=details,
                               email=session['email1'])
    else:
        return render_template('books.html', username="", msg=msg, detail=details, email="")

@app.route('/follow/<string:id>', methods=['GET', 'POST'])
def follow(id):
    update_fine()
    if 'loggedin' in session:

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print(id)
        cur.execute('insert into follower_following values (%s, %s)', (session['id'], id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('registeredusers'))
    else:
        return redirect(url_for('login'))

@app.route('/unfollow/<string:id>', methods=['GET', 'POST'])
def unfollow(id):
    update_fine()
    if 'loggedin' in session:

        cur = mysql.connection.cursor()
        cur.execute('delete from follower_following where M_Id2= %s', ( id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('registeredusers'))

    else:
        return redirect(url_for('login'))

@app.route('/borrow_book/<string:id>', methods=['GET', 'POST'])
def borrow_book(id):
    update_fine()
    msg=''
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select count(*) from borrow where M_Id=%s',[session['id'], ])
        c=cursor.fetchone()
        cursor.execute('select unpaid_fines from lib_member where M_Id=%s', [session['id'], ])
        g = cursor.fetchone();
        email=session['email1']
        if(email[:3]!='lib'):
            if (email[:7]!='faculty'):
              if(c['count(*)']>=3):
                msg='Oops!! you have already issued 3 books. You cannot issue more than 3 books.'
              elif g['unpaid_fines']>1000:
                  msg = 'Oops!! first pay the unpaid fines :('
              else:
                cursor.execute('select * from borrow where M_Id=%s and book_id=%s',([session['id'], ],[id, ]))
                flag=cursor.fetchone()
                if flag:
                    msg='Oops!! you can issue a particular book only one time until you return the same!'
                else:
                    start_date = date.today()
                    end_date = start_date + timedelta(15)
                    cursor.execute('insert into borrow values (%s,%s,%s,%s)',(session['id'],[id],start_date,end_date))
                    cursor.execute('insert into book_status values (%s,%s,%s)',(session['id'],[id],'borrowed'))
                    cursor.execute('update book set borrow_count =borrow_count+1 where book_id=%s',[id])
                    cursor.execute('update book set book_shelf_status="not on shelf" where book_id=%s', [id])
                    cursor.execute('update shelf set capacity =capacity+1 where shelf_Id=(select shelf_Id from book where book_id=%s)', [id])
                    msg='Book got issued succesfully! :)'
            else:
             cursor.execute('select * from borrow where M_Id=%s and book_id=%s', ([session['id'], ], [id, ]))
             flag = cursor.fetchone()
             if flag:
                msg = 'Oops!! you can issue a particular book only one time until you return the same!'
             elif g['unpaid_fines'] > 1000:
                 msg = 'Oops!! first pay the unpaid fines :('
             else:
                 start_date = date.today()
                 end_date = start_date + timedelta(15)
                 cursor.execute('insert into borrow values (%s,%s,%s,%s)', ([session['id']], [id], start_date, end_date))
                 cursor.execute('insert into book_status values (%s,%s,%s)', ([session['id']], [id], 'borrowed'))
                 cursor.execute('update book set borrow_count =borrow_count+1 where book_id=%s', [id])
                 cursor.execute('update book set book_shelf_status="not on shelf" where book_id=%s', [id])
                 cursor.execute(
                     'update shelf set capacity =capacity+1 where shelf_Id=(select shelf_Id from book where book_id=%s)',[id])
                 msg = 'Book got issued succesfully! :)'
        cursor.execute('select * from book ')
        details = cursor.fetchall()
        mysql.connection.commit()
        return render_template('books.html', username=session['username'],msg=msg,detail=details,email=email)
    else:
        return redirect(url_for('login'))

@app.route('/on_hold/<string:id>', methods=['GET', 'POST'])
def on_hold(id):
    update_fine()
    msg=''
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select count(*) from onhold where M_Id=%s',[session['id'], ])
        c=cursor.fetchone()
        email=session['email1']
        if(email[:3]!='lib'):
            if (email[:7]!='faculty'):
                cursor.execute('select * from onhold where M_Id=%s and book_id=%s',([session['id'], ],[id, ]))
                flag=cursor.fetchone()
                cursor.execute('select * from borrow where M_Id=%s and book_id=%s', ([session['id'], ], [id, ]))
                fl = cursor.fetchone()
                if flag:
                    msg='Oops!! you can put on hold a particular book only one time!'
                elif fl:
                    msg = 'Oops!! you have already borrowed that book!'
                else:
                    hold_date = date.today()
                    hold_time = datetime.now()
                    cursor.execute('insert into onhold values (%s,%s,%s,%s)',([session['id']],[id],hold_date,hold_time))
                    cursor.execute('insert into book_status values (%s,%s,%s)',([session['id']],[id],'onhold'))
                    cursor.execute('update book set book_shelf_status="not on shelf" where book_id=%s',[id])
                    msg='Book put on hold succesfully! :)'
            else:
             cursor.execute('select * from onhold where M_Id=%s and book_id=%s', ([session['id'], ], [id, ]))
             flag = cursor.fetchone()
             cursor.execute('select * from borrow where M_Id=%s and book_id=%s', ([session['id'], ], [id, ]))
             fl = cursor.fetchone()
             if flag:
                msg='Oops!! you can put on hold a particular book only one time!'
             elif fl:
                 msg = 'Oops!! you have already borrowed that book!'
             else:
                 hold_date = date.today()
                 hold_time = datetime.now()
                 cursor.execute('insert into onhold values (%s,%s,%s,%s)', ([session['id']], [id], hold_date, hold_time))
                 cursor.execute('insert into book_status values (%s,%s,%s)', ([session['id']], [id], 'onhold'))
                 cursor.execute('update book set book_shelf_status="not on shelf" where book_id=%s', [id, ])
                 msg = 'Book put on hold succesfully! :)'
        cursor.execute('select * from book ')
        details = cursor.fetchall()
        mysql.connection.commit()
        return render_template('books.html', username=session['username'],msg=msg,detail=details,email=email)
    else:
        return redirect(url_for('login'))

@app.route('/follower_following', methods=['GET', 'POST'])
def follower_following():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] != 'lib':
            cur = mysql.connection.cursor()
            cur.execute(
                'select member_name,M_Id from lib_member where M_Id in (select M_ID2 from follower_following where M_Id1= %s)',
                ([session['id']],))
            list = cur.fetchall()
            cur.execute(
            'select member_name from lib_member where M_Id in (select M_ID1 from follower_following where M_Id2= %s)',
            ([session['id']],))
            list1 = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            m = 0
            for i in list:
                m = m + 1
            l1 = []
            for i in list1:
                l1.append(i[0])
            return render_template('follower_following.html', username=session['username'], list=list, l1=l1, m=m,
                                   email=session['email1'])
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/shelf', methods=['GET', 'POST'])
def shelf():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select * from shelf ')
            list = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('shelf.html', username=session['username'],shelfDetails=list,email=session['email1'])
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_shelf', methods=['GET', 'POST'])
def edit_shelf():
    update_fine()
    msg = ''
    if request.method == 'POST':
        book_id = request.form['book_id']
        shelf_Id = request.form['shelf_Id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select shelf_Id from book where book_id = %s', [book_id,])
        a = cursor.fetchone()
        cursor.execute('select capacity, shelf_status from shelf where shelf_Id = %s', [shelf_Id,])
        c = cursor.fetchone()
        cursor.execute('select capacity, shelf_status from shelf where shelf_Id = %s', (a['shelf_Id'],))
        d = cursor.fetchone()

        if int(shelf_Id) == int(a['shelf_Id']):
            msg = 'Already in the same shelf.'
        else:
            if 1<=int(c['capacity']) and 74>=int(d['capacity']):
                cursor.execute('update book set shelf_Id=%s where book_id=%s', ([shelf_Id], [book_id]))
                cursor.execute('Update shelf set capacity=%s where shelf_Id=%s', (c['capacity'] - 1, [shelf_Id],) )
                cursor.execute('Update shelf set capacity=%s where shelf_Id=%s', (d['capacity'] + 1, a['shelf_Id'],) )
                if 0==int(c['capacity']):
                    cursor.execute('update shelf set shelf_status = %s where shelf_Id = %s',
                                ('no space', [shelf_Id],))
                msg = 'Shelf edited successfully.'
            else:
                msg = 'Cannot move the required book.'
        mysql.connection.commit()
        cursor.close()

    if 'loggedin' in session:
            email = session['email1']
            if email[:3] == 'lib':
                return render_template('edit_shelf.html', username=session['username'], msg=msg,
                                           email=session['email1'])
            else:
                return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/book_return/<string:id>', methods=['GET', 'POST'])
def book_return(id):
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] != 'lib':
            cur = mysql.connection.cursor()
            cur.execute('insert into approve_return values (%s,%s)',([session['id']],[id]))
            mysql.connection.commit()
            cur.close()
        return redirect(url_for('personal_bookshelf'))
    else:
        return redirect(url_for('login'))

@app.route('/return_book/', methods=['GET', 'POST'])
def return_book():
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select * from approve_return ')
            list = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('return_book.html', username=session['username'],returnbookdeatails=list,email=session['email1'])
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/approve_return/<string:id>', methods=['GET', 'POST'])
def approve_return(id):
    update_fine()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select count(*) from onhold where book_id=%s',[id, ])
        c=cursor.fetchone()
        cursor.execute('select M_Id from approve_return where book_id=%s', [id, ])
        v = cursor.fetchone()
        v = v['M_Id']
        cursor.execute('delete from approve_return where book_id=%s', [id, ])
        cursor.execute('select unpaid_fines from lib_member where M_Id=%s', (v, ))
        unpaidfines = cursor.fetchone()
        print(unpaidfines['unpaid_fines'])
        cursor.execute('select due_date from borrow where book_id=%s', ([id, ]))
        due_date = cursor.fetchone()
        print(due_date)
        email=session['email1']
        if(email[:3]=='lib'):


            if(c['count(*)']==0):
                cursor.execute('delete from book_status where book_id=%s and M_Id=%s', ([id],v))
                cursor.execute('delete from borrow where book_id=%s and M_Id=%s', ([id],v))
                cursor.execute('select count(*) from borrow where book_id=%s', [id, ])
                h=cursor.fetchone()
                if(h['count(*)']==0):
                   cursor.execute('update book set book_shelf_status="on shelf" where book_id=%s', [id])
                   cursor.execute(
                       'update shelf set capacity =capacity-1 where shelf_Id=(select shelf_Id from book where book_id=%s)',
                       [id, ])
                cursor.execute('update book set borrow_count =borrow_count-1 where book_id=%s',[id])
            else:
                cursor.execute('select M_Id, hold_date,hold_time from onhold where book_id=%s and M_Id in (select M_Id from lib_member where unpaid_fines<1000) order by hold_date,hold_time',[id, ])
                x=cursor.fetchall()
                if(x):
                   r=-1
                   for o in x:
                       cursor.execute('select email from lib_member where M_Id=%s',[o['M_Id'], ])
                       e=cursor.fetchone()
                       e=e['email']
                       if (e[:7]!='faculty'):
                           cursor.execute('select count(*) from borrow where M_Id=%s',[o['M_Id'], ])
                           z=cursor.fetchone()
                           if(z['count(*)']<3):
                               print(1)
                               r=o['M_Id']
                               break
                       else:
                           r = o['M_Id']
                           break
                       if(r!=-1):
                            break
                   if(r==-1):
                       cursor.execute('delete from book_status where book_id=%s and M_Id=%s',
                                      ([id],[session['id']]))
                       cursor.execute('delete from borrow where book_id=%s and M_Id=%s', ([id],v))
                       cursor.execute('update book set borrow_count =borrow_count-1 where book_id=%s', [id])
                       cursor.execute('select count(*) from borrow where book_id=%s', [id, ])
                       g = cursor.fetchone()
                       if (g['count(*)']==0):
                           cursor.execute('update book set book_shelf_status="on shelf" where book_id=%s',[id])
                           cursor.execute(
                               'update shelf set capacity =capacity-1 where shelf_Id=(select shelf_Id from book where book_id=%s)',[id])

                   else:
                       cursor.execute('delete from onhold where book_id=%s and M_Id=%s', ([id],r))
                       cursor.execute('delete from book_status where book_id=%s and M_Id=%s',
                                      ([id], v))
                       cursor.execute('update book_status set status1="borrow" where book_id=%s and M_Id=%s',
                                      ([id], r))
                       start_date = date.today()
                       end_date = start_date + timedelta(15)
                       cursor.execute('delete from borrow where book_id=%s and M_Id=%s', ([id], v))
                       cursor.execute('insert into borrow values (%s,%s,%s,%s)',
                                      (r, [id], start_date, end_date))
                else:
                    cursor.execute('delete from book_status where book_id=%s and M_Id=%s', ([id], v))
                    cursor.execute('delete from borrow where book_id=%s and M_Id=%s', ([id],v))
                    cursor.execute('update book set borrow_count =borrow_count-1 where book_id=%s', [id])
                    cursor.execute('select count(*) from borrow where book_id=%s', [id, ])
                    g = cursor.fetchone()
                    print(g)
                    if (g['count(*)']==0):
                        cursor.execute('update book set book_shelf_status="on shelf" where book_id=%s', [id])
                        cursor.execute(
                            'update shelf set capacity =capacity-1 where shelf_Id=(select shelf_Id from book where book_id=%s)',[id])
            delta = (date.today() - due_date['due_date']).days

            if (delta - 30) > 0:

                y=unpaidfines['unpaid_fines'] - ((delta - 30) * 10)
                
                cursor.execute('update lib_member set unpaid_fines =%s where M_Id=%s',(y, v))
        mysql.connection.commit()
        return redirect(url_for('personal_bookshelf'))
    else:
        return redirect(url_for('login'))

@app.route("/personal_bookshelf/")
def personal_bookshelf():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] != 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select borrow.book_id,image,ISBN,title,author,year_of_publication,start_date,due_date from book inner join borrow on book.book_id= borrow.book_id  where borrow.M_Id=%s',([session['id']]))
            list = cur.fetchall()
            print(list)
            mysql.connection.commit()
            cur.close()
            return render_template('personal_bookshelf.html',list=list, username=session['username'], email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/fines/")
def fines():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] != 'lib':
            cur = mysql.connection.cursor()
            print('1')
            cur.execute('select borrow.book_id,image,ISBN,title,author,year_of_publication,start_date,due_date from book inner join borrow on book.book_id= borrow.book_id  where borrow.M_Id=%s',([session['id']]))
            list = cur.fetchall()
            print('2')
            cur.execute(
                'select due_date from book inner join borrow on book.book_id= borrow.book_id where borrow.M_Id=%s',
                ([session['id']]))
            list1 = cur.fetchall()
            print(list1)
            l = []
            sum = 0
            m=0
            for i in list1:
                m=m+1
                mdate1 = date.today()
                rdate1 = i[0]
                delta = (mdate1 - rdate1).days
                print(delta)
                if delta > 30:
                    l.append((delta-30) * 10)
                    sum = sum + (delta-30) * 10
                else:
                    l.append(0)
            cur.execute('update lib_member set unpaid_fines=%s where M_Id=%s', (sum, session['id']))
            print('4')
            mysql.connection.commit()
            cur.close()
            return render_template('fines.html', list=list, l=l, sum=sum,m=m,
                                   username=session['username'], email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route("/detail/<string:id>")
def detail(id):
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] != 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select borrow.book_id,image,ISBN,title,author,year_of_publication,start_date,due_date from book inner join borrow on book.book_id= borrow.book_id  where borrow.M_Id=%s',([id, ]))
            list = cur.fetchall()
            print(list)
            mysql.connection.commit()
            cur.close()
            return render_template('detail.html',list=list, username=session['username'], email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route("/book_show/")
def book_show():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select * from book')
            list = cur.fetchall()
            print(list)
            mysql.connection.commit()
            cur.close()
            return render_template('book_show.html',list=list, username=session['username'], email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/borrow_show/")
def borrow_show():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select * from borrow')
            list = cur.fetchall()
            print(list)
            mysql.connection.commit()
            cur.close()
            return render_template('borrow_show.html',list=list, username=session['username'], email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/onhold_show/")
def onhold_show():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cur = mysql.connection.cursor()
            cur.execute('select * from onhold')
            list = cur.fetchall()
            list1=[]
            m=0
            for i in list:
                list1.append((date.today()-i[2]).days)
                m+=1
            mysql.connection.commit()
            cur.close()
            return render_template('onhold_show.html', username=session['username'], list=list,list1=list1,m=m,
                                   email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/remove_onhold/<string:id>")
def remove_onhold(id):
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cursor = mysql.connection.cursor()
            cursor.execute('select M_Id from onhold where book_id=%s', [id, ])
            v = cursor.fetchone()
            v = v[0]
            cursor.execute('delete from onhold where book_id=%s and M_Id=%s', ([id], v))
            cursor.execute('update book_status set status1="borrowed" where book_id=%s and M_Id=%s',
                           ([id], v))
            cursor.execute('update book set book_shelf_status="not on shelf" where book_id=%s', [id])
            cursor.execute(
                'update shelf set capacity =capacity+1 where shelf_Id=(select shelf_Id from book where book_id=%s)',
                [id, ])
            cursor.execute('update book set borrow_count =borrow_count+1 where book_id=%s',[id])
            start_date = date.today()
            end_date = start_date + timedelta(15)
            cursor.execute('insert into borrow values (%s,%s,%s,%s)',
                           (v, [id], start_date, end_date))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('onhold_show'))
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/report/")
def borrow_report():
    update_fine()
    if 'loggedin' in session:
        email = session['email1']
        if email[:3] == 'lib':
            cur = mysql.connection.cursor()
            
            # Get data for visualization
            # 1. Most borrowed books
            cur.execute('''
                SELECT b.title, COUNT(*) as borrow_count 
                FROM borrow br JOIN book b ON br.book_id = b.book_id 
                GROUP BY b.title 
                ORDER BY borrow_count DESC 
                LIMIT 10
            ''')
            popular_books = cur.fetchall()
            book_titles = [book[0] for book in popular_books]
            borrow_counts = [book[1] for book in popular_books]
            
            # 2. Borrows by month
            cur.execute('''
                SELECT DATE_FORMAT(start_date, '%Y-%m') as month, COUNT(*) as borrow_count 
                FROM borrow 
                GROUP BY month 
                ORDER BY month
            ''')
            monthly_data = cur.fetchall()
            months = [data[0] for data in monthly_data]
            monthly_counts = [data[1] for data in monthly_data]
            
            # 3. Current borrowed books by category
            cur.execute('''
                SELECT b.category, COUNT(*) as borrow_count 
                FROM borrow br JOIN book b ON br.book_id = b.book_id 
                GROUP BY b.category
            ''')
            category_data = cur.fetchall()
            categories = [data[0] for data in category_data]
            category_counts = [data[1] for data in category_data]
            
            # Generate plots
            plt.style.use('ggplot')
            
            # Plot 1: Most popular books
            plt.figure(figsize=(10, 6))
            plt.barh(book_titles, borrow_counts, color='skyblue')
            plt.xlabel('Number of Borrows')
            plt.title('Top 10 Most Borrowed Books')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            
            # Save plot to bytes
            buf1 = BytesIO()
            plt.savefig(buf1, format='png', bbox_inches='tight')
            buf1.seek(0)
            plot1 = base64.b64encode(buf1.getvalue()).decode('utf8')
            buf1.close()
            plt.close()
            
            # Plot 2: Monthly borrows
            plt.figure(figsize=(10, 6))
            plt.plot(months, monthly_counts, marker='o', color='green')
            plt.xlabel('Month')
            plt.ylabel('Number of Borrows')
            plt.title('Monthly Book Borrows')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            
            buf2 = BytesIO()
            plt.savefig(buf2, format='png', bbox_inches='tight')
            buf2.seek(0)
            plot2 = base64.b64encode(buf2.getvalue()).decode('utf8')
            buf2.close()
            plt.close()
            
            # Plot 3: Borrows by category
            plt.figure(figsize=(10, 6))
            plt.pie(category_counts, labels=categories, autopct='%1.1f%%', startangle=140)
            plt.title('Borrowed Books by Category')
            plt.axis('equal')
            plt.tight_layout()
            
            buf3 = BytesIO()
            plt.savefig(buf3, format='png', bbox_inches='tight')
            buf3.seek(0)
            plot3 = base64.b64encode(buf3.getvalue()).decode('utf8')
            buf3.close()
            plt.close()
            
            mysql.connection.commit()
            cur.close()
            
            return render_template('borrow_report.html', 
                                 plot1=plot1, 
                                 plot2=plot2, 
                                 plot3=plot3,
                                 username=session['username'], 
                                 email=session['email1'])
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

app.run(debug=True)
