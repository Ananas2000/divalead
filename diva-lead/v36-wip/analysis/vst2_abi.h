#ifndef LEAD_FINISH_VST2_ABI_H
#define LEAD_FINISH_VST2_ABI_H
#include <stdint.h>
typedef struct AEffect AEffect;
typedef intptr_t (*AudioMaster)(AEffect*,int32_t,int32_t,intptr_t,void*,float);
typedef intptr_t (*Dispatcher)(AEffect*,int32_t,int32_t,intptr_t,void*,float);
struct AEffect {
    int32_t magic; Dispatcher dispatcher;
    void (*process)(AEffect*,float**,float**,int32_t);
    void (*setParameter)(AEffect*,int32_t,float);
    float (*getParameter)(AEffect*,int32_t);
    int32_t numPrograms,numParams,numInputs,numOutputs,flags;
    intptr_t reserved1,reserved2;
    int32_t initialDelay,realQualities,offQualities; float ioRatio;
    void *object,*user; int32_t uniqueID,version;
    void (*processReplacing)(AEffect*,float**,float**,int32_t);
    void (*processDoubleReplacing)(AEffect*,double**,double**,int32_t);
    char future[56];
};
typedef struct {
    double samplePos,sampleRate,nanoSeconds,ppqPos,tempo,barStartPos,cycleStartPos,cycleEndPos;
    int32_t timeSigNumerator,timeSigDenominator,smpteOffset,smpteFrameRate,samplesToNextClock,flags;
} VstTimeInfo;
#endif
