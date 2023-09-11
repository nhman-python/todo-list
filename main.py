from flask import Flask, render_template, redirect, url_for, flash, request, abort
from typing import Any
from datetime import datetime
from module import db, ToDo, CreateNewForm, MarkDone, UpdateTodoForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db.init_app(app)
app.secret_key = b'secure_key'


def time_now() -> str:
    """
    Get the current timestamp as a formatted string.

    :return: A string representing the current timestamp in 'YYYY-MM-DD HH:MM:SS' format.
    :rtype: str
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def edit_todo_by_id(todo_id: str, new_text: str) -> bool:
    """
    Edit a todo item's text by its ID.

    :param todo_id: The ID of the todo item to be edited.
    :type todo_id: str
    :param new_text: The new text to replace the existing text.
    :type new_text: str

    :return: True if the todo item was successfully edited, False otherwise.
    :rtype: bool
    """
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        todo.text = new_text
        todo.last_edit = time_now()
        db.session.commit()
        return True
    return False


def create_todo(text: str, done=False) -> bool:
    """
    Create a new todo item.

    :param text: The text of the new todo item.
    :type text: str
    :param done: Whether the todo item is marked as done. Default is False.
    :type done: bool

    :return: True if the todo item was successfully created, False otherwise.
    :rtype: bool
    """
    new_todo = ToDo(text=text, done=done, create_at=time_now())
    db.session.add(new_todo)
    db.session.commit()
    return True


def get_all_todo() -> Any | None:
    """
    Get a list of all todo items.

    :return: A list of todo items if there are any, otherwise None.
    :rtype: list[ToDo] | None
    """
    todo_list = ToDo.query.all()
    if todo_list:
        return todo_list
    return None


def done_by_id(todo_id: int) -> bool:
    """
    Mark a todo item as done or undone by its ID.

    :param todo_id: The ID of the todo item to be marked as done/undone.
    :type todo_id: int

    :return: True if the todo item's status was successfully updated, False otherwise.
    :rtype: bool
    """
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        todo.done = not todo.done
        db.session.commit()
        return True
    return False


def path_one(todo_id) -> ToDo | bool:
    """
    Get a specific todo item by its ID.

    :param todo_id: The ID of the todo item to retrieve.

    :return: The todo item if found, or False if not found.
    :rtype: ToDo | bool
    """
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        return todo
    return False


def delete_by_id(todo_id) -> bool:
    """
    Delete a todo item by its ID.

    :param todo_id: The ID of the todo item to be deleted.

    :return: True if the todo item was successfully deleted, False otherwise.
    :rtype: bool
    """
    todo = ToDo.query.filter_by(id=todo_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Display the main todo list page.

    :return: The main todo list page with a list of todos and a form for creating new todos.
    :rtype: HTML page
    """
    form = CreateNewForm()
    todo_list = get_all_todo()
    return render_template('index.html', form=form, todo_list=todo_list)


@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo_list(todo_id):
    """
    Delete a todo item by ID and redirect to the main page.

    :param todo_id: The ID of the todo item to be deleted.
    :type todo_id: int

    :return: Redirects to the main page after deleting the todo item.
    :rtype: redirect
    """
    if delete_by_id(todo_id):
        flash('Delete message successfully', 'success')
    else:
        flash('Delete message failed', 'danger')
    return redirect(url_for('index'))


@app.route('/done/<int:todo_id>', methods=['POST'])
def mark_done(todo_id):
    """
    Mark a todo item as done or undone and redirect to the main page.

    :param todo_id: The ID of the todo item to be marked as done/undone.
    :type todo_id: int

    :return: Redirects to the main page after marking the todo item.
    :rtype: redirect
    """
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
    """
    Edit a todo item by ID and display the edit form.

    :param todo_id: The ID of the todo item to be edited.

    :return: The edit todo page with the edit form.
    :rtype: HTML page
    """
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
    """
    Create a new todo item and redirect to the main page.

    :return: Redirects to the main page after creating a new todo item.
    :rtype: redirect
    """
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
