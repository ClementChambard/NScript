;;; sdas-mode.el --- Description -*- lexical-binding: t; -*-
;;
;; Copyright (C) 2022 Clement Chambard
;;
;; Author: Clement Chambard <https://github.com/clement>
;; Maintainer: Clement Chambard <cclems2002@gmail.com>
;; Created: March 26, 2022
;; Modified: March 26, 2022
;; Version: 0.0.1
;; Keywords: abbrev bib c calendar comm convenience data docs emulations extensions faces files frames games hardware help hypermedia i18n internal languages lisp local maint mail matching mouse multimedia news outlines processes terminals tex tools unix vc wp
;; Homepage: https://github.com/clement/sdas-mode
;; Package-Requires: ((emacs "24.3"))
;;
;; This file is not part of GNU Emacs.
;;
;;; Commentary:
;;
;;  Description
;;
;;; Code:

;; syntax table
(defconst sdas-mode-syntax-table
  (let ((table (make-syntax-table)))
    ;; coments
    (modify-syntax-entry ?/  ". 124b")
    (modify-syntax-entry ?*  ". 23")
    (modify-syntax-entry ?\n "> b")
    ;; strings
    (modify-syntax-entry ?\" "\"")
    table))

;; keywords highlighting
(eval-and-compile
  (defconst sdas-keywords
    '("using" "var" "variable" "ins" "instruction" "val" "value" "begin" "end" "sub" "if" "Pedro" "Mohamed" "MohamedChar" "Clement")))

(defconst sdas-highlights
  `((,(regexp-opt sdas-keywords 'symbols) . font-lock-keyword-face)))

;; define the mode
;;;###autoload
(define-derived-mode sdas-mode prog-mode "sdas"
  "Major mode for editing sdas files."
  :syntax-table sdas-mode-syntax-table
  (setq font-lock-defaults '(sdas-highlights))
  (setq-local comment-start "// "))

;; automatically run the mode when the file extension is sdas
;;;###autoload
(add-to-list 'auto-mode-alist '("\\.sdas\\'" . sdas-mode))

;; add this line to provide the package
(provide 'sdas-mode)

;;; sdas-mode.el ends here
;;
;; testtesttes
;; testtesttesttes
;; testtt
;; tes
