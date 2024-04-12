/**
 * @file TI_chess.cpp
 * @authors
 * Jens Boomgaard
 * Sebastiaan van Straten
 * Patrick Vreeburg
 * @brief The C++ version of TI-chess
 * @version 0.1
 * @date 2024-03-30
 * 
 * @copyright Copyright (c) 2024
 * 
 */
#include <stdint.h>
#include <graphx.h>
#include <fileioc.h>
#include <intce.h>
#include <ti/getcsc.h>
#include <ti/ui.h>
#include <sys/timers.h>

#include "gfx/vargfx.h"

#define NULL_VALUE -1

#define DEBUG false

const uint8_t BG_COLOR = 210;

const uint8_t SQUARE_WIDTH = 27;
const uint8_t BOARD_UPPER_LEFT_X = GFX_LCD_WIDTH / 2 - 4 * SQUARE_WIDTH;
const uint8_t BOARD_UPPER_LEFT_Y = GFX_LCD_HEIGHT / 2 - 4 * SQUARE_WIDTH;

const uint8_t PIECE_SIZE = 17;
const uint8_t PIECE_OFFSET = (SQUARE_WIDTH - PIECE_SIZE) / 2;

uint8_t lastMoveDelta = 0;
uint8_t lastMoveTarget = 0;

bool white_to_move = true;

uint64_t whiteBitboard = 0x0;
uint64_t blackBitboard = 0x0;
uint64_t totalBitboard = 0x0;

int16_t selectIndex = 0;
int16_t selectedIndex = 0;

// 30 legal moves is the max for only pawns
const uint8_t MAX_LEGAL_MOVES = 40;
int16_t legalMoves[MAX_LEGAL_MOVES][3];

enum moveType {
  NORMAL = 0,
  EN_PASSANT
};

// Get the pixel length of the strings in askCorrect()
const uint8_t VALID_LENGTH = gfx_GetCharWidth('V') + gfx_GetCharWidth('a') + gfx_GetCharWidth('l') + gfx_GetCharWidth('i') + gfx_GetCharWidth('d') + gfx_GetCharWidth('?');
const uint8_t YES_LENGTH = gfx_GetCharWidth('Y') + gfx_GetCharWidth('e') + gfx_GetCharWidth('s');
const uint8_t NO_LENGTH = gfx_GetCharWidth('N') + gfx_GetCharWidth('o');

const uint8_t WON_WIDTH = gfx_GetCharWidth('W') + gfx_GetCharWidth('h') + gfx_GetCharWidth('i') + gfx_GetCharWidth('t') + gfx_GetCharWidth('e') + gfx_GetCharWidth(' ') + gfx_GetCharWidth('w') + gfx_GetCharWidth('o') + gfx_GetCharWidth('n') + gfx_GetCharWidth('!');

// Function declarations
void setRightColor(const uint8_t i);
inline void fillSquare(const uint8_t i);
inline void placePiece(const bool white, const uint8_t i);
void selectInit();
void makeMove(const int16_t move[3]);
bool askCorrect();
void clearAsk();
void getAllLegalMoves(const bool white);
void init();

inline bool checkOverlap(const uint64_t& board, const uint8_t i);
int16_t movePossible(const uint8_t from, const uint8_t to);

