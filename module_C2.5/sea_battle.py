import random

SHIP_SYMBOL = '⯀'
CONTOUR_SYMBOL = '￭'

# ship nomenclature
SIZES = [(3, 1), (2, 2), (1, 4)]
DIM = 6

class Dot():
  def __init__(self, x, y):
    self.x = x
    self.y =y
  def __eq__(self, dots):
    lst = [(dot.x, dot.y) for dot in dots]
    return (self.x, self.y) in lst


class Ship():
  def __init__(self, l: int, nose: Dot, vertical: bool):
    self.l = l
    self.nose = nose
    self.vertical = vertical
    self.life = l

  @property
  def dots(self):
    lst = []
    for x, y in  [(self.nose.x + i, self.nose.y) for i in range(self.l)] if self.vertical else [(self.nose.x, self.nose.y + i) for i in range(self.l)] :
      lst.append(Dot(x, y))
    return lst

  def correct(self, board, forbidden):
    for dot in self.dots:
      if board.out(dot) or dot == forbidden:        
        return False
    return True 
    
  # decrease life if shot succeeded & return remaining life else return None
  def life_minus(self, dot):  
    if dot == self.dots:
      self.life -= 1
      return self.life
    return None
    


class Board():
  # statical variable to store countoures of user killed ships
  fob_ai = []
  def __init__(self, hid=True):
    self.field = [['O' for i in range(DIM)] for j in range(DIM)]
    self.hid = hid
    self.ships = []

  def add_ship(self, ship):
    self.ships.append(ship)
    for dot in ship.dots:
      self.field[dot.x][dot.y] = SHIP_SYMBOL

  # ship countoure
  def contour(self, ship):
    ship_dots = ship.dots
    cont = []
    for dot in ship_dots:
      cont.append(Dot(dot.x + (0 if ship.vertical else 1), dot.y + (1 if ship.vertical else 0)))
      cont.append(Dot(dot.x - (0 if ship.vertical else 1), dot.y - (1 if ship.vertical else 0)))

    for i in range(3):
      if ship.vertical:
        cont.append(Dot(ship.nose.x - 1, ship.nose.y - 1 + i))
        cont.append(Dot(ship.nose.x + ship.l, ship.nose.y - 1 + i ))
      else:
        cont.append(Dot(ship.nose.x - 1 + i, ship.nose.y - 1))
        cont.append(Dot(ship.nose.x - 1 + i, ship.nose.y + ship.l))

    dot_out = set([(dot.x, dot.y) if self.out(dot) else None for dot in cont])
    result = list(set([(dot.x, dot.y) for dot in cont]).difference(dot_out))
    return [Dot(dot[0], dot[1]) for dot in result]

  # check dot in board
  def out(self, dot):
    condition = [0 <= dot.x < DIM,
                 0 <= dot.y < DIM]
    return not all(condition)

  # test method to show ship contour
  def show_contour(self, ship):
    field = [['O' for i in range(DIM)] for j in range(DIM)]
    dots = self.contour(ship)
    for dot in dots:
      if self.out(dot):
        continue
      field[dot.x][dot.y] = CONTOUR_SYMBOL
    for dot in ship.dots:
      field[dot.x][dot.y] = SHIP_SYMBOL
    self.show(field)

  # hide AI ships in row 
  def shadow(self, row):
    if self.hid:
      for i in range(DIM):
        row[i] = 'O' if row[i] == SHIP_SYMBOL else row[i]
    return row   
  
  # show board for user (debug=False) & for test (debug=True) 
  def show(self, field=None, debug=False):
    field = self.field if field is None else field
    print('  |', ' | '.join([str(i) for i in range(DIM)]))
    print('-'*26)
    row =''
    for i in range(DIM):
      row = field[i] if debug else self.shadow(field[i].copy()) 
      print(str(i), '|' , ' | '.join(row))
      print('-'*26)

  # fill board with ships
  def allocate(self):

    last = SIZES[len(SIZES) - 1]
    # loop for new allocation
    while True:
      # forbidden dots
      forbidden_dots = []
      self.field = [['O' for i in range(DIM)] for j in range(DIM)]
      self.ships = []
      # each ship type
      for size in SIZES:
        # each ship
        l = size[0]
        all = 0
        for num in range(0, size[1]):
          # create ship
          while True:
            # no free cell in the board
            if len(forbidden_dots) == DIM**2:
              break
            vertical = random.randint(0, 1)
            nose = Dot(random.randint(0, DIM - 1), random.randint(0, DIM - 1))
            ship = Ship(l, nose, vertical)
            if not ship.correct(self, forbidden_dots):
              continue

            all += 1
            self.add_ship(ship)
            forbidden_dots = forbidden_dots + ship.dots + self.contour(ship)
            dots = set([(dot.x, dot.y) for dot in forbidden_dots])
            forbidden_dots = [Dot(dot[0], dot[1]) for dot in dots]

            # print(f'forbidden lenth = {len(forbidden_dots)}')
            # for dot in forbidden_dots:
            #   self.field[dot.x][dot.y] = SHIP_SYMBOL if dot == [(dot.x, dot.y) for dot in ship.dots] else CONTOUR_SYMBOL
            # print('*' * 28)
            break
      # all ships correctly allocated
      if (l == last[0]) and (size[1] == all):
        break


  # do shot
  def shot(self, dot):

    if self.out(dot):
      raise Exception('Выстрел за границами поля!')
    if self.field[dot.x][dot.y] == 'T' or self.field[dot.x][dot.y] == 'X':
      raise Exception('Поле уже было обстреляно')

    if self.field[dot.x][dot.y] == SHIP_SYMBOL:
      print('Попадание!')
      self.field[dot.x][dot.y] = 'X'
      for ship in self.ships:
        life = ship.life_minus(dot) 
        if life == 0:
          if not self.hid:
            Board.fob_ai += self.contour(ship)  
          print(f'Корабль уничтожен!')
          return None
        elif life is None:
          continue
        elif life > 0:
          return None          
    self.field[dot.x][dot.y] = 'T'
    return False

  # check if all ships killed
  def game_over(self):
    life = [ship.life for ship in self.ships]
    return sum(life) == 0

