.PHONY: all
all: autotrash.1
	

autotrash.1: autotrash.md
	pandoc -s -t man $< > $@

clean:
	rm -f autotrash.1
.PHONY: clean
