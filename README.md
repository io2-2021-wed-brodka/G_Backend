# Salty Bikes

## Architecture

Our backend stack is a simple Django + DRF.

For a database, we use SQLite for now, but will port to PostgreSQL in the future.

## To run the project

To simply run project do so as docker container.
```
docker-compose up
```
This will backend on http://0.0.0.0:8080.
There is a pre-created `admin` user with password `admin`.

If you are a contributor however, it's best to run the server locally.   
You have to have `python3` installed.

You must create a file called `.env` in top level directory with following contents:
```
# any random string (the one used in production should be kept a secret)
SECRET_KEY=mysecretkey
# can be set to False by other teams using the release version
DEBUG=True
```

Then simply run these commands in project directory:
```
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py loaddata fixtures/development.json
python manage.py runserver 8080 
```
Running `loaddata` creates some mock data and most importantly an admin user with username `admin` and password `admin`.

Internal documentation of endpoints is available as [swagger](https://127.0.0.1:8080/swagger/).

## How to contribute

Given an issue, create a branch named `{feat,bug,chore}/<jira-issue-id>-some-meaningful-name` (e.g. `feat/70-rented-bike-list`) and a PR to `main` branch.   
- `feat` for new functionality (remember to add test for it)
- `bug` for fixing existing code (remember to add test preventing the bug in the future)
- `chore` for clean-ups, refactors, code quality changes and CI improvements
  
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
Remember to run `chmod +x .git/hooks/pre-commit` or equivalent.
It won't let you commit code with bad style and save you a push to branch that will fail at linter checks.

Additionally, add this to `/git/hooks/pre-push`:
```
python manage.py test
```
Remember to run `chmod +x .git/hooks/pre-push` or equivalent.
