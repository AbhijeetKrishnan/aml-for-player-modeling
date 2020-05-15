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
	:precondition (and (at ?o1 ?o2) (is-nongoal ?o2) (is-nongoal ?o3) (clear ?o3))
	:effect (and 
		(not (at ?o1 ?o2))
		(clear ?o2)
		(at ?o1 ?o3)
		(not (clear ?o3))
	)
)

(:action push-to-nongoal
	:parameters (?p - player ?s - stone ?ppos - location ?from - location ?to - location ?dir - direction)
	:precondition (and (move-dir ?o3 ?o4 ?o6) (move-dir ?o4 ?o5 ?o6) (at ?o2 ?o4) (at ?o1 ?o3) (clear ?o5))
	:effect (and 
		(clear ?o3)
		(is-nongoal ?o5)
		(at ?o2 ?o5)
		(at ?o1 ?o4)
		(not (at ?o2 ?o4))
		(not (at ?o1 ?o3))
		(not (clear ?o5))
	)
)

(:action push-to-goal
	:parameters (?p - player ?s - stone ?ppos - location ?from - location ?to - location ?dir - direction)
	:precondition (and (is-nongoal ?o4) (move-dir ?o3 ?o4 ?o6) (move-dir ?o4 ?o5 ?o6) (is-nongoal ?o3) (at ?o2 ?o4) (at ?o1 ?o3) (clear ?o5))
	:effect (and 
		(clear ?o3)
		(at-goal ?o2)
		(at ?o2 ?o5)
		(at ?o1 ?o4)
		(not (at ?o2 ?o4))
		(not (at ?o1 ?o3))
		(not (clear ?o5))
	)
))