# Esse arquivo é responsável por armazenar as informações do jogo e determinar os movimentos
# válidos e desfazer movimentos
from tkinter import *
from tkinter import messagebox
import pygame as p





class GameState():
    def __init__(self):
         #TABULEIRO 8X8 CADA ELEMENTO POSSUI 2 CARACTERES
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4) # RASTREAR A POSIÇÃO DO REI BRANCO
        self.blackKingLocation = (0, 4) # RASTREAR A POSIÇÃO DO REI NEGRO
        self.checkmate = False
        self.stalemate = False
        self.running = True
        self.playerOne = [(self.Menu)]
        self.playerTwo = [(self.Menu)]
        self.gameOver = False
        self.moveMade = False
        self.sqSelected = ()
        self.check = [(self.Menu)]
        self.playerClicks = []
        self.enPassantPossible = () # COORDENADAS DO QUADRADO ONDE ENPASSANT É POSSIVEL
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
    def Menu(self):
        self.check = True
        self.gameOver = True
        self.running = False
        self.moveMade = False
        tela = Tk()
        tela.geometry('512x512')
        tela.resizable(False, False)
        tela.configure(bg='saddlebrown')
        tela.title('Jogo de Xadrez')
        image = PhotoImage(file='images/xes.png' )
        image = image.subsample(1, 1)
        icon = PhotoImage(file='images/bK.png')
        tela.iconphoto(False, icon)
        labelimage = Label(image=image)
        labelimage.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        labeldev = Label(tela, text='Developed by: Nicolas Bieberbach Candido (nicolasbieberbach.dev@gmail.com)', anchor=NE,
                         font='Arial 10 bold', bg='black', fg='dimgrey')
        labeldev.place(x=0, y=490)
        def Players():
            self.moveMade = False
            self.playerClicks = []
            self.sqSelected = ()
            self.running = True
            self.gameOver = False
            self.playerOne = True
            self.playerTwo = True
            tela.destroy()

        def PvsC():
            self.moveMade = False
            self.playerClicks = []
            self.sqSelected = ()
            result = messagebox.askquestion('VERIFICAR !!!', 'Deseja jogar com as peças brancas?')
            if result == 'yes':
                self.running = True
                self.gameOver = False
                self.playerOne = True
                self.playerTwo = False
                tela.destroy()
            elif result == 'no':
                self.running = True
                self.gameOver = False
                self.playerOne = False
                self.playerTwo = True
                tela.destroy()

        def CvsC():
            self.running = True
            self.gameOver = False
            self.playerOne = False
            self.playerTwo = False
            tela.destroy()

        def Exit(event):
            result = messagebox.askquestion('VERIFICAR: ', 'Deseja realmente sair?')
            if result == 'yes':
                self.check = False
                self.running = False
                self.gameOver = True
                tela.destroy()
                p.quit()

        pvsp = Button(tela, text='PLAYER VS PLAYER', command=Players, width=18, height=2, bd=4,
                      font=('algerian 14 bold'),
                      bg='burlywood', fg='black', relief=RAISED, overrelief=RIDGE)
        pvsp.place(x=130, y=150)

        pvsc = Button(tela, text='PLAYER VS CPU', command=PvsC, width=18, height=2, bd=4,
                      font=('algerian 14 bold'),
                      bg='burlywood', fg='black', relief=RAISED, overrelief=RIDGE)
        pvsc.place(x=130, y=250)

        cvsc = Button(tela, text='CPU VS CPU', command=CvsC, width=18, height=2, bd=4,
                      font=('algerian 14 bold'),
                      bg='burlywood', fg='black', relief=RAISED, overrelief=RIDGE)
        cvsc.place(x=130, y=350)

        sair = Button(tela, text='SAIR DO JOGO', command=lambda:Exit(event='<Escape>'), width=18, height=1, bd=4, font=('algerian 14 bold'),
                      bg='firebrick', fg='black', relief=RAISED, overrelief=RIDGE)
        sair.place(x=130, y=450)
        
        tela.bind('<Escape>', Exit)
        tela.mainloop()



    def MakeMoves(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove # TROCA DE PLAYERS
        # ATUALIZAR A POSIÇÃO DO REI, CASO MOVIDO
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #PROMOÇÃO DE PEÕES
        if move.pawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'


        # ENPASSANT
        if move.enPassantMove:
            self.board[move.startRow][move.endCol] = '--' # CAPTURA O PEÃO


        # ATUALIZAR A VARIAVEL enPassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # SOMENTE NO 2º QUADRADO QUE O PEÃO AVANÇAR
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)

        else:

            self.enPassantPossible = ()

        if move.CastleMoves:
            if move.endCol - move.startCol == 2: # CASTLING DO LADO DO REI
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #MOVE A TORRE
                self.board[move.endRow][move.endCol+1] = '--'
            else: # CASTLING DO LADO DA RAINHA
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #MOVE A TORRE
                self.board[move.endRow][move.endCol-2] = '--'

        self.enPassantPossibleLog.append(self.enPassantPossible)
        # ATUALIZAR O CASTLING RIGHTS - SEMPRE QUE O REI OU A TORRE SE MEXEREM
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                     self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))



