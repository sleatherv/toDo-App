from flask import request, redirect, make_response, render_template, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user
import unittest
from app import create_app
from app.forms import TodoForm, DeleteTodoForm, UpdateTodoForm
from app.firestore_service import update_todo, get_todos, put_todo, delete_todo

app = create_app()
# Creando un nuevo comando para test
@app.cli.command()
def test():
    test = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(test)

# manejando errores
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html', error=error)


#creamos una nueva ruta raiz
@app.route('/')
def index():
    #obtenemos la ip del usuario
    user_ip = request.remote_addr
#   usamos make_reponse y redirect a hello
    response = make_response(redirect('/hello'))
    #agregamos la ip del usuario a una cookie    # response.set_cookie('user_ip', user_ip)
    session['user_ip'] = user_ip #guardamos la variable en una sesion
    #regresamos la respuesta de flask
    return response


@app.route('/hello', methods=['GET', 'POST'])
@login_required #importante el orden en que se coloca el login required
def hello():
    #obtenemos la ip del usuario desde la cookie
    user_ip = session.get('user_ip')
    username = current_user.id #ahora viene desde el login_form
    todo_form = TodoForm()
    delete_form = DeleteTodoForm()
    update_form = UpdateTodoForm()
# creamos un contexto para las variables del template
    context = {
        'user_ip':user_ip,
        'todos':get_todos(user_id=username),
        'username': username,
        'todo_form': todo_form,
        'delete_form': delete_form,
        'update_form': update_form
    }

    if todo_form.validate_on_submit():
        put_todo(user_id=username, description=todo_form.description.data)
        flash('Your task was created successfully')
        return redirect(url_for('hello'))

    return render_template('hello.html', **context)


@app.route('/todos/delete/<todo_id>', methods=['POST'])
def delete(todo_id):
    user_id = current_user.id
    delete_todo(user_id=user_id, todo_id=todo_id)

    return redirect(url_for('hello'))


@app.route('/todos/update/<todo_id>/<int:done>', methods=['POST'])
def update(todo_id, done):
    user_id = current_user.id

    update_todo(user_id=user_id, todo_id=todo_id, done=done)

    return redirect(url_for('hello'))