int main() {

  if (!VARGFX_init()) {
    return 1;
  }
  
  int_Disable();

  gfx_Begin();

  os_RunIndicOff();

  // gfx_SetPalette(global_palette, sizeof_global_palette, 0);
  gfx_palette[208] = gfx_RGBTo1555(121, 92, 52);
  gfx_palette[209] = gfx_RGBTo1555(228, 217, 202);
  gfx_palette[210] = gfx_RGBTo1555(87, 87, 87);
  gfx_SetTransparentColor(5);

  init();

  while (true) {

    uint8_t key;

    while (!(key = os_GetCSC())) {};

    if (key == sk_Left && selectIndex % 8 != 7) {
      selectInit();
      gfx_Rectangle_NoClip(
        BOARD_UPPER_LEFT_X + SQUARE_WIDTH * ( 7 - (selectIndex + 1) % 8 ),
        BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * ( 7 - (selectIndex + 1) / 8 ),
        SQUARE_WIDTH,
        SQUARE_WIDTH
      );
      ++selectIndex;
    } else if (key == sk_Right && selectIndex % 8 != 0) {
      selectInit();
      gfx_Rectangle_NoClip(
        BOARD_UPPER_LEFT_X + SQUARE_WIDTH * ( 7 - (selectIndex - 1) % 8 ),
        BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * ( 7 - (selectIndex - 1) / 8 ),
        SQUARE_WIDTH,
        SQUARE_WIDTH
      );
      --selectIndex;
    } else if (key == sk_Down && selectIndex / 8 != 0) {
      selectInit();
      gfx_Rectangle_NoClip(
        BOARD_UPPER_LEFT_X + SQUARE_WIDTH * ( 7 - (selectIndex - 8) % 8 ),
        BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * ( 7 - (selectIndex - 8) / 8 ),
        SQUARE_WIDTH,
        SQUARE_WIDTH
      );
      selectIndex -= 8;
    } else if (key == sk_Up && selectIndex / 8 != 7) {
      selectInit();
      gfx_Rectangle_NoClip(
        BOARD_UPPER_LEFT_X + SQUARE_WIDTH * ( 7 - (selectIndex + 8) % 8 ),
        BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * ( 7 - (selectIndex + 8) / 8 ),
        SQUARE_WIDTH,
        SQUARE_WIDTH
      );
      selectIndex += 8;
    } else if (key == sk_Enter) {
      
      if (DEBUG) {
        gfx_FillRectangle_NoClip(0, 0, GFX_LCD_WIDTH, BOARD_UPPER_LEFT_Y);
        gfx_PrintStringXY(
          ((checkOverlap(whiteBitboard, selectIndex) && white_to_move) || (checkOverlap(blackBitboard, selectIndex) && !white_to_move)) ? "Yes" : "No"
        , 0, 0);
      }

      if (selectedIndex == NULL_VALUE) {

        if ( !((checkOverlap(whiteBitboard, selectIndex) && white_to_move) || (checkOverlap(blackBitboard, selectIndex) && !white_to_move)) ) {
          continue;
        }

        selectedIndex = selectIndex;
        gfx_SetColor(24);
        gfx_FillRectangle_NoClip(
          BOARD_UPPER_LEFT_X + SQUARE_WIDTH * (7 - selectedIndex % 8),
          BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * (7 - selectedIndex / 8),
          SQUARE_WIDTH,
          SQUARE_WIDTH
        );
        placePiece(checkOverlap(whiteBitboard, selectedIndex), selectedIndex);

      } else {

        setRightColor(selectedIndex);
        gfx_FillRectangle_NoClip(
          BOARD_UPPER_LEFT_X + SQUARE_WIDTH * (7 - selectedIndex % 8),
          BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * (7 - selectedIndex / 8),
          SQUARE_WIDTH,
          SQUARE_WIDTH
        );

        int16_t moveType = movePossible(selectedIndex, selectIndex);

        if (moveType == NULL_VALUE) {
          placePiece(checkOverlap(whiteBitboard, selectedIndex), selectedIndex);
          if (selectIndex != selectedIndex) {
            gfx_Rectangle_NoClip(
              BOARD_UPPER_LEFT_X + SQUARE_WIDTH * (7 - selectedIndex % 8),
              BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * (7 - selectedIndex / 8),
              SQUARE_WIDTH,
              SQUARE_WIDTH
            );
          }
        } else {
          bool correct = askCorrect();
          clearAsk();
          if (!correct) {
            setRightColor(selectedIndex);
            fillSquare(selectedIndex);
            placePiece(white_to_move, selectedIndex);
            selectedIndex = NULL_VALUE;
            continue;
          }
          int16_t move[3] = {selectedIndex, selectIndex, moveType};
          makeMove(move);
        }

        selectedIndex = NULL_VALUE;

      }
    } else if (key == sk_Clear) {
      break;
    }
  }

  os_RunIndicOn();

  gfx_End();

  int_Enable();

  return 0;
}

bool checkOverlap(const uint64_t& board, const uint8_t i) {
  return ( (board >> i) & 1 );
}

int16_t movePossible(const uint8_t from, const uint8_t to) {
  for (uint8_t i = 0; i < MAX_LEGAL_MOVES; ++i) {
    int16_t* move = legalMoves[i];
    if (move[0] == from && move[1] == to) {
      return move[2];
    }
  }
  return NULL_VALUE;
}

