#ifndef _GAME_H
#define _GAME_H

#include <stdbool.h>
#include <SDL.h>

typedef struct {
  int x;
  int y;
} Vector2;

typedef struct {
  Vector2 pos;
} Player;

typedef struct {
  SDL_Window *rootWindow;
  SDL_Renderer *renderer;
  bool isRunning;
  Player *player;
} Game;

bool game_init (Game *game);
void game_loop (Game *game);
void game_exit (Game *Game);

#endif  /* _GAME_H */
