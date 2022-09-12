.DEFAULT_GOAL := run

run:
ifdef logfile
	python task.py $(logfile)
else
	python task.py programming-task-example-data.log
endif

test:
	python tests.py
