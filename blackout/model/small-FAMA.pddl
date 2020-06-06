(define (domain sokoban-sequential)
(:requirements :typing)
(:predicates
	(clear ?l - location)
	(at ?t - thing ?l - location)
	(at-goal ?s - stone)
	(is-goal ?l - location)
	(is-nongoal ?l - location)
	(move-dir ?from - location ?to - location ?dir - direction)
)

(:action move
	:parameters (?p - player ?from - location ?to - location ?dir - direction)
	:precondition (and (clear ?o3) (at ?o1 ?o2) (is-nongoal ?o2))
	:effect (and 
		(clear ?o2)
		(not (clear ?o3))
		(is-nongoal ?o3)
		(not (at ?o1 ?o2))
		(at ?o1 ?o3)
	)
)

(:action push-to-nongoal
	:parameters (?p - player ?s - stone ?ppos - location ?from - location ?to - location ?dir - direction)
	:precondition (and (clear ?o5) (move-dir ?o3 ?o4 ?o6) (at ?o2 ?o4) (is-nongoal ?o4) (at ?o1 ?o3) (move-dir ?o4 ?o5 ?o6))
	:effect (and 
		(not (clear ?o5))
		(at ?o2 ?o5)
		(clear ?o3)
		(not (at ?o2 ?o4))
		(at ?o1 ?o4)
		(not (at ?o1 ?o3))
	)
)

(:action push-to-goal
	:parameters (?p - player ?s - stone ?ppos - location ?from - location ?to - location ?dir - direction)
	:precondition (and (clear ?o5) (at ?o2 ?o4) (is-nongoal ?o3) (at ?o1 ?o3) (is-goal ?o5))
	:effect (and 
		(not (clear ?o5))
		(at ?o2 ?o5)
		(clear ?o3)
		(move-dir ?o3 ?o4 ?o6)
		(not (at ?o2 ?o4))
		(at ?o1 ?o4)
		(is-nongoal ?o4)
		(not (at ?o1 ?o3))
		(at-goal ?o2)
	)
))