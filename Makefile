MAIN    := master
LATEXMK := latexmk
FLAGS   := -pdf -interaction=nonstopmode -halt-on-error -file-line-error

# private/ holds the poster notes, kept out of the published document on purpose.
# Its driver lives in private/ but needs preamble.sty and macros.tex from here.
PRIVATE := private/posters
PENV    := TEXINPUTS=".:$(CURDIR):" BIBINPUTS=".:$(CURDIR):"

.PHONY: all posters both check pages preview clean distclean

all:
	$(LATEXMK) $(FLAGS) $(MAIN).tex

posters:
	$(PENV) $(LATEXMK) $(FLAGS) -cd $(PRIVATE).tex

both: all posters

# Fail loudly on the things a zero exit status does not catch.
# -g forces at least one pass so the .log is always from a converged run; without it a
# stale .log from an earlier failed build gets checked instead. latexmk's own stdout is
# discarded because it re-echoes warnings from intermediate passes, which interleave with
# these checks and read as failures of the final document.
check:
	@$(LATEXMK) -g $(FLAGS) $(MAIN).tex > /dev/null 2>&1 || \
	  (echo "FAIL: build failed, run 'make' to see why"; exit 1)
	@$(PENV) $(LATEXMK) -g $(FLAGS) -cd $(PRIVATE).tex > /dev/null 2>&1 || \
	  (echo "FAIL: posters build failed, run 'make posters' to see why"; exit 1)
	@echo "== undefined references, citations, missing files =="
	@! grep -a -nE 'LaTeX Warning: (Reference|Citation)|File .* not found|There were undefined' \
	     $(MAIN).log $(PRIVATE).log \
	  || (echo "FAIL: unresolved above"; exit 1)
	@echo "none"
	@echo "== overfull hboxes worse than 15pt =="
	@! grep -a -hoE 'Overfull \\hbox \([0-9]+\.[0-9]+pt' $(MAIN).log $(PRIVATE).log \
	   | awk -F'[(]' '{ if ($$2+0 > 15) print }' | grep . \
	  || (echo "FAIL: see above"; exit 1)
	@echo "none"
	@echo "== em dashes =="
	@! grep -rnE --include='*.tex' --include='*.sty' --include='*.md' -e '—' -e '\-{3}' -e '\\textemdash' . \
	  || (echo "FAIL: em dashes above"; exit 1)
	@echo "none"

# Per-chapter page counts, to police the 2 to 3 page budget.
pages: all
	@python3 tools/page_report.py

preview: all
	@mkdir -p ../build/preview
	pdftoppm -r 110 -jpeg -jpegopt quality=85 $(MAIN).pdf ../build/preview/page
	@ls ../build/preview | tail -3

clean:
	$(LATEXMK) -c $(MAIN).tex
	-$(PENV) $(LATEXMK) -c -cd $(PRIVATE).tex
	rm -f $(MAIN).bbl $(MAIN).bbl-SAVE-ERROR $(MAIN).run.xml $(MAIN).aux \
	      chapters/*.aux tutorials/*.aux synthesis/*.aux

distclean: clean
	$(LATEXMK) -C $(MAIN).tex
	-$(PENV) $(LATEXMK) -C -cd $(PRIVATE).tex
	rm -f $(MAIN).pdf $(PRIVATE).pdf
