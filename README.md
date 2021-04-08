# Salty Bikes

## Description



## Architecture

Our backend stack is a simple Django + DRF.

For a database, we use SQLite for now, but will port to PostgreSQL in the future.

## To run the project

You have to have python3 installed, preferably in virtual environment.  
Then simply run these commands in project directory:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

then go to http://127.0.0.1:8000/stations/ and http://127.0.0.1:8000/bikes/.

## How to contribute

Given an issue, create a branch named `{feat,bug,chore}/some-meaningful-name` and a PR to `main` branch.   
- `feat` for new functionality
- `bug` for fixing existing code
- `chore` for clean-ups, refactors, code quality changes
  
When ready, add at least two reviewers and wait for CR.   
If accepted, squash merge your changes into main and delete the feature branch.


## Code style

We use [`black`](https://github.com/psf/black) and [`flakehell`](https://flakehell.readthedocs.io/), which are included in the requirements.
There are tests that won't let you merge changes to `main` if checks for any of these fail.

It is recommended to add such code to your `.git/hooks/pre-commit` file:
```
black . --check
flakehell lint .
```
It won't let you commit code with bad style and save you a push to branch that will fail at linter checks.