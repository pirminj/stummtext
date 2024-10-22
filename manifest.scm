;;; Dependencies of this project
;;; run this program inside `guix shell -m manifest.scm`

(specifications->manifest
 '("python"
   "python-jinja2"

   "texlive-scheme-basic"
   "texlive-pgfplots"
   "texlive-float"
   ))
