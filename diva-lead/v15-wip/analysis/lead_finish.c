#include "vst2_abi.h"
#include "tuned_settings.h"
#include "fir_finish.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

#define RING_SIZE 65536
#define RING_MASK (RING_SIZE-1)
#define EFFECT_ID 0x444c4646
#define PI 3.1415926535897932384626433832795
typedef struct {double b[3],a[2],state[2][2];} Biquad;
typedef struct {uint32_t version,id;float amount,level;} Chunk;
typedef struct {
    AEffect effect;AudioMaster master;double rate;
    Biquad eq[5],hp,side_eq[TUNED_SIDE_COUNT],post_side_eq[POST_SIDE_COUNT];
    FirFinish fir;float dry_delay[2][RING_SIZE];
    Biquad differential[2][TUNED_DIFF_COUNT];
    double ap_a[2][3],ap_x[2][3],ap_y[2][3],ring[2][RING_SIZE];
    double energy_fast,energy_slow,fast_coefficient,slow_coefficient;
    double match_reference_energy,match_output_energy,match_coefficient,match_floor;
    uint32_t cursor;uint64_t counter;double last_host;
    float amount,level;int bypass,was_playing;Chunk chunk;
} Finish;
static void reset(Finish *s) {
    for(int i=0;i<5;i++)memset(s->eq[i].state,0,sizeof(s->eq[i].state));
    memset(s->hp.state,0,sizeof(s->hp.state));
    for(int i=0;i<TUNED_SIDE_COUNT;i++)memset(s->side_eq[i].state,0,sizeof(s->side_eq[i].state));
    for(int c=0;c<2;c++)for(int i=0;i<TUNED_DIFF_COUNT;i++)memset(s->differential[c][i].state,0,sizeof(s->differential[c][i].state));
    memset(s->ap_x,0,sizeof(s->ap_x));memset(s->ap_y,0,sizeof(s->ap_y));
    memset(s->ring,0,sizeof(s->ring));s->cursor=0;s->counter=0;s->last_host=-1;s->was_playing=0;
    s->energy_fast=0;s->energy_slow=0;s->match_reference_energy=0;s->match_output_energy=0;
    for(int i=0;i<POST_SIDE_COUNT;i++)memset(s->post_side_eq[i].state,0,sizeof(s->post_side_eq[i].state));
    fir_reset(&s->fir);memset(s->dry_delay,0,sizeof(s->dry_delay));
}
static void coefficients(Finish *s) {
    fir_prepare(&s->fir,s->rate);s->effect.initialDelay=s->fir.latency;
    s->match_coefficient=exp(-1/(MATCH_ENERGY_MS*.001*s->rate));
    s->match_floor=1e-12/pow(10,TUNED_OUTPUT_DB/10);
    s->fast_coefficient=exp(-1/(TUNED_FAST_MS*.001*s->rate));
    s->slow_coefficient=exp(-1/(TUNED_SLOW_MS*.001*s->rate));
    const double frequencies[5]={120,420,1200,3400,8000};
    for(int i=0;i<5;i++) {
        double frequency=fmin(frequencies[i],s->rate*.45);
        double amplitude=pow(10,TUNED_EQ[i]/40),w=2*PI*frequency/s->rate;
        double alpha=sin(w)/(2*.7),c=cos(w),a0=1+alpha/amplitude;
        s->eq[i].b[0]=(1+alpha*amplitude)/a0;s->eq[i].b[1]=-2*c/a0;
        s->eq[i].b[2]=(1-alpha*amplitude)/a0;
        s->eq[i].a[0]=-2*c/a0;s->eq[i].a[1]=(1-alpha/amplitude)/a0;
    }
    for(int i=0;i<TUNED_SIDE_COUNT;i++) {
        double frequency=fmin(TUNED_SIDE_FREQ[i],s->rate*.45);
        double amplitude=pow(10,TUNED_SIDE_GAIN[i]/40),w=2*PI*frequency/s->rate;
        double alpha=sin(w)/(2*TUNED_SIDE_Q),c=cos(w),a0=1+alpha/amplitude;
        Biquad *d=&s->side_eq[i];
        d->b[0]=(1+alpha*amplitude)/a0;d->b[1]=-2*c/a0;d->b[2]=(1-alpha*amplitude)/a0;
        d->a[0]=-2*c/a0;d->a[1]=(1-alpha/amplitude)/a0;
    }
    for(int i=0;i<POST_SIDE_COUNT;i++) {
        double frequency=fmin(POST_SIDE_FREQ[i],s->rate*.45);
        double amplitude=pow(10,POST_SIDE_GAIN[i]/40),w=2*PI*frequency/s->rate;
        double alpha=sin(w)/(2*POST_SIDE_Q),c=cos(w),a0=1+alpha/amplitude;
        Biquad *d=&s->post_side_eq[i];
        d->b[0]=(1+alpha*amplitude)/a0;d->b[1]=-2*c/a0;d->b[2]=(1-alpha*amplitude)/a0;
        d->a[0]=-2*c/a0;d->a[1]=(1-alpha/amplitude)/a0;
    }
    for(int channel=0;channel<2;channel++) {
        for(int i=0;i<TUNED_DIFF_COUNT;i++) {
            double frequency=fmin(TUNED_DIFF_FREQ[i],s->rate*.45);
            double db=TUNED_DIFF_GAIN[i]*(channel?-1:1);
            double amplitude=pow(10,db/40),w=2*PI*frequency/s->rate;
            double alpha=sin(w)/(2*TUNED_DIFF_Q),c=cos(w),a0=1+alpha/amplitude;
            Biquad *d=&s->differential[channel][i];
            d->b[0]=(1+alpha*amplitude)/a0;d->b[1]=-2*c/a0;d->b[2]=(1-alpha*amplitude)/a0;
            d->a[0]=-2*c/a0;d->a[1]=(1-alpha/amplitude)/a0;
        }
        for(int i=0;i<3;i++) {
            double tangent=tan(PI*fmin(TUNED_AP[channel][i],s->rate*.45)/s->rate);
            s->ap_a[channel][i]=(tangent-1)/(tangent+1);
        }
    }
    double w=2*PI*fmin(TUNED_HP,s->rate*.45)/s->rate;
    double c=cos(w),alpha=sin(w)/(2*.7071067811865476),a0=1+alpha;
    s->hp.b[0]=(1+c)/2/a0;s->hp.b[1]=-(1+c)/a0;s->hp.b[2]=(1+c)/2/a0;
    s->hp.a[0]=-2*c/a0;s->hp.a[1]=(1-alpha)/a0;
}
static double biquad(Biquad *s,int channel,double input) {
    double result=s->b[0]*input+s->state[channel][0];
    s->state[channel][0]=s->b[1]*input-s->a[0]*result+s->state[channel][1];
    s->state[channel][1]=s->b[2]*input-s->a[1]*result;
    if(fabs(s->state[channel][0])<1e-25)s->state[channel][0]=0;
    if(fabs(s->state[channel][1])<1e-25)s->state[channel][1]=0;
    return result;
}
static void process(AEffect *effect,float **inputs,float **outputs,int32_t frames) {
    Finish *s=effect->object;
    VstTimeInfo *time=(void*)s->master(effect,7,0,0,NULL,0);
    if(time&&isfinite(time->samplePos)&&time->samplePos>=0) {
        int playing=(time->flags&2)!=0;
        if((playing&&!s->was_playing)||(s->last_host>=0&&time->samplePos+.5<s->last_host))reset(s);
        s->last_host=time->samplePos;s->was_playing=playing;
    }
    double gain=pow(10,(-12+24*s->level)/20);
    double pan[2]={pow(10,TUNED_PAN/40),pow(10,-TUNED_PAN/40)};
    double side_balance=pow(10,TUNED_SIDE_BALANCE/40);
    double post_pan[2]={pow(10,TUNED_POST_PAN/40),pow(10,-TUNED_POST_PAN/40)};
    for(int32_t i=0;i<frames;i++,s->counter++,s->cursor=(s->cursor+1)&RING_MASK) {
        double seconds=(double)s->counter/s->rate;
        double phase=2*PI*(seconds*TUNED_RATE+TUNED_PHASE);
        double finished_channels[2];
        for(int channel=0;channel<2;channel++) {
            double input=inputs[channel][i];
            double shaped=input;
            if(TUNED_DRIVE>1e-7) {
                double compensation=channel?TUNED_DRIVE_RIGHT:1;
                shaped=tanh(TUNED_DRIVE*input*compensation)/TUNED_DRIVE/compensation;
            }
            double z=shaped;
            for(int band=0;band<TUNED_DIFF_COUNT;band++)z=biquad(&s->differential[channel][band],channel,z);
            for(int stage=0;stage<3;stage++) {
                double a=s->ap_a[channel][stage];
                double previous=z;z=a*previous+s->ap_x[channel][stage]-a*s->ap_y[channel][stage];
                s->ap_x[channel][stage]=previous;s->ap_y[channel][stage]=z;
            }
            for(int band=0;band<5;band++)z=biquad(&s->eq[band],channel,z);
            double high=biquad(&s->hp,channel,z);
            s->ring[channel][s->cursor]=high;
            double delayed=0;
            for(int tap=0;tap<3;tap++) {
                double modulation=sin(phase+tap*2*PI/3+(channel?PI/2:0));
                double samples=(TUNED_DELAY+TUNED_DEPTH*modulation)*s->rate/1000;
                samples=fmax(1,fmin(samples,RING_SIZE-2));
                uint32_t integer=(uint32_t)floor(samples);double fraction=samples-integer;
                delayed+=((1-fraction)*s->ring[channel][(s->cursor-integer)&RING_MASK]+fraction*s->ring[channel][(s->cursor-integer-1)&RING_MASK])/3;
            }
            finished_channels[channel]=(z+TUNED_WET*(delayed-high))*pan[channel];
        }
        double left=finished_channels[0]/side_balance,right=finished_channels[1]*side_balance;
        double side=(left-right)*.5,corrected_side=side;
        for(int band=0;band<TUNED_SIDE_COUNT;band++)corrected_side=biquad(&s->side_eq[band],0,corrected_side);
        double delta=corrected_side-side;
        finished_channels[0]=(left+delta)*side_balance;
        finished_channels[1]=(right-delta)/side_balance;
        finished_channels[0]*=post_pan[0];
        finished_channels[1]*=post_pan[1];
        double energy=(finished_channels[0]*finished_channels[0]+finished_channels[1]*finished_channels[1])*.5;
        s->energy_fast=(1-s->fast_coefficient)*energy+s->fast_coefficient*s->energy_fast;
        s->energy_slow=(1-s->slow_coefficient)*energy+s->slow_coefficient*s->energy_slow;
        double envelope_delta=fmax(-.45,fmin(.45,.5*log((s->energy_fast+1e-12)/(s->energy_slow+1e-12))));
        double transient_gain=exp((envelope_delta>=0?TUNED_ATTACK_AMOUNT:TUNED_RELEASE_AMOUNT)*envelope_delta);
        finished_channels[0]*=transient_gain;
        finished_channels[1]*=transient_gain;
        double corrected[4];fir_push(&s->fir,finished_channels,corrected);
        double reference_energy=(corrected[2]*corrected[2]+corrected[3]*corrected[3])*.5;
        double output_energy=(corrected[0]*corrected[0]+corrected[1]*corrected[1])*.5;
        s->match_reference_energy=(1-s->match_coefficient)*reference_energy+s->match_coefficient*s->match_reference_energy;
        s->match_output_energy=(1-s->match_coefficient)*output_energy+s->match_coefficient*s->match_output_energy;
        double matching_log_gain=.5*MATCH_ENERGY_STRENGTH*log((s->match_reference_energy+s->match_floor)/(s->match_output_energy+s->match_floor));
        double matching_gain=exp(fmax(-MATCH_MAX_LOG_GAIN,fmin(MATCH_MAX_LOG_GAIN,matching_log_gain)));
        corrected[0]*=matching_gain;corrected[1]*=matching_gain;
        /* Fixed post-side EQ is incorporated in the 2x2 FIR coefficients. */
        for(int channel=0;channel<2;channel++) {
            s->dry_delay[channel][s->cursor]=inputs[channel][i];
            double dry=s->dry_delay[channel][(s->cursor-s->fir.latency)&RING_MASK];
            double output=gain*(dry*(1-s->amount)+corrected[channel]*s->amount);
            outputs[channel][i]=(float)(s->bypass?dry:output);
        }
    }
}
static float get(AEffect *effect,int32_t index) {
    Finish *s=effect->object;return index==0?s->amount:index==1?s->level:0;
}
static void set(AEffect *effect,int32_t index,float value) {
    Finish *s=effect->object;
    if(!isfinite(value))return;value=fmaxf(0,fminf(1,value));
    if(index==0)s->amount=value;else if(index==1)s->level=value;
}
static intptr_t dispatch(AEffect *effect,int32_t opcode,int32_t index,intptr_t value,void *ptr,float opt) {
    Finish *s=effect->object;
    switch(opcode) {
        case 0:return 1;
        case 1:free(s);return 1;
        case 2:return index==0?1:0;
        case 3:return 0;
        case 4:return 1;
        case 5:if(ptr)strcpy(ptr,"Lead Match v15 WIP");return 1;
        case 6:if(ptr)strcpy(ptr,index==0?"%":"dB");return 1;
        case 7:if(ptr)snprintf(ptr,8,"%.2f",index==0?s->amount*100:-12+24*s->level);return 1;
        case 8:if(ptr)strcpy(ptr,index==0?"Amount":"Output");return 1;
        case 10:if(opt<8000||opt>192000)return 0;s->rate=opt;coefficients(s);reset(s);return 1;
        case 11:return value>0;
        case 12:if(value)reset(s);return 1;
        case 23:
            if(!ptr)return 0;s->chunk=(Chunk){1,EFFECT_ID,s->amount,s->level};
            *(void**)ptr=&s->chunk;return sizeof(s->chunk);
        case 24:
            if(!ptr||value!=sizeof(Chunk))return 0;
            {Chunk chunk;memcpy(&chunk,ptr,sizeof(chunk));
             if(chunk.version!=1||chunk.id!=EFFECT_ID||!isfinite(chunk.amount)||!isfinite(chunk.level))return 0;
             set(effect,0,chunk.amount);set(effect,1,chunk.level);reset(s);return 1;}
        case 26:return 1;
        case 29:if(ptr)strcpy(ptr,"Lead Match v15 WIP");return 1;
        case 35:return 1;
        case 44:s->bypass=value!=0;return 1;
        case 45:if(ptr)strcpy(ptr,"Diva Lead Finish v15 WIP");return 1;
        case 47:if(ptr)strcpy(ptr,"Codex");return 1;
        case 48:if(ptr)strcpy(ptr,"Diva Lead Finish v15 WIP");return 1;
        case 49:return 1000;
        case 51:return ptr&&!strcmp(ptr,"x2in2out")?1:0;
        case 52:return (intptr_t)(s->rate*.10);
        case 58:return 2400;
        case 71:case 72:return 1;
        default:return 0;
    }
}
__declspec(dllexport) AEffect *VSTPluginMain(AudioMaster master) {
    if(!master||!master(NULL,1,0,0,NULL,0))return NULL;
    Finish *s=calloc(1,sizeof(*s));if(!s)return NULL;
    s->master=master;s->rate=48000;s->amount=1;s->level=(TUNED_OUTPUT_DB+12)/24;
    s->effect.magic=0x56737450;s->effect.dispatcher=dispatch;
    s->effect.process=process;s->effect.processReplacing=process;
    s->effect.setParameter=set;s->effect.getParameter=get;
    s->effect.numPrograms=1;s->effect.numParams=2;s->effect.numInputs=2;s->effect.numOutputs=2;
    s->effect.flags=(1<<4)|(1<<5);s->effect.object=s;s->effect.uniqueID=EFFECT_ID;s->effect.version=1000;
    coefficients(s);reset(s);return &s->effect;
}
