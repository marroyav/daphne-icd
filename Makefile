
PDF=main.pdf
all: $(PDF)
$(PDF): main.tex
	latexmk -pdf main.tex
clean:
	latexmk -C
