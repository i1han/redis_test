# app.py
# Flask 애플리케이션의 진입점입니다. 애플리케이션을 생성하고 실행합니다.
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # 디버그 모드를 활성화하여 애플리케이션을 실행합니다.