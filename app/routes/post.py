# FlaskApp/app/routes/post.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from datetime import datetime
from app import mysql, redis_cluster  # app 모듈에서 직접 mysql 객체를 가져옵니다. 이 객체를 통해 데이터베이스 작업을 수행합니다.
import MySQLdb.cursors

# 포스트 관련 함수를 위한 블루프린트 생성
post = Blueprint('post', __name__)

@post.route('/posts', methods=['GET', 'POST'])
def posts():
    # 사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트합니다.
    if 'username' not in session:
        flash('로그인 후에 게시물을 보고 작성할 수 있습니다.', 'error')
        return redirect(url_for('auth.login'))

    # Redis에서 세션 정보를 가져옵니다.
    user_id = session.get('user_id')
    session_data = redis_cluster.hgetall(f'user:{user_id}:session')

    # MySQL 데이터베이스 연결에 대한 커서를 생성합니다.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # 모든 게시물을 조회합니다.
        cursor.execute('SELECT * FROM post')
        posts = cursor.fetchall()  # 검색 결과를 가져옵니다.
    except Exception as e:
        # 데이터베이스 쿼리 중 오류가 발생한 경우 오류 메시지를 표시합니다.
        flash(f'오류가 발생했습니다: {e}', 'error')
        return render_template('posts.html', posts=[], session_data=session_data)
    
    # 세션에서 사용자 이름을 가져와 템플릿에 전달합니다.
    session_data = {'username': session.get('username')}
    
    # 게시물 목록 페이지를 렌더링합니다.
    return render_template('posts.html', posts=posts, session_data=session_data)

@post.route('/createposts', methods=['GET', 'POST'])
def createposts():
    # 사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트합니다.
    if 'username' not in session:
        flash('로그인 후에 게시물을 보고 작성할 수 있습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # POST 요청을 처리하여 새로운 게시물을 만듭니다.
    if request.method == 'POST':
        title = request.form['title']  # 폼 데이터에서 게시물 제목을 추출합니다.
        content = request.form['content']  # 폼 데이터에서 게시물 내용을 추출합니다.
        user_id = session.get('user_id')  # 세션에서 사용자 ID를 추출합니다.
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간을 문자열로 형식화합니다.

        try:
            # MySQL 데이터베이스에 새로운 게시물 데이터를 삽입합니다.
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO post (title, content, created_at, user_id) VALUES (%s, %s, %s, %s)',
                           (title, content, created_at, user_id))
            mysql.connection.commit()  # 변경 사항을 커밋합니다.
            flash('게시물이 성공적으로 작성되었습니다!', 'success')  # 성공 메시지를 표시합니다.
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
        
        return redirect(url_for('post.posts'))

    # GET 요청을 처리하여 새로운 게시물 작성 페이지를 렌더링합니다.
    return render_template('createposts.html')