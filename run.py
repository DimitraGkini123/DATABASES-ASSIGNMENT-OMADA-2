from flask import Flask, request, redirect, render_template, flash, url_for, session
from itsdangerous import URLSafeTimedSerializer
from dbdemo import app, db
from datetime import date
import datetime
import base64

def custom_b64encode(value):
    encoded_bytes = base64.b64encode(value)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string

# Register the filter function in the Flask app
app.jinja_env.filters['custom_b64encode'] = custom_b64encode


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/process_login', methods=['GET','POST'])
def process_login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        session['username'] = username
        session['role'] = role

        if role == 'student':
            query = "SELECT username, password, school_name, date_of_birth, first_name, last_name FROM student_teacher WHERE username = %s AND password= %s AND role = %s AND active =1"
            values = (username,password,role)
            cur = db.connection.cursor()
            cur.execute(query, values)
            row = cur.fetchone()

            if row:
                user_data = {
                    'username': row[0],
                    'password': row[1],
                    'school_name': row[2],
                    'date_of_birth': row[3],
                    'first_name': row[4],
                    'last_name': row[5]
                }
                session['user_data'] = user_data
                return render_template('student.html')
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                return redirect(url_for('index'))
        
        elif role == 'teacher':
            query = "SELECT username, password, school_name, date_of_birth, first_name, last_name FROM student_teacher WHERE username = %s AND password = %s AND role = %s AND active = 1 "
            values = (username,password,role)
            cur = db.connection.cursor()
            cur.execute(query, values)
            row = cur.fetchone()

            if row:
                user_data = {
                    'username': row[0],
                    'password': row[1],
                    'school_name': row[2],
                    'date_of_birth': row[3],
                    'first_name': row[4],
                    'last_name': row[5]
                }
                session['user_data'] = user_data
                return render_template('teacher.html')
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                return redirect(url_for('index'))
        
        elif role == 'manager':
            query = "SELECT username, password, school_name, date_of_birth, first_name, last_name FROM manager WHERE username = %s AND password = %s AND approve_manager = 1"
            values = (username,password)
            cur = db.connection.cursor()
            cur.execute(query, values)
            row = cur.fetchone()

            if row:
                user_data = {
                    'username': row[0],
                    'password': row[1],
                    'school_name': row[2],
                    'date_of_birth': row[3],
                    'first_name': row[4],
                    'last_name': row[5]
                }
                session['user_data'] = user_data
                return render_template('manager.html')
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                return redirect(url_for('index'))
        else:
            query = "SELECT ID, username, password FROM admin WHERE username = %s AND password = %s "
            values = (username,password)
            cur = db.connection.cursor()
            cur.execute(query, values)
            row = cur.fetchone()

            if row:
                user_data = {
                    'id': row[0],
                    'username': row[1],
                    'password': row[2],
                }
                session['user_data'] = user_data
                return render_template('admin.html')
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                return redirect(url_for('index'))
    else:
        role=session['role']
        if role == 'student':
            return render_template('student.html')
        if role == 'teacher':
            return render_template('teacher.html')
        if role == 'manager':
            return render_template('manager.html')
        else:
            return render_template('admin.html')

@app.route('/student')
def student():
    user_data = session['user_data']

    if user_data:
        return render_template('my_account.html', user_data=user_data, role = 'student')
    
    return render_template('student.html')

@app.route('/teacher')
def teacher():
    user_data = session['user_data']

    if user_data:
        return render_template('my_account.html', user_data=user_data, role = 'teacher')
        
    return render_template('teacher.html')

@app.route('/manager')
def manager():
    user_data = session['user_data']

    if user_data:
        return render_template('my_account.html', user_data=user_data, role = 'manager')
        
    return render_template('manager.html')

@app.route('/admin')
def admin():
    user_data = session['user_data']

    if user_data:
        return render_template('my_account.html', user_data=user_data, role = 'admin')
    
    return render_template('admin.html')

@app.route('/backup')
def backup(filename = None):
    cur = db.connection.curson()
    if filename is None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'backup_{timestamp}.sql'
    try:
        cur.execute(f"BACKUP DATABASE librare TO DISK = '{filename}'")
        db.connection.commit()
        print(f'Backup created successfully: {filename}')
    except Exception as e:
        print(f'Error creating backup: {str(e)}')
    cur.close()

@app.route('/restore')
def restore(backup_file):
    cur = db.connection.curson()
    try:
        with open(backup_file, 'r') as f:
            sql_script = f.read()
        cur.execute(sql_script)
        db.connection.commit()
        print("My database restored successfully.")
    except Exception as e:
        print(f'Error restoring database: {str(e)}')
    cur.close()

@app.route('/student_change_password',methods=['GET','POST'])
def student_change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        username = request.form.get('username')
        query = "UPDATE student_teacher SET password = %s WHERE username = %s"
        try:
            cur = db.connection.cursor()
            values=(new_password,username)
            cur.execute(query,values)  # Pass the values as a second argument to cur.execute()
            db.connection.commit()
            cur.close()
            flash('Password changed successfully', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('student_change_password'))
    
    return render_template('change_password.html')

@app.route('/teacher_change_password',methods=['GET','POST'])
def teacher_change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        username = request.form.get('username')
        query = "UPDATE student_teacher SET password = %s WHERE username = %s"
        try:
            cur = db.connection.cursor()
            values=(new_password,username)
            cur.execute(query,values)  # Pass the values as a second argument to cur.execute()
            db.connection.commit()
            cur.close()
            flash('Password changed successfully', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('teacher_change_password'))
    
    return render_template('change_password2.html')
    
@app.route('/manager_change_password',methods=['GET', 'POST'])
def manager_change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        username = request.form.get('username')
        query = "UPDATE manager SET password = %s WHERE username = %s"
        try:
            cur = db.connection.cursor()
            values=(new_password,username)
            cur.execute(query,values)  # Pass the values as a second argument to cur.execute()
            db.connection.commit()
            cur.close()
            flash('Password changed successfully', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('manager_change_password'))
    return render_template('change_password3.html')

