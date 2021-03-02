;; ###@###
;; ### ###
;; . $ $ .

(define (problem levels/level-2-1.lvl)
  (:domain sokoban-sequential)

  (:objects 
    dir-down - direction
    dir-left - direction
    dir-right - direction
    dir-up - direction
    pos-01-01 - location
    pos-02-01 - location
    pos-03-01 - location
    pos-04-01 - location
    pos-05-01 - location
    pos-06-01 - location
    pos-07-01 - location
    pos-01-02 - location
    pos-02-02 - location
    pos-03-02 - location
    pos-04-02 - location
    pos-05-02 - location
    pos-06-02 - location
    pos-07-02 - location
    pos-01-03 - location
    pos-02-03 - location
    pos-03-03 - location
    pos-04-03 - location
    pos-05-03 - location
    pos-06-03 - location
    pos-07-03 - location
    player-01 - player
    stone-01 - stone
    stone-02 - stone
  )
  
  (:init 
    (IS-GOAL pos-01-03)
    (IS-GOAL pos-07-03)
    (IS-NONGOAL pos-01-01)
    (IS-NONGOAL pos-01-02)
    (IS-NONGOAL pos-02-01)
    (IS-NONGOAL pos-02-02)
    (IS-NONGOAL pos-02-03)
    (IS-NONGOAL pos-03-01)
    (IS-NONGOAL pos-03-02)
    (IS-NONGOAL pos-03-03)
    (IS-NONGOAL pos-04-01)
    (IS-NONGOAL pos-04-02)
    (IS-NONGOAL pos-04-03)
    (IS-NONGOAL pos-05-01)
    (IS-NONGOAL pos-05-02)
    (IS-NONGOAL pos-05-03)
    (IS-NONGOAL pos-06-01)
    (IS-NONGOAL pos-06-02)
    (IS-NONGOAL pos-06-03)
    (IS-NONGOAL pos-07-01)
    (IS-NONGOAL pos-07-02)
    (MOVE-DIR pos-01-03 pos-02-03 dir-right)
    (MOVE-DIR pos-02-03 pos-01-03 dir-left)
    (MOVE-DIR pos-02-03 pos-03-03 dir-right)
    (MOVE-DIR pos-03-03 pos-02-03 dir-left)
    (MOVE-DIR pos-03-03 pos-04-03 dir-right)
    (MOVE-DIR pos-04-01 pos-04-02 dir-down)
    (MOVE-DIR pos-04-02 pos-04-01 dir-up)
    (MOVE-DIR pos-04-02 pos-04-03 dir-down)
    (MOVE-DIR pos-04-03 pos-03-03 dir-left)
    (MOVE-DIR pos-04-03 pos-04-02 dir-up)
    (MOVE-DIR pos-04-03 pos-05-03 dir-right)
    (MOVE-DIR pos-05-03 pos-04-03 dir-left)
    (MOVE-DIR pos-05-03 pos-06-03 dir-right)
    (MOVE-DIR pos-06-03 pos-05-03 dir-left)
    (MOVE-DIR pos-06-03 pos-07-03 dir-right)
    (MOVE-DIR pos-07-03 pos-06-03 dir-left)
    (at player-01 pos-04-01)
    (at stone-01 pos-03-03)
    (at stone-02 pos-05-03)
    (clear pos-01-03)
    (clear pos-02-03)
    (clear pos-04-02)
    (clear pos-04-03)
    (clear pos-06-03)
    (clear pos-07-03)
  )

  (:goal (and
    (at-goal stone-01)
    (at-goal stone-02)
  ))
)
