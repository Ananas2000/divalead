#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "vst2_abi.h"
static VstTimeInfo clock_info;
static intptr_t callback(AEffect *e,int32_t op,int32_t index,intptr_t value,void *ptr,float opt) {
    (void)e;(void)index;(void)value;(void)ptr;(void)opt;
    if(op==1)return 2400;if(op==7)return (intptr_t)&clock_info;
    if(op==16)return (intptr_t)clock_info.sampleRate;if(op==17)return 512;
    return 0;
}
static uint32_t read_be32(const unsigned char *p) {
    return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
}
int main(int argc,char **argv) {
    if(argc!=4){fprintf(stderr,"Usage: probe effect.dll save-chunk.bin verify-program.fxp\n");return 2;}
    HMODULE h=LoadLibraryA(argv[1]);if(!h)return 3;
    AEffect *(*entry)(AudioMaster)=(void*)GetProcAddress(h,"VSTPluginMain");if(!entry)return 4;
    clock_info.sampleRate=48000;AEffect *e=entry(callback);
    if(!e||e->magic!=0x56737450||e->uniqueID!=0x444c3732||e->numInputs!=2||e->numOutputs!=2||e->numParams!=2)return 5;
    e->dispatcher(e,0,0,0,NULL,0);char name[128]={0},product[128]={0},program[128]={0};
    e->dispatcher(e,45,0,0,name,0);e->dispatcher(e,48,0,0,product,0);e->dispatcher(e,5,0,0,program,0);
    if(strcmp(name,"Diva Lead Finish v72 WIP")||strcmp(product,name)||strcmp(program,"Lead Match v72 WIP"))return 6;
    if(e->flags&1)return 7; /* Generic host editor, no custom GUI advertised. */
    float amount=e->getParameter(e,0),level=e->getParameter(e,1);
    if(amount!=1||fabs((-12+24*level)-1.8525063970852007)>2e-6)return 8;
    void *chunk=NULL;intptr_t size=e->dispatcher(e,23,1,0,&chunk,0);if(size!=16||!chunk)return 9;
    unsigned char saved[16];memcpy(saved,chunk,16);FILE *f=fopen(argv[2],"wb");if(!f)return 10;fwrite(saved,1,16,f);fclose(f);
    e->setParameter(e,0,.1f);e->setParameter(e,1,.2f);
    if(!e->dispatcher(e,24,1,16,saved,0)||e->getParameter(e,0)!=amount||e->getParameter(e,1)!=level)return 11;
    unsigned char wrong[16];memcpy(wrong,saved,16);wrong[4]^=1;
    if(e->dispatcher(e,24,1,16,wrong,0))return 12;
    int delays[4];const int rates[4]={44100,48000,96000,192000};
    for(int i=0;i<4;i++) {
        clock_info.sampleRate=rates[i];e->dispatcher(e,10,0,0,NULL,(float)rates[i]);
        e->dispatcher(e,11,0,512,NULL,0);e->dispatcher(e,12,0,1,NULL,0);
        delays[i]=e->initialDelay;if(delays[i]<=0||delays[i]>rates[i])return 13;
        if(rates[i]==48000&&delays[i]!=12416)return 14;
        float in[2][512]={{0}},out[2][512]={{0}};float *ip[2]={in[0],in[1]},*op[2]={out[0],out[1]};
        memset(&clock_info,0,sizeof(clock_info));clock_info.sampleRate=rates[i];clock_info.flags=2;
        for(int block=0;block<4;block++) {
            clock_info.samplePos=block*512;e->processReplacing(e,ip,op,512);
            for(int c=0;c<2;c++)for(int k=0;k<512;k++)if(!isfinite(out[c][k])||out[c][k]!=0)return 15;
        }
        e->dispatcher(e,12,0,0,NULL,0);
    }
    int fxp_checked=0;f=fopen(argv[3],"rb");
    if(f) {
        unsigned char data[128]={0};size_t n=fread(data,1,sizeof(data),f);fclose(f);
        if(n!=76||memcmp(data,"CcnK",4)||memcmp(data+8,"FPCh",4)||read_be32(data+4)!=68||read_be32(data+16)!=0x444c3732||read_be32(data+56)!=16)return 16;
        e->setParameter(e,0,.25f);e->setParameter(e,1,.3f);
        if(!e->dispatcher(e,24,1,16,data+60,0)||e->getParameter(e,0)!=amount||e->getParameter(e,1)!=level)return 17;
        fxp_checked=1;
    }
    printf("{\"effect\":\"%s\",\"ID\":\"0x444c3732\",\"parameters\":2,\"generic_editor\":true,\"amount\":%.9g,\"output_dB\":%.9g,\"chunk_roundtrip\":true,\"wrong_ID_chunk_rejected\":true,\"FXP_program_checked\":%s,\"rates\":[44100,48000,96000,192000],\"latencies\":[%d,%d,%d,%d],\"silence_exact\":true,\"FL_GUI_tested\":false}\n",name,amount,-12+24*level,fxp_checked?"true":"false",delays[0],delays[1],delays[2],delays[3]);
    e->dispatcher(e,1,0,0,NULL,0);FreeLibrary(h);return 0;
}
