// This file was generated with the command-line:
//    /usr/local/bin/gd3asset -f xxx testdata/felix.png,format=L2 testdata/Hobby-of-night.ttf testdata/0.wav Aurek-Besh.ttf

#define FELIX_HANDLE 0
#define FELIX_WIDTH 320
#define FELIX_HEIGHT 200
#define FELIX_CELLS 1
#define HOBBY_OF_NIGHT_HANDLE 1
#define HOBBY_OF_NIGHT_WIDTH 10
#define HOBBY_OF_NIGHT_HEIGHT 16
#define HOBBY_OF_NIGHT_CELLS 96
#define 0 23832UL
#define 0_LENGTH 3272
#define 0_FREQ 8000
#define AUREK_BESH_HANDLE 2
#define AUREK_BESH_WIDTH 21
#define AUREK_BESH_HEIGHT 15
#define AUREK_BESH_CELLS 96
#define ASSETS_END 43092UL
#define LOAD_ASSETS()  (GD.safeload("xxx"), GD.loadptr = ASSETS_END)

static const shape_t FELIX_SHAPE = {0, 320, 200, 0};
static const shape_t HOBBY_OF_NIGHT_SHAPE = {1, 10, 16, 0};
static const shape_t AUREK_BESH_SHAPE = {2, 21, 15, 0};
struct {
  Bitmap felix;
  Bitmap hobby_of_night;
  Bitmap aurek_besh;
} bitmaps = {
 /*            felix */  {{320, 200}, {160, 100},      0x0UL, 17,  0},
 /*   hobby_of_night */  {{ 10,  16}, {  5,   8},   0x3e80UL,  2,  1},
 /*       aurek_besh */  {{ 21,  15}, { 10,   7},   0x69e0UL,  2,  2}
};
