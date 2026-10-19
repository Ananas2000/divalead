#include <stdlib.h>
#include "spectral_ms.h"
int spectral_component_render(const double *processed,const double *dry,double *output,int frames,int sr,int base_latency){
 SpectralMS *s=malloc(sizeof(*s));PitchTracker *t=malloc(sizeof(*t));if(!s||!t){free(s);free(t);return 0;}
 sms_prepare(s,sr,base_latency);pitch_prepare(t,sr,base_latency,50);
 for(int i=0;i<frames;i++){pitch_track(t,dry[2*i],dry[2*i+1]);double x[2]={processed[2*i],processed[2*i+1]},y[2];sms_push(s,t,x,y);output[2*i]=y[0];output[2*i+1]=y[1];t->frame++;}
 free(s);free(t);return 1;
}
