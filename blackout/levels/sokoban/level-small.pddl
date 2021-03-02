;; %)[] ;;
;; ()   ;;
;;      ;;
;;      ;;

(define (problem level1-sequential)
  (:domain sokoban-sequential)
  (:objects
    dir-down
    dir-left
    dir-right
    dir-up - direction
    player-01 - player
    pos-01-01
    pos-02-01
    pos-01-02
    pos-02-02
    pos-01-03
    pos-02-03
    pos-01-04
    pos-02-04 - location
    stone-01 - stone
    )
  (:init
    (IS-GOAL pos-01-01)
    (IS-NONGOAL pos-02-01)
    (IS-NONGOAL pos-01-02)
    (IS-NONGOAL pos-02-02)
    (IS-NONGOAL pos-01-03)
    (IS-NONGOAL pos-02-03)
    (IS-NONGOAL pos-01-04)
    (IS-NONGOAL pos-02-04)
    (MOVE-DIR pos-01-01 pos-01-02 dir-down)
    (MOVE-DIR pos-01-02 pos-01-03 dir-down)
    (MOVE-DIR pos-01-03 pos-01-04 dir-down)
    (MOVE-DIR pos-02-02 pos-02-03 dir-down)
    (MOVE-DIR pos-02-03 pos-02-04 dir-down)
    (MOVE-DIR pos-01-02 pos-01-01 dir-up)
    (MOVE-DIR pos-01-03 pos-01-02 dir-up)
    (MOVE-DIR pos-01-04 pos-01-03 dir-up)
    (MOVE-DIR pos-02-03 pos-02-02 dir-up)
    (MOVE-DIR pos-02-04 pos-02-03 dir-up)
    (MOVE-DIR pos-01-02 pos-02-02 dir-right)
    (MOVE-DIR pos-01-03 pos-02-03 dir-right)
    (MOVE-DIR pos-01-04 pos-02-04 dir-right)
    (MOVE-DIR pos-02-02 pos-01-02 dir-left)
    (MOVE-DIR pos-02-03 pos-01-03 dir-left)
    (MOVE-DIR pos-02-04 pos-01-04 dir-left)
    (at player-01 pos-01-01)
    (at stone-01 pos-01-02)
    (clear pos-02-02)
    (clear pos-01-03)
    (clear pos-02-03)
    (clear pos-01-04)
    (clear pos-02-04)
    )
  (:goal (and
           (at-goal stone-01)
           ))
  )


