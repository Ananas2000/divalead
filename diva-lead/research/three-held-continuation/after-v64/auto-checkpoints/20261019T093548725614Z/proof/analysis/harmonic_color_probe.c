#include <stdlib.h>
#include "harmonic_color.h"
/* Isolated probe for input-driven harmonic tracking on synthetic frequencies. */
int color_probe(const double *input,const double *processed,double *output,int frames,int rate,int latency){
 if(!input||!processed||!output||frames<0||rate<1000)return 0;
 HarmonicColor *s=malloc(sizeof(*s));if(!s)return 0;color_prepare(s,rate,latency);
 for(int i=0;i<frames;i++){
  color_track(s,input[2*i],input[2*i+1]);double x[2]={processed[2*i],processed[2*i+1]};
  color_process(s,x);output[2*i]=x[0];output[2*i+1]=x[1];
 }
 free(s);return 1;
}
