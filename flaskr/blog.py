from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, nb_like'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@login_required
@bp.route('/<int:id>/like')
def like(id):
    db = get_db()
    if db.execute('SELECT * FROM likes WHERE post_id = ? AND author_id = ?',(id, g.user['id'])).fetchone():
        return redirect(url_for('blog.index'))
    else:
        db.execute(
            'INSERT INTO likes (post_id, author_id)'
            ' VALUES (?, ?)',
            (id, g.user['id'])
        )
        db.execute(
            'UPDATE post SET nb_like = nb_like+1'
            ' WHERE id = ?',
            (id,)
        )
        db.commit()
        return redirect(request.url)
    

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, nb_like'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

def get_comment(id):
    comments = get_db().execute(
        'SELECT *'
        ' FROM comment JOIN user u ON author_id = u.id'
        ' WHERE post_id = ?',
        (id,)
    )

    return comments

@bp.route('/show/<int:id>')
def show_post(id):
    post = get_post(id, check_author=False)
    comments = get_comment(id)

    if comments is None:
        return "Hello World"
    else:
        return render_template('blog/show.html', post=post, comments=comments)

@bp.route('/<int:id>/comment', methods=('GET', 'POST'))
@login_required
def comment(id):
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Write something noob'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (post_id, author_id, body)'
                ' VALUES (?, ?, ?)',
                (id, g.user['id'], body)
            )
            db.commit()
    #return render_template('blog/comment.html')
    return redirect(url_for('blog.show_post', id=id))

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))