@app.route('/register_school', methods=['GET', 'POST'])
def register_school():
    if request.method == 'POST':
        # Get form data
        school_name = request.form.get('school_name')
        school_address = request.form.get('school_address')
        email = request.form.get('email')
        city = request.form.get('city')
        phone_number = request.form.get('phone_number')
        principal_name = request.form.get('principal_name')
        query = "INSERT INTO school (school_name, school_address, email, city, phone_number, principal_name) "\
                "VALUES (%s, %s, %s, %s, %s, %s)"
        values = (school_name, school_address, email, city, phone_number, principal_name)
        query2 = "INSERT INTO admin(ID, Username, Password, school_name)" \
            "VALUES(%s, 'administrator', '000', %s)"
        values2 = (0,school_name,)
        print(query2)
        try:
            cur = db.connection.cursor()
            cur.execute(query, values)
            db.connection.commit()
            cur.execute(query2, values2)
            db.connection.commit()
            cur.close()
            flash('School registered successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('register_school'))

    else:
        return render_template('register_school.html', pageTitle='Register School')
    
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        school_name = request.form.get('school_name')
        date_of_birth = request.form.get('date_of_birth')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        session['username'] = username
      
        if role == 'manager' :
            query = "INSERT INTO manager (username, password, school_name, first_name, last_name, date_of_birth ) "\
                "VALUES (%s, %s, %s, %s, %s, %s)"
            values = (username, password, school_name, first_name, last_name, date_of_birth)
            try:
                cur = db.connection.cursor()
                cur.execute(query, values)  # Pass the values as a second argument to cur.execute()
                db.connection.commit()
                cur.close()
                flash('Manager registered successfully', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(str(e), 'danger')
            return redirect(url_for('register_user'))
        
        else:
            query = "INSERT INTO student_teacher(username, password, school_name, role, date_of_birth, first_name, last_name) "\
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (username, password, school_name, role, date_of_birth, first_name, last_name )
            try:
                cur = db.connection.cursor()
                cur.execute(query, values)  # Pass the values as a second argument to cur.execute()
                db.connection.commit()
                cur.close()
                flash('User registered successfully', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(str(e), 'danger')
            return redirect(url_for('register_user'))
    else:
        return render_template('signup.html', pageTitle='Sign Up')

@app.route('/add_book', methods=['GET','POST'])
def add_book():
    username = session['username']
    if request.method == 'POST':
        title = request.form.get('title')
        publisher = request.form.get('publisher')
        ISBN = request.form.get('ISBN')
        num_of_pages = request.form.get('num_of_pages')
        summary = request.form.get('summary')
        cover_image = request.files['cover_image']
        language = request.form.get('language')
        keywords = request.form.get('keywords')
        copies = request.form.get('copies')
        authors = request.form.get('authors')
        author_list = authors.split(',')
        categories = request.form.get('categories')
        category_list = categories.split(',')
        school_name = request.form.get('school_name')
        session['ISBN'] = ISBN
        
        cur = db.connection.cursor()
        cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
        manager = cur.fetchone()
        manager_school = manager[0]


        if school_name != manager_school:
            flash('You can only add books in your school')
            return render_template('add_book.html')
        else:        
            try:
                cur = db.connection.cursor()
                cur.execute("SELECT copies FROM books WHERE ISBN = %s AND school_name = %s", (ISBN,school_name))
                existing_copies = cur.fetchone()
                if existing_copies:
                    # Book already exists, update the number of copies
                    new_copies = int(existing_copies[0]) + int(copies)
                    cur.execute("UPDATE books SET copies = %s WHERE ISBN = %s AND school_name = %s", (new_copies, ISBN, school_name))
                    db.connection.commit()
                    flash('Number of copies updated successfully', 'success')
                else:
                    # Book doesn't exist, insert it into the database
                    query1 = "INSERT INTO books (ISBN, title, publisher, num_of_pages, summary, cover_image, language, keywords, copies, school_name)" \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values1 = (ISBN, title, publisher, num_of_pages, summary, cover_image.read(), language, keywords, copies, school_name)
                    cur.execute(query1,values1)
                    db.connection.commit()

                    if author_list:
                        for author in author_list:
                            cur.execute("SELECT author_id FROM author WHERE author_name = %s", (author,))
                            existing_author = cur.fetchone()
                            if existing_author:
                                author_id = existing_author[0]
                            else:
                                cur.execute("INSERT INTO author (author_name) VALUES (%s)", (author,))
                                author_id = cur.lastrowid
                            cur.execute("INSERT INTO is_author (ISBN, author_id) VALUES (%s, %s)", (ISBN, author_id))
                    if category_list:
                        for category in category_list:
                            cur.execute("SELECT theme FROM category WHERE theme = %s", (category,))
                            existing_category = cur.fetchone()
                            if existing_category:
                                category = existing_category[0]
                            else:
                                cur.execute("INSERT INTO category(theme) VALUES(%s)", (category,))
                            cur.execute("INSERT INTO book_category (ISBN, theme) VALUES (%s, %s)", (ISBN, category))
        
                    db.connection.commit()
                    flash('Book added successfully', 'success')
                    return redirect(url_for('add_book', show_add_book=False))

            except Exception as e:
                flash(str(e), 'danger')
                return redirect(url_for('add_book', show_add_book=True))

    return render_template('add_book.html')
            
           

@app.route('/teacher_change_data',methods=['GET','POST'])
def teacher_change_data():
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_date_of_birth = request.form.get('new_date_of_birth')
        new_first_name = request.form.get('new_first_name')
        new_last_name = request.form.get('new_last_name')
        username = request.form.get('username')
        query = "UPDATE student_teacher SET "
        values = []
        if new_username:
            query += "username = %s, "
            values.append(new_username)
        if new_date_of_birth:
            query += "date_of_birth = %s, "
            values.append(new_date_of_birth)
        if new_first_name:
            query += "first_name = %s, "
            values.append(new_first_name)
        if new_last_name:
            query += "last_name = %s, "
            values.append(new_last_name)
        query = query.rstrip(', ')
        query += "WHERE username = %s"
        values.append(username)

        try:
            cur = db.connection.cursor()
            cur.execute(query,values)  # Pass the values as a second argument to cur.execute()
            db.connection.commit()
            cur.close()
            flash('Personal data changed successfully', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('teacher_change_data'))
    
    return render_template('change_data.html')

@app.route('/user_school')
def user_school():
    username = session['username']
    cur = db.connection.cursor()
    cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
    manager = cur.fetchone()
    school_name = manager[0]
    cur.execute("SELECT * FROM student_teacher WHERE school_name = %s AND active = 1 " , [school_name])
    users = cur.fetchall()
    
    cur.close()
    return render_template('school_users.html', school_name=school_name, users=users)

@app.route('/borrows_per_user', methods=['GET', 'POST'])
def borrows_per_user():
    if request.method == 'POST':
        username = session['username']
        cur = db.connection.cursor()
        cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
        manager = cur.fetchone()
        school = manager[0]
        username2 = request.form.get('username')
        
        if not username2:
            query = "SELECT st.ID, st.username, st.first_name, st.last_name, st.role, br.ISBN, br.date_of_borrow, br.situation "\
                    "FROM student_teacher st "\
                    "INNER JOIN borrowing br ON br.ID = st.ID "\
                    "WHERE br.date_of_borrow IS NOT NULL AND st.school_name = %s"
            values = (school,)

        elif username2:
            query = "SELECT st.ID, st.username, st.first_name, st.last_name, st.role, br.ISBN, br.date_of_borrow, br.situation "\
                    "FROM student_teacher st "\
                    "INNER JOIN borrowing br ON br.ID = st.ID "\
                    "WHERE br.date_of_borrow IS NOT NULL AND st.username = %s AND st.school_name = %s"
            values = (username2, school)

        try:
            cur = db.connection.cursor()
            cur.execute(query, values)
            users = cur.fetchall()
            cur.close()
        
        except Exception as e:
            print("An exception occurred:", str(e))
            flash(str(e), 'danger')
            return redirect(url_for('process_login'))
        
        return render_template('borrows_per_user.html', users=users)
    
    return render_template('index.html')


#Query 3.3.1
@app.route('/search_books', methods=['GET','POST'])
def search_books():
    if(request.method == 'POST'):
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        username = session['username']
        cur = db.connection.cursor()
        cur.execute("SELECT username,password,school_name,date_of_birth,first_name,last_name FROM student_teacher WHERE username = %s", [username])
        user_data = cur.fetchone()
        school_name = user_data[2]

        # We use the COALESCE function to replace the NULL value of avg(r.Likert) with 0 if there are no matching records in the reviews table for a book
        # We also use LEFT JOIN instead of INNER JOIN in order to take all the books regardless of they have been reviewd. If the are not, we set the average reiew 0.
        if not title and not author and not category:
            query = "SELECT b.*, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM (SELECT * FROM books WHERE school_name = %s) AS b "\
                "LEFT JOIN reviews r ON b.ISBN = r.ISBN "\
                "GROUP BY b.ISBN"
            values = [school_name]

        elif title and not author and not category:
            query = "SELECT b.*, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM (SELECT * FROM books b WHERE b.title = %s AND b.school_name = %s) AS b "\
                "LEFT JOIN reviews r ON b.ISBN = r.ISBN "\
                "GROUP BY b.ISBN"
            values = (title,school_name)

        elif not title and author and not category:
            query = "SELECT COALESCE(b.ISBN, '') AS ISBN, COALESCE(b.title, '') AS title, COALESCE(b.publisher, '') AS publisher, COALESCE(b.num_of_pages, 0) AS num_of_pages, COALESCE(b.summary, '') AS summary, COALESCE(b.cover_image, '') AS cover_image, COALESCE(b.language, '') AS language, COALESCE(b.keywords, '') AS keywords, COALESCE(b.copies, 0) AS copies, COALESCE(b.school_name, '') AS school_name, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM books b LEFT JOIN reviews r ON b.ISBN = r.ISBN "\
                "LEFT JOIN is_author ia ON b.ISBN = ia.ISBN "\
                "LEFT JOIN author a ON ia.author_id = a.author_id "\
                "WHERE a.author_name = %s AND b.school_name = %s "\
                "GROUP BY b.ISBN"
            values = (author,school_name)

        elif not title and not author and category:
            query = "SELECT COALESCE(b.ISBN, '') AS ISBN, COALESCE(b.title, '') AS title, COALESCE(b.publisher, '') AS publisher, COALESCE(b.num_of_pages, 0) AS num_of_pages, COALESCE(b.summary, '') AS summary, COALESCE(b.cover_image, '') AS cover_image, COALESCE(b.language, '') AS language, COALESCE(b.keywords, '') AS keywords, COALESCE(b.copies, 0) AS copies, COALESCE(b.school_name, '') AS school_name, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM books b LEFT JOIN reviews r ON b.ISBN = r.ISBN "\
                "LEFT JOIN book_category bc ON b.ISBN = bc.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE c.theme = %s AND b.school_name = %s "\
                "GROUP BY b.ISBN"
            values = (category,school_name)

        elif title and author and not category:
            query = "SELECT COALESCE(b.ISBN, '') AS ISBN, COALESCE(b.title, '') AS title, COALESCE(b.publisher, '') AS publisher, COALESCE(b.num_of_pages, 0) AS num_of_pages, COALESCE(b.summary, '') AS summary, COALESCE(b.cover_image, '') AS cover_image, COALESCE(b.language, '') AS language, COALESCE(b.keywords, '') AS keywords, COALESCE(b.copies, 0) AS copies, COALESCE(b.school_name, '') AS school_name, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM books b LEFT JOIN reviews r ON b.ISBN = r.ISBN "\
                "LEFT JOIN is_author ia ON b.ISBN = ia.ISBN "\
                "LEFT JOIN author a ON ia.author_id = a.author_id "\
                "WHERE b.title = %s AND a.author_name = %s AND b.school_name = %s "\
                "GROUP BY b.ISBN"
            values = (title,author,school_name)

        elif title and not author and category:
            query = "SELECT COALESCE(b.ISBN, '') AS ISBN, COALESCE(b.title, '') AS title, COALESCE(b.publisher, '') AS publisher, COALESCE(b.num_of_pages, 0) AS num_of_pages, COALESCE(b.summary, '') AS summary, COALESCE(b.cover_image, '') AS cover_image, COALESCE(b.language, '') AS language, COALESCE(b.keywords, '') AS keywords, COALESCE(b.copies, 0) AS copies, COALESCE(b.school_name, '') AS school_name, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM books b LEFT JOIN reviews r ON b.ISBN = r.ISBN "\
                "LEFT JOIN book_category bc ON b.ISBN = bc.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE b.title = %s AND c.theme = %s AND b.school_name = %s "\
                "GROUP BY b.ISBN"
            values = (title,category,school_name)
    
        elif not title and author and category:
            query = "SELECT COALESCE(ba.ISBN, '') AS ISBN, COALESCE(ba.title, '') AS title, COALESCE(ba.publisher, '') AS publisher, COALESCE(ba.num_of_pages, 0) AS num_of_pages, COALESCE(ba.summary, '') AS summary, COALESCE(ba.cover_image, '') AS cover_image, COALESCE(ba.language, '') AS language, COALESCE(ba.keywords, '') AS keywords, COALESCE(ba.copies, 0) AS copies, COALESCE(ba.school_name, '') AS school_name, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM book_author ba LEFT JOIN reviews r ON ba.ISBN = r.ISBN "\
                "LEFT JOIN book_category bc ON ba.ISBN = bc.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE ba.author_name = %s AND c.theme = %s AND ba.school_name = %s "\
                "GROUP BY ba.ISBN"
            values = (author,category,school_name)
    
        elif title and author and category:
            query = "SELECT COALESCE(ba.ISBN, '') AS ISBN, COALESCE(ba.title, '') AS title, COALESCE(ba.publisher, '') AS publisher, COALESCE(ba.num_of_pages, 0) AS num_of_pages, COALESCE(ba.summary, '') AS summary, COALESCE(ba.cover_image, '') AS cover_image, COALESCE(ba.language, '') AS language, COALESCE(ba.keywords, '') AS keywords, COALESCE(ba.copies, 0) AS copies, COALESCE(ba.school_name, '') AS school_name, COALESCE(avg(r.Likert), 0) AS average_likert "\
                "FROM book_author ba LEFT JOIN reviews r ON ba.ISBN = r.ISBN "\
                "LEFT JOIN book_category bc ON ba.ISBN = bc.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE ba.title = %s AND ba.author_name = %s AND c.theme = %s AND ba.school_name = %s "\
                "GROUP BY ba.ISBN"
            values = (title,author,category,school_name)

        try:
            cur = db.connection.cursor()
            cur.execute(query,values)  # Pass the values as a second argument to cur.execute()
            books = cur.fetchall()
            cur.close()
        
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('process_login'))
        
        return render_template('books.html',books = books)
    
    return render_template('index.html')
    
#Query 3.2.1
@app.route('/manager_search_books', methods=['GET','POST'])
def manager_search_books():
    if(request.method == 'POST'):
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        copies = request.form.get('copies')
        username = session['username']
        cur = db.connection.cursor()
        cur.execute("SELECT username,password,school_name,first_name,last_name,date_of_birth FROM manager WHERE username = %s", [username])
        user_data = cur.fetchone()
        school_name = user_data[2]

        if not title and not author and not category and not copies:
            query = "SELECT * FROM books WHERE school_name = %s"
            values = [school_name]

        elif title and not author and not category and not copies:
            query = "SELECT * FROM books WHERE title = %s AND school_name = %s"
            values = (title,school_name)

        elif not title and author and not category and not copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN is_author ia ON b.ISBN = ia.ISBN "\
                "INNER JOIN author a ON ia.author_id = a.author_id "\
                "WHERE a.author_name = %s and b.school_name = %s ORDER BY b.title"
            values = (author,school_name)

        elif not title and not author and category and not copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN book_category bc ON b.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE c.theme = %s and b.school_name = %s ORDER BY b.title"
            values = (category,school_name)

        elif not title and not author and not category and copies:
            query = "SELECT * FROM books WHERE copies = %s and school_name = %s ORDER BY title"
            values = (copies,school_name)

        elif title and author and not category and not copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN is_author ia ON b.ISBN = ia.ISBN "\
                "INNER JOIN author a ON ia.author_id = a.author_id "\
                "WHERE b.title = %s and a.author_name = %s and b.school_name = %s ORDER BY b.title"
            values = (title,author,school_name)

        elif title and not author and category and not copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN book_category bc ON b.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE b.title = %s and c.theme = %s and b.school_name = %s ORDER BY b.title"
            values = (title,category,school_name)

        elif title and not author and not category and copies:
            query = "SELECT * FROM books b WHERE title = %s and copies= %s and school_name = %s ORDER BY b.title"
            values = (title,copies,school_name)
    
        elif not title and author and category and not copies:
            query = "SELECT ba.ISBN,ba.title,ba.publisher,ba.num_of_pages,ba.summary,ba.cover_image,ba.language,ba.keywords,ba.copies,ba.school_name FROM book_author ba "\
                "INNER JOIN book_category bc ON ba.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE ba.author_name = %s and c.theme = %s and ba.school_name = %s ORDER BY ba.title"
            values = (author,category,school_name)

        elif not title and author and not category and copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN is_author ia ON b.ISBN = ia.ISBN "\
                "INNER JOIN author a ON ia.author_id = a.author_id "\
                "WHERE a.author_name = %s and b.copies = %s and b.school_name = %s ORDER BY b.title"
            values = (author,copies,school_name)

        elif not title and not author and category and copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN book_category bc ON b.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE c.theme = %s and b.copies = %s and b.school_name = %s ORDER BY b.title"
            values = (category,copies,school_name)
        
        elif title and author and category and not copies:
            query = "SELECT ba.ISBN,ba.title,ba.publisher,ba.num_of_pages,ba.summary,ba.cover_image,ba.language,ba.keywords,ba.copies,ba.school_name FROM book_author ba "\
                "INNER JOIN book_category bc ON ba.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE ba.title = %s and ba.author_name = %s and c.theme = %s  and ba.school_name = %s ORDER BY ba.title"
            values = (title,author,category,school_name)

        elif title and author and not category and copies:
            query = "SELECT * FROM books b "\
                "INNER JOIN is_author ia ON b.ISBN = ia.ISBN "\
                "INNER JOIN author a ON ia.author_id = a.author_id "\
                "WHERE b.title = %s and a.author_name = %s and b.copies = %s  and b.school_name = %s ORDER BY b.title"
            values = (title,author,copies,school_name)

        elif not title and author and category and copies:
            query = "SELECT ba.ISBN,ba.title,ba.publisher,ba.num_of_pages,ba.summary,ba.cover_image,ba.language,ba.keywords,ba.copies,ba.school_name FROM book_author ba "\
                "INNER JOIN book_category bc ON ba.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE ba.author_name = %s and c.theme = %s and ba.copies = %s and ba.school_name = %s ORDER BY ba.title"
            values = (author,category,copies,school_name)

        elif title and author and category and copies:
            query = "SELECT ba.ISBN,ba.title,ba.publisher,ba.num_of_pages,ba.summary,ba.cover_image,ba.language,ba.keywords,ba.copies,ba.school_name FROM book_author ba "\
                "INNER JOIN book_category bc ON ba.ISBN = bc.ISBN "\
                "INNER JOIN category c ON bc.theme = c.theme "\
                "WHERE ba.title = %s and ba.author_name = %s and c.theme = %s and ba.copies = %s and ba.school_name = %s ORDER BY ba.title"
            values = (title,author,category,copies,school_name)

        try:
            cur = db.connection.cursor()
            cur.execute(query,values)  # Pass the values as a second argument to cur.execute()
            books = cur.fetchall()
            cur.close()
        
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('process_login'))
        
        return render_template('books_manager.html',books = books)
    
    return render_template('index.html')
    
    

@app.route('/update_books/<isbn>',methods=['GET','POST'])
def update_books(isbn):
    if request.method == 'POST':
        new_title = request.form.get('new_title')
        new_publisher = request.form.get('new_publisher')
        new_num_of_pages = request.form.get('new_num_of_pages')
        new_summary = request.form.get('new_summary')
        new_cover_image = request.files['new_cover_image']
        new_language = request.form.get('new_language')
        new_keywords = request.form.get('new_keywords')
        new_authors = request.form.get('new_authors')
        if new_authors is not None:
            new_author_list = new_authors.split(',')
        new_categories = request.form.get('new_categories')
        if new_categories is not None:
            new_category_list = new_categories.split(',')
        
        query1 = "UPDATE books SET "
        values1 = []

        if new_title:
            query1 += "title = %s, "
            values1.append(new_title)
        if new_publisher:
            query1 += "publisher = %s, "
            values1.append(new_publisher)
        if new_num_of_pages:
            query1 += "num_of_pages = %s, "
            values1.append(new_num_of_pages)
        if new_summary:
            query1 += "summary = %s, "
            values1.append(new_summary)
        if new_cover_image:
            cover_image_data = new_cover_image.read()
            query1 += "cover_image = %s, "
            values1.append(cover_image_data)
        if new_language:
            query1 += "language = %s, "
            values1.append(new_language)
        if new_keywords:
            query1 += "keywords = %s, "
            values1.append(new_keywords)
    
        query1 = query1.rstrip(', ')
        query1 += "WHERE ISBN = %s"
        values1.append(isbn)
        
        queries2 = []
        values2 = []
        if new_authors:
            for new_author in new_author_list:
                query2 = "UPDATE author a INNER JOIN is_author ia "\
            "ON a.author_id = ia.author_id INNER JOIN books b "\
            "ON ia.ISBN = b.ISBN SET a.author_name = %s WHERE b.ISBN = %s"

                queries2.append(query2)
                values2.append((new_author,isbn))

        queries3 = []
        values3 = []
        if new_categories:
            for new_category in new_category_list:
                query3 = "UPDATE category c INNER JOIN book_category bc"\
                    "ON c.theme = bc.theme INNER JOIN books b"\
                    "ON bc.ISBN = b.ISBN SET c.theme = %s WHERE b.ISBN = %s"
                queries3.append(query3)
                values3.append((new_category,isbn))

        try:
            cur = db.connection.cursor()
            cur.execute(query1,values1)  # Pass the values as a second argument to cur.execute()
            db.connection.commit()
            
            for query2, values in zip(queries2, values2):
                cur.execute(query2, values)
                db.connection.commit()
            
            for query3, values in zip(queries3, values3):
                cur.execute(query3, values)
                db.connection.commit()

            cur.close()
            flash('Book changed successfully', 'success')
            return render_template('manager.html')
        
        except Exception as e:
            print(e)
            flash(str(e), 'danger')
            return redirect(url_for('update_books', isbn = isbn))
        
    return render_template('update_book.html', isbn = isbn)

@app.route('/manager_approvals')
def manager_approvals():
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM manager WHERE approve_manager IS NULL ")
    managers = cur.fetchall()
    cur.close()
    return render_template('manager_approvals.html', managers=managers)


@app.route('/approve_manager/<string:school_name>/<string:first_name>', methods=['POST'])
def approve_manager(school_name,first_name):
    action = request.form.get('action')
    cur = db.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM manager WHERE school_name = %s AND approve_manager = 1", (school_name,))
    count = cur.fetchone()[0]
    cur.close()
    if count == 0 :
        if action == 'approve':
            cur = db.connection.cursor()
            cur.execute("UPDATE admin SET approve_manager = 1 WHERE school_name = %s", (school_name,))
            db.connection.commit()
            #cur.execute("UPDATE manager SET approve_manager = 1 WHERE school_name = %s AND first_name = %s", (school_name,first_name))
            #db.connection.commit()
            cur.close()
            flash('Manager has been approved.', 'success')
        else:
            cur = db.connection.cursor()
            #cur.execute("UPDATE admin SET approve_manager = 0 WHERE school_name = %s", (school_name,))
            #db.connection.commit()
            cur.execute("DELETE FROM manager WHERE school_name = %s AND first_name = %s", (school_name,first_name))
            db.connection.commit()
            cur.close()
            flash('Manager has not been approved.')
    elif count >= 1 :
        if action == 'reject':
            cur = db.connection.cursor()
            #cur.execute("UPDATE admin SET approve_manager = 0 WHERE school_name = %s", (school_name,))
            #db.connection.commit()
            cur.execute("DELETE FROM manager WHERE school_name = %s AND first_name = %s", (school_name,first_name))
            db.connection.commit()
            cur.close()
            flash('Manager has not been approved.')
        else:
            flash('Invalid action.', 'error')

    return redirect(url_for('manager_approvals'))

@app.route('/delayed_borrows', methods=['GET'])
def delayed_borrows():
    username=session['username']
    cur = db.connection.cursor()
    cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
    manager = cur.fetchone()
    school_name = manager[0]

    cur.execute("SELECT b.*, st.first_name, st.last_name, st.role, " \
        "(SELECT CASE " \
        "WHEN b1.situation = 'borrowed' AND b1.date_of_return IS NULL THEN DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) " \
        "WHEN b1.situation = 'delayed' THEN DATEDIFF(b1.date_of_return, b1.date_of_borrow) " \
        "END " \
        "FROM borrowing b1 WHERE ID = b.ID AND ISBN = b.ISBN) AS days_diff " \
        "FROM borrowing b " \
        "JOIN student_teacher st ON b.ID = st.ID " \
        "JOIN books bk ON b.ISBN = bk.ISBN " \
        "WHERE (b.situation = 'delayed' OR ( " \
        "b.situation = 'borrowed' " \
        "AND ( ( (DATEDIFF(CURRENT_DATE(), b.date_of_borrow) > 14) AND st.role = 'student' ) OR ( (DATEDIFF(CURRENT_DATE(), b.date_of_borrow) > 7) AND st.role = 'teacher' ) ) " \
        " ) ) " \
        "AND st.school_name = %s", [school_name])
        
    delayed_borrows = cur.fetchall()
    cur.close()
    return render_template('delayed_borrows.html', delayed_borrows=delayed_borrows)
    
@app.route('/delete_user/<string:school_name>/<string:username>', methods=['POST'])
def delete_user(school_name, username):
    action = request.form.get('action')
    if action == 'delete':
        cur = db.connection.cursor()
        cur.execute("UPDATE student_teacher "
                    "SET  active = 0 "
                    "WHERE school_name = %s AND username = %s", (school_name, username))
        db.connection.commit()
        cur.close()
        flash('User has been deleted', 'success')

    return redirect(url_for('user_school'))

        
@app.route("/new_borrow/<isbn>/<role>", methods=['GET', 'POST'])
def new_borrows(isbn,role):
    if request.method == 'POST':
        username = session['username']
        role = session['role']
        if username != session.get('username'):
            flash('Invalid username.', 'danger')
            if role == 'student': return render_template('student.html')
            else: return render_template('teacher.html')
        try:
            cur = db.connection.cursor()
            cur.execute("SELECT ID from student_teacher WHERE username = %s", (username,))
            id = cur.fetchone()
            query_check = "SELECT 1 FROM reservation WHERE id = %s AND isbn = %s"
            values_check= (id,isbn)
            cur.execute(query_check, values_check)
            result = cur.fetchone()
            if not result:
                query = "INSERT INTO borrowing (ID, ISBN) "\
                "SELECT st.ID, b.ISBN " \
                "FROM student_teacher st " \
                "INNER JOIN books b ON st.school_name = b.school_name " \
                "WHERE st.username = %s AND b.ISBN = %s; "
        
                values=(username,isbn)
                cur.execute(query, values)
                db.connection.commit()
                cur.close()
            
                if role == 'student': return render_template('student.html')
                else: return render_template('teacher.html')
            else: return "You have made a reservation request so you can't do a borrow request for this book"
        except Exception as e:
            print("You cannot borrow this book!", e)
            return "You cannot borrow this book!"
    else:
        # Handle GET request (displaying the page)
        if role == 'student': return render_template('student.html')
        else: return render_template('teacher.html')

@app.route('/borrowing_approvals')
def borrowing_approvals():
    username = session['username']
    cur = db.connection.cursor()
    cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
    manager = cur.fetchone()
    school_name = manager[0]

    query_approval = "UPDATE student_teacher st SET approve_borrowing = " \
        "CASE " \
        "WHEN ((st.role = 'student' AND st.num_of_borrows < 2) OR (st.role = 'teacher' AND st.num_of_borrows < 1)) " \
        "AND NOT EXISTS ( "\
        "SELECT 1 FROM borrowing b1 WHERE ID = st.ID AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL AND " \
        "( ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14) AND st.role = 'student' ) OR ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7) AND st.role = 'teacher' ) ) "\
        ")" \
        "THEN 1 ELSE 0 END " \
        "WHERE st.school_name=%s "

    cur.execute(query_approval, [school_name])
    db.connection.commit()

    cur.execute("SELECT b.*, st.first_name, st.last_name, st.role, st.approve_borrowing, st.num_of_borrows, bk.copies,  "
        "(SELECT COUNT(*) FROM borrowing b1 WHERE ID = b.ID AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL AND" \
        "( ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14) AND st.role = 'student' ) OR ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7) AND st.role = 'teacher' ) ) ) " \
        "FROM borrowing b " \
        "JOIN student_teacher st ON b.ID = st.ID " \
        "JOIN books bk ON b.ISBN = bk.ISBN " \
        "WHERE ((date_of_borrow IS NULL) OR (b.situation='borrowed' AND date_of_return IS NOT NULL)) AND st.school_name = bk.school_name " \
        "AND st.school_name=%s", [school_name])
    borrowers = cur.fetchall()
    cur.close()
    return render_template('borrowing_approvals.html', borrowers=borrowers)
    
@app.route('/approved_b/<isbn>/<role>/<id>', methods=['POST'])
def approve_b(isbn, role, id):
    action = request.form.get('action')
    if action == 'approve':
        cur = db.connection.cursor()
        #check if the user can borrow and if there are enough available copies
        query_check = "SELECT st.approve_borrowing, bk.copies,bk.school_name " \
                "FROM student_teacher st " \
                "JOIN books bk ON st.school_name = bk.school_name " \
                "WHERE bk.ISBN = %s AND st.ID = %s"
        cur.execute(query_check, (isbn, id))
        result = cur.fetchone()
        approve_borrowing = result[0]
        copies = result[1]
        school = result[2]

        values = (id,isbn.strip())
    
        #not able to borrow the same book??????
        query_check_return = "SELECT COUNT(*) FROM borrowing WHERE ID = %s AND ISBN = %s AND date_of_return IS NOT NULL AND date_of_borrow IS NOT NULL AND situation='borrowed'"
        cur.execute(query_check_return,values)
        result = cur.fetchone()
        date_of_return_not_null = result[0]
    
        if approve_borrowing == 1 and copies > 0 and date_of_return_not_null==0:    #If the borrowing is approved
        
        #Check if there is a reservation of this book by this user
            query_check_reservation = "SELECT COUNT(*) FROM reservation WHERE ID = %s AND ISBN = %s"
            cur.execute(query_check_reservation, values)
            reservation_exists = cur.fetchone()[0]
    
            if reservation_exists:
                # Delete the reservation from table reservation
                query_delete_reservation_r = "DELETE FROM reservation WHERE ID = %s AND ISBN = %s AND date_of_reservation IS NOT NULL"
                cur.execute(query_delete_reservation_r, values)
                db.connection.commit()

                #Update number of reservations to this student
                query_delete_reservation_n = "UPDATE student_teacher st SET num_of_reserves = num_of_reserves - 1 WHERE id = %s "
                cur.execute(query_delete_reservation_n, (id,))
                db.connection.commit()
        
            #Update the situation of the borrowing from null or waiting to borrowed
            query_approved_b = "UPDATE borrowing b SET situation='borrowed', date_of_borrow = CURRENT_DATE() WHERE isbn = %s AND id = %s "
            values = (isbn,id)
            cur.execute(query_approved_b, values)
            db.connection.commit()
    
            #Update number of books that the student or teacher has
            query_approved_n = "UPDATE student_teacher st SET num_of_borrows = num_of_borrows + 1 WHERE id = %s "
            cur.execute(query_approved_n, (id,))
            db.connection.commit()

            #Update the copies of the book on this school
            query_approved_c = "UPDATE books b SET copies = copies - 1 WHERE isbn = %s AND b.school_name = %s"
            cur.execute(query_approved_c, (isbn,school))
            db.connection.commit()

            cur.close()
            return redirect(url_for('borrowing_approvals'))
        else:
            return "You cannot borrow this book now"
    
@app.route('/rejected_b/<isbn>/<role>/<id>', methods=['POST'])
def reject_b(isbn, role, id):
    action = request.form.get('action')
    if action == 'reject':
        cur = db.connection.cursor()
        #check if the user can borrow
        query_check1 = "SELECT st.approve_borrowing FROM student_teacher st WHERE st.ID = %s"
        cur.execute(query_check1, (id, ))
        result = cur.fetchone()
        approve_borrowing = result[0]
    
        #Check if the user has delayed a borrowing
        query_check2 = "SELECT COUNT(*) FROM borrowing b1 " \
            "JOIN student_teacher st ON b1.ID = st.ID " \
            "WHERE b1.ID = %s AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL " \
            "AND ((DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14 AND st.role = 'student') " \
            "OR (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7 AND st.role = 'teacher'))"

        cur.execute(query_check2, (id,))
        count_delayed = cur.fetchone()[0]
    
        values = (id,isbn.strip())

        query_check_return = "SELECT COUNT(*) FROM borrowing WHERE ID=%s AND ISBN=%s AND date_of_return IS NOT NULL AND date_of_borrow IS NOT NULL AND situation='borrowed'"
        cur.execute(query_check_return,values)
        result = cur.fetchone()
        date_of_return_not_null = result[0]

        if (approve_borrowing == 0 or count_delayed > 0) and date_of_return_not_null == 0:
            query_rejected = "DELETE FROM borrowing WHERE isbn = %s AND id = %s "
            values = (isbn,id)
            cur.execute(query_rejected, values)
            db.connection.commit()
            cur.close()
            return redirect(url_for('borrowing_approvals'))
        else:
            return "You should not reject it."

@app.route('/waiting_b/<isbn>/<role>/<id>', methods=['POST'])
def waiting_b(isbn, role, id):
    action = request.form.get('action')
    if action == 'waiting':
        cur = db.connection.cursor()
        query_check1 = "SELECT st.approve_borrowing, bk.copies " \
                  "FROM student_teacher st " \
                  "JOIN books bk ON bk.ISBN = %s " \
                  "WHERE st.ID = %s"
        cur.execute(query_check1, (isbn, id))
        result = cur.fetchone()
        approve_borrowing = result[0]
        copies = result[1]
        query_check2 = "SELECT COUNT(*) FROM borrowing b1 " \
                "JOIN student_teacher st ON b1.ID = st.ID " \
                "WHERE b1.ID = %s AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL " \
                "AND ((DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14 AND st.role = 'student') " \
                "OR (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7 AND st.role = 'teacher'))"
        cur.execute(query_check2, (id,))
        count_delayed = cur.fetchone()[0]
    
        values = (id,isbn.strip())
        query_check_return = "SELECT COUNT(*) FROM borrowing WHERE ID=%s AND ISBN=%s AND date_of_return IS NOT NULL AND date_of_borrow IS NOT NULL AND situation='borrowed'"
        cur.execute(query_check_return,values)
        result = cur.fetchone()
        date_of_return_not_null = result[0]

        if approve_borrowing == 1 and copies <= 0 and count_delayed == 0 and date_of_return_not_null == 0:
    
            query_waiting = "UPDATE borrowing b SET situation='waiting' WHERE isbn = %s AND id = %s "
            values = (isbn,id)
            cur.execute(query_waiting, values)
            db.connection.commit()
            cur.close()
            return redirect(url_for('borrowing_approvals'))
        else:
            return "You should not wait"

@app.route('/my_borrows')
def my_borrows():
    username = session['username']
    role = session['role']
    try:
        cur = db.connection.cursor()
        query = "SELECT b.ISBN, bk.title, b.date_of_borrow, b.date_of_return, b.situation " \
            "FROM borrowing b " \
            "INNER JOIN books bk ON b.ISBN = bk.ISBN " \
            "INNER JOIN student_teacher st ON b.ID = st.ID " \
            "WHERE st.username = %s AND st.school_name = bk.school_name AND b.situation IS NOT NULL; " 
        
        values=(username,)
        cur.execute(query, values)
        borrows = cur.fetchall()
        db.connection.commit()
        cur.close()
        return render_template('borrows.html', borrows=borrows)

    except Exception as e:
            print("Error ", e)
            return "Error "
    
@app.route('/return_book/<isbn>', methods=['POST'])
def return_book(isbn):
    username = session['username']
    cur = db.connection.cursor()
    cur.execute("SELECT id FROM student_teacher WHERE username=%s ", (username,))
    id=cur.fetchone()[0]
    query_check= "SELECT situation FROM borrowing WHERE ID=%s AND ISBN=%s"
    values=(id,isbn.strip())
    cur.execute(query_check,values)
    result = cur.fetchone()
    sit = result[0]
    if sit == 'returned' or sit == 'delayed':
        return redirect(url_for('my_borrows'))
    else:
        try:
            query = "UPDATE borrowing b SET b.date_of_return=CURRENT_DATE() WHERE ID = %s AND ISBN = %s"
            cur.execute(query, values)
            db.connection.commit()
            return redirect(url_for('my_borrows'))

        except Exception as e:
            print("Error ", e)
            return "Error "
    
@app.route('/approve_return/<isbn>/<role>/<id>', methods=['POST'])
def approve_return(isbn,role,id):
    action = request.form.get('action')
    if action == 'return':
        cur = db.connection.cursor()
        values=(id,isbn.strip())

        query_check_return = "SELECT COUNT(*) FROM borrowing WHERE ID=%s AND ISBN=%s AND date_of_return IS NOT NULL AND date_of_borrow IS NOT NULL AND situation='borrowed'"
        cur.execute(query_check_return,values)
        result = cur.fetchone()
        date_of_return_not_null = result[0]

        if date_of_return_not_null == 1:
            query_update_situation = "UPDATE borrowing b " \
                "JOIN student_teacher st ON b.ID = st.ID " \
                "SET situation = CASE " \
                "WHEN (st.role = 'student' AND DATEDIFF(b.date_of_return, b.date_of_borrow) <= 14) OR (st.role = 'teacher' AND DATEDIFF(b.date_of_return, b.date_of_borrow) <= 7) " \
                "THEN 'returned' ELSE 'delayed' END " \
                "WHERE b.ID = %s AND b.ISBN = %s "
            cur.execute(query_update_situation, values)
            db.connection.commit()
    
            query_update_n = "UPDATE student_teacher " \
                "SET num_of_borrows = num_of_borrows - 1, approve_borrowing = "\
                "CASE WHEN num_of_borrows - 1 = 1 THEN 1 ELSE approve_borrowing END " \
                "WHERE ID = %s"
            cur.execute(query_update_n, (id,))
            db.connection.commit()

            query_approved_c = "UPDATE books b SET copies = copies + 1 WHERE isbn=%s "
            cur.execute(query_approved_c, (isbn,))
            db.connection.commit()

            cur.close()
            return redirect(url_for('borrowing_approvals'))
        else:
            return redirect(url_for('borrowing_approvals'))
    
@app.route('/do_not_approve_return/<isbn>/<role>/<id>', methods=['POST'])
def do_not_approve_return(isbn,role,id):
    action = request.form.get('action')
    if action == 'do_not_return':
        cur = db.connection.cursor()
        values=(id,isbn.strip())
        try:
            query = "UPDATE borrowing b SET b.date_of_return=NULL WHERE ID=%s AND ISBN=%s"
            cur.execute(query, values)
            db.connection.commit()
            return redirect(url_for('borrowing_approvals'))

        except Exception as e:
            print("Error ", e)
            return "Error "

@app.route("/new_reservation/<isbn>/<role>", methods=['GET', 'POST'])
def new_reservations(isbn,role):
    if request.method == 'POST':
        username = session['username']
        role = session['role']

        if username != session.get('username'):
            flash('Invalid username.', 'danger')
            if role == 'student': return render_template('student.html')
            else: return render_template('teacher.html')
        try:
            cur = db.connection.cursor()
            cur.execute("SELECT ID from student_teacher where username=%s", (username,))
            id = cur.fetchone()
            query_check = "SELECT 1 FROM borrowing WHERE id = %s AND isbn = %s"
            values_check=(id,isbn)
            cur.execute(query_check, values_check)
            result= cur.fetchone()
            if not result:
                query = "INSERT INTO reservation (ID, ISBN) "\
                "SELECT st.ID, b.ISBN " \
                "FROM student_teacher st " \
                "INNER JOIN books b ON st.school_name = b.school_name " \
                "WHERE st.username = %s AND b.ISBN = %s; "

                values=(username,isbn)
            
                cur.execute(query, values)
                db.connection.commit()
                cur.close()
            
                if role == 'student': return render_template('student.html')
                else: return render_template('teacher.html')
            else: return "You have made a request to borrow this book so you can't reserve it"
        except Exception as e:
            print("You cannot reserve this book!:", e)
            return "You cannot reserve this book!"
    else:
        # Handle GET request (displaying the page)
        if role == 'student': return render_template('student.html')
        else: return render_template('teacher.html')

@app.route('/reservation_approvals')
def reservation_approvals():
    username = session['username']
    cur = db.connection.cursor()
    #only see the reservations of your school
    cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
    manager = cur.fetchone()
    school_name = manager[0]

    #every time you get here reservation approvals for each student are updated
    query_approval = "UPDATE student_teacher st SET approve_reservation= " \
        "CASE " \
        "WHEN ((st.role = 'student' AND st.num_of_reserves < 2) OR (st.role = 'teacher' AND st.num_of_reserves < 1)) " \
        "AND NOT EXISTS ( " \
        "SELECT 1 FROM borrowing b1 WHERE ID = st.ID AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL AND " \
        "( ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14) AND st.role = 'student' ) OR ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7) AND st.role = 'teacher' ) ) "\
        ")" \
        "THEN 1 ELSE 0 END " \
        "WHERE st.school_name=%s;"
    cur.execute(query_approval, [school_name])
    
    db.connection.commit()

    #Show all the requests for reservations
    cur.execute("SELECT r.*, st.first_name, st.last_name, st.role, st.approve_reservation, st.num_of_reserves, bk.copies,  " \
        "(SELECT COUNT(*) FROM borrowing b1 WHERE ID = r.ID AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL AND" \
        "( ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14) AND st.role = 'student' ) OR ( (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7) AND st.role = 'teacher' ) ) ) " \
        "FROM reservation r " \
        "JOIN student_teacher st ON r.ID = st.ID " \
        "JOIN books bk ON r.ISBN = bk.ISBN " \
        "WHERE st.school_name=%s AND bk.school_name=%s", [school_name,school_name,])
    reservations = cur.fetchall()
    #cur.close()
    #also check if every reservation's duration is less than 7 days or equal. If not, the reservation is deleted
    for reservation in reservations:
        isbn = reservation[1]
        id = reservation[0]
        date_of_reservation = reservation[2]

        if date_of_reservation is not None and date_of_reservation != 'NULL':
            duration = (date.today() - date_of_reservation).days

            if duration > 7:
                # Delete the reservation
                query_delete_reservation = "DELETE FROM reservation WHERE ISBN =%s AND ID =%s"
                cur.execute(query_delete_reservation, (isbn, id))
                deleted_rows = cur.rowcount
                db.connection.commit()
                print(f"Deleted {deleted_rows} rows.")

                # Update student's number of reservations
                query_update_num_of_reserves = "UPDATE student_teacher SET num_of_reserves = num_of_reserves - 1 WHERE ID = %s"
                cur.execute(query_update_num_of_reserves, (id,))
                db.connection.commit()

    return render_template('reservation_approvals.html', reservations=reservations)

@app.route('/approved_r/<isbn>/<role>/<id>', methods=['POST'])
def approve_r(isbn, role, id):
    action = request.form.get('action')
    if action == 'approve':
        cur = db.connection.cursor()
        #Checks if it possible to approve the reservation according to user's situation
        query_check1 = "SELECT st.approve_reservation" \
                "FROM student_teacher st " \
                "WHERE st.ID = %s"
        cur.execute(query_check1,  id)
        result = cur.fetchone()
        approve_reservation = result[0]
        
    
        #Check if you haven't returned a book and it is delayed
        query_check2 = "SELECT COUNT(*) FROM borrowing b1 " \
                "JOIN student_teacher st ON b1.ID = st.ID " \
                "WHERE b1.ID = %s AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL " \
                "AND ((DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14 AND st.role = 'student') " \
                "OR (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7 AND st.role = 'teacher'))"
        cur.execute(query_check2, (id,))
        count_delayed = cur.fetchone()[0]

        if approve_reservation == 1 and count_delayed==0 :
            #here it checks if the reservation is approved in general
            query_check = "SELECT 1 FROM borrowing WHERE ID = %s AND ISBN = %s"
            cur.execute(query_check, (id, isbn))
            result = cur.fetchone()
        
            if not result:
                #here it checks if this certain user can reserve it
                query_approved_r = "UPDATE reservation b SET date_of_reservation = CURRENT_DATE() WHERE isbn = %s AND id = %s "
                values = (isbn,id)
                cur.execute(query_approved_r, values)
                db.connection.commit()
    
                query_approved_n = "UPDATE student_teacher st SET num_of_reserves = num_of_reserves + 1 WHERE id = %s "
                cur.execute(query_approved_n, (id,))
                db.connection.commit()

                query_goto_b = "INSERT INTO borrowing (ID, ISBN, situation) "\
                    "SELECT st.ID, b.ISBN, 'waiting' " \
                    "FROM student_teacher st " \
                    "INNER JOIN books b ON st.school_name = b.school_name " \
                    "WHERE st.id = %s AND b.ISBN = %s; "
                cur.execute(query_goto_b, (id, isbn))
                db.connection.commit()
                cur.close()
                return redirect(url_for('reservation_approvals'))
            else:
                return "You have already borrowed this book. You can check for another one"
        else:
            "You are not allowed to reserve a book or this book is not avaliable now."

@app.route('/rejected_r/<isbn>/<role>/<id>', methods=['POST'])
def reject_r(isbn, role, id):
    action = request.form.get('action')
    if action == 'reject':
        cur = db.connection.cursor()
        query_check2 = "SELECT COUNT(*) FROM borrowing b1 " \
            "JOIN student_teacher st ON b1.ID = st.ID " \
            "WHERE b1.ID = %s AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL " \
            "AND ((DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14 AND st.role = 'student') " \
            "OR (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7 AND st.role = 'teacher'))"
        cur.execute(query_check2, (id,))
        count_delayed = cur.fetchone()[0]

        query_check = "SELECT 1 FROM borrowing WHERE ID = %s AND ISBN = %s"
        cur.execute(query_check, (id, isbn))
        result = cur.fetchone()
    
        if count_delayed > 0 or result: 
            #this check is for when it should reject it
            query_rejected = "DELETE FROM reservation WHERE isbn = %s AND id = %s "
            values = (isbn,id)
            cur.execute(query_rejected, values)
            db.connection.commit()
            cur.close()
            return redirect(url_for('reservation_approvals'))
        else:
            return "You should not reject this reservation"

@app.route('/waiting_r/<isbn>/<role>/<id>', methods=['POST'])
def waiting_r(isbn, role, id):
    action = request.form.get('action')
    if action == 'waiting':
        cur = db.connection.cursor()
        query_check1 = "SELECT st.approve_reservation, bk.copies" \
                "FROM student_teacher st " \
                "JOIN books bk ON st.school_name = bk.school_name " \
                "WHERE st.ID = %s AND bk.ISBN = %s"
        cur.execute(query_check1, (id, isbn))
        result = cur.fetchone()
        approve_reservation = result[0]
        copies = result[1]
        query_check2 = "SELECT COUNT(*) FROM borrowing b1 " \
                "JOIN student_teacher st ON b1.ID = st.ID " \
                "WHERE b1.ID = %s AND b1.situation = 'borrowed' AND b1.date_of_return IS NULL " \
                "AND ((DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 14 AND st.role = 'student') " \
                "OR (DATEDIFF(CURRENT_DATE(), b1.date_of_borrow) > 7 AND st.role = 'teacher'))"
        cur.execute(query_check2, (id,))
        count_delayed = cur.fetchone()[0]

        if approve_reservation == 1 and copies > 0 and count_delayed == 0:
            #this check is for when it should not wait
            return "You should either approve it or reject it, not wait."
        return redirect(url_for('reservation_approvals'))
    
@app.route('/delete_my_reservation/<isbn>',methods=['POST'])
def delete_my_reservation(isbn):
    action = request.form.get('action')
    username = session['username']
    cur = db.connection.cursor()
    if action == 'delete' :
        try:
            cur.execute("SELECT id FROM student_teacher WHERE username=%s ", (username,))
            id=cur.fetchone()[0]
            values=(id,isbn.strip())
            query_delete_my_reservation = "DELETE from reservation WHERE ID = %s AND ISBN = %s"
            cur.execute(query_delete_my_reservation, values)
            db.connection.commit()
            return redirect(url_for('my_reservations'))
        except Exception as e:
            print("Error ", e)
            return "Error "

@app.route('/my_reservations')
def my_reservations():
    username = session['username']
    try:
        cur = db.connection.cursor()
        query = "SELECT r.ISBN, bk.title, r.date_of_reservation, r.ID " \
            "FROM reservation r " \
            "INNER JOIN books bk ON r.ISBN = bk.ISBN " \
            "INNER JOIN student_teacher st ON r.ID = st.ID " \
            "WHERE st.username = %s AND r.date_of_reservation IS NOT NULL AND st.school_name = bk.school_name;"
        
        values=(username,)
        cur.execute(query, values)
        reservations = cur.fetchall()
        db.connection.commit()
        for reservation in reservations:
            isbn = reservation[0]
            id = reservation[3]
            date_of_reservation = reservation[2]
            if date_of_reservation is not None:
                duration = (date.today() - date_of_reservation).days
                if duration > 7:
                    # Delete the reservation
                    query_delete_reservation = "DELETE FROM reservation WHERE ISBN =%s AND ID =%s"
                    cur.execute(query_delete_reservation, (isbn, id))
                    deleted_rows = cur.rowcount
                    db.connection.commit()
                    print(f"Deleted {deleted_rows} rows.")

                    # Update student's number of reservations
                    query_update_num_of_reserves = "UPDATE student_teacher SET num_of_reserves = num_of_reserves - 1 WHERE ID = %s"
                    cur.execute(query_update_num_of_reserves, (id,))
                    db.connection.commit()
        cur.close()
        return render_template('reservations.html', reservations = reservations)

    except Exception as e:
            print("Error ", e)
            return "Error ."

@app.route('/review_approvals')
def review_approvals():
    username = session['username']
    cur = db.connection.cursor()
    cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
    manager = cur.fetchone()
    school_name = manager[0]
    cur = db.connection.cursor()
    cur.execute("SELECT r.*, st.first_name, st.last_name, st.school_name "
                "FROM reviews r "
                "JOIN student_teacher st ON r.ID = st.ID "
                "WHERE r.approve_student_review IS NULL AND school_name=%s AND st.role = 'student'", [school_name])
    reviews = cur.fetchall()
    cur.close()
    return render_template('review_approvals.html', reviews=reviews)


@app.route('/user_approvals')
def user_approvals():
    username = session['username']
    cur = db.connection.cursor()
    cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
    manager = cur.fetchone()
    school_name = manager[0]
    cur.execute("SELECT * FROM student_teacher WHERE approve_user_registration IS NULL AND school_name = %s ", [school_name])
    users = cur.fetchall()
    cur.close()
    return render_template('user_approvals.html', users=users)

@app.route('/approve_user/<string:school_name>/<string:username>', methods=['POST'])
def approve_user(school_name, username):
    action = request.form.get('action')
    if action == 'approve':
        cur = db.connection.cursor()
        cur.execute("UPDATE manager m "
                    "INNER JOIN school s ON m.school_name = s.school_name "
                    "INNER JOIN student_teacher st ON s.school_name = st.school_name "
                    "SET m.approve_user_registration = 1 "
                    "WHERE m.school_name = %s AND st.username = %s", (school_name, username))
        db.connection.commit()
        cur.execute("UPDATE student_teacher "
                    "SET approve_user_registration = 1 , active = 1 "
                    "WHERE school_name = %s AND username = %s", (school_name, username))
        db.connection.commit()
        cur.close()
        flash('Manager has been approved.', 'success')
    else:
        cur = db.connection.cursor()
        cur.execute("UPDATE manager m "
                    "INNER JOIN school s ON m.school_name = s.school_name "
                    "INNER JOIN student_teacher st ON s.school_name = st.school_name "
                    "SET m.approve_user_registration = 0 "
                    "WHERE m.school_name = %s AND st.username = %s", (school_name, username))
        db.connection.commit()
        cur.execute("UPDATE student_teacher "
                    "SET approve_user_registration = 0, active = 0 "
                    "WHERE school_name = %s AND username = %s", (school_name, username))
        db.connection.commit()
        cur.close()
        flash('Manager has not been approved.')

    return redirect(url_for('user_approvals'))

@app.route('/approve_review/<string:school_name>/<id>/<string:isbn>', methods=['POST'])
def approve_review(school_name, id,isbn):
    action = request.form.get('action')
    if action == 'approve':
        cur = db.connection.cursor()
        cur.execute("UPDATE manager m "
                    "INNER JOIN school s ON m.school_name = s.school_name "
                    "INNER JOIN student_teacher st ON m.ID = st.ID "
                    "SET m.approve_student_review = 1 "
                    "WHERE m.school_name = %s AND st.ID = %s ", (school_name, id))
        db.connection.commit()
        cur.execute("UPDATE student_teacher "
                    "SET approve_student_review = 1 "
                    "WHERE school_name = %s AND ID = %s", (school_name, id))
        db.connection.commit()
        cur.execute("UPDATE reviews "
                    "SET approve_student_review = 1 "
                    "WHERE ID = %s AND ISBN = %s", (id,isbn))
        db.connection.commit()
        cur.close()
        flash('Review has been approved.', 'success')
    else:
        cur = db.connection.cursor()
        cur.execute("DELETE r FROM reviews AS r "
                "INNER JOIN student_teacher AS st ON r.ID = st.ID "
                "WHERE st.ID = %s", (id,))
        db.connection.commit()
        cur.close()
        flash('Manager has not been approved.')

    return redirect(url_for('review_approvals'))

@app.route("/new_review/<isbn>", methods=['GET', 'POST'])
def new_review(isbn):
    username = session['username']
    review = request.form.get('review')
    likert = request.form.get('likert')
    query = "INSERT INTO reviews (ID, ISBN, Likert, free_text) "\
            "SELECT st.ID, b.ISBN, %s, %s "\
            "FROM student_teacher st "\
            "INNER JOIN books b ON st.school_name = b.school_name "\
            "WHERE st.username = %s AND b.ISBN = %s"
    values = (likert, review, username, isbn)
    try:
        cur = db.connection.cursor()
        cur.execute(query, values)
        db.connection.commit()
        cur.close()
    except Exception as e:
            print("You can't review this book", e)
            return "You can't review this book."
    
    flash('Review submitted successfully.', 'success')
    return render_template("student.html")


@app.route('/print_card/<id>', methods=['GET', 'POST'])
def print_card(id):
    if request.method == 'POST':
        try:
            query = "SELECT * FROM student_teacher WHERE ID = %s"
            cur = db.connection.cursor()
            cur.execute(query, (id,))
            users = cur.fetchall()
            cur.close()
            return render_template('card.html', users=users)
        except Exception as e:
            flash(str(e), 'danger')
            print("Error executing query:", e)
            return render_template('manager.html')
    else:
        return redirect(url_for('manager'))
    
#Query 3.1.1
@app.route('/search_with_date', methods=['GET','POST'])
def search_with_date():
    if(request.method == 'POST'):
        month = request.form.get('month')
        year = request.form.get('year')

        if not year and not month:
            query = "SELECT s.school_name, COUNT(*) AS num_of_borrows_per_school FROM school_borrows s GROUP BY school_name "
            values = []

        elif year and not month:
            query = "SELECT s.school_name, COUNT(*) AS num_of_borrows_per_school FROM school_borrows s "\
                "WHERE YEAR(s.date_of_borrow) = %s GROUP BY school_name "
            values = (year,)

        elif not year and month:
            query = "SELECT s.school_name, COUNT(*) AS num_of_borrows_per_school FROM school_borrows s "\
                "WHERE MONTH(s.date_of_borrow) = %s GROUP BY school_name "
            values = (month,)

        elif year and month:
            query = "SELECT s.school_name, COUNT(*) AS num_of_borrows_per_school FROM school_borrows s "\
                "WHERE MONTH(s.date_of_borrow) = %s AND YEAR(s.date_of_borrow) = %s GROUP BY school_name"
            values = (month,year)

        try:
            cur = db.connection.cursor()
            cur.execute(query,values)
            borrows = cur.fetchall()
            cur.close()
        
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('process_login'))
        
        return render_template('borrows_per_school.html',borrows = borrows)


