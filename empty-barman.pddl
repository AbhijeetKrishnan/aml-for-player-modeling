(define (domain barman)
  (:requirements :strips :typing)
  (:types hand level beverage dispenser container - object
  	  ingredient cocktail - beverage
          shot shaker - container)
  (:predicates  (ontable ?c - container)
                (holding ?h - hand ?c - container)
		(handempty ?h - hand)
		(empty ?c - container)
                (contains ?c - container ?b - beverage)
		(clean ?c - container)
                (used ?c - container ?b - beverage)
                (dispenses ?d - dispenser ?i - ingredient)
		(shaker-empty-level ?s - shaker ?l - level)
		(shaker-level ?s - shaker ?l - level)
		(next ?l1 ?l2 - level)
		(unshaked ?s - shaker)
		(shaked ?s - shaker)
                (cocktail-part1 ?c - cocktail ?i - ingredient)
                (cocktail-part2 ?c - cocktail ?i - ingredient))
		
  (:action grasp
             :parameters (?h - hand ?c - container)
             :precondition ()
             :effect ()
             )

  (:action leave
             :parameters (?h - hand ?c - container)
             :precondition ()
             :effect ()
             )
  
  (:action fill-shot
           :parameters (?s - shot ?i - ingredient ?h1 ?h2 - hand ?d - dispenser)
           :precondition ()
           :effect ()
           )

  (:action refill-shot
           :parameters (?s - shot ?i - ingredient ?h1 ?h2 - hand ?d - dispenser)
           :precondition ()
           :effect ()
           )

  (:action empty-shot
           :parameters (?h - hand ?p - shot ?b - beverage)
           :precondition ()
           :effect ()
           )

  (:action clean-shot
  	   :parameters (?s - shot ?b - beverage ?h1 ?h2 - hand)
           :precondition ()
           :effect ()
           )

  (:action pour-shot-to-clean-shaker
           :parameters (?s - shot ?i - ingredient ?d - shaker ?h1 - hand ?l ?l1 - level)
           :precondition ()
           :effect ()
           )


  (:action pour-shot-to-used-shaker
           :parameters (?s - shot ?i - ingredient ?d - shaker ?h1 - hand ?l ?l1 - level)
           :precondition ()
           :effect ()
           )

  (:action empty-shaker
           :parameters (?h - hand ?s - shaker ?b - cocktail ?l ?l1 - level)
           :precondition ()
           :effect ()
	   )

  (:action clean-shaker
  	   :parameters (?h1 ?h2 - hand ?s - shaker)
           :precondition ()
           :effect ()
           )
  
  (:action shake
  	   :parameters (?b - cocktail ?d1 ?d2 - ingredient ?s - shaker ?h1 ?h2 - hand)
           :precondition ()			      
           :effect ()
           )

  (:action pour-shaker-to-shot
           :parameters (?b - beverage ?d - shot ?h - hand ?s - shaker ?l ?l1 - level)
           :precondition ()
           :effect ()
           )
 )
