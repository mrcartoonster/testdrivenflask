# -*- coding: utf-8 -*-
from project import create_app, db
from project.models import Stock

# Call the application factory function to construct a Flask application
# instance using the development configuration
app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Stock=Stock)
