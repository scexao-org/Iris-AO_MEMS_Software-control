/***************************************************************************************************************\
 
    FILE:       irisao.mirrors.h  Copyright © 2009-2015 Iris AO, Inc. All Rights Reserved.
  
    PURPOSE:    Provides mirror level interface communications support.
  
    VERSION:    1.0.2.5
  
\***************************************************************************************************************/


#ifndef IRISAO_MIRRORS_INCLUDED /* VERSION 1.0.2.5 */
#define IRISAO_MIRRORS_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

#define ZERNIKE_PISTON                              0
#define ZERNIKE_TILT_VERTICAL                       1
#define ZERNIKE_TILT_HORIZONTAL                     2
#define ZERNIKE_ASTIGMATISM_OBLIQUE                 3
#define ZERNIKE_DEFOCUS                             4
#define ZERNIKE_ASTIGMATISM_VERTICAL                5
#define ZERNIKE_TREFOIL_VERTICAL                    6
#define ZERNIKE_COMA_VERTICAL                       7
#define ZERNIKE_COMA_HORIZONTAL                     8
#define ZERNIKE_TREFOIL_OBLIQUE                     9
#define ZERNIKE_QUADRAFOIL_OBLIQUE                  10
#define ZERNIKE_ASTIGMATISM_OBLIQUE_SECONDARY       11
#define ZERNIKE_SPHERICAL_PRIMARY                   12
#define ZERNIKE_ASTIGMATISM_VERTICAL_SECONDARY      13
#define ZERNIKE_QUADRAFOIL_VERTICAL                 14
#define ZERNIKE_PENTAFOIL_VERTICAL                  15
#define ZERNIKE_TREFOIL_VERTICAL_SECONDARY          16
#define ZERNIKE_COMA_VERTICAL_SECONDARY             17
#define ZERNIKE_COMA_HORIZONTAL_SECONDARY           18
#define ZERNIKE_TREFOIL_OBLIQUE_SECONDARY           19
#define ZERNIKE_PENTAFOIL_OBLIQUE                   20

typedef const unsigned int Exception;
Exception InsufficientMemory   = 1000; // insufficient memory exception
Exception InvalidArgument      = 1001; // invalid function argument argument exception
Exception InvalidDriverType    = 1002; // invalid configuration driver type exception
Exception InvalidMirrorType    = 1003; // invalid configuration mirror type exception
Exception InvalidFileName      = 1004; // invalid configuration filname exception
Exception MissingTag           = 1005; // missing required configuration tag exception
Exception NullPointer          = 1006; // null pointer argument exception
Exception InvalidConfiguration = 1007; // invalid configuration exception

typedef bool HardwareDisabled;
typedef void* MirrorHandle;
typedef void* MirrorCommands;
typedef const char* SerialNumber;
typedef unsigned int CoefficientNumber;
typedef unsigned int SegmentNumber;

extern MirrorCommands MirrorInitSettings;

extern MirrorCommands MirrorSendSettings;

void MirrorCommand (MirrorHandle mirror, MirrorCommands command);

MirrorHandle MirrorConnect (SerialNumber mirror, SerialNumber driver, HardwareDisabled disabled);

bool MirrorIterate (MirrorHandle mirror, SegmentNumber &segment);

MirrorHandle MirrorRelease (MirrorHandle mirror);

struct MirrorPosition
    {
    float z;         // piston z position value
    float xgrad;     // gradient x position value
    float ygrad;     // gradient y position value
    bool  locked;    // segment locked flag
    bool  reachable; // segment reachable flag
    
    MirrorPosition()
        {
        z = 0.0f;
        xgrad = 0.0f;
        ygrad = 0.0f;
        locked = false;
        reachable = false;
        }

    };

void GetMirrorPosition (MirrorHandle mirror, SegmentNumber segment, MirrorPosition* position);

void SetMirrorPosition (MirrorHandle mirror, SegmentNumber segment, float z, float xgrad, float ygrad);

void SetModalPosition (MirrorHandle mirror, CoefficientNumber number, float value);

#ifdef __cplusplus
}
#endif

#endif // IRISAO_MIRRORS_INCLUDED
