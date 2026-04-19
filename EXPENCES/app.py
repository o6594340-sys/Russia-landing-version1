import sqlite3
import random
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'majordomo.db'

QUOTES = [
    ("Знать, куда уходят деньги — уже половина победы.", ""),
    ("Финансовая свобода начинается с одного шага: знать.", ""),
    ("Управляй деньгами, пока они не управляют тобой.", ""),
    ("Каждый платёж вовремя — это шаг к свободе.", ""),
    ("Богатство — это не деньги, это спокойствие.", ""),
    ("Лучшее вложение — в себя.", "Уоррен Баффет"),
    ("Порядок в финансах — это порядок в жизни.", ""),
    ("Ты справляешься. Один шаг за раз.", ""),
    ("Сегодня хороший день, чтобы быть в порядке.", ""),
    ("Маленькие победы складываются в большие результаты.", ""),
    ("Деньги любят счёт и уважение.", ""),
    ("Каждый рубль на своём месте — это твоя сила.", ""),
    ("Знание своих финансов — это суперспособность.", ""),
    ("Спокойствие важнее любой суммы. Ты на верном пути.", ""),
    ("Доверяй процессу. Деньги любят тех, кто их замечает.", ""),
]


# ---------- Database ----------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL DEFAULT 0,
                type TEXT DEFAULT 'debit',
                credit_limit REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS obligations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                day_of_month INTEGER NOT NULL,
                category TEXT DEFAULT 'other',
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                account_id INTEGER,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS obligation_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                obligation_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                is_paid INTEGER DEFAULT 0,
                paid_date TEXT,
                actual_amount REAL,
                UNIQUE(obligation_id, year, month),
                FOREIGN KEY (obligation_id) REFERENCES obligations(id)
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                deadline TEXT,
                current_amount REAL DEFAULT 0,
                description TEXT
            );
        ''')
        db.commit()


# ---------- Helpers ----------

def fmt_money(amount):
    """Format number as Russian money string."""
    if amount is None:
        return "0 ₽"
    return f"{int(amount):,}".replace(",", " ") + " ₽"


app.jinja_env.filters['money'] = fmt_money


def calculate_free_money():
    db = get_db()
    today = date.today()

    row = db.execute('SELECT COALESCE(SUM(balance), 0) as total FROM accounts').fetchone()
    total_balance = row['total']

    # Sum of unpaid obligations this month
    unpaid = db.execute('''
        SELECT COALESCE(SUM(o.amount), 0) as total
        FROM obligations o
        LEFT JOIN obligation_payments op
            ON op.obligation_id = o.id AND op.year = ? AND op.month = ?
        WHERE o.is_active = 1
          AND (op.is_paid IS NULL OR op.is_paid = 0)
    ''', (today.year, today.month)).fetchone()

    reserved = unpaid['total']
    free = total_balance - reserved
    return free, total_balance, reserved


def get_upcoming_obligations(days=7):
    db = get_db()
    today = date.today()
    result = []
    for row in db.execute(
        'SELECT * FROM obligations WHERE is_active = 1 ORDER BY day_of_month'
    ).fetchall():
        pay_day = row['day_of_month']
        pay_date = date(today.year, today.month, min(pay_day, 28))
        delta = (pay_date - today).days
        if -2 <= delta <= days:
            payment = db.execute('''
                SELECT is_paid FROM obligation_payments
                WHERE obligation_id = ? AND year = ? AND month = ?
            ''', (row['id'], today.year, today.month)).fetchone()
            is_paid = payment['is_paid'] if payment else 0
            result.append({
                'id': row['id'],
                'name': row['name'],
                'amount': row['amount'],
                'day': pay_day,
                'delta': delta,
                'is_paid': is_paid,
            })
    return sorted(result, key=lambda x: x['delta'])


# ---------- Routes ----------

@app.route('/')
def index():
    quote = random.choice(QUOTES)
    free, total, reserved = calculate_free_money()
    upcoming = get_upcoming_obligations(days=10)
    db = get_db()
    goals = db.execute('SELECT * FROM goals').fetchall()
    today = date.today()
    return render_template('index.html',
        quote=quote,
        free=free,
        total=total,
        reserved=reserved,
        upcoming=upcoming,
        goals=goals,
        today=today,
    )


@app.route('/income', methods=['GET', 'POST'])
def income():
    db = get_db()
    if request.method == 'POST':
        amount = float(request.form['amount'].replace(' ', '').replace(',', '.'))
        account_id = request.form.get('account_id') or None
        description = request.form.get('description', '')
        txn_date = request.form.get('date') or date.today().isoformat()

        db.execute(
            'INSERT INTO transactions (date, amount, type, description, account_id) VALUES (?, ?, ?, ?, ?)',
            (txn_date, amount, 'income', description, account_id)
        )
        if account_id:
            db.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, account_id))
        db.commit()
        return redirect(url_for('index'))

    accounts = db.execute('SELECT * FROM accounts ORDER BY name').fetchall()
    recent = db.execute(
        "SELECT t.*, a.name as account_name FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id "
        "WHERE t.type = 'income' ORDER BY t.date DESC LIMIT 10"
    ).fetchall()
    return render_template('income.html', accounts=accounts, recent=recent, today=date.today().isoformat())


@app.route('/expense', methods=['GET', 'POST'])
def expense():
    db = get_db()
    if request.method == 'POST':
        amount = float(request.form['amount'].replace(' ', '').replace(',', '.'))
        account_id = request.form.get('account_id') or None
        description = request.form.get('description', '')
        obligation_id = request.form.get('obligation_id') or None
        txn_date = request.form.get('date') or date.today().isoformat()
        today = date.today()

        db.execute(
            'INSERT INTO transactions (date, amount, type, description, account_id) VALUES (?, ?, ?, ?, ?)',
            (txn_date, amount, 'expense', description, account_id)
        )
        if account_id:
            db.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, account_id))

        if obligation_id:
            db.execute('''
                INSERT OR REPLACE INTO obligation_payments (obligation_id, year, month, is_paid, paid_date, actual_amount)
                VALUES (?, ?, ?, 1, ?, ?)
            ''', (obligation_id, today.year, today.month, txn_date, amount))

        db.commit()
        return redirect(url_for('index'))

    accounts = db.execute('SELECT * FROM accounts ORDER BY name').fetchall()
    obligations = db.execute('SELECT * FROM obligations WHERE is_active = 1 ORDER BY day_of_month').fetchall()
    recent = db.execute(
        "SELECT t.*, a.name as account_name FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id "
        "WHERE t.type = 'expense' ORDER BY t.date DESC LIMIT 10"
    ).fetchall()
    return render_template('expense.html', accounts=accounts, obligations=obligations,
                           recent=recent, today=date.today().isoformat())


@app.route('/calendar')
def calendar_view():
    db = get_db()
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    obligations = db.execute(
        'SELECT * FROM obligations WHERE is_active = 1 ORDER BY day_of_month'
    ).fetchall()

    items = []
    for ob in obligations:
        payment = db.execute('''
            SELECT * FROM obligation_payments
            WHERE obligation_id = ? AND year = ? AND month = ?
        ''', (ob['id'], year, month)).fetchone()
        is_paid = payment['is_paid'] if payment else 0
        pay_date = date(year, month, min(ob['day_of_month'], 28))
        overdue = not is_paid and pay_date < today
        items.append({
            'id': ob['id'],
            'name': ob['name'],
            'amount': ob['amount'],
            'day': ob['day_of_month'],
            'is_paid': is_paid,
            'overdue': overdue,
            'date': pay_date,
        })

    total_month = sum(i['amount'] for i in items)
    total_paid = sum(i['amount'] for i in items if i['is_paid'])
    total_left = total_month - total_paid

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    month_names = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    return render_template('calendar.html',
        items=items,
        year=year, month=month,
        month_name=month_names[month],
        today=today,
        total_month=total_month,
        total_paid=total_paid,
        total_left=total_left,
        prev_month=prev_month, prev_year=prev_year,
        next_month=next_month, next_year=next_year,
    )


@app.route('/toggle-paid/<int:obligation_id>', methods=['POST'])
def toggle_paid(obligation_id):
    db = get_db()
    today = date.today()
    year = int(request.form.get('year', today.year))
    month = int(request.form.get('month', today.month))

    existing = db.execute('''
        SELECT * FROM obligation_payments
        WHERE obligation_id = ? AND year = ? AND month = ?
    ''', (obligation_id, year, month)).fetchone()

    if existing:
        new_val = 0 if existing['is_paid'] else 1
        db.execute('''
            UPDATE obligation_payments SET is_paid = ?, paid_date = ?
            WHERE obligation_id = ? AND year = ? AND month = ?
        ''', (new_val, today.isoformat() if new_val else None, obligation_id, year, month))
    else:
        db.execute('''
            INSERT INTO obligation_payments (obligation_id, year, month, is_paid, paid_date)
            VALUES (?, ?, ?, 1, ?)
        ''', (obligation_id, year, month, today.isoformat()))

    db.commit()
    return redirect(request.referrer or url_for('calendar_view'))


@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form['name']
            balance = float(request.form.get('balance', 0) or 0)
            acc_type = request.form.get('type', 'debit')
            credit_limit = float(request.form.get('credit_limit', 0) or 0)
            db.execute(
                'INSERT INTO accounts (name, balance, type, credit_limit) VALUES (?, ?, ?, ?)',
                (name, balance, acc_type, credit_limit)
            )
        elif action == 'update_balance':
            acc_id = request.form['account_id']
            balance = float(request.form['balance'].replace(' ', '').replace(',', '.'))
            db.execute('UPDATE accounts SET balance = ? WHERE id = ?', (balance, acc_id))
        elif action == 'delete':
            acc_id = request.form['account_id']
            db.execute('DELETE FROM accounts WHERE id = ?', (acc_id,))
        db.commit()
        return redirect(url_for('accounts'))

    all_accounts = db.execute('SELECT * FROM accounts ORDER BY name').fetchall()
    total = sum(a['balance'] for a in all_accounts)
    return render_template('accounts.html', accounts=all_accounts, total=total)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_obligation':
            name = request.form['name']
            amount = float(request.form['amount'].replace(' ', '').replace(',', '.'))
            day = int(request.form['day_of_month'])
            category = request.form.get('category', 'other')
            db.execute(
                'INSERT INTO obligations (name, amount, day_of_month, category) VALUES (?, ?, ?, ?)',
                (name, amount, day, category)
            )
        elif action == 'delete_obligation':
            ob_id = request.form['obligation_id']
            db.execute('UPDATE obligations SET is_active = 0 WHERE id = ?', (ob_id,))
        elif action == 'add_goal':
            name = request.form['name']
            target = float(request.form['target_amount'].replace(' ', '').replace(',', '.'))
            deadline = request.form.get('deadline') or None
            description = request.form.get('description', '')
            db.execute(
                'INSERT INTO goals (name, target_amount, deadline, description) VALUES (?, ?, ?, ?)',
                (name, target, deadline, description)
            )
        elif action == 'goal_contribute':
            goal_id = request.form['goal_id']
            amount = float(request.form['amount'].replace(' ', '').replace(',', '.'))
            db.execute('UPDATE goals SET current_amount = current_amount + ? WHERE id = ?', (amount, goal_id))
        elif action == 'delete_goal':
            goal_id = request.form['goal_id']
            db.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
        db.commit()
        return redirect(url_for('settings'))

    obligations = db.execute(
        'SELECT * FROM obligations WHERE is_active = 1 ORDER BY day_of_month'
    ).fetchall()
    goals = db.execute('SELECT * FROM goals').fetchall()
    return render_template('settings.html', obligations=obligations, goals=goals)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
