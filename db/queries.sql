--- CREATE TABLES

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL primary key,
    username VARCHAR (200) unique not null,
    hashed_password VARCHAR (1000) not null,
    balance BIGINT default 0,
    is_verified BOOL default false
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL primary key,
    transaction_type BOOLEAN not null,
    amount BIGINT not null,
    created_at TIMESTAMP default NOW(),
    id_user BIGINT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id BIGSERIAL primary key,
    start_date TIMESTAMP not null,
    end_date TIMESTAMP not null,
    id_user BIGINT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS report_transactions (
    id BIGSERIAL primary key,
    id_report BIGINT REFERENCES reports(id),
    id_transaction BIGINT REFERENCES transactions(id)
);

--- INSERT ROW

INSERT INTO users (username, hashed_password, balance, is_verified) VALUES
('george', 'sfasa323r', 100, false),
('maria', 'sdafa3rkn', 200, false);

INSERT INTO transactions (transaction_type, amount, id_user) VALUES
(false, 100, 1),
(true, 200, 2);

INSERT INTO transactions (transaction_type, amount, created_at, id_user) VALUES
(false, 100, '2024-01-08', 1),
(true, 200, '2024-01-08', 2);

INSERT INTO reports (start_date, end_date, id_user) VALUES
('2023-01-01', '2024-01-01', 1),
('2024-03-05', '2024-07-11', 2);

INSERT INTO report_transactions (id_report, id_transaction,) VALUES
(1,1),
(1,2),
(1,3),
(2,2),
(2,3);

--- SELECT ROW

SELECT id, username, balance, is_verified
FROM users
WHERE username = 'george';


SELECT id, transaction_type, amount, created_at, id_user
FROM transactions
WHERE id_user = 2;

SELECT
    reports.id,
    reports.start_date,
    reports.end_date,
    reports.id_user,
    report_transactions.id_transaction
FROM reports
INNER JOIN report_transactions
ON reports.id = report_transactions.id_report
WHERE id_user = 2;

SELECT
    reports.id,
    reports.start_date,
    reports.end_date,
    reports.id_user,
    transactions.created_at,
    transactions.amount,
    transactions.transaction_type
FROM reports
INNER JOIN transactions
ON transactions.created_at >= reports.start_date AND transactions.created_at <= reports.end_date
WHERE transactions.created_at = '2024-01-08';

--- UPDATE ROW

UPDATE users
SET is_verified = true
WHERE username = 'george';

UPDATE users
SET balance = balance - 100
WHERE username = 'george';

UPDATE transactions
SET amount = 50
FROM users
WHERE transactions.id_user = users.id AND users.username = 'george';

UPDATE reports
SET start_date = '2022-02-02'
WHERE transactions.id_user = (SELECT users.id FROM users WHERE users.username = 'george');

--- DELETE ROW

DELETE FROM users
WHERE id = 2;

DELETE FROM transactions
WHERE created_at >= '2023-05-01' AND created_at <= '2024-05-01';

DELETE FROM reports
WHERE reports.id_user = (SELECT users.id FROM users WHERE users.username = 'george');
