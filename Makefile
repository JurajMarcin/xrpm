PREFIX ?= /usr

install: xrpm
	install -D xrpm $(DESTDIR)$(PREFIX)/bin/xrpm

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/xrpm

.PHONY: install uninstall
