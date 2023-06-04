CREATE TABLE IF NOT EXISTS school(
    school_name VARCHAR(50) NOT NULL,
    school_address VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    city VARCHAR(20) NOT NULL,
    principal_name VARCHAR(40) NOT NULL,
    phone_number bigint(20) NOT NULL,
    UNIQUE(email),
    UNIQUE(phone_number),
    PRIMARY KEY(school_name)
    );

CREATE TABLE IF NOT EXISTS student_teacher(
    ID int(9) NOT NULL AUTO_INCREMENT,
    Username VARCHAR(20) NOT NULL,
    Password VARCHAR(15) NOT NULL,
    school_name VARCHAR(50) NOT NULL,
    num_of_borrows int(1) NOT NULL DEFAULT 0,
    num_of_reserves int(1) NOT NULL DEFAULT 0,
    approve_user_registration BOOLEAN,
    approve_borrowing BOOLEAN,
    approve_reservation BOOLEAN,
    role enum('student','teacher'),
    active BOOLEAN,
    date_of_birth date NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    approve_student_review BOOLEAN DEFAULT NULL,
    PRIMARY KEY(ID),
    UNIQUE(Username),
    CONSTRAINT school_name_fk FOREIGN KEY(school_name) REFERENCES school(school_name)
    );

CREATE TABLE IF NOT EXISTS admin (
    ID int(9) NOT NULL,
    approve_manager BOOLEAN,
    Username VARCHAR(20) NOT NULL,
    Password VARCHAR(15) NOT NULL,
    school_name VARCHAR(50) NOT NULL,
    PRIMARY KEY(ID,school_name),
    FOREIGN KEY(school_name) REFERENCES school(school_name)
    );

CREATE TABLE IF NOT EXISTS manager(
    ID int(9) NOT NULL AUTO_INCREMENT,
    Username VARCHAR(20) NOT NULL,
    Password VARCHAR(15) NOT NULL,
    approve_manager BOOLEAN,
    approve_user_registration BOOLEAN,
    approve_student_review BOOLEAN,
    approve_borrowing BOOLEAN,
    approve_reservation BOOLEAN,
    school_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    date_of_birth date NOT NULL,
    PRIMARY KEY(ID,first_name,last_name),
    UNIQUE(Username),
    CONSTRAINT school_name__fk FOREIGN KEY(school_name) REFERENCES school(school_name) ON UPDATE CASCADE
    );

CREATE TABLE IF NOT EXISTS books(
	ISBN VARCHAR(13) NOT NULL,
	title VARCHAR(50) NOT NULL,
	publisher VARCHAR(50) NOT NULL,
	num_of_pages int(4) NOT NULL,
	summary TEXT,
	cover_image BLOB NOT NULL,
	language VARCHAR(15) NOT NULL,
    keywords TEXT NOT NULL,
	copies int(3),
	school_name VARCHAR(50) NOT NULL,
	PRIMARY KEY(ISBN,school_name),
	FOREIGN KEY (school_name) REFERENCES school(school_name)
	);

CREATE TABLE IF NOT EXISTS reviews(
    ID int(9) NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    Likert int(5) NOT NULL,
    free_text TEXT NOT NULL DEFAULT '',
    approve_student_review BOOLEAN DEFAULT NULL,
    PRIMARY KEY(ID,ISBN),
    FOREIGN KEY(ID) REFERENCES student_teacher(ID),
    FOREIGN KEY(ISBN) REFERENCES books(ISBN)
    );

CREATE TABLE IF NOT EXISTS reservation(
    ID int(9) NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    date_of_reservation date,
    PRIMARY KEY(ID,ISBN),
    FOREIGN KEY(ID) REFERENCES student_teacher(ID),
    FOREIGN KEY(ISBN) REFERENCES books(ISBN)
    );

CREATE TABLE IF NOT EXISTS borrowing(
    ID int(9) NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    date_of_borrow date,
    date_of_return date,
    situation enum('delayed','borrowed','returned','waiting') DEFAULT NULL,
    PRIMARY KEY(ID,ISBN),
    FOREIGN KEY(ID) REFERENCES student_teacher(ID),
    FOREIGN KEY(ISBN) REFERENCES books(ISBN)
    );

CREATE TABLE IF NOT EXISTS category(
    theme VARCHAR(50) NOT NULL,
    PRIMARY KEY(theme)
    );

CREATE TABLE IF NOT EXISTS book_category(
    theme VARCHAR(50) NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    PRIMARY KEY(theme,ISBN),
    FOREIGN KEY(ISBN) REFERENCES books(ISBN),
    FOREIGN KEY(theme) REFERENCES category(theme) ON UPDATE CASCADE
    );

CREATE TABLE IF NOT EXISTS author(
    author_id int(7) NOT NULL auto_increment,
    author_name VARCHAR(50) NOT NULL,
    PRIMARY KEY(author_id)
    );

CREATE TABLE IF NOT EXISTS is_author(
    ISBN VARCHAR(13) NOT NULL,
    author_id int(7) NOT NULL AUTO_INCREMENT,
    PRIMARY KEY(ISBN,author_id),
    FOREIGN KEY(author_id) REFERENCES author(author_id),
    FOREIGN KEY(ISBN) REFERENCES books(ISBN)
    );

CREATE INDEX idx_situation ON borrowing(situation);

CREATE INDEX idx_role ON student_teacher(role);

DELIMITER $$
CREATE OR REPLACE TRIGGER update_manager_approval_trigger
AFTER UPDATE ON admin
FOR EACH ROW
BEGIN
    IF NEW.approve_manager = 1 THEN
        UPDATE manager
        SET approve_manager = 1
        WHERE school_name = NEW.school_name;
    END IF;
END $$
DELIMITER ;


CREATE VIEW book_author(ISBN,title,publisher,num_of_pages,summary,cover_image,language,keywords,copies,school_name,author_id,author_name) AS
    SELECT b.ISBN,b.title,b.publisher,b.num_of_pages,b.summary,b.cover_image,b.language,b.keywords,b.copies,b.school_name,a.author_id,a.author_name FROM books b
    INNER JOIN is_author ia
    ON b.ISBN = ia.ISBN
    INNER JOIN author a
    ON ia.author_id = a.author_id;

CREATE VIEW manager_borrowing AS
    SELECT m.ID, m.first_name, m.last_name, b.ISBN, br.date_of_borrow
    FROM manager m
    INNER JOIN school s ON m.school_name = s.school_name
    INNER JOIN student_teacher st ON st.school_name  = s.school_name
    INNER JOIN borrowing br on st.ID = br.ID
    INNER JOIN books b on br.ISBN = b.ISBN
    WHERE br.date_of_borrow IS NOT NULL AND b.school_name = m.school_name;

CREATE VIEW school_borrows AS
    SELECT s.school_name, br.ISBN ,br.date_of_borrow FROM school s
    INNER JOIN student_teacher st ON st.school_name = s.school_name
    INNER JOIN borrowing br ON st.ID = br.ID
    WHERE br.date_of_borrow is NOT NULL ;

