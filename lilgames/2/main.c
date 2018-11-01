#include <stdbool.h>
#include <stdlib.h>
#include <SDL.h>

#include "game.h"

/* Default window size */
#define SCREEN_WIDTH  1024
#define SCREEN_HEIGHT 768

/* Size of each tile in the grid */
#define TILE_SIZE     32

static void draw_grid (Game *game)
{
  int width, height, i, j;
  SDL_GetWindowSize (game->rootWindow, &width, &height);
  SDL_SetRenderDrawColor (game->renderer, 0xff, 0x0, 0x0, SDL_ALPHA_OPAQUE);

  for (i = TILE_SIZE; i < width; i += TILE_SIZE) {
    SDL_RenderDrawLine (game->renderer, 0, i, width, i);

    for (j = 0; j < height; j += TILE_SIZE) {
      SDL_RenderDrawLine (game->renderer, i, 0, i, height);
    }
  }
}

static void draw_player (Game *game)
{
  SDL_Rect rect;

  if (!game->player) return;

  rect.x = game->player->pos.x * TILE_SIZE;
  rect.y = game->player->pos.y * TILE_SIZE;
  rect.w = rect.h = TILE_SIZE;

  SDL_SetRenderDrawColor (game->renderer, 0xff, 0xcc, 0x0, SDL_ALPHA_OPAQUE);
  SDL_RenderFillRect (game->renderer, &rect);
}

void game_loop (Game *game)
{
  draw_grid (game);
  draw_player (game);

  SDL_RenderPresent (game->renderer);
  SDL_Delay (5000);
}

bool game_init (Game *game)
{
  if (SDL_Init (SDL_INIT_VIDEO) < 0) {
    SDL_LogError (SDL_LOG_CATEGORY_APPLICATION,
                  "Couldn't initialize SDL: %s\n",
                  SDL_GetError());
    return false;
  }
  if (SDL_CreateWindowAndRenderer (SCREEN_WIDTH,  /* Width */
                                   SCREEN_HEIGHT, /* Height */
                                   0,             /* Flags */
                                   &game->rootWindow,
                                   &game->renderer) != 0) {
    SDL_LogError (SDL_LOG_CATEGORY_APPLICATION,
                  "Couldn't create SDL window: %s\n",
                  SDL_GetError());
    return false;
  }
  game->isRunning = true;
  return true;
}

void game_quit (Game *game)
{
  SDL_DestroyWindow (game->rootWindow);
  SDL_Quit ();
}

int main (int argc, char **argv)
{
  Game g;
  Player p;
  p.pos.x = 20;
  p.pos.y = 10;
  g.player = &p;

  if (!game_init (&g))
    return EXIT_FAILURE;
  game_loop (&g);
  game_quit (&g);
  /* Aaaand we're out! */
  return EXIT_SUCCESS;
}