#Query 3.1.2
@app.route('/search_with_category',methods=['GET','POST'])
def search_with_category():
    if(request.method == 'POST'):
        category = request.form.get('category')
        # Which authors have written books of that category
        query1 = "SELECT DISTINCT author_name FROM book_author ba "\
            "INNER JOIN book_category bc ON ba.ISBN = bc.ISBN "\
            "INNER JOIN category c ON bc.theme = c.theme "\
            "WHERE c.theme = %s"
        
        values = (category,)
        query2 = "SELECT st.ID, st.username, st.first_name, st.last_name FROM student_teacher st "\
            "INNER JOIN borrowing br ON st.ID = br.ID "\
            "INNER JOIN books b ON br.ISBN = b.ISBN "\
            "INNER JOIN book_category bc ON b.ISBN = bc.ISBN "\
            "INNER JOIN category c ON bc.theme = c.theme "\
            "WHERE c.theme = %s AND br.date_of_borrow >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND st.role = 'teacher' AND (br.situation = 'borrowed' OR br.situation = 'returned')"

        try:
            cur = db.connection.cursor()
            cur.execute(query1, values)
            authors = cur.fetchall()
            cur.close()
        except Exception as e:
            flash(str(e), 'danger')
            print("Error executing query1:", e)
            return redirect(url_for('admin'))
        try:
            cur = db.connection.cursor()
            cur.execute(query2, values)
            teachers = cur.fetchall()
            cur.close()
        except Exception as e:
            flash(str(e), 'danger')
            print("Error executing query2:", e)
            return redirect(url_for('admin'))

        return render_template('admin_search.html', authors=authors, teachers = teachers)

    return render_template('admin.html')

