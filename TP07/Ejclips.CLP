(defrule leer-clima
	=>
	(printout t "Seleccione el clima actual (soleado/nublado/lluvioso): ")
	(assert (clima(read)))
)

(defrule leer-humedad
	(clima ?)
	=>
	(printout t "Que nivel de humedad hay? (alta/normal): ")
	(assert (humedad(read)))
)

(defrule leer-viento
	(clima ?)
	=>
	(printout t "Que fuerza tiene el viento? (fuerte/d�bil): ")
	(assert (viento(read)))
)

(defrule clima-nublado
	(clima ?c)
	=>
	(if (eq ?c nublado)
	then
		(assert (jugar si))
	)
)

(defrule clima-soleado-humedad
	(clima ?c)
	(humedad ?h)
	=>
	(if (eq ?c soleado)
	then
		(if (eq ?h alta)
		then
			(assert (jugar no))
		else
			(assert (jugar si))
		)
	)
)

(defrule clima-lluvioso-viento
	(clima ?c)
	(viento ?v)
	=>
	(if (eq ?c lluvioso)
	then
		(if (eq ?v fuerte)
		then
			(assert (jugar no))
		else
			(assert (jugar si))
		)
	)
)

(defrule jugamos
	(jugar ?j)
	(clima ?)
	(humedad ?)
	(viento ?)
	=>
	(printout t ?j " conviene jugar hoy.")
) 