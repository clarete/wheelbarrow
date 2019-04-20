; -*- Mode: lisp; -*-

(define f (quote (1 2 3)))

(define loopfn (lambda (lst)
                 (if (> (len lst) 0)
                       (progn
                         (print (car lst))
                         (loopfn (cdr lst))))))

(loopfn f)
