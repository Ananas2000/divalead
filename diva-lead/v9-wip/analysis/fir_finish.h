#ifndef DIVA_LEAD_FIR_FINISH_H
#define DIVA_LEAD_FIR_FINISH_H
#include <math.h>
#include <string.h>
#include "fir_kernels.h"
#define FIR_BLOCK 128
#define FIR_FFT 256
#define FIR_MAX_PARTS 256
#define FIR_PI 3.1415926535897932384626433832795
typedef struct {double r,i;} FirComplex;
typedef struct {
    FirComplex h[2][FIR_MAX_PARTS][FIR_FFT],x[2][FIR_MAX_PARTS][FIR_FFT],twiddle[FIR_FFT/2];
    double input[2][FIR_BLOCK],output[2][FIR_BLOCK],overlap[2][FIR_BLOCK];
    int parts,slot,position,latency;
} FirFinish;
static void fir_fft(FirComplex *a,const FirComplex *twiddle,int inverse) {
    for(int i=1,j=0;i<FIR_FFT;i++) {
        int bit=FIR_FFT>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;
        if(i<j){FirComplex t=a[i];a[i]=a[j];a[j]=t;}
    }
    for(int length=2;length<=FIR_FFT;length<<=1)for(int start=0;start<FIR_FFT;start+=length)for(int j=0;j<length/2;j++) {
        FirComplex w=twiddle[j*FIR_FFT/length];if(inverse)w.i=-w.i;
        FirComplex v=a[start+j+length/2],u=a[start+j];
        FirComplex t={w.r*v.r-w.i*v.i,w.r*v.i+w.i*v.r};
        a[start+j]=(FirComplex){u.r+t.r,u.i+t.i};a[start+j+length/2]=(FirComplex){u.r-t.r,u.i-t.i};
    }
    if(inverse)for(int i=0;i<FIR_FFT;i++){a[i].r/=FIR_FFT;a[i].i/=FIR_FFT;}
}
static double fir_coefficient(int channel,int index,int center,double rate) {
    if(rate==48000)return index<FIR_BASE_LENGTH?FIR_KERNELS[channel][index]:0;
    double scale=48000/rate,position=(index-center)*scale+FIR_BASE_LENGTH/2.,value=0;
    int nearest=(int)floor(position);
    /* Resample only the band-limited correction, retaining an exact delayed
       identity above its correction band. No audio sample is stored here. */
    for(int tap=nearest-16;tap<=nearest+16;tap++) {
        if(tap<0||tap>=FIR_BASE_LENGTH)continue;
        double d=position-tap;if(fabs(d)>16)continue;
        double sinc=fabs(d)<1e-12?1:sin(FIR_PI*d)/(FIR_PI*d);
        double window=.5+.5*cos(FIR_PI*d/16);
        double correction=FIR_KERNELS[channel][tap]-(tap==FIR_BASE_LENGTH/2?1.:0.);
        value+=correction*sinc*window;
    }
    return value*scale+(index==center?1.:0.);
}
static void fir_prepare(FirFinish *s,double rate) {
    int center=(int)llround(FIR_BASE_LENGTH*.5*rate/48000),length=center*2;
    s->parts=(length+FIR_BLOCK-1)/FIR_BLOCK;s->latency=center+FIR_BLOCK;
    for(int i=0;i<FIR_FFT/2;i++){s->twiddle[i].r=cos(2*FIR_PI*i/FIR_FFT);s->twiddle[i].i=-sin(2*FIR_PI*i/FIR_FFT);}
    memset(s->h,0,sizeof(s->h));
    for(int c=0;c<2;c++)for(int p=0;p<s->parts;p++) {
        for(int i=0;i<FIR_BLOCK;i++)if(p*FIR_BLOCK+i<length)s->h[c][p][i].r=fir_coefficient(c,p*FIR_BLOCK+i,center,rate);
        fir_fft(s->h[c][p],s->twiddle,0);
    }
}
static void fir_reset(FirFinish *s) {
    memset(s->x,0,sizeof(s->x));memset(s->input,0,sizeof(s->input));
    memset(s->output,0,sizeof(s->output));memset(s->overlap,0,sizeof(s->overlap));s->slot=0;s->position=0;
}
static void fir_push(FirFinish *s,const double input[2],double output[2]) {
    for(int c=0;c<2;c++){output[c]=s->output[c][s->position];s->input[c][s->position]=input[c];}
    if(++s->position<FIR_BLOCK)return;
    s->position=0;
    for(int c=0;c<2;c++) {
        FirComplex *current=s->x[c][s->slot];memset(current,0,sizeof(FirComplex)*FIR_FFT);
        for(int i=0;i<FIR_BLOCK;i++)current[i].r=s->input[c][i];fir_fft(current,s->twiddle,0);
        FirComplex sum[FIR_FFT];memset(sum,0,sizeof(sum));
        for(int p=0;p<s->parts;p++) {
            int previous=(s->slot+s->parts-p)%s->parts;
            for(int k=0;k<FIR_FFT;k++) {
                FirComplex h=s->h[c][p][k],x=s->x[c][previous][k];
                sum[k].r+=h.r*x.r-h.i*x.i;sum[k].i+=h.r*x.i+h.i*x.r;
            }
        }
        fir_fft(sum,s->twiddle,1);
        for(int i=0;i<FIR_BLOCK;i++){s->output[c][i]=sum[i].r+s->overlap[c][i];s->overlap[c][i]=sum[i+FIR_BLOCK].r;}
    }
    s->slot=(s->slot+1)%s->parts;
}
#endif