void setRightColor(const uint8_t i) {
  const uint8_t row = i/8 + 1;
  if ( (row % 2 == 0) ? (i % 2 == 0) : (i % 2 == 1) ) {
    gfx_SetColor(208); // (121, 92, 52) in RGB
    return;
  }
  gfx_SetColor(209); // (228, 217, 202) in RGB
}

void fillSquare(const uint8_t i) {
  gfx_FillRectangle_NoClip(
    BOARD_UPPER_LEFT_X + SQUARE_WIDTH * (7 - i % 8),
    BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * (7 - i / 8),
    SQUARE_WIDTH,
    SQUARE_WIDTH
  );
}

void placePiece(const bool white, const uint8_t i) {
  gfx_TransparentSprite_NoClip(
    (white) ? wp : bp,
    BOARD_UPPER_LEFT_X + PIECE_OFFSET + SQUARE_WIDTH * (7 - i % 8),
    BOARD_UPPER_LEFT_Y + PIECE_OFFSET + SQUARE_WIDTH * (7 - i / 8)
  );
}

void selectInit() {
  if (selectIndex == selectedIndex) {
    gfx_SetColor(24); // Blue
  } else {
    setRightColor(selectIndex);
  }
  gfx_Rectangle_NoClip(
    BOARD_UPPER_LEFT_X + SQUARE_WIDTH * (7 - selectIndex % 8),
    BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * (7 - selectIndex / 8),
    SQUARE_WIDTH,
    SQUARE_WIDTH
  );
  gfx_SetColor(31); // Cyan
}

// ! DEBUG
void printBitboard(const uint64_t& board) {
  gfx_FillRectangle_NoClip(0,0,GFX_LCD_WIDTH,BOARD_UPPER_LEFT_Y);
  gfx_SetTextFGColor(224);
  uint8_t x = 0;
  for (uint8_t i = 0; i < 64; ++i) {
    if (!checkOverlap(board, i)) continue;
    gfx_SetTextXY(x, 0);
    gfx_PrintUInt(i, 2);
    x += 20;
  }
  gfx_SetColor(0xff);
}

void makeMove(const int16_t move[3]) {
  uint64_t& player = (white_to_move) ? whiteBitboard : blackBitboard;
  uint64_t& opponent = (white_to_move) ? blackBitboard : whiteBitboard;

  if (DEBUG) {
    gfx_FillRectangle_NoClip(0,0,GFX_LCD_WIDTH,BOARD_UPPER_LEFT_Y);
    gfx_SetTextFGColor(31);
    gfx_SetTextXY(0,0);
    gfx_PrintInt(move[0], 2);
    gfx_SetTextXY(20,0);
    gfx_PrintInt(move[1], 2);
    gfx_SetTextXY(40,0);
    gfx_PrintInt(move[2], 1);
    sleep(2);
  }

  player += (1ull << move[1]);
  if ( checkOverlap(opponent, move[1]) ) opponent -= (1ull << move[1]);
  player -= (1ull << move[0]);
  
  if (DEBUG) printBitboard(player);

  setRightColor(move[0]);
  fillSquare(move[0]);
  setRightColor(move[1]);
  fillSquare(move[1]);

  placePiece(white_to_move, move[1]);

  if (move[2] == EN_PASSANT) { // En passant
    uint8_t ep_vanish = move[1] + 8 * ( (white_to_move) ? -1 : 1 );
    opponent -= (1ull << ep_vanish);
    setRightColor(ep_vanish);
    fillSquare(ep_vanish);
  }

  lastMoveDelta = (move[1] - move[0] > 0) ? (move[1] - move[0]) : (move[0] - move[1]);
  lastMoveTarget = move[1];

  if (move[1] / 8 == ((white_to_move) ? 7 : 0)) {
    gfx_SetTextFGColor(15);
    gfx_SetTextScale(2, 2);
    gfx_SetColor(0xff);
    gfx_FillRectangle_NoClip(0.5f * GFX_LCD_WIDTH - 1.1f * WON_WIDTH, 0.5f * GFX_LCD_HEIGHT - 0.1f * WON_WIDTH - 8, 2.2f * WON_WIDTH, 0.2f * WON_WIDTH + 16);
    gfx_PrintStringXY( (white_to_move) ? "White won!" : "Black won!", 0.5f * GFX_LCD_WIDTH - WON_WIDTH, 0.5f * GFX_LCD_HEIGHT - 8 );
    sleep(3);
    init();
    return;
  }

  white_to_move = !white_to_move;
  totalBitboard = whiteBitboard | blackBitboard;
  getAllLegalMoves(white_to_move);
  selectInit();
}

