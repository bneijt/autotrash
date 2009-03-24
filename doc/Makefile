.PHONY: all
all: autotrash.1
	

autotrash.1: autotrash.sgml
	docbook-to-man $< > $@

clean:
	rm -f autotrash.1
.PHONY: clean
