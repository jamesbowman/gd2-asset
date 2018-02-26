// This file was generated with the command-line:
//    /usr/local/bin/gd2asset -f xxx testdata/felix.png,format=RGB332 testdata/Hobby-of-night.ttf,topchar=0x39 testdata/0.wav Aurek-Besh.ttf

#define FELIX_HANDLE 0
#define FELIX_WIDTH 320
#define FELIX_HEIGHT 200
#define FELIX_CELLS 1
#define HOBBY_OF_NIGHT_HANDLE 1
#define HOBBY_OF_NIGHT_WIDTH 9
#define HOBBY_OF_NIGHT_HEIGHT 13
#define HOBBY_OF_NIGHT_CELLS 26
#define 0 65840UL
#define 0_LENGTH 3272
#define 0_FREQ 8000
#define AUREK_BESH_HANDLE 2
#define AUREK_BESH_WIDTH 21
#define AUREK_BESH_HEIGHT 15
#define AUREK_BESH_CELLS 96
#define ASSETS_END 85100UL
#define LOAD_ASSETS()  (GD.safeload("xxx"), GD.loadptr = ASSETS_END)

static const shape_t FELIX_SHAPE = {0, 320, 200, 0};
static const shape_t HOBBY_OF_NIGHT_SHAPE = {1, 9, 13, 0};
static const shape_t AUREK_BESH_SHAPE = {2, 21, 15, 0};
struct {
  Bitmap felix;
  Bitmap hobby_of_night;
  Bitmap aurek_besh;
} bitmaps = {
 /*            felix */  {{320, 200}, {160, 100},      0x0UL,  4,  0},
 /*   hobby_of_night */  {{  9,  13}, {  4,   6},   0xfa00UL,  2,  1},
 /*       aurek_besh */  {{ 21,  15}, { 10,   7},  0x10df8UL,  2,  2}
};
