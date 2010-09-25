
all: run

run:
	python main.py

install:
	mkdir -p /usr/share/ibus-mycloud
	cp *.py /usr/share/ibus-mycloud
	mkdir -p /usr/share/ibus-mycloud/icons
	mkdir -p /usr/share/ibus/component
	cp *.xml /usr/share/ibus/component
	install ibus-engine-mycloud /usr/bin

clean:
	@echo Done.
