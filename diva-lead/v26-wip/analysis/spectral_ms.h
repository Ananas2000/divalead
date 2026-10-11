#ifndef DIVA_LEAD_SPECTRAL_MS_H
#define DIVA_LEAD_SPECTRAL_MS_H
#include <math.h>
#include <stdint.h>
#include <string.h>
#include "pitch_tracker.h"
#include "spectral_ms_settings.h"
#define SMS_MAX 16384
#define SMS_RING 65536
#define SMS_MASK (SMS_RING-1)
#define SMS_PI 3.1415926535897932384626433832795
typedef struct {double r,i;} SmsComplex;
typedef struct {
 int window,fft,hop,latency,base_latency;double rate;
 uint64_t frame;double input[2][SMS_MAX],ola[2][SMS_RING],norm[SMS_RING],window_values[SMS_MAX];
 SmsComplex spectrum[2][SMS_MAX],twiddle[SMS_MAX/2];
} SpectralMS;
static void sms_fft(SmsComplex *a,int n,const SmsComplex *tw,int inverse){
 for(int i=1,j=0;i<n;i++){int bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;if(i<j){SmsComplex t=a[i];a[i]=a[j];a[j]=t;}}
 for(int length=2;length<=n;length<<=1)for(int start=0;start<n;start+=length)for(int j=0;j<length/2;j++){
  SmsComplex w=tw[j*n/length];if(inverse)w.i=-w.i;SmsComplex v=a[start+j+length/2],u=a[start+j];
  SmsComplex t={w.r*v.r-w.i*v.i,w.r*v.i+w.i*v.r};a[start+j]=(SmsComplex){u.r+t.r,u.i+t.i};a[start+j+length/2]=(SmsComplex){u.r-t.r,u.i-t.i};
 }
 if(inverse)for(int i=0;i<n;i++){a[i].r/=n;a[i].i/=n;}
}
static void sms_prepare(SpectralMS *s,double rate,int base_latency){
 memset(s,0,sizeof(*s));s->rate=rate;s->base_latency=base_latency;
 s->hop=(int)llround(rate*(4096./48000)/8);if(s->hop<1)s->hop=1;
 s->window=s->hop*8;if(s->window>SMS_MAX)s->window=SMS_MAX;s->latency=s->window;
 s->fft=1;while(s->fft<s->window)s->fft<<=1;
 for(int i=0;i<s->window;i++)s->window_values[i]=.5-.5*cos(2*SMS_PI*i/s->window);
 for(int i=0;i<s->fft/2;i++)s->twiddle[i]=(SmsComplex){cos(2*SMS_PI*i/s->fft),-sin(2*SMS_PI*i/s->fft)};
}
static double sms_curve(int row,double frequency){
 if(frequency<=SMS_ANCHORS[0]||frequency>=SMS_ANCHORS[5])return 0;
 for(int j=0;j<5;j++)if(frequency<SMS_ANCHORS[j+1]){
  double a=j?SMS_PARAMETERS[row][j-1]:0,b=j<4?SMS_PARAMETERS[row][j]:0;
  double u=log(frequency/SMS_ANCHORS[j])/log(SMS_ANCHORS[j+1]/SMS_ANCHORS[j]);return a+(b-a)*u;
 }
 return 0;
}
static void sms_analyze(SpectralMS *s,const PitchTracker *tracker){
 int n=s->fft,w=s->window;int64_t start=(int64_t)s->frame+1-w,center=start+w/2;
 int64_t source=center-s->base_latency+(int64_t)llround(.05*s->rate);
 double f0=source<0?100:tracker->history[(uint64_t)source&PITCH_MASK];f0=fmax(45,fmin(220,f0));
 for(int c=0;c<2;c++){
  memset(s->spectrum[c],0,sizeof(SmsComplex)*n);
  for(int i=0;i<w;i++){int64_t pos=start+i;s->spectrum[c][i].r=(pos<0?0:s->input[c][(uint64_t)pos%w])*s->window_values[i];}
  sms_fft(s->spectrum[c],n,s->twiddle,0);
 }
 for(int k=0;k<=n/2;k++){
  double f=k*s->rate/n,d=f-f0*floor(f/f0+.5),h=exp(-.5*(d/(SMS_SIGMA*f0))*(d/(SMS_SIGMA*f0))),off=1-h;
  double gm=1+h*sms_curve(0,f)+off*sms_curve(1,f),gs=1+h*sms_curve(2,f)+off*sms_curve(3,f);
  double qi=h*sms_curve(4,f),re=h*sms_curve(5,f),nm=off*sms_curve(6,f);
  SmsComplex m=s->spectrum[0][k],side=s->spectrum[1][k];
  s->spectrum[0][k]=(SmsComplex){gm*m.r+nm*side.r,gm*m.i+nm*side.i};
  s->spectrum[1][k]=(SmsComplex){gs*side.r+re*m.r-qi*m.i,gs*side.i+re*m.i+qi*m.r};
  if(k==0||k==n/2){s->spectrum[0][k].i=0;s->spectrum[1][k].i=0;}
  else for(int c=0;c<2;c++)s->spectrum[c][n-k]=(SmsComplex){s->spectrum[c][k].r,-s->spectrum[c][k].i};
 }
 for(int c=0;c<2;c++)sms_fft(s->spectrum[c],n,s->twiddle,1);
 for(int i=0;i<w;i++){
  int64_t pos=start+i;if(pos<0)continue;uint32_t slot=(uint64_t)pos&SMS_MASK;double win=s->window_values[i];
  s->ola[0][slot]+=s->spectrum[0][i].r*win;s->ola[1][slot]+=s->spectrum[1][i].r*win;s->norm[slot]+=win*win;
 }
}
/* Causal OLA: the extra complete window is explicitly reported to the host.
   Only input-derived frequency history and live processed audio enter here. */
static void sms_push(SpectralMS *s,const PitchTracker *tracker,const double input[2],double output[2]){
 uint32_t slot=s->frame%s->window;s->input[0][slot]=.5*(input[0]+input[1]);s->input[1][slot]=.5*(input[0]-input[1]);
 if(s->frame+1>=(uint64_t)s->window/2&&(s->frame+1-s->window/2)%s->hop==0)sms_analyze(s,tracker);
 output[0]=output[1]=0;
 if(s->frame>=(uint64_t)s->latency){
  uint32_t read=(s->frame-s->latency)&SMS_MASK;double den=s->norm[read];double m=den>1e-15?s->ola[0][read]/den:0,side=den>1e-15?s->ola[1][read]/den:0;
  output[0]=m+side;output[1]=m-side;s->ola[0][read]=s->ola[1][read]=s->norm[read]=0;
 }
 s->frame++;
}
#endif
