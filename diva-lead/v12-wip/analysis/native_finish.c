#define __declspec(x)
#include "lead_finish.c"
static VstTimeInfo native_time;
static intptr_t native_master(AEffect *effect,int32_t opcode,int32_t index,intptr_t value,void *ptr,float opt) {
    (void)effect;(void)index;(void)value;(void)ptr;(void)opt;
    if(opcode==1)return 2400;
    if(opcode==7)return (intptr_t)&native_time;
    return 0;
}
int native_render(const float *input,float *output,int frames,int sr) {
    memset(&native_time,0,sizeof(native_time));native_time.flags=2;native_time.sampleRate=sr;
    AEffect *e=VSTPluginMain(native_master);if(!e)return 0;
    e->dispatcher(e,10,0,0,0,(float)sr);
    float in[2][512],out[2][512];float *ip[2]={in[0],in[1]},*op[2]={out[0],out[1]};
    for(int start=0;start<frames;start+=512) {
        int n=frames-start;if(n>512)n=512;native_time.samplePos=start;
        for(int i=0;i<n;i++)for(int c=0;c<2;c++)in[c][i]=input[(start+i)*2+c];
        e->processReplacing(e,ip,op,n);
        for(int i=0;i<n;i++)for(int c=0;c<2;c++)output[(start+i)*2+c]=out[c][i];
    }
    e->dispatcher(e,1,0,0,0,0);return 1;
}
