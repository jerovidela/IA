(defrule leer-estado
  =>
  (printout t "Ingrese el estado de la enfermedad (incipiente/avanzado/terminal): ")
  (assert (estado (read)))
)

(defrule leer-dosis
  =>
  (printout t "Ingrese el nivel de dosis (baja/alta): ")
  (assert (dosis (read)))
)

(defrule leer-fisico
  =>
  (printout t "Ingrese la condición física (fuerte/debil): ")
  (assert (fisico (read)))
)

(defrule estado-avanzado
		(estado ?e)
		=>
		(if (eq ?e avanzado)
		then
			(assert (curacion si))
		)
)

(defrule estado-incipiente-dosis
		(estado ?e)
		(dosis ?d)
		=>
		(if (eq ?e incipiente)
		then
			(if (eq ?d alta)
			then 
				(assert (curacion no))
			else 
				(assert (curacion si))
			)
		)
)


(defrule estado-terminal-fisico
		(estado ?e)
		(fisico ?f)
		=>
		(if (eq ?e terminal)
		then
			(if (eq ?f fuerte)
			then
				(assert (curacion no))
			else
				(assert (curacion si))
			)
		)
)

(defrule seCura
		(curacion ?c)
		(estado ?)
		(dosis ?)
		(fisico ?)
		=>
		(printout t " La persona se cura: " ?c crlf)
)