class Player():
  
  def __init__(self, foe_board, my_board):
    self.foe_board = foe_board
    self.my_board = my_board


  def ask(self):
    pass

  def move(self, dot):
    reply = self.foe_board.shot(dot)
    return reply is None

  def input_error(gamer = ''):
    print(f'Ошибка ввода координат {gamer}!')

class AI(Player):
  
  def __init__(self, foe_board, my_board):
    super().__init__(foe_board, my_board)
    self.shots = []
  

  def ask(self, fob_ai=[]):
    while True:
      dot = Dot(random.randint(0, DIM -1), random.randint(0, DIM -1))
      # if shot hasn't been made and not in contoure user killed ships, get it 
      if (not (dot == self.shots)) and (len(fob_ai) == 0 or not(dot == fob_ai)):
        break
    self.shots.append(dot)
    print(f'Выстрел AI')
    return dot



class User(Player):

  def ask(self):
    while True:
      i, j = input(f'Введите координаты выстрела через пробел: ').split()
      # digit symbol checking
      if not all([i.isdigit(), j.isdigit()]):
        self.input_error()
        continue    
      break
    lst = list(map(int, [i, j]))
    return Dot(lst[0], lst[1])



class Game():

  def __init__(self):
    self.user_board = Board(False)
    self.ai_board = Board(True)
    self.user = User(self.ai_board, self.user_board)    
    self.ai = AI(self.user_board, self.ai_board)


  def random_boards(self):
    self.ai_board.allocate()
    self.user_board.allocate()

  def greet(self):
    print('*' * 36)
    print('*' + ' '*34 + '*')
    print('*            SEA BATTLE            *')
    print('* Обозначения:' + ' ' * 21 + '*')
    print('* O - чистое поле'  + ' ' * 18 + '*')
    print('* Т - промах'  + ' ' * 23 + '*')
    print('* X - попадание'  + ' ' * 20 + '*')
    print('* ⯀ - корабль'  + ' ' * 22 + '*')
    print('*' + ' '* 34 + '*')
    print('*' * 36)    
    print('game started!')

  def start(self):
    self.greet()
    self.random_boards()
    self.loop()

  def loop(self):
    
    # game loop
    game_over = False
    while not game_over:
      go = True
      
      # user shot loop
      while go:
        try:
          self.ai_board.show()     
          go = self.user.move(self.user.ask())
        except Exception as e: print(e)
        game_over = self.ai_board.game_over()
        if game_over:
          print(f'Победил Пользователь!')
          break
      if game_over:
        break
      print(' Ход AI:')
      go = True
      
      # AI shot loop
      while go:
        try:
          go = self.ai.move(self.ai.ask(Board.fob_ai))
        except Exception as e: print(e)
        game_over = self.user_board.game_over()
        self.user_board.show()
        if game_over:
          print(f'Победил AI')
          break
        
if __name__ == "__main__":
  game = Game()
  game.start()