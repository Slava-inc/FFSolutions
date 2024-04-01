import sea_battle as sb

# SHIP_SYMBOL = '⯀'
# CONTOUR_SYMBOL = '￭'

# # ship nomenclature
# SIZES = [(3, 1), (2, 2), (1, 4)]
# DIM = 6

game = sb.Game()
game.random_boards()

print('*' * 50)
game.ai_board.show(debug=True)
print('*' * 50)
# game.user_board.show()

game.loop()