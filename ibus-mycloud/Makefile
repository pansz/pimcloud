
all: run

run:
	python main.py

install:
	mkdir -p /usr/share/ibus-mycloud
	cp *.py /usr/share/ibus-mycloud
	mkdir -p /usr/share/ibus-mycloud/icons
	cp icons/* /usr/share/ibus-mycloud/icons
	mkdir -p /usr/share/ibus/component
	cp *.xml /usr/share/ibus/component
	install ibus-engine-mycloud /usr/bin

uninstall:
	rm -rf /usr/share/ibus-mycloud
	rm -f /usr/share/ibus/component/mycloud-python.xml
	rm -f /usr/bin/ibus-engine-mycloud

clean:
	@echo Done.