#Query 3.1.3
@app.route('/young_teachers')
def young_teachers():
    query =" SELECT st.ID, st.first_name, st.last_name, st.username, st.school_name, COUNT(*) AS num_of_borrows "\
        "FROM student_teacher st "\
        "JOIN borrowing b ON st.ID = b.ID "\
        "JOIN books bk ON b.ISBN = bk.ISBN "\
        "WHERE st.role = 'teacher' AND (DATEDIFF(CURRENT_DATE(), st.date_of_birth))/365 < 40 AND st.school_name = bk.school_name "\
        "GROUP BY st.ID "\
        "HAVING COUNT(*) = ( "\
        "       SELECT COUNT(*) "\
        "       FROM borrowing b2 "\
        "       JOIN student_teacher st2 ON b2.ID = st2.ID "\
        "       WHERE st2.role = 'teacher' AND (DATEDIFF(CURRENT_DATE(), st2.date_of_birth))/365 < 40 "\
        "       GROUP BY st2.ID "\
        "       ORDER BY COUNT(*) DESC "\
        "       LIMIT 1 "\
        ");"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        teachers = cur.fetchall()
        cur.close()

    except Exception as e:
        flash(str(e), 'danger')
        print( e)
        return redirect(url_for('admin'))
    
    return render_template('young_teachers.html', teachers = teachers)

