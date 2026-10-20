#ifndef DIVA_LEAD_PITCH_TRACKER_H
#define DIVA_LEAD_PITCH_TRACKER_H
#include <math.h>
#include <stdint.h>
#include <string.h>
#define PITCH_HISTORY 65536
#define PITCH_MASK (PITCH_HISTORY-1)
#define PITCH_PI 3.14159265358979323846
typedef struct {double b0,b1,b2,a1,a2,z1[2],z2[2];} PitchBiquad;
typedef struct {
 PitchBiquad highpass,lowpass[2];
 double history[PITCH_HISTORY],previous,last_cross,periods[3],raw,tracked,smooth;
 double rate;uint64_t frame;int has_cross,count,delay;
} PitchTracker;
static double pitch_biquad(PitchBiquad *s,double x,int c){double y=s->b0*x+s->z1[c];s->z1[c]=s->b1*x-s->a1*y+s->z2[c];s->z2[c]=s->b2*x-s->a2*y;return y;}
static void pitch_pass(PitchBiquad *s,double sr,double f,double q,int high){
 double w=2*PITCH_PI*f/sr,c=cos(w),alpha=sin(w)/(2*q),den=1+alpha;
 s->b0=(high?1+c:1-c)/2/den;s->b1=(high?-1:1)*(high?1+c:1-c)/den;s->b2=s->b0;s->a1=-2*c/den;s->a2=(1-alpha)/den;
}
static void pitch_prepare(PitchTracker *s,double rate,int latency,double lookahead_ms){
 memset(s,0,sizeof(*s));s->rate=rate;s->raw=s->tracked=100;s->smooth=exp(-1/(rate*.005));s->delay=latency-(int)llround(lookahead_ms*.001*rate);if(s->delay<1)s->delay=1;if(s->delay>=PITCH_HISTORY)s->delay=PITCH_HISTORY-1;
 for(int i=0;i<PITCH_HISTORY;i++)s->history[i]=100;
 pitch_pass(&s->highpass,rate,35,sqrt(.5),1);pitch_pass(s->lowpass,rate,200,.541196100146197,0);pitch_pass(s->lowpass+1,rate,200,1.3065629648763766,0);
}
/* Only incoming audio determines frequency. Existing FIR latency supplies
   the lookahead; no reference, MIDI schedule, tuning grid or note table. */
static void pitch_track(PitchTracker *s,double left,double right){
 double z=pitch_biquad(&s->highpass,(left+right)*.5,0);z=pitch_biquad(s->lowpass,z,0);z=pitch_biquad(s->lowpass+1,z,0);
 if(s->frame&&s->previous<=0&&z>0){
  double crossing=(double)s->frame-1-s->previous/(z-s->previous);
  if(s->has_cross){double f=s->rate/(crossing-s->last_cross);if(f>45&&f<220){
   if(s->count<3)s->periods[s->count++]=f;else{s->periods[0]=s->periods[1];s->periods[1]=s->periods[2];s->periods[2]=f;}
   double sorted[3];memcpy(sorted,s->periods,sizeof(sorted));for(int i=0;i<s->count;i++)for(int j=i+1;j<s->count;j++)if(sorted[j]<sorted[i]){double t=sorted[i];sorted[i]=sorted[j];sorted[j]=t;}
   s->raw=s->count==2?(sorted[0]+sorted[1])*.5:sorted[s->count/2];
  }}s->last_cross=crossing;s->has_cross=1;
 }
 s->previous=z;s->tracked=(1-s->smooth)*s->raw+s->smooth*s->tracked;s->history[s->frame&PITCH_MASK]=s->tracked;
}
#endif
