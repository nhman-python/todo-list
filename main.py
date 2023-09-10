from typing import Any
from module import db, ToDo, CreateNewForm, MarkDone, UpdateTodoForm
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_talisman import Talisman
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db.init_app(app)
app.secret_key = b'secure_key'


def time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def edit_todo_by_id(todo_id: str, new_text: str) -> bool:
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        todo.text = new_text
        todo.last_edit = time_now()
        db.session.commit()
        return True
    return False


def create_todo(text: str, done=False):
    new_todo = ToDo(text=text, done=done, create_at=time_now())
    db.session.add(new_todo)
    db.session.commit()
    return True


def get_all_todo() -> Any | None:
    todo_list = ToDo.query.all()
    if todo_list:
        return todo_list
    return None


def done_by_id(todo_id: int):
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo.done:
        todo.done = False
    else:
        todo.done = True
    db.session.commit()
    return True


def path_one(todo_id):
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        return todo
    return False


def delete_by_id(todo_id):
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreateNewForm()
    todo_list = get_all_todo()
    return render_template('index.html', form=form, todo_list=todo_list)


@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo_list(todo_id):
    if delete_by_id(todo_id):
        flash('Delete message successfully', 'success')
    else:
        flash('Delete message failed', 'danger')
    return redirect(url_for('index'))


@app.route('/done/<int:todo_id>', methods=['POST'])
def mark_done(todo_id):
    form = MarkDone()
    if form.validate_on_submit():
        if done_by_id(todo_id):
            flash('משימה הושלמה בהצלחה', 'success')
        else:
            flash('המשימה לא הושלמה', 'danger')
    else:
        flash('אופס!... קרתה שגיאה נא לטעון את הדף מחדש', 'danger')
    return redirect(url_for('index'))


@app.route('/edit-todo/<todo_id>', methods=['POST', 'GET'])
def edit_todo(todo_id):
    form = UpdateTodoForm()
    todo = path_one(todo_id)
    if not todo:
        return abort(404)
    if request.method == 'POST':
        if form.validate_on_submit():
            update_text = form.text.data
            if edit_todo_by_id(todo_id, update_text):
                flash('המשימה עודכנה בהצלחה', 'success')
                return redirect(url_for('index'))
            flash('המשימה לא עודכנה :-(', 'danger')
            return redirect(url_for('index'))
        flash('אופס!... קרתה שגיאה נא לטעון את הדף מחדש', 'danger')
        return redirect(url_for('index'))
    return render_template('edit_todo.html', form=form, todo_content=todo)


@app.route('/new-todo', methods=['POST'])
def create_todos():
    form = CreateNewForm()
    if form.validate_on_submit():
        text = form.text.data
        done = form.done.data
        if create_todo(text, done):
            flash('המשימה נוספה בהצלחה', 'success')
        else:
            flash('לא הצלחנו ללהוסיף את המשימה', 'danger')
    else:
        flash('אופס!... קרתה שגיאה נא לטעון את הדף מחדש', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