#Query 3.1.4
@app.route('/search_authors_no_borrowing')
def search_authors_no_borrowing():
    query = "SELECT DISTINCT ba.author_name FROM book_author ba "\
        "LEFT JOIN borrowing br ON ba.ISBN = br.ISBN "\
        "WHERE br.ISBN IS NULL"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        authors = cur.fetchall()
        cur.close()

    except Exception as e:
        flash(str(e), 'danger')
        print("Error executing query2:", e)
        return redirect(url_for('admin'))
    
    return render_template('search_authors_no_borrowing.html', authors=authors)

#Query 3.1.5
@app.route('/manager_borrowing')
def manager_borrowing():
    query = "SELECT m.ID, m.first_name, m.last_name, COUNT(*) AS num_of_books_borrowed "\
        "FROM manager_borrowing m "\
        "JOIN (SELECT ID, YEAR(date_of_borrow) AS year_of_borrow "\
        "      FROM manager_borrowing "\
        "      GROUP BY ID, year_of_borrow "\
        "      HAVING COUNT(*) > 20) subquery "\
        "ON m.ID = subquery.ID "\
        "WHERE YEAR(m.date_of_borrow) = subquery.year_of_borrow "\
        "GROUP BY m.ID, m.first_name, m.last_name;"
    
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        managers = cur.fetchall()
        cur.close()
        return render_template('manager_borrowing.html', managers = managers)

    except Exception as e:
        flash(str(e), 'danger')
        print(e)
        return render_template('admin.html')
    
