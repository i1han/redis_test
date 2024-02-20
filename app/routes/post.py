# FlaskApp/app/routes/post.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app import mysql, redis_cluster
import MySQLdb.cursors
import json
from datetime import datetime

post = Blueprint('post', __name__)
serialized_posts = []


@post.route('/posts', methods=['GET', 'POST'])
def posts():
    # 사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트합니다.
    if 'username' not in session:
        flash('로그인 후에 게시물을 보고 작성할 수 있습니다.', 'error')
        return redirect(url_for('auth.login'))

    # Redis에서 세션 정보를 가져옵니다.
    user_id = session.get('user_id')
    session_data = redis_cluster.hgetall(f'user:{user_id}:session')

    # 캐시된 게시물을 불러옵니다.
    cached_posts = redis_cluster.get('cached_posts')
    
    serialized_posts = []
    
    if cached_posts:
        # 캐시된 게시물이 있는 경우 디코딩하여 사용합니다.
        posts = json.loads(cached_posts)
        serialized_posts = posts  # 값 할당

    else:
        try:
            # MySQL 데이터베이스 연결에 대한 커서를 생성합니다.
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
            # 모든 게시물을 조회합니다.
            cursor.execute('SELECT * FROM post ORDER BY created_at DESC')
            posts = cursor.fetchall()  # 검색 결과를 가져옵니다.
            
            # 각 게시물을 딕셔너리로 변환하여 직렬화합니다.

            for post in posts:
                serialized_post = {
                    'id': post['id'],
                    'title': post['title'],
                    'content': post['content'],
                    'created_at': post['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id': post['user_id']
                }
                serialized_posts.append(serialized_post)
            
            # 캐시된 게시물을 Redis에 저장합니다.
            redis_cluster.set('cached_posts', json.dumps(serialized_posts))
        except Exception as e:
            # 데이터베이스 쿼리 중 오류가 발생한 경우 오류 메시지를 표시합니다.
            flash(f'오류가 발생했습니다: {e}', 'error')
            return render_template('posts.html', posts=[], session_data=session_data)

    # 세션에서 사용자 이름을 가져와 템플릿에 전달합니다.
    session_data = {'username': session.get('username')}
    
    return render_template('posts.html', posts=serialized_posts, session_data=session_data)



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
        created_at = datetime.now()  # 현재 시간을 가져옵니다.

        try:
            # MySQL 데이터베이스에 새로운 게시물 데이터를 삽입합니다.
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO post (title, content, created_at, user_id) VALUES (%s, %s, %s, %s)',
                           (title, content, created_at, user_id))
            mysql.connection.commit()  # 변경 사항을 커밋합니다.
            
            # 게시물이 성공적으로 추가되었으므로 캐시된 데이터를 업데이트합니다.
            cursor.execute('SELECT * FROM post ORDER BY created_at DESC')
            posts_tuple = cursor.fetchall()  # 새로운 게시물이 추가된 목록을 가져옵니다.
            
            # 각 게시물을 딕셔너리로 변환하여 직렬화합니다.
            serialized_posts = []
            for post_tuple in posts_tuple:
                post = {'id': post_tuple[0], 'title': post_tuple[1], 'content': post_tuple[2], 'created_at': post_tuple[3], 'user_id': post_tuple[4]}
                post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                serialized_posts.append(post)
            
            # 캐시된 게시물을 Redis에 업데이트합니다.
            redis_cluster.set('cached_posts', json.dumps(serialized_posts))
            
            flash('게시물이 성공적으로 작성되었습니다!', 'success')  # 성공 메시지를 표시합니다.
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'error')
        
        return redirect(url_for('post.posts'))

    # GET 요청을 처리하여 새로운 게시물 작성 페이지를 렌더링합니다.
    return render_template('createposts.html')
