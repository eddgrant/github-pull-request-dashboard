COMPONENT_NAME=github-pull-requests-dashboard
PYENV_VERSIONS_BASEDIR=~/.pyenv/versions
PYTHON_VERSION=2.7.10
VENV_NAME="venv-${COMPONENT_NAME}-${PYTHON_VERSION}"
VENV_DIR=${PYENV_VERSIONS_BASEDIR}/${VENV_NAME}
TARGET_DIR=target
PIP_OUTPUT_DIR=${TARGET_DIR}/pip
PIP_LOG=${PIP_OUTPUT_DIR}/pip.log
PIP_ERROR_LOG=${PIP_OUTPUT_DIR}/pip-errors.log

all: test docker

clean:
	pyenv uninstall -f ${VENV_NAME}
	rm -fr ${TARGET_DIR} ${PIP_OUTPUT_DIR}

venv:
	test -d ${VENV_DIR} || pyenv virtualenv ${PYTHON_VERSION} ${VENV_NAME}
	touch ${VENV_DIR}/bin/activate
	echo "virtualenv prepared, please run 'source ${VENV_DIR}/bin/activate' if you wish to use it in your current shell"

deps: venv
	${VENV_DIR}/bin/pip install -q --log ${PIP_LOG} --log-file ${PIP_ERROR_LOG} -r requirements.txt
	${VENV_DIR}/bin/pip install -q --log ${PIP_LOG} --log-file ${PIP_ERROR_LOG} -r requirements-tests.txt

pep8: deps
	. ${VENV_DIR}/bin/activate && pep8 pull_requests/.
	. ${VENV_DIR}/bin/activate && pep8 tests/.

test: pep8
	mkdir -p ${TARGET_DIR}/coverage
	. ${VENV_DIR}/bin/activate && ${VENV_DIR}/bin/nosetests --with-xunit --xunit-file=target/nosetests.xml --with-xcover --xcoverage-file=target/coverage/coverage.xml --cover-package=pull_requests --cover-erase --cover-html-dir=target/coverage --cover-html

run: pep8
	./run.sh &

docker:
	docker build -t pull-requests .