#Query 3.1.6
@app.route('/top_3_category_pairs', methods=['GET'])
def top_3_category_pairs():
    query_top_3 = "SELECT c1.theme AS category1, c2.theme AS category2, COUNT(DISTINCT b.ISBN) AS frequency " \
        "FROM ( "\
        "SELECT DISTINCT ISBN "\
        "FROM borrowing "\
        "WHERE situation IS NOT NULL AND situation != 'waiting' "\
        ") AS b "\
        "JOIN book_category bc1 ON b.ISBN = bc1.ISBN "\
        "JOIN category c1 ON bc1.theme = c1.theme "\
        "JOIN book_category bc2 ON b.ISBN = bc2.ISBN "\
        "JOIN category c2 ON bc2.theme = c2.theme "\
        "WHERE c1.theme <> c2.theme "\
        "GROUP BY LEAST(c1.theme, c2.theme), GREATEST(c1.theme, c2.theme) "\
        "ORDER BY COUNT(*) DESC "\
        "LIMIT 3; "
    
    try:
        cur = db.connection.cursor()
        cur.execute(query_top_3)
        top3categories = cur.fetchall()
        cur.close()

    except Exception as e:
        print(e)
        flash(str(e), 'danger')
        return redirect(url_for('admin'))
    
    return render_template('top_3_category_pairs.html', top3categories=top3categories)

