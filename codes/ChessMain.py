# Esse é o arquivo principal, será responsável por receber os inputs
import ChessEngine, ChessIA
import pygame as p

# DETERMINAÇÃO DO TAMANHO GERAL
LARGURA = ALTURA = 512
DIMENSION = 8

SQ_SIZE = ALTURA // DIMENSION

MAX_FPS = 15

IMAGES = {}


# CARREGAR AS IMAGENS ATRAVES DO NOME DELAS
def loadimages():
    path = 'images/'
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(path + piece + '.png'), (SQ_SIZE, SQ_SIZE))


# RESPONSAVEL POR FAZER O JOGO RODAR
def main():
    gs = ChessEngine.GameState()
    gs.Menu()
    if gs.check == False:
        pass
    elif gs.check == True:
        p.init()

        screen = p.display.set_mode((LARGURA, ALTURA))
        clock = p.time.Clock()
        screen.fill(p.Color('white'))
        p.display.set_caption('Jogo de Xadrez')
        p.display.set_icon(p.image.load('images/bK.png'))
        validMoves = gs.getValidMoves()
        animate = False
        loadimages()
        player1 = gs.playerOne
        player2 = gs.playerTwo

        while gs.running:
            humanTurn = (gs.whiteToMove and player1) or (not gs.whiteToMove and     player2)
            for e in p.event.get():
                if e.type == p.QUIT:
                    gs.running = False
                # CONTROLE DAS PEÇAS COM O MOUSE
                elif e.type == p.MOUSEBUTTONDOWN:
                    if not gs.gameOver and humanTurn: # VERIFICA SE O JOGO TA   RODANDO E SE UM HUMANO VAI JOGAR
                        location = p.mouse.get_pos()
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if gs.sqSelected == (row, col): # CLICOU 2 VEZES NO MESMO   LUGAR
                            gs.sqSelected = () # DESELECIONAR
                            gs.playerClicks = [] # LIMPAR OS CLICKS DO USUARIO
                        else:
                            gs.sqSelected = (row, col)
                            gs.playerClicks.append(gs.sqSelected)

                        if len(gs.playerClicks) == 2: #DEPOIS DO 2º CLICK
                            move = ChessEngine.Moves(gs.playerClicks[0], gs.    playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.MakeMoves(validMoves[i])
                                    gs.moveMade = True
                                    animate = True
                                    gs.sqSelected = ()
                                    gs.playerClicks = []
                            if not gs.moveMade:
                                gs.playerClicks = [gs.sqSelected]
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:  # DESFAZER QUANDO APERTAR Z
                        gs.undoMoves()
                        gs.moveMade = True
                        animate = False
                        gs.gameOver = False
                    if e.key == p.K_r:  # RESETAR O TABULEIRO QUANDO APERTAR R
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        gs.sqSelected = ()
                        gs.playerClicks = []
                        gs.moveMade = False
                        animate = False
                        gs.gameOver = False

                    if e.key == p.K_t:
                        gs.running = False
                        gs.gameOver = True
                        gs.moveMade = False
                        p.quit()
                        return main()
                    if e.key == p.K_ESCAPE:
                        gs.running = False
                        p.quit()


            # IA MOVE FINDER
            if not gs.gameOver and not humanTurn:
                IAMove = ChessIA.findBestMove(gs, validMoves)
                if IAMove is None:
                    IAMove = ChessIA.findRandomMove(validMoves)
                gs.MakeMoves(IAMove)
                gs.moveMade = True
                animate = True

            if gs.moveMade:
                if animate:
                    animateMove(gs.moveLog[-1], screen, gs.board, clock)
                validMoves = gs.getValidMoves()
                gs.moveMade = False
                animate = False

            drawGameState(screen, gs, validMoves, gs.sqSelected, gs.TelaMenu)

            if gs.checkmate:
                gs.gameOver = True
                if gs.whiteToMove:
                    drawText(screen, "Negras ganharam por Xeque-Mate", "Pressione T     para voltar ao menu", "Pressione R para reiniciar", "Pressione  ESC para sair")

                else:
                    drawText(screen, "Brancas ganharam por Xeque-Mate", "Pressione  T para voltar ao menu", "Pressione R para reiniciar",    "Pressione ESC para sair")

            elif gs.stalemate:
                gs.gameOver = True
                if gs.whiteToMove:
                    drawText(screen, "Negras ganharam!!", "Pressione T para voltar  ao menu", "Pressione R para reiniciar", "Pressione ESC para  sair")
                else:
                    drawText(screen, "Brancas ganharam!!", "Pressione T para voltar     ao menu", "Pressione R para reiniciar", "Pressione ESC para     sair")
            clock.tick(MAX_FPS)
            p.display.flip()

# MARCAR A PEÇA SELECIONADA E AS POSIÇÕES POSSIVEIS
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # sqSelected É UMA PEÇA QUE PODE MOVER

            # MARCA A PEÇA SELECIONADA
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(120)
            s.fill(p.Color('yellow' if gs.whiteToMove else 'red'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            # MARCA AS POSIÇÕES POSSÍVEIS
            s.fill(p.Color('yellow' if gs.whiteToMove else 'red'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))



# RESPONSÁVEL PELOS GRÁFICOS DO JOGO
def drawGameState(screen, gs, validMoves, sqSelected, TelaMenu):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, gs.sqSelected)
    drawPieces(screen, gs.board)


# RESPONSÁVEL POR DESENHAR O TABULEIRO, O TOPO ESQUERDO SEMPRE É CLARO
def drawBoard(screen):

    global colors
    colors = [p.Color('burlywood'), p.Color('saddlebrown')]
    for r in range(DIMENSION):

        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))



# RESPONSÁVEL POR DESENHAR AS PEÇAS
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 # FRAMES PARA MOVER 1 QUADRADO
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # APAGAR A PEÇA MOVIDA DA SUA POSIÇÃO DE CHEGADA
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # DESENHAR A PEÇA CAPTURADA, CASO TENHA
        if move.pieceCaptured != '--':
            if move.enPassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # DESENHAR A PEÇA MOVIDA
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text, text2, text3, text4):
    font = p.font.SysFont("Elephant", 25, True, True)
    fonte = p.font.SysFont("Aharoni", 32, True, True)

    textObject = font.render(text, False, p.Color('red'))

    textLocation = p.Rect(0, -50, LARGURA, ALTURA).move(LARGURA/2 - textObject.get_width()/2,
                                                      ALTURA/2 - textObject.get_height()/2)
    textObject2 = fonte.render(text2, False, p.Color('indigo'))

    textLocation2 = p.Rect(10, 30, LARGURA, ALTURA).move(LARGURA/2 - textObject2.get_width()/2,
                                                       ALTURA/2 - textObject2.get_height()/2)
    textObject3 = fonte.render(text3, False, p.Color('indigo'))

    textLocation3 = p.Rect(10, 80, LARGURA, ALTURA).move(LARGURA / 2 - textObject3.get_width() / 2,
                                                         ALTURA / 2 - textObject3.get_height() / 2)
    textObject4 = fonte.render(text4, False, p.Color('indigo'))

    textLocation4 = p.Rect(10, 130, LARGURA, ALTURA).move(LARGURA / 2 - textObject4.get_width() / 2,
                                                         ALTURA / 2 - textObject4.get_height() / 2)

    screen.blit(textObject, textLocation)
    screen.blit(textObject2, textLocation2)
    screen.blit(textObject3, textLocation3)
    screen.blit(textObject4, textLocation4)


if __name__ == '__main__':
    main()