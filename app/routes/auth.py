# FlaskApp/app/routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql  # app 패키지에서 MySQL 인스턴스를 가져옵니다. 이를 통해 데이터베이스 작업을 수행합니다.
import MySQLdb.cursors, uuid


# 사용자 인증 기능을 위한 블루프린트 생성
auth = Blueprint('auth', __name__)


# 로그인 페이지 및 로그인 기능 라우트
@auth.route('/', methods=['GET', 'POST'])
def login():
    # 이미 로그인한 사용자는 게시글 목록 페이지로 리다이렉트
    if 'username' in session:
        return redirect(url_for('post.posts'))
    
    # POST 요청 처리: 사용자 로그인 시도
    if request.method == 'POST':
        username = request.form['username']  # 폼 데이터에서 사용자 이름 추출
        password = request.form['password']  # 폼 데이터에서 비밀번호 추출
        
        # MySQL 데이터베이스 커넥션에서 커서 생성
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # 사용자 이름을 기준으로 사용자 정보 조회
            cursor.execute('SELECT * FROM user WHERE username = %s', [username])
            user = cursor.fetchone()  # 조회 결과를 가져옴
        except Exception as e:
            # 데이터베이스 조회 중 오류 발생 시 사용자에게 오류 메시지 표시
            flash(f'오류가 발생했습니다: {e}', 'error')
            return render_template('login.html')
        
        # 사용자가 존재하고 비밀번호가 일치하는 경우 세션에 사용자 정보 저장
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['session_id'] = str(uuid.uuid4())
            return redirect(url_for('post.posts'))  # 게시글 목록 페이지로 리다이렉트
        else:
            # 사용자 이름이나 비밀번호가 일치하지 않는 경우 오류 메시지 표시
            flash('유효하지 않은 사용자 이름 또는 비밀번호입니다. 다시 시도하세요.', 'error')
    
    # GET 요청 또는 인증 실패 시 로그인 페이지를 다시 렌더링
    return render_template('login.html')

# 회원가입 페이지 및 회원가입 기능 라우트
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # POST 요청 처리: 사용자 회원가입 시도
    if request.method == 'POST':
        username = request.form['username']  # 폼 데이터에서 사용자 이름 추출
        password = request.form['password']  # 폼 데이터에서 비밀번호 추출
        hashed_password = generate_password_hash(password)  # 비밀번호 해싱

        # MySQL 데이터베이스 커넥션에서 커서 생성
        cursor = mysql.connection.cursor()
        
        try:
            # 사용자 정보를 데이터베이스에 삽입
            cursor.execute('INSERT INTO user (username, password) VALUES (%s, %s)', (username, hashed_password))
            mysql.connection.commit()  # 변경사항 커밋
        except Exception as e:
            # 데이터베이스 삽입 중 오류 발생 시 롤백
            mysql.connection.rollback()
            flash(f'오류가 발생했습니다: {e}', 'error')
            return render_template('signup.html')
        
        # 회원가입 성공 시 메시지 표시 및 로그인 페이지로 리다이렉트
        flash('계정이 생성되었습니다. 이제 로그인할 수 있습니다.', 'success')
        return redirect(url_for('auth.login'))
    
    # GET 요청 시 회원가입 페이지를 렌더링
    return render_template('signup.html')

# 로그아웃 기능 라우트
@auth.route('/logout', methods=['POST'])
def logout():
    # 세션에서 사용자 정보 제거
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('session_id', None)
    
    # 로그아웃 메시지 표시
    flash('로그아웃되었습니다.', 'info')
    
    # 로그인 페이지로 리다이렉트
    return redirect(url_for('auth.login'))