#Query 3.1.7
@app.route('/authors_5_books')
def authors_5_books():
    query = "SELECT a.author_name, COUNT(DISTINCT(ia.ISBN)) AS num_of_books FROM is_author ia "\
        "INNER JOIN author a ON ia.author_id = a.author_id "\
        "INNER JOIN books b ON b.ISBN = ia.ISBN "\
        "GROUP BY ia.author_id "\
        "HAVING num_of_books <= (SELECT MAX(num_of_books) - 5 FROM (SELECT COUNT(DISTINCT ia.ISBN) AS num_of_books FROM is_author ia GROUP BY ia.author_id) AS subquery) "
    
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        authors = cur.fetchall()
        cur.close()

    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('admin'))
    
    return render_template('authors_5_books.html', authors=authors)

#Query 3.2.2
@app.route('/user_with_delayed_book', methods=['GET','POST'])
def user_with_delayed_book():
    if(request.method == 'POST'):
        username = session['username']
        cur = db.connection.cursor()
        cur.execute("SELECT school_name FROM manager WHERE username = %s", [username])
        manager = cur.fetchone()
        school_name = manager[0]
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        days = request.form.get('days')

        if not first_name and not last_name and not days:

            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID, b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s"
            values = (school_name,)

        elif  first_name and not last_name and not days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID, b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND st.first_name = %s"
            values = (school_name,first_name)
        
        elif  first_name and  last_name and not days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID , b.ISBNFROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND st.first_name = %s AND st.last_name = %s"
            values = (school_name,first_name, last_name)

        elif  first_name and  last_name and  days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID , b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND st.first_name = %s st.AND last_name = %s AND days_of_delay = %s"
            values = (school_name,first_name, last_name, days)
        
        elif not first_name and last_name and not days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID, b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND st.last_name = %s"
            values = (school_name,last_name)

        elif not first_name and last_name and days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID, b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND st.last_name = %s AND days_of_delay=%s"
            values = (school_name,last_name,days)

        elif first_name and not last_name and days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID, b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND st.first_name = %s AND days_of_delay=%s"
            values = (school_name,first_name,days)
        
        elif not first_name and not last_name and days:
            query = "SELECT DATEDIFF(CURRENT_DATE(), b.date_of_borrow) AS days_of_delay, st.first_name, st.last_name, st.ID, b.ISBN FROM student_teacher st "\
                        "INNER JOIN borrowing b"\
                        " ON st.ID = b.ID" \
                        " WHERE b.situation = 'borrowed' AND b.date_of_return IS NULL AND DATEDIFF(CURRENT_DATE(), b.date_of_borrow)>7 AND st.school_name = %s AND days_of_delay=%s"
            values = (school_name,days)

        try:
            cur.execute(query,values)
            users = cur.fetchall()
            cur.close()
        
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('process_login'))
        
        return render_template('delayed_users.html',users = users)