# DESFAZER OS MOVIMENTOS
    def undoMoves(self):
        if len(self.moveLog) != 0: # CONFIRMAR SE TEM UM MOVIMENTO PARA DESFAZER
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # DESFAZER O ENPASSANT
            if move.enPassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured


            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]


            self.castleRightsLog.pop()
            CastleRights = self.castleRightsLog[-1]
            self.currentCastlingRight.wks = CastleRights.wks
            self.currentCastlingRight.bks = CastleRights.bks
            self.currentCastlingRight.wqs = CastleRights.wqs
            self.currentCastlingRight.bqs = CastleRights.bqs

            if move.CastleMoves:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved =='bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                if move.startCol == 7:
                    self.currentCastlingRight.bks = False

        # CASO A TORRE SEJA CAPTURADA
        if move.pieceCaptured == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
             if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

# TODOS OS MOVIMENTOS CONSIDERANDO XEQUE
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.MakeMoves(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMoves()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True

        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

#DETERMINAR SE O JOGADOR ATUAL ESTÁ EM XEQUE
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

#DETERMINAR SE O INIMIGO PODE ATACAR A POSIÇÃO R, C
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #POSIÇÃO EM ATAQUE/AMEAÇA
                return True
        return False



# TODOS OS MOVIMENTOS MENOS XEQUE
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #NUMERO DE LINHAS
            for c in range(len(self.board[r])): #NUMERO DE COLUNAS NA LINHA RECEBIDA
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # CHAMA A FUNÇÃO DE MOVIMENTO APROPRIADA PARA O TIPO DE PEÇA

        return moves

# MOVIMENTOS DOS PEÕES
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # MOVIMENTO DOS PEÕES BRANCOS

            if self.board[r-1][c] == '--':  #PEÃO AVANÇA 1 CASA

                moves.append(Moves((r, c), (r - 1, c), self.board))

                if r == 6 and self.board[r-2][c] == '--': # PEÃO AVANÇA 2 CASAS

                    moves.append(Moves((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:   #CAPTURAS PARA A ESQUERDA

                if self.board[r-1][c-1][0] == 'b': #PEÇA INIMIGA PARA CAPTURAR

                    moves.append(Moves((r, c), (r - 1, c - 1), self.board))

                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Moves((r, c), (r - 1, c - 1), self.board, enPassantMove=True))

            if c + 1 <= 7:   #CAPTURAS PARA A DIREITA

                if self.board[r-1][c+1][0] == 'b': #PEÇA INIMIGA PARA CAPTURAR

                    moves.append(Moves((r, c), (r - 1, c + 1), self.board))

                elif (r - 1, c + 1) == self.enPassantPossible:

                    moves.append(Moves((r, c), (r - 1, c + 1), self.board, enPassantMove=True))
        else:
            # MOVIMENTOS DOS PEÕES PRETOS
            if self.board[r + 1][c] == '--':  # PEÃO AVANÇA UMA CASA
                moves.append(Moves((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':  # PEÃO AVANÇA 2 CASAS
                    moves.append(Moves((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # CAPTURAS PARA A ESQUERDA

                if self.board[r + 1][c - 1][0] == 'w':  # PEÇA INIMIGA PARA CAPTURAR

                    moves.append(Moves((r, c), (r + 1, c - 1), self.board))

                elif (r + 1, c - 1) == self.enPassantPossible:

                    moves.append(Moves((r, c), (r + 1, c - 1), self.board, enPassantMove=True))
            if c + 1 <= 7:  # CAPTURAS PARA A DIREITA

                if self.board[r + 1][c + 1][0] == 'w':  # PEÇA INIMIGA PARA CAPTURAR

                    moves.append(Moves((r, c), (r + 1, c + 1), self.board))

                elif (r + 1, c + 1) == self.enPassantPossible:

                    moves.append(Moves((r, c), (r + 1, c + 1), self.board, enPassantMove=True))

# MOVIMENTOS DAS TORRES
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # CIMA, BAIXO, ESQUERDA DIREITA
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:

            for i in range(1, 8):  # MÁXIMO DE 7 CASAS

                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:  # CONDIÇÃO PARA VERIFICAR O TABULEIRO

                    endPiece = self.board[endRow][endCol]

                    if endPiece == '--':  # ESPAÇO VAZIO (VÁLIDO)

                        moves.append(Moves((r, c), (endRow, endCol), self.board))

                    elif endPiece[0] == enemyColor:  # PEÇA INIMIGA (VÁLIDO)

                        moves.append(Moves((r, c), (endRow, endCol), self.board))
                        break

                    else:  # PEÇA ALIADA (INVÁLIDO)

                        break
                else:  # FORA DO TABULEIRO (INVÁLIDO)

                    break
#MOVIMENTOS DOS CAVALOS
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for m in knightMoves:

            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:

                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor:  # ESPAÇO VAZIO OU PEÇA INIMIGA

                    moves.append(Moves((r, c), (endRow, endCol), self.board))
#MOVIMENTO DOS BISPOS
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 DIAGONAIS
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:

            for i in range(1, 8):  # MÁXIMO DE 7 CASAS

                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:

                    endPiece = self.board[endRow][endCol]

                    if endPiece == '--':  # ESPAÇO VAZIO (VÁLIDO)

                        moves.append(Moves((r, c), (endRow, endCol), self.board))

                    elif endPiece[0] == enemyColor:  # PEÇA INIMIGA (VÁLIDO)

                        moves.append(Moves((r, c), (endRow, endCol), self.board))
                        break

                    else:  # PEÇA ALIADA (INVÁLIDO)

                        break

                else:  # FORA DO TABULEIRO (INVÁLIDO)

                    break
#MOVIMENTOS DAS RAINHAS = TORRE + BISPO
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for i in range(8):

            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:

                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor:  # SE FOR UM ESPAÇO VAZIO OU PEÇA INIMIGA

                    moves.append(Moves((r, c), (endRow, endCol), self.board))


    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Moves((r, c), (r, c + 2), self.board, CastleMoves=True))


    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Moves((r, c), (r, c - 2), self.board, CastleMoves=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
# DEFINIR OS MOVIMENTOS E AS CAPTURAS DE PEÇAS
class Moves():
        # maps keys to value
        # key : value

        ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4,
                      '5': 3, '6': 2, '7': 1, '8': 0}
        rowsToRanks = {v: k for k, v in ranksToRows.items()}
        filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                       'e': 4, 'f': 5, 'g': 6, 'h': 7}
        colsToFiles = {v: k for k, v in filesToCols.items()}

        def __init__(self, startSq, endSq, board, enPassantMove=False, CastleMoves=False):
            self.startRow = startSq[0]
            self.startCol = startSq[1]
            self.endRow = endSq[0]
            self.endCol = endSq[1]
            self.pieceMoved = board[self.startRow][self.startCol]
            self.pieceCaptured = board[self.endRow][self.endCol]
            self.pawnPromotion = self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7)
            self.enPassantMove = enPassantMove
            if self.enPassantMove:
                self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'
            self.CastleMoves = CastleMoves
            self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        def __eq__(self, other):
            if isinstance(other, Moves):
                return self.moveID == other.moveID
            return False



        def GetChessNotation(self):
            return self.GetRankFile(self.startRow, self.startCol) + self.GetRankFile(self.endRow, self.endCol)


        def GetRankFile(self, r, c):

            return self.colsToFiles[c] + self.rowsToRanks[r]