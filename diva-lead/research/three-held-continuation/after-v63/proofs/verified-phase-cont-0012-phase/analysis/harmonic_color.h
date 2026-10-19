#ifndef DIVA_LEAD_HARMONIC_COLOR_H
#define DIVA_LEAD_HARMONIC_COLOR_H
#include "pitch_tracker.h"
#define COLOR_COUNT 10
static const double COLOR_ORDERS[COLOR_COUNT]={3,4,6,11,13,14,16,20,23,24};
static const double COLOR_GAINS[COLOR_COUNT]={-0.47869667537546351,1.0307270692621191,-4.3692475656247503,-1.7748298323937111,4.8993992026017414,-0.88431765608698398,-1.0867929294819745,0.90827850076011407,-4.5859713371085968,-1.2995417713169486};
static const double COLOR_Q_FACTORS[COLOR_COUNT]={3,3,3,3,4,3,3,3,3,3};
#define COLOR_LOOKAHEAD_MS 50
typedef struct {PitchTracker tracker;PitchBiquad eq[COLOR_COUNT];} HarmonicColor;
static void color_peak(PitchBiquad *s,double sr,double frequency,double q,double gain){
 double w=2*PITCH_PI*fmin(frequency,sr*.45)/sr,c=cos(w),alpha=sin(w)/(2*q),A=pow(10,gain/40),den=1+alpha/A;
 s->b0=(1+alpha*A)/den;s->b1=-2*c/den;s->b2=(1-alpha*A)/den;s->a1=-2*c/den;s->a2=(1-alpha/A)/den;
}
static void color_prepare(HarmonicColor *s,double rate,int latency){memset(s,0,sizeof(*s));pitch_prepare(&s->tracker,rate,latency,COLOR_LOOKAHEAD_MS);}
static void color_track(HarmonicColor *s,double left,double right){pitch_track(&s->tracker,left,right);}
static void color_process(HarmonicColor *s,double x[2]){
 PitchTracker *t=&s->tracker;
 if((t->frame&15)==0){double f=fmax(45,fmin(220,t->history[(t->frame-t->delay)&PITCH_MASK]));for(int j=0;j<COLOR_COUNT;j++)color_peak(s->eq+j,t->rate,f*COLOR_ORDERS[j],COLOR_ORDERS[j]*COLOR_Q_FACTORS[j],COLOR_GAINS[j]);}
 for(int c=0;c<2;c++)for(int j=0;j<COLOR_COUNT;j++)x[c]=pitch_biquad(s->eq+j,x[c],c);t->frame++;
}
#endif