#Query 3.2.3
@app.route('/manager_average_rating', methods=['GET','POST'])
def manager_average_rating():
    if(request.method == 'POST'):
        user_name = session['username']
        cur = db.connection.cursor()
        cur.execute("SELECT school_name FROM manager WHERE username = %s", [user_name])
        manager = cur.fetchone()
        school = manager[0]
        category = request.form.get('category')
        username = request.form.get('username')
        cur = db.connection.cursor()

        if not username and not category:
            query = "SELECT st.username, c.theme, COALESCE(AVG(r.likert), 0) AS average_likert FROM student_teacher st "\
                "LEFT JOIN reviews r ON st.ID = r.ID " \
                "LEFT JOIN books b ON b.ISBN=r.ISBN " \
                "LEFT JOIN book_category bc ON bc.ISBN = b.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE st.school_name = %s "\
                "GROUP BY st.username, c.theme"
            values = (school,)
        elif username and not category:
            query = "SELECT st.username, c.theme, COALESCE(AVG(r.likert),  0) AS average_likert FROM student_teacher st "\
                "LEFT JOIN reviews r ON st.ID = r.ID "\
                "LEFT JOIN books b ON b.ISBN=r.ISBN "\
                "LEFT JOIN book_category bc ON bc.ISBN = b.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE st.username = %s AND st.school_name = %s " \
                "GROUP BY c.theme"
            values=(username,school)
        elif not username and category:
            query = "SELECT st.username, c.theme, COALESCE(AVG(r.likert), 0) AS average_likert FROM student_teacher st "\
                "LEFT JOIN reviews r ON st.ID = r.ID "\
                "LEFT JOIN books b ON b.ISBN=r.ISBN "\
                "LEFT JOIN book_category bc ON bc.ISBN = b.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE c.theme = %s st.school_name = %s " \
                "GROUP BY c.theme"
            values = (category,school)
        elif username and category:
            query = "SELECT st.username, c.theme, COALESCE(AVG(r.likert),  0) AS average_likert FROM student_teacher st "\
                "LEFT JOIN reviews r ON st.ID = r.ID "\
                "LEFT JOIN books b ON b.ISBN=r.ISBN "\
                "LEFT JOIN book_category bc ON bc.ISBN = b.ISBN "\
                "LEFT JOIN category c ON bc.theme = c.theme "\
                "WHERE c.theme = %s AND username = %s st.school_name = %s " \
                "GROUP BY c.theme"
            values=(category,username,school)
        try:
            cur = db.connection.cursor()
            cur.execute(query,values)
            users = cur.fetchall()
            cur.close()
            return render_template('average_rating_per_user.html',users=users)
        
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('process_login'))
    
    return render_template('index.html')


if(__name__ == "__main__"):
    app.run(debug=True, host="localhost", port=3000)