bool askCorrect() {
  gfx_SetTextFGColor(31); // White
  gfx_PrintStringXY("Valid?", 0.5 * GFX_LCD_WIDTH - 0.5 * VALID_LENGTH, GFX_LCD_HEIGHT - 10);
  gfx_SetTextFGColor(7); // Green
  gfx_PrintStringXY("Yes", 0.05 * GFX_LCD_WIDTH, GFX_LCD_HEIGHT - 10);
  gfx_SetTextFGColor(224); // Red
  gfx_PrintStringXY("No", 0.95 * GFX_LCD_WIDTH - NO_LENGTH, GFX_LCD_HEIGHT - 10);

  uint8_t key;

  while (!(key = os_GetCSC())) {};

  return (key == sk_Yequ);
}

void clearAsk() {
  gfx_SetColor(BG_COLOR);
  gfx_FillRectangle_NoClip(0, GFX_LCD_HEIGHT - 10, GFX_LCD_WIDTH, 10);
}

void setMove(int16_t from, int16_t to, moveType type, uint8_t& counter) {
  legalMoves[counter][0] = from;
  legalMoves[counter][1] = to;
  legalMoves[counter][2] = type;
  ++counter;
}

void getAllLegalMoves(const bool white) {

  for (uint8_t i = 0; i < MAX_LEGAL_MOVES; ++i) {
    legalMoves[i][0] = NULL_VALUE;
    legalMoves[i][1] = NULL_VALUE;
    legalMoves[i][2] = NULL_VALUE;
  }

  const int8_t MULTIPLIER = -1 + 2 * white;

  uint8_t counter = 0;

  const uint64_t& player = (white_to_move) ? whiteBitboard : blackBitboard;
  const uint64_t& opponent = (white_to_move) ? blackBitboard : whiteBitboard;

  for (uint8_t i = 0; i < 64; ++i) {
    if ( checkOverlap(opponent, i) || !checkOverlap(player, i) ) {
      continue;
    }

    const int16_t i8m = i + 8 * MULTIPLIER;
    const int16_t i16m = i + 16 * MULTIPLIER;

    if (i % 8 > 0) {
      if ( checkOverlap(opponent, i - 1) && lastMoveDelta == 16 && lastMoveTarget == i - 1 ) {
        setMove(i, i8m - 1, EN_PASSANT, counter);
      }
      if ( checkOverlap(opponent, i8m - 1) ) {
        setMove(i, i8m - 1, NORMAL, counter);
      }
    }
    if (i % 8 < 7) {
      if ( checkOverlap(opponent, i + 1) && lastMoveDelta == 16 && lastMoveTarget == i + 1 ) {
        setMove(i, i8m + 1, EN_PASSANT, counter);
      }
      if ( checkOverlap(opponent, i8m + 1) ) {
        setMove(i, i8m + 1, NORMAL, counter);
      }
    }
    if (checkOverlap(totalBitboard, i8m)) {
      continue;
    }
    setMove(i, i8m, NORMAL, counter);
    if ( checkOverlap(totalBitboard, i16m) || i / 8 == ( (white_to_move) ? 6 : 1 ) ) {
      continue;
    }
    setMove(i, i16m, NORMAL, counter);
  }
}

void init() {
  whiteBitboard = 0xff00;
  blackBitboard = 0xff000000000000;
  totalBitboard = whiteBitboard | blackBitboard;
  selectIndex = 7;
  selectedIndex = NULL_VALUE;
  white_to_move = true;
  lastMoveTarget = 0;
  getAllLegalMoves(true);
  
  // Draw the board
  gfx_FillScreen(BG_COLOR);
  for (uint8_t i = 0; i < 64; ++i) {
    setRightColor(i);
    fillSquare(i);

    if (checkOverlap(whiteBitboard, i)) {
      placePiece(true, i);
    } else if (checkOverlap(blackBitboard, i)) {
      placePiece(false, i);
    }
  }
  gfx_SetColor(31); // Cyan
  gfx_Rectangle_NoClip(
    BOARD_UPPER_LEFT_X + SQUARE_WIDTH * (7 - selectIndex % 8),
    BOARD_UPPER_LEFT_Y + SQUARE_WIDTH * (7 - selectIndex / 8),
    SQUARE_WIDTH,
    SQUARE_WIDTH
  );
}