FROM python:2-onbuild
EXPOSE 8000
CMD [ "pip" "install" "-q" "${PIP_ERROR_LOG}" "-r", "requirements.txt"]
CMD [ "gunicorn", "--config=gunicorn.py", "pull_requests.pull_requests_web:app", "--debug", "--access-logfile", "-", "--error-log", "-", "--log-config", "logging.conf" ]