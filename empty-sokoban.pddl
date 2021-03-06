(define (domain sokoban-sequential)
  (:requirements :typing)
  (:types thing location direction - object
          player stone - thing)
  (:predicates (clear ?l - location)
	       (at ?t - thing ?l - location)
	       (at-goal ?s - stone)
	       (IS-GOAL ?l - location)
	       (IS-NONGOAL ?l - location)
               (MOVE-DIR ?from ?to - location ?dir - direction))

  (:action move
   :parameters (?o1 - player ?from ?o2 - location ?o3 - direction)
   :precondition ()
   :effect       ()
   )

  (:action push-to-nongoal
   :parameters (?o1 - player ?o2 - stone
                ?o3 ?from ?o4 - location
                ?o5 - direction)
   :precondition ()
   :effect       ()
   )

  (:action push-to-goal
   :parameters (?o1 - player ?o2 - stone
                ?o3 ?from ?o4 - location
                ?o5 - direction)
   :precondition ()
   :effect       ()
   )
)
