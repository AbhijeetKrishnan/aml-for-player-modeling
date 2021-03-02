(define (domain barman)
(:requirements :strips :typing)
(:types object hand - object level - object beverage - object dispenser - object container - object ingredient - beverage cocktail - beverage shot - container shaker - container)
(:predicates
	(ontable ?c - container)
	(holding ?h - hand ?c - container)
	(handempty ?h - hand)
	(empty ?c - container)
	(contains ?c - container ?b - beverage)
	(clean ?c - container)
	(used ?c - container ?b - beverage)
	(dispenses ?d - dispenser ?i - ingredient)
	(shaker-empty-level ?s - shaker ?l - level)
	(shaker-level ?s - shaker ?l - level)
	(next ?l1 - level ?l2 - level)
	(unshaked ?s - shaker)
	(shaked ?s - shaker)
	(cocktail-part1 ?c - cocktail ?i - ingredient)
	(cocktail-part2 ?c - cocktail ?i - ingredient)
)

(:action grasp
	:parameters (?h - hand ?c - container)
	:precondition (and (handempty ?o1) (ontable ?o2))
	:effect (and 
		(not (handempty ?o1))
		(holding ?o1 ?o2)
		(not (ontable ?o2))
		0
	)
)

(:action leave
	:parameters (?h - hand ?c - container)
	:precondition (and (holding ?o1 ?o2))
	:effect (and 
		(handempty ?o1)
		(not (holding ?o1 ?o2))
		(ontable ?o2)
		0
	)
)

(:action fill-shot
	:parameters (?s - shot ?i - ingredient ?h1 - hand ?h2 - hand ?d - dispenser)
	:precondition (and (clean ?o1) (empty ?o1))
	:effect (and 
		(handempty ?o4)
		(contains ?o1 ?o2)
		(dispenses ?o5 ?o2)
		(holding ?o3 ?o1)
		(not (empty ?o1))
		(not (clean ?o1))
		(used ?o1 ?o2)
		0
	)
)

(:action refill-shot
	:parameters (?s - shot ?i - ingredient ?h1 - hand ?h2 - hand ?d - dispenser)
	:precondition (and (empty ?o1))
	:effect (and 
		(handempty ?o4)
		(contains ?o1 ?o2)
		(dispenses ?o5 ?o2)
		(holding ?o3 ?o1)
		(not (empty ?o1))
		0
	)
)

(:action empty-shot
	:parameters (?h - hand ?p - shot ?b - beverage)
	:precondition (and (clean ?o2) (handempty ?o1) (holding ?o1 ?o2) (ontable ?o2) (used ?o2 ?o3) (empty ?o2))
	:effect (and 
		(not (handempty ?o1))
		(not (ontable ?o2))
		(not (used ?o2 ?o3))
		(not (empty ?o2))
		(contains ?o2 ?o3)
		0
	)
)

(:action clean-shot
	:parameters (?s - shot ?b - beverage ?h1 - hand ?h2 - hand)
	:precondition (and (used ?o1 ?o2))
	:effect (and 
		(handempty ?o4)
		(holding ?o3 ?o1)
		(empty ?o1)
		(clean ?o1)
		(not (used ?o1 ?o2))
		0
	)
)

(:action pour-shot-to-clean-shaker
	:parameters (?s - shot ?i - ingredient ?d - shaker ?h1 - hand ?l - level ?l1 - level)
	:precondition (and (next ?o5 ?o6) (contains ?o1 ?o2) (holding ?o4 ?o1) (shaker-level ?o3 ?o5) (empty ?o3) (clean ?o3) (used ?o1 ?o2))
	:effect (and 
		(not (contains ?o1 ?o2))
		(unshaked ?o3)
		(empty ?o1)
		(not (shaker-level ?o3 ?o5))
		(shaker-empty-level ?o3 ?o5)
		(shaker-level ?o3 ?o6)
		(not (empty ?o3))
		(contains ?o3 ?o2)
		(not (clean ?o3))
		0
	)
)

(:action pour-shot-to-used-shaker
	:parameters (?s - shot ?i - ingredient ?d - shaker ?h1 - hand ?l - level ?l1 - level)
	:precondition (and (shaker-level ?o3 ?o5) (unshaked ?o3) (contains ?o1 ?o2))
	:effect (and 
		(next ?o5 ?o6)
		(not (contains ?o1 ?o2))
		(empty ?o1)
		(holding ?o4 ?o1)
		(not (shaker-level ?o3 ?o5))
		(shaker-level ?o3 ?o6)
		(contains ?o3 ?o2)
		(used ?o1 ?o2)
		0
	)
)

(:action empty-shaker
	:parameters (?h - hand ?s - shaker ?b - cocktail ?l - level ?l1 - level)
	:precondition (and (shaker-empty-level ?o2 ?o5) (shaker-level ?o2 ?o4) (shaked ?o2) (contains ?o2 ?o3))
	:effect (and 
		(not (shaker-level ?o2 ?o4))
		(holding ?o1 ?o2)
		(next ?o5 ?o4)
		(not (shaked ?o2))
		(empty ?o2)
		(shaker-level ?o2 ?o5)
		(not (contains ?o2 ?o3))
		0
	)
)

(:action clean-shaker
	:parameters (?h1 - hand ?h2 - hand ?s - shaker)
	:precondition (and )
	:effect (and 
		(handempty ?o2)
		(clean ?o3)
		(empty ?o3)
		0
	)
)

(:action shake
	:parameters (?b - cocktail ?d1 - ingredient ?d2 - ingredient ?s - shaker ?h1 - hand ?h2 - hand)
	:precondition (and (unshaked ?o4) (cocktail-part2 ?o1 ?o3) (contains ?o4 ?o3) (contains ?o4 ?o2) (handempty ?o6))
	:effect (and 
		(cocktail-part1 ?o1 ?o2)
		(contains ?o4 ?o1)
		(not (unshaked ?o4))
		(not (contains ?o4 ?o3))
		(holding ?o5 ?o4)
		(not (contains ?o4 ?o2))
		(shaked ?o4)
		0
	)
)

(:action pour-shaker-to-shot
	:parameters (?b - beverage ?d - shot ?h - hand ?s - shaker ?l - level ?l1 - level)
	:precondition (and (shaker-level ?o4 ?o5) (clean ?o2) (empty ?o2))
	:effect (and 
		(not (clean ?o2))
		(holding ?o3 ?o4)
		(not (shaker-level ?o4 ?o5))
		(shaker-level ?o4 ?o6)
		(shaked ?o4)
		(not (empty ?o2))
		(contains ?o2 ?o1)
		(next ?o6 ?o5)
		0
	)
))