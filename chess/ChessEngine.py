'''
Storing all the information about the current state of chess game.
Determining valid moves at current state.
It will keep move log.
'''

class GameState():
    def __init__(self):
        """
        Board is an 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = ()  # coordinates for the square where en-passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def makeMove(self, move):
        """
        Takes a Move as a parameter and executes it.
        (this will not work for castling, pawn promotion and en-passant)
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # log the move so we can undo it later
        self.white_to_move = not self.white_to_move  # switch players
        # update king's location if moved
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            # if not is_AI:
            #    promoted_piece = input("Promote to Q, R, B, or N:") #take this to UI later
            #    self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            # else:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # enpassant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"  # capturing the pawn

        # update enpassant_possible variable
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advance
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king-side castle move
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # moves the rook to its new square
                self.board[move.end_row][move.end_col + 1] = '--'  # erase old rook
            else:  # queen-side castle move
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # moves the rook to its new square
                self.board[move.end_row][move.end_col - 2] = '--'  # erase old rook

        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def undoMove(self):
        """
        Undo the last move
        """
        if len(self.move_log) != 0:  # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # swap players
            # update the king's position if needed
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            # undo en passant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # undo castle rights
            self.castle_rights_log.pop()  # get rid of the new castle rights from the move we are undoing
            self.current_castling_rights = self.castle_rights_log[
                -1]  # set the current castle rights to the last one in the list
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move
        """
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False