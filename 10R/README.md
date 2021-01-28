# 10R
tlqkf

10R is a checkers-like abstract strategy game.
 
This project is to implement 10R and design AI of it.
Various AI will be designed, and one of it will follow AlphaZero's method.

Rules
 10R is played on a board 7 lines wide and 11 lines long.
 As in the game Go, the pieces are placed on the intersections, which are known as points.
 Each Player in turn moves his piece from the point it occupies, to another point. 
 Some move may capture an enemy piece and a player must move a piece to capture an enemy piece if it is possible.
 일반적으로는 한 차례에 하나의 기물만을 움직이지만,
 상대 기물을 포획하는 경우에는 until he can no longer capture enemy pieces 차례를 넘기지 않고 몇개의 기물이든 몇번이든 움직입니다.
 
 각 플레이어는 Ping이라는 기본적인 기물들만을 가지고 시작하며, 
 상대방 진영쪽 끝에 도달한 Ping은 Pong이라는 더 발빠른 기물로 승급합니다.
 두 기물의 이동 방식은 다음과 같습니다.
 
 Ping:
  walk(move without capturing)
   양 옆으로 1칸 이동 혹은 상대 진영 쪽으로 1칸 전진.
  eat(move with capturing)
   양 옆 혹은 앞/뒤에 상대 말이 있고, 그 바로 너머가 비어있는 경우 상대 말을 잡고 그 바로 너머로 이동.
   
 Pong:
  walk(move without capturing)
   양 옆 혹은 앞 뒤로 얼마든지 이동하되, 다른 기물을 뛰어넘을 수는 없다.
  eat(move with capturing)
   같은 가로줄 혹은 세로줄에 상대 말이 있고 그 너머가 비어있는 경우 상대 말을 잡고 그 너머로 얼마든지 이동하되, 하나의 기물만을 뛰어넘어야 한다.
 
 상대가 자신의 차례에 할 수 있는 행동이 없게 되면 승리합니다.
 만약 10턴 연속으로 핑의 전진이나 기물의 포획이 없다면 비깁니다.
 