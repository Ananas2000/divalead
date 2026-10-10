#include <math.h>
#include <stddef.h>
typedef struct { double b0,b1,b2,a1,a2,z1[2],z2[2]; } BQ;
static void co(BQ *q,double f,double Q,double g,double sr,int band){
 double w=2*3.14159265358979323846*f/sr,c=cos(w),s=sin(w),alpha=s/(2*Q),A=pow(10.,g/40.),den=1+alpha/A;
 if(band){den=1+alpha;q->b0=alpha/den;q->b1=0;q->b2=-alpha/den;}
 else{q->b0=(1+alpha*A)/den;q->b1=-2*c/den;q->b2=(1-alpha*A)/den;}
 q->a1=-2*c/den;q->a2=(1-alpha/A)/den;if(band)q->a2=(1-alpha)/den;
}
static double sample(BQ *q,double x,int c){double y=q->b0*x+q->z1[c];q->z1[c]=q->b1*x-q->a1*y+q->z2[c];q->z2[c]=q->b2*x-q->a2*y;return y;}

#define DYNAMIC_BANDS 3
static const double DYNAMIC_PARAMETERS[19]={175.93053201881443,5.3287760886837008,11.887502898039168,-16.866446107952434,3.8377942857786533,107.76323532469188,3.4354430461229102,17.995177464014649,-13.41453425162984,2.061260092606886,544.33096382620147,6.7656718824034403,-4.5516672411153127,-21.422347593006172,2.4441313463409853,10.184022376515459,3.039647216896018,0,-0.019744153565678005};

typedef struct { BQ detector[DYNAMIC_BANDS],eq[DYNAMIC_BANDS];double energy[DYNAMIC_BANDS],g[DYNAMIC_BANDS],total,a,aGain,floor,rate; } DynamicEQ;
static void dynamic_prepare(DynamicEQ *s,double sr){
 memset(s,0,sizeof(*s));s->rate=sr;s->a=exp(-1/(DYNAMIC_PARAMETERS[15]*.001*sr));s->aGain=exp(-1/(DYNAMIC_PARAMETERS[16]*.001*sr));s->floor=1e-15/pow(10.,TUNED_OUTPUT_DB/10.);
 for(int j=0;j<DYNAMIC_BANDS;j++){co(s->detector+j,DYNAMIC_PARAMETERS[j*5],DYNAMIC_PARAMETERS[j*5+1],0,sr,1);co(s->eq+j,DYNAMIC_PARAMETERS[j*5],DYNAMIC_PARAMETERS[j*5+1],0,sr,0);}
}
static void dynamic_process(DynamicEQ *s,double *x){
 double input[2]={x[0],x[1]};s->total=s->a*s->total+(1-s->a)*.5*(input[0]*input[0]+input[1]*input[1]);
 for(int j=0;j<DYNAMIC_BANDS;j++){
  double l=sample(s->detector+j,input[0],0),r=sample(s->detector+j,input[1],1);s->energy[j]=s->a*s->energy[j]+(1-s->a)*.5*(l*l+r*r);
  double relative=10*log10((s->energy[j]+s->floor)/(s->total+s->floor));double mix=fmax(0,fmin(1,(DYNAMIC_PARAMETERS[j*5+3]-relative)/DYNAMIC_PARAMETERS[j*5+4]));
  s->g[j]=s->aGain*s->g[j]+(1-s->aGain)*DYNAMIC_PARAMETERS[j*5+2]*mix;co(s->eq+j,DYNAMIC_PARAMETERS[j*5],DYNAMIC_PARAMETERS[j*5+1],s->g[j],s->rate,0);
  x[0]=sample(s->eq+j,x[0],0);x[1]=sample(s->eq+j,x[1],1);
 }
 x[0]*=pow(10.,(DYNAMIC_PARAMETERS[17]+DYNAMIC_PARAMETERS[18]/2)/20.);x[1]*=pow(10.,(DYNAMIC_PARAMETERS[17]-DYNAMIC_PARAMETERS[18]/2)/20.);
}
