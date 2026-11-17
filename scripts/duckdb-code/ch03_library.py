"""Глава 3. Мини-библиотека из книги: порядок таблиц в LEFT JOIN, просрочки, view, вложенный запрос.
Настоящий запуск консоли duckdb. Даты зафиксированы: вместо CURRENT_DATE стоит '2024-04-18'."""
import subprocess

SETUP = """
CREATE TABLE Authors (author_id INTEGER PRIMARY KEY, name TEXT NOT NULL, nationality TEXT, birth_year INTEGER);
CREATE TABLE Borrowers (borrower_id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, member_since DATE);
CREATE TABLE Books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER NOT NULL, genre TEXT,
    publication_year INTEGER, FOREIGN KEY (author_id) REFERENCES Authors(author_id));
CREATE TABLE Borrowings (borrowing_id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, borrower_id INTEGER NOT NULL,
    borrow_date DATE, return_date DATE, status TEXT,
    FOREIGN KEY (book_id) REFERENCES Books(book_id), FOREIGN KEY (borrower_id) REFERENCES Borrowers(borrower_id));
INSERT INTO Authors VALUES (1,'Jane Austen','British',1775),(2,'Charles Dickens','British',1812),
    (3,'Agatha Christie','British',1890),(4,'J.K. Rowling','British',1965),(5,'Tolkien','British',1892),
    (6,'Mark Twain','American',1835);
INSERT INTO Borrowers VALUES (1,'John Smith','john.smith@example.com','2022-01-01'),
    (2,'Emma Johnson','emma.johnson@example.com','2021-12-15'),(3,'Michael Brown','michael.brown@example.com','2022-02-20'),
    (4,'Sophia Wilson','sophia.wilson@example.com','2022-03-10'),(5,'William Taylor','william.taylor@example.com','2022-04-05');
INSERT INTO Books VALUES (1,'Pride and Prejudice',1,'Classic',1813),(2,'Oliver Twist',2,'Novel',1837),
    (3,'Murder on the Orient Express',3,'Mystery',1934),(4,'Harry Potter and the Philosopher''s Stone',4,'Fantasy',1997),
    (5,'The Hobbit',5,'Fantasy',1937);
INSERT INTO Borrowings VALUES (1,1,1,'2022-04-10','2022-04-25','Returned'),(2,3,2,'2022-03-20',NULL,'On Loan'),
    (3,4,3,'2022-04-05','2022-04-05','Returned'),(4,2,4,'2022-04-15',NULL,'On Loan'),
    (5,5,5,'2022-03-30','2022-04-20','Returned'),(6,1,3,'2022-04-26',NULL,'On Loan');
"""


def run(sql):
    r = subprocess.run(["duckdb", "-csv", "-header"], input=SETUP + sql, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    return r.stdout.rstrip("\n")


print("-- Authors LEFT JOIN Books: шесть строк, Mark Twain без книги")
print(run("""SELECT a.name, b.title FROM Authors a LEFT JOIN Books b ON a.author_id = b.author_id ORDER BY a.author_id;"""))
print("\n-- Books INNER JOIN Authors: пять строк")
print(run("""SELECT count(*) AS books FROM Books b INNER JOIN Authors a ON b.author_id = a.author_id;"""))
print("\n-- Средний возраст авторов и самый старый автор на 2024 год")
print(run("""SELECT avg(2024 - birth_year) AS avg_age FROM Authors;"""))
print(run("""SELECT name, 2024 - birth_year AS age FROM Authors WHERE birth_year = (SELECT min(birth_year) FROM Authors);"""))
print("\n-- View просрочек: возвращённые книги (срок 14 дней)")
print(run("""CREATE VIEW overdue_borrowings AS
SELECT bw.name AS borrower_name, b.title AS book_title,
       date_diff('day', br.borrow_date, br.return_date) - 14 AS overdue
FROM Borrowings br
JOIN Books b ON br.book_id = b.book_id
JOIN Borrowers bw ON br.borrower_id = bw.borrower_id
WHERE br.return_date IS NOT NULL AND date_diff('day', br.borrow_date, br.return_date) > 14;
SELECT * FROM overdue_borrowings ORDER BY borrower_name;"""))
print("\n-- Невозвращённые книги на дату 2022-06-10")
print(run("""SELECT b.title, bw.name AS borrower_name, date_diff('day', br.borrow_date, DATE '2022-06-10') - 14 AS overdue
FROM Borrowings br
JOIN Books b ON br.book_id = b.book_id
JOIN Borrowers bw ON br.borrower_id = bw.borrower_id
WHERE br.return_date IS NULL AND date_diff('day', br.borrow_date, DATE '2022-06-10') > 14
ORDER BY b.book_id;"""))
print("\n-- Самая популярная книга: три вложенных SELECT")
print(run("""SELECT b.title, bw.name AS borrower_name, br.borrow_date
FROM Borrowings br
JOIN Books b ON br.book_id = b.book_id
JOIN Borrowers bw ON br.borrower_id = bw.borrower_id
WHERE b.book_id IN (
    SELECT book_id FROM Borrowings GROUP BY book_id
    HAVING count(*) = (SELECT max(cnt) FROM (SELECT count(*) AS cnt FROM Borrowings GROUP BY book_id))
)
ORDER BY br.borrow_date;"""))
print("\n-- Ошибка: удалить таблицу, на которую ссылаются")
r = subprocess.run(["duckdb"], input=SETUP + "DROP TABLE Authors;", capture_output=True, text=True, timeout=60)
print(r.stderr.strip().splitlines()[0])
