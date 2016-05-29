
def RGB(r, g, b):
    return (r << 16) | (g << 8) | b

def DEGREES(n):
    # Convert degrees to Furmans
    return 65536 * n / 360

NEVER                = 0
LESS                 = 1
LEQUAL               = 2
GREATER              = 3
GEQUAL               = 4
EQUAL                = 5
NOTEQUAL             = 6
ALWAYS               = 7

ARGB1555             = 0
L1                   = 1
L4                   = 2
L8                   = 3
RGB332               = 4
ARGB2                = 5
ARGB4                = 6
RGB565               = 7
PALETTED             = 8
TEXT8X8              = 9
TEXTVGA              = 10
BARGRAPH             = 11

NEAREST              = 0
BILINEAR             = 1

BORDER               = 0
REPEAT               = 1

KEEP                 = 1
REPLACE              = 2
INCR                 = 3
DECR                 = 4
INVERT               = 5

DLSWAP_DONE          = 0
DLSWAP_LINE          = 1
DLSWAP_FRAME         = 2

INT_SWAP             = 1
INT_TOUCH            = 2
INT_TAG              = 4
INT_SOUND            = 8
INT_PLAYBACK         = 16
INT_CMDEMPTY         = 32
INT_CMDFLAG          = 64
INT_CONVCOMPLETE     = 128

TOUCHMODE_OFF        = 0
TOUCHMODE_ONESHOT    = 1
TOUCHMODE_FRAME      = 2
TOUCHMODE_CONTINUOUS = 3

ZERO                 = 0
ONE                  = 1
SRC_ALPHA            = 2
DST_ALPHA            = 3
ONE_MINUS_SRC_ALPHA  = 4
ONE_MINUS_DST_ALPHA  = 5

BITMAPS              = 1
POINTS               = 2
LINES                = 3
LINE_STRIP           = 4
EDGE_STRIP_R         = 5
EDGE_STRIP_L         = 6
EDGE_STRIP_A         = 7
EDGE_STRIP_B         = 8
RECTS                = 9

OPT_MONO             = 1
OPT_NODL             = 2
OPT_FLAT             = 256
OPT_CENTERX          = 512
OPT_CENTERY          = 1024
OPT_CENTER           = (OPT_CENTERX | OPT_CENTERY)
OPT_NOBACK           = 4096
OPT_NOTICKS          = 8192
OPT_NOHM             = 16384
OPT_NOPOINTER        = 16384
OPT_NOSECS           = 32768
OPT_NOHANDS          = 49152
OPT_RIGHTX           = 2048
OPT_SIGNED           = 256

LINEAR_SAMPLES       = 0
ULAW_SAMPLES         = 1
ADPCM_SAMPLES        = 2

RAM_CMD              = 1081344
RAM_DL               = 1048576
RAM_PAL              = 1056768
RAM_REG              = 1057792
RAM_TOP              = 1064960
REG_CLOCK            = 1057800
REG_CMD_DL           = 1058028
REG_CMD_READ         = 1058020
REG_CMD_WRITE        = 1058024
REG_CPURESET         = 1057820
REG_CSPREAD          = 1057892
REG_DITHER           = 1057884
REG_DLSWAP           = 1057872
REG_FRAMES           = 1057796
REG_FREQUENCY        = 1057804
REG_GPIO             = 1057936
REG_GPIO_DIR         = 1057932
REG_HCYCLE           = 1057832
REG_HOFFSET          = 1057836
REG_HSIZE            = 1057840
REG_HSYNC0           = 1057844
REG_HSYNC1           = 1057848
REG_ID               = 1057792
REG_INT_EN           = 1057948
REG_INT_FLAGS        = 1057944
REG_INT_MASK         = 1057952
REG_J1_INT           = 1057940
REG_MACRO_0          = 1057992
REG_MACRO_1          = 1057996
REG_OUTBITS          = 1057880
REG_PCLK             = 1057900
REG_PCLK_POL         = 1057896
REG_PLAY             = 1057928
REG_PLAYBACK_FORMAT  = 1057972
REG_PLAYBACK_FREQ    = 1057968
REG_PLAYBACK_LENGTH  = 1057960
REG_PLAYBACK_LOOP    = 1057976
REG_PLAYBACK_PLAY    = 1057980
REG_PLAYBACK_READPTR = 1057964
REG_PLAYBACK_START   = 1057956
REG_PWM_DUTY         = 1057988
REG_PWM_HZ           = 1057984
REG_RENDERMODE       = 1057808
REG_ROTATE           = 1057876
REG_SNAPSHOT         = 1057816
REG_SNAPY            = 1057812
REG_SOUND            = 1057924
REG_SWIZZLE          = 1057888
REG_TAG              = 1057912
REG_TAG_X            = 1057904
REG_TAG_Y            = 1057908
REG_TOUCH_ADC_MODE   = 1058036
REG_TOUCH_CHARGE     = 1058040
REG_TOUCH_DIRECT_XY  = 1058164
REG_TOUCH_DIRECT_Z1Z2 = 1058168
REG_TOUCH_MODE       = 1058032
REG_TOUCH_OVERSAMPLE = 1058048
REG_TOUCH_RAW_XY     = 1058056
REG_TOUCH_RZ         = 1058060
REG_TOUCH_RZTHRESH   = 1058052
REG_TOUCH_SCREEN_XY  = 1058064
REG_TOUCH_SETTLE     = 1058044
REG_TOUCH_TAG        = 1058072
REG_TOUCH_TAG_XY     = 1058068
REG_TOUCH_TRANSFORM_A = 1058076
REG_TOUCH_TRANSFORM_B = 1058080
REG_TOUCH_TRANSFORM_C = 1058084
REG_TOUCH_TRANSFORM_D = 1058088
REG_TOUCH_TRANSFORM_E = 1058092
REG_TOUCH_TRANSFORM_F = 1058096
REG_TRACKER          = 1085440
REG_VCYCLE           = 1057852
REG_VOFFSET          = 1057856
REG_VOL_PB           = 1057916
REG_VOL_SOUND        = 1057920
REG_VSIZE            = 1057860
REG_VSYNC0           = 1057864
REG_VSYNC1           = 1057868

def VERTEX2II(x, y, handle, cell):
    return ((2 << 30) | ((x & 511) << 21) | ((y & 511) << 12) | ((handle & 31) << 7) | ((cell & 127) << 0))
