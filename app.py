from flask import Flask, render_template
from routes import app as application

if __name__ == '__main__':
    application.run(debug=True, port=3000)
