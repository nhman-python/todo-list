from flask import Flask, render_template, redirect, url_for, flash, request, abort
from typing import Any, Type
from datetime import datetime
from module import db, ToDo, CreateNewForm, MarkDone, UpdateTodoForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db.init_app(app)
app.secret_key = b'secure_key'


def get_current_time() -> str:
    """
    Get the current timestamp as a formatted string.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def edit_todo_by_id(todo_id: str, new_text: str) -> bool:
    """
    edit the todo by id
    :param todo_id: the id of todo
    :param new_text: the new content
    :return: true if the todo exist and update false otherwise
    """
    with db.session() as session:
        todo = session.query(ToDo).filter_by(id=todo_id).first()
        if todo:
            todo.text = new_text
            todo.last_edit = get_current_time()
            db.session.commit()
            return True
        return False


def create_todo(text: str, done=False) -> bool:
    """
    create new todo
    :param text: the text
    :param done: mark as dont default false
    :return:
    """
    new_todo = ToDo(text=text, done=done, create_at=get_current_time())
    db.session.add(new_todo)
    db.session.commit()
    return True


def get_all_todos() -> Any:
    """
    patch all the todo list
    :return: the todo as a list
    """
    with db.session() as session:
        todo_list = session.query(ToDo).all()
        if todo_list:
            return todo_list
        return None


def mark_done_by_id(todo_id: int) -> bool:
    """
    mark the todo as done
    :param todo_id: the todo id
    :return: true if exist false otherwise
    """
    with db.session() as session:
        todo = session.query(ToDo).filter_by(id=todo_id).first()
        if todo:
            todo.done = not todo.done
            db.session.commit()
            return True
        return False


def get_todo_by_id(todo_id) -> bool | Any:
    """
    get todo content by id
    :param todo_id:
    :return:
    """
    with db.session() as session:
        todo = session.query(ToDo).filter_by(id=todo_id).first()
        if todo:
            return todo
        return False


def delete_todo_by_id(todo_id) -> bool:
    """
    delete todo by the id
    :param todo_id: the todo id
    :return: true if the to todo is exist in the db
    """
    with db.session() as session:
        todo = session.query(ToDo).filter_by(id=todo_id).first()
        if todo:
            db.session.delete(todo)
            db.session.commit()
            return True
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Display the main todo list page.
    """
    form = CreateNewForm()
    todo_list = get_all_todos()
    return render_template('index.html', form=form, todo_list=todo_list)


@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    """
    Delete a todo item by its ID and redirect to the main page.
    """
    if delete_todo_by_id(todo_id):
        flash('משימה נמחקה בהצלחה', 'success')
    else:
        flash('נכשלה מחיקת המשימה', 'danger')
    return redirect(url_for('index'))


@app.route('/done/<int:todo_id>', methods=['POST'])
def mark_todo_done(todo_id):
    """
    Mark a todo item as done or undone and redirect to the main page.
    """
    form = MarkDone()
    if form.validate_on_submit():
        if mark_done_by_id(todo_id):
            flash('משימה סומנה שהושלמה 🎉', 'success')
        else:
            flash('אופס לא הצלחנו לסמן את המשימה כהושלמה', 'danger')
    else:
        flash('Oops! An error occurred. Please reload the page', 'danger')
    return redirect(url_for('index'))


@app.route('/edit-todo/<todo_id>', methods=['POST', 'GET'])
def edit_todo(todo_id):
    """
    Edit a todo item by ID and display the edit form.
    """
    form = UpdateTodoForm()
    todo = get_todo_by_id(todo_id)
    if not todo:
        return abort(404)
    if request.method == 'POST' and form.validate_on_submit():
        update_text = form.text.data
        if edit_todo_by_id(todo_id, update_text):
            flash('משימה עודכנה בהמלחה', 'success')
        else:
            flash('עידכון המשימה נכשל :-(', 'danger')
        return redirect(url_for('index'))
    return render_template('edit_todo.html', form=form, todo_content=todo)


@app.post('/new-todo')
def create_new_todo():
    """
    Create a new todo item and redirect to the main page.
    """
    form = CreateNewForm()
    if form.validate_on_submit():
        text = form.text.data
        done = form.done.data
        if create_todo(text, done):
            flash('משימה נוספה בהצלחה', 'success')
        else:
            flash('נכשל העת הוספת המשימה', 'danger')
    else:
        flash('Oops! An error occurred. Please reload the page', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
