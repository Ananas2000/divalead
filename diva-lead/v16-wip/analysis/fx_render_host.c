#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "vst2_abi.h"
static VstTimeInfo time_info;
static double rate=48000;static int block_size=512;
static intptr_t master(AEffect *effect,int32_t opcode,int32_t index,intptr_t value,void *ptr,float opt) {
    (void)effect;(void)index;(void)value;(void)ptr;(void)opt;
    switch(opcode){case 1:return 2400;case 7:return (intptr_t)&time_info;case 16:return rate;
        case 17:return block_size;case 23:return 4;case 42:return 1;default:return 0;}
}
static void u32(FILE *f,uint32_t x){fwrite(&x,4,1,f);}static void u16(FILE *f,uint16_t x){fwrite(&x,2,1,f);}
int main(int argc,char **argv) {
    if(argc<4){fprintf(stderr,"Usage: fx_render_host plugin.dll input_float32.wav output.wav [block_size] [amount] [output_db]\n");return 2;}
    FILE *f=fopen(argv[2],"rb");if(!f)return 3;
    char tag[4];uint32_t length;uint16_t format=0,channels=0,bits=0;uint32_t sr=0;
    if(fread(tag,4,1,f)!=1||memcmp(tag,"RIFF",4))return 4;
    fread(&length,4,1,f);fread(tag,4,1,f);if(memcmp(tag,"WAVE",4))return 4;
    long start=0;uint32_t size=0;
    while(fread(tag,4,1,f)==1&&fread(&length,4,1,f)==1){
        long next=ftell(f)+length+(length&1);
        if(!memcmp(tag,"fmt ",4)){uint32_t discard;uint16_t discard16;
            fread(&format,2,1,f);fread(&channels,2,1,f);fread(&sr,4,1,f);fread(&discard,4,1,f);fread(&discard16,2,1,f);fread(&bits,2,1,f);}
        if(!memcmp(tag,"data",4)){start=ftell(f);size=length;break;}fseek(f,next,SEEK_SET);
    }
    if(!start||format!=3||channels!=2||bits!=32||size%8){fprintf(stderr,"Input must be stereo IEEE float32 WAV\n");return 5;}
    int frames=size/8;float *audio=malloc(size);fseek(f,start,SEEK_SET);if(fread(audio,1,size,f)!=size)return 6;fclose(f);
    rate=sr;if(argc>4)block_size=atoi(argv[4]);if(block_size<1||block_size>16384)return 7;
    HMODULE library=LoadLibraryA(argv[1]);if(!library){fprintf(stderr,"LoadLibrary error %lu\n",GetLastError());return 8;}
    AEffect *(*entry)(AudioMaster)=(void*)GetProcAddress(library,"VSTPluginMain");if(!entry)return 9;
    AEffect *e=entry(master);if(!e||e->magic!=0x56737450||e->numInputs!=2||e->numOutputs!=2)return 10;
    e->dispatcher(e,0,0,0,NULL,0);e->dispatcher(e,10,0,0,NULL,(float)rate);e->dispatcher(e,11,0,block_size,NULL,0);
    if(argc>5)e->setParameter(e,0,(float)atof(argv[5]));if(argc>6)e->setParameter(e,1,(float)((atof(argv[6])+12)/24));
    void *chunk=NULL;intptr_t bytes=e->dispatcher(e,23,1,0,&chunk,0);void *saved=malloc(bytes);memcpy(saved,chunk,bytes);
    float amounts[2]={e->getParameter(e,0),e->getParameter(e,1)};
    e->setParameter(e,0,.2f);e->setParameter(e,1,.4f);
    if(!e->dispatcher(e,24,1,bytes,saved,0))return 11;free(saved);
    if(fabs(e->getParameter(e,0)-amounts[0])>1e-7||fabs(e->getParameter(e,1)-amounts[1])>1e-7)return 12;
    e->dispatcher(e,12,0,1,NULL,0);
    f=fopen(argv[3],"wb");if(!f)return 13;
    fwrite("RIFF",1,4,f);u32(f,36+size);fwrite("WAVEfmt ",1,8,f);u32(f,16);u16(f,3);u16(f,2);u32(f,sr);u32(f,sr*8);u16(f,8);u16(f,32);fwrite("data",1,4,f);u32(f,size);
    float *inputs[2],*outputs[2];for(int c=0;c<2;c++){inputs[c]=calloc(block_size,4);outputs[c]=calloc(block_size,4);}
    memset(&time_info,0,sizeof(time_info));time_info.sampleRate=sr;time_info.tempo=180;time_info.flags=2|512|1024|2048;
    /* Optional simulated stopped-host preroll; no wall-clock waiting. */
    if(argc>7) {
        int idle_blocks=atoi(argv[7]);if(idle_blocks<0||idle_blocks>10000)return 15;
        time_info.flags&=~2;
        for(int idle=0;idle<idle_blocks;idle++)e->processReplacing(e,inputs,outputs,block_size);
        time_info.flags|=2;
    }
    double peak=0,sum=0;
    for(int frame=0;frame<frames;frame+=block_size){
        int n=frames-frame;if(n>block_size)n=block_size;time_info.samplePos=frame;time_info.ppqPos=(double)frame/sr*3;
        for(int i=0;i<n;i++)for(int c=0;c<2;c++)inputs[c][i]=audio[2*(frame+i)+c];
        e->processReplacing(e,inputs,outputs,n);
        for(int i=0;i<n;i++)for(int c=0;c<2;c++){float sample=outputs[c][i];if(!isfinite(sample))return 14;peak=fmax(peak,fabs(sample));sum+=sample*sample;fwrite(&sample,4,1,f);}
    }
    fclose(f);printf("RENDER rate=%u frames=%d block=%d peak=%.9f rms=%.9f chunk_roundtrip=1 amount=%.9g output_db=%.9g\n",sr,frames,block_size,peak,sqrt(sum/(2*frames)),amounts[0],-12+24*amounts[1]);
    e->dispatcher(e,12,0,0,NULL,0);e->dispatcher(e,1,0,0,NULL,0);FreeLibrary(library);
    for(int c=0;c<2;c++){free(inputs[c]);free(outputs[c]);}free(audio);return 0;
}
