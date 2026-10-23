/* Minimal Win64 VST3 audio-effect research host. MIT.
 * ABI declarations follow Steinberg's downloaded MIT pluginterfaces headers.
 * The original reference is never an input to this host. */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef int32_t Result;
typedef struct { void **v; } Object;
#define FN(o,n,T) ((T)((Object*)(o))->v[n])
#define UID(a,b,c,d) {(a)&255,((a)>>8)&255,((a)>>16)&255,((a)>>24)&255,((b)>>16)&255,((b)>>24)&255,(b)&255,((b)>>8)&255,((c)>>24)&255,((c)>>16)&255,((c)>>8)&255,(c)&255,((d)>>24)&255,((d)>>16)&255,((d)>>8)&255,(d)&255}
static const uint8_t unknown_iid[16]=UID(0,0,0xc0000000,0x46);
static const uint8_t component_iid[16]=UID(0xE831FF31,0xF2D54301,0x928EBBEE,0x25697802);
static const uint8_t processor_iid[16]=UID(0x42043F99,0xB7DA453C,0xA569E79D,0x9AAEC33D);
static const uint8_t controller_iid[16]=UID(0xDCD7BBE3,0x7742448D,0xA874AACC,0x979C759E);
static const uint8_t connection_iid[16]=UID(0x70A4156F,0x6E6E4026,0x989148BF,0xAA60D8D1);
static const uint8_t host_iid[16]=UID(0x58E595CC,0xDB2D4969,0x8B6AAF8C,0x36A664E5);
static const uint8_t stream_iid[16]=UID(0xC3BF6EA2,0x30994752,0x9B6BF990,0x1EE33E9B);
static const uint8_t handler_iid[16]=UID(0x93A0BEA3,0x0BD045DB,0x8E890B0C,0xC1E46AC6);
static const uint8_t changes_iid[16]=UID(0xA4779663,0x0BB64A56,0xB44384A8,0x466FEB9D);
static const uint8_t queue_iid[16]=UID(0x01263A18,0xED074F6F,0x98C9D356,0x4686F9BA);
#define NO_INTERFACE ((Result)0x80004002)
static uint32_t keep(void *p){(void)p;return 1;}
static Result query(void *p,const uint8_t *id,void **out){return FN(p,0,Result(*)(void*,const uint8_t*,void**))(p,id,out);}
static void release(void *p){if(p)FN(p,2,uint32_t(*)(void*))(p);}
static Result simple(void*p,int n){return FN(p,n,Result(*)(void*))(p);}
static Result flag(void*p,int n,int value){return FN(p,n,Result(*)(void*,uint8_t))(p,(uint8_t)value);}

typedef struct {void **v;uint8_t *data;int64_t length,capacity,pos;} Stream;
static Result stream_query(void*p,const uint8_t*id,void**out){*out=NULL;if(!memcmp(id,stream_iid,16)||!memcmp(id,unknown_iid,16)){*out=p;return 0;}return NO_INTERFACE;}
static Result stream_read(Stream*s,void*buffer,int32_t n,int32_t*got){if(n<0)return 1;int64_t remain=s->length-s->pos;if(remain<=0){if(got)*got=0;return 1;}if(n>remain)n=(int32_t)remain;if(n>0)memcpy(buffer,s->data+s->pos,n);s->pos+=n;if(got)*got=n;return n?0:1;}
static Result stream_write(Stream*s,void*buffer,int32_t n,int32_t*got){if(n<0)return 1;int64_t end=s->pos+n;if(end>s->capacity){s->capacity=end*2+4096;s->data=realloc(s->data,(size_t)s->capacity);if(!s->data)return 1;}memcpy(s->data+s->pos,buffer,n);s->pos=end;if(end>s->length)s->length=end;if(got)*got=n;return 0;}
static Result stream_seek(Stream*s,int64_t off,int32_t mode,int64_t*out){int64_t pos=off+(mode==1?s->pos:mode==2?s->length:0);if(pos<0)return 1;s->pos=pos;if(out)*out=pos;return 0;}
static Result stream_tell(Stream*s,int64_t*out){*out=s->pos;return 0;}
static void *stream_v[]={stream_query,keep,keep,stream_read,stream_write,stream_seek,stream_tell};
static Stream stream(void){Stream s={stream_v,NULL,0,0,0};return s;}

static Result host_query(void*p,const uint8_t*id,void**out){*out=NULL;if(!memcmp(id,host_iid,16)||!memcmp(id,unknown_iid,16)){*out=p;return 0;}return NO_INTERFACE;}
static Result host_name(void*p,uint16_t*out){(void)p;const char*s="DivaLeadResearch";for(int i=0;i<128;i++){out[i]=(uint8_t)*s;if(*s)s++;}return 0;}
static Result host_create(void*p,const uint8_t*a,const uint8_t*b,void**out){(void)p;(void)a;(void)b;*out=NULL;return NO_INTERFACE;}
static void *host_v[]={host_query,keep,keep,host_name,host_create};
static Object host={host_v};
static Result handler_query(void*p,const uint8_t*id,void**out){*out=NULL;if(!memcmp(id,handler_iid,16)||!memcmp(id,unknown_iid,16)){*out=p;return 0;}return NO_INTERFACE;}
static Result handler_begin(void*p,uint32_t id){(void)p;(void)id;return 0;}
static Result handler_perform(void*p,uint32_t id,double value){(void)p;(void)id;(void)value;return 0;}
static Result handler_restart(void*p,int32_t flags){(void)p;printf("RESTART %d\n",flags);return 0;}
static void *handler_v[]={handler_query,keep,keep,handler_begin,handler_perform,handler_begin,handler_restart};
static Object handler={handler_v};

typedef struct{void **v;uint32_t id;double value;} Queue;
typedef struct{void **v;int32_t count;Queue queues[4096];} Changes;
static Result queue_query(void*p,const uint8_t*id,void**out){*out=NULL;if(!memcmp(id,queue_iid,16)||!memcmp(id,unknown_iid,16)){*out=p;return 0;}return NO_INTERFACE;}
static uint32_t queue_id(Queue*q){return q->id;}
static int32_t queue_count(Queue*q){(void)q;return 1;}
static Result queue_get(Queue*q,int32_t i,int32_t*off,double*value){if(i)return 1;*off=0;*value=q->value;return 0;}
static Result queue_add(Queue*q,int32_t off,double value,int32_t*index){(void)off;q->value=value;*index=0;return 0;}
static void *queue_v[]={queue_query,keep,keep,queue_id,queue_count,queue_get,queue_add};
static Result changes_query(void*p,const uint8_t*id,void**out){*out=NULL;if(!memcmp(id,changes_iid,16)||!memcmp(id,unknown_iid,16)){*out=p;return 0;}return NO_INTERFACE;}
static int32_t changes_count(Changes*c){return c->count;}
static Queue* changes_get(Changes*c,int32_t i){return i>=0&&i<c->count?&c->queues[i]:NULL;}
static Queue* changes_add(Changes*c,const uint32_t*id,int32_t*index){for(int i=0;i<c->count;i++)if(c->queues[i].id==*id){*index=i;return &c->queues[i];}if(c->count==4096)return NULL;*index=c->count;Queue*q=&c->queues[c->count++];q->v=queue_v;q->id=*id;q->value=0;return q;}
static void *changes_v[]={changes_query,keep,keep,changes_count,changes_get,changes_add};
static Changes changes={changes_v,0,{{0}}};

typedef struct{uint8_t cid[16];int32_t cardinality;char category[32],name[64];} ClassInfo;
typedef struct{uint32_t id;uint16_t title[128],shortTitle[128],units[128];int32_t steps;double defaultValue;int32_t unitID,flags;} ParamInfo;
typedef struct{int32_t type,direction,channels;uint16_t name[128];int32_t busType;uint32_t flags;} BusInfo;
typedef struct{int32_t mode,format,maxBlock;double rate;} Setup;
typedef struct{int32_t channels;uint64_t silence;float **buffers;} AudioBus;
typedef struct{int32_t mode,format,samples,numInputs,numOutputs;AudioBus *inputs,*outputs;void *inChanges,*outChanges,*inEvents,*outEvents,*context;} Process;
static Object *component,*processor,*controller;
static int blocksize=512;static float in0[8192],in1[8192],side0[8192],side1[8192],out0[8192],out1[8192];
static float *main_in[]={in0,in1},*side_in[]={side0,side1},*main_out[]={out0,out1};
static AudioBus inputs[2]={{2,0,main_in},{2,0,side_in}},outputs[1]={{2,0,main_out}};
static int input_buses=1;
static void pump(void){MSG m;while(PeekMessage(&m,NULL,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessage(&m);}}
static int process(int n){Process p={0,0,n,input_buses,1,inputs,outputs,changes.count?&changes:NULL,NULL,NULL,NULL,NULL};Result r=FN(processor,9,Result(*)(void*,Process*))(processor,&p);changes.count=0;if(r){printf("ERROR process %ld\n",(long)r);return 0;}return 1;}
static int reset(void){flag(processor,8,0);flag(component,11,0);Setup s={0,0,blocksize,48000.};if(FN(processor,7,Result(*)(void*,Setup*))(processor,&s))return 0;if(flag(component,11,1)||flag(processor,8,1))return 0;memset(in0,0,sizeof in0);memset(in1,0,sizeof in1);memset(side0,0,sizeof side0);memset(side1,0,sizeof side1);for(int i=0;i<128;i++)if(!process(blocksize))return 0;pump();return 1;}
static int render(const char*input,const char*output){FILE*f=fopen(input,"rb");if(!f)return 0;fseek(f,0,SEEK_END);long size=ftell(f);rewind(f);if(size<0||size%8){fclose(f);return 0;}int frames=size/8;float *data=malloc((size_t)size);if(fread(data,1,size,f)!=(size_t)size){fclose(f);free(data);return 0;}fclose(f);if(!reset()){free(data);return 0;}f=fopen(output,"wb");if(!f){free(data);return 0;}double peak=0,sum=0;for(int start=0;start<frames;start+=blocksize){int n=frames-start;if(n>blocksize)n=blocksize;for(int i=0;i<n;i++){in0[i]=data[2*(start+i)];in1[i]=data[2*(start+i)+1];}if(!process(n)){fclose(f);free(data);return 0;}for(int i=0;i<n;i++){float pair[]={out0[i],out1[i]};if(!isfinite(pair[0])||!isfinite(pair[1])){fclose(f);free(data);return 0;}fwrite(pair,4,2,f);for(int k=0;k<2;k++){double a=fabs(pair[k]);if(a>peak)peak=a;sum+=(double)pair[k]*pair[k];}}}fclose(f);free(data);pump();printf("DONE frames=%d peak=%.12g rms=%.12g latency=%u\n",frames,peak,sqrt(sum/(frames*2)),FN(processor,6,uint32_t(*)(void*))(processor));return 1;}
static void utf8(uint16_t*src,char*out,int cap){WideCharToMultiByte(CP_UTF8,0,(WCHAR*)src,-1,out,cap,NULL,NULL);out[cap-1]=0;}
static int dump(const char*path){FILE*f=fopen(path,"wb");if(!f)return 0;int count=FN(controller,8,int32_t(*)(void*))(controller);fprintf(f,"index\tid\tnormalized\tplain\tdefault\tsteps\tflags\ttitle\tdisplay\tunits\n");for(int i=0;i<count;i++){ParamInfo p={0};if(FN(controller,9,Result(*)(void*,int32_t,ParamInfo*))(controller,i,&p))continue;double v=FN(controller,14,double(*)(void*,uint32_t))(controller,p.id);uint16_t display[128]={0};FN(controller,10,Result(*)(void*,uint32_t,double,uint16_t*))(controller,p.id,v,display);char title[512]={0},text[512]={0},units[512]={0};utf8(p.title,title,sizeof title);utf8(display,text,sizeof text);utf8(p.units,units,sizeof units);double plain=FN(controller,12,double(*)(void*,uint32_t,double))(controller,p.id,v);fprintf(f,"%d\t%u\t%.17g\t%.17g\t%.17g\t%d\t%d\t%s\t%s\t%s\n",i,p.id,v,plain,p.defaultValue,p.steps,p.flags,title,text,units);}fclose(f);printf("DUMP %d\n",count);return 1;}
static int save(const char*path){if(changes.count&&!reset())return 0;Stream s=stream();Result r=FN(component,13,Result(*)(void*,Stream*))(component,&s);if(r){free(s.data);return 0;}FILE*f=fopen(path,"wb");if(!f){free(s.data);return 0;}fwrite(s.data,1,(size_t)s.length,f);fclose(f);printf("SAVED %lld\n",(long long)s.length);free(s.data);return 1;}
static int load(const char*path){FILE*f=fopen(path,"rb");if(!f)return 0;Stream s=stream();fseek(f,0,SEEK_END);s.length=s.capacity=ftell(f);rewind(f);s.data=malloc((size_t)s.length);fread(s.data,1,(size_t)s.length,f);fclose(f);flag(processor,8,0);flag(component,11,0);Result r=FN(component,12,Result(*)(void*,Stream*))(component,&s);s.pos=0;Result cr=FN(controller,5,Result(*)(void*,Stream*))(controller,&s);changes.count=0;free(s.data);printf("LOADED %ld %ld\n",(long)r,(long)cr);return r==0&&cr==0;}

int main(int argc,char**argv){setvbuf(stdout,NULL,_IONBF,0);if(argc<2)return 2;SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);CoInitializeEx(NULL,COINIT_APARTMENTTHREADED);HMODULE dll=LoadLibraryA(argv[1]);if(!dll){printf("ERROR LoadLibrary %lu\n",GetLastError());return 3;}uint8_t(*init)(void)=(void*)GetProcAddress(dll,"InitDll");if(init)printf("INITDLL %d\n",init());Object*(*factory_fn)(void)=(void*)GetProcAddress(dll,"GetPluginFactory");if(!factory_fn)return 4;Object*factory=factory_fn();int count=FN(factory,4,int32_t(*)(void*))(factory);ClassInfo chosen={0};for(int i=0;i<count;i++){ClassInfo c={0};Result r=FN(factory,5,Result(*)(void*,int32_t,ClassInfo*))(factory,i,&c);printf("CLASS %d %s %s %ld\n",i,c.name,c.category,(long)r);if(!strcmp(c.category,"Audio Module Class"))chosen=c;}if(!chosen.name[0])return 5;
    Result r=FN(factory,6,Result(*)(void*,const uint8_t*,const uint8_t*,void**))(factory,chosen.cid,component_iid,(void**)&component);printf("COMPONENT %ld\n",(long)r);if(r||!component)return 6;r=FN(component,3,Result(*)(void*,Object*))(component,&host);printf("INITIALIZE %ld\n",(long)r);if(r)return 7;if(query(component,processor_iid,(void**)&processor)||!processor)return 8;
    if(query(component,controller_iid,(void**)&controller)||!controller){uint8_t cid[16]={0};r=FN(component,5,Result(*)(void*,uint8_t*))(component,cid);if(r)return 9;r=FN(factory,6,Result(*)(void*,const uint8_t*,const uint8_t*,void**))(factory,cid,controller_iid,(void**)&controller);if(r||!controller)return 10;r=FN(controller,3,Result(*)(void*,Object*))(controller,&host);printf("CONTROLLER_INIT %ld\n",(long)r);if(r)return 11;}
    FN(controller,16,Result(*)(void*,Object*))(controller,&handler);
    Object*pc=NULL,*cc=NULL;if(!query(component,connection_iid,(void**)&pc)&&!query(controller,connection_iid,(void**)&cc)){FN(pc,3,Result(*)(void*,Object*))(pc,cc);FN(cc,3,Result(*)(void*,Object*))(cc,pc);}
    input_buses=FN(component,7,int32_t(*)(void*,int32_t,int32_t))(component,0,0);int nbout=FN(component,7,int32_t(*)(void*,int32_t,int32_t))(component,0,1);printf("BUSSES %d %d\n",input_buses,nbout);if(input_buses<1||input_buses>2||nbout!=1)return 12;uint64_t arrangements[2]={3,3},out_arrangement=3;r=FN(processor,3,Result(*)(void*,uint64_t*,int32_t,uint64_t*,int32_t))(processor,arrangements,input_buses,&out_arrangement,1);printf("ARRANGEMENTS %ld\n",(long)r);
    for(int direction=0;direction<2;direction++)for(int bus=0;bus<(direction?nbout:input_buses);bus++){BusInfo b={0};r=FN(component,8,Result(*)(void*,int32_t,int32_t,int32_t,BusInfo*))(component,0,direction,bus,&b);printf("BUS %d %d channels=%d result=%ld\n",direction,bus,b.channels,(long)r);if(r||b.channels!=2)return 13;FN(component,10,Result(*)(void*,int32_t,int32_t,int32_t,uint8_t))(component,0,direction,bus,1);}
    printf("READY name=%s params=%d latency=%u\n",chosen.name,FN(controller,8,int32_t(*)(void*))(controller),FN(processor,6,uint32_t(*)(void*))(processor));
    char line[8192];while(fgets(line,sizeof line,stdin)){line[strcspn(line,"\r\n")]=0;if(!strncmp(line,"dump ",5)){if(!dump(line+5))puts("ERROR dump");}else if(!strncmp(line,"save ",5)){if(!save(line+5))puts("ERROR save");}else if(!strncmp(line,"load ",5)){if(!load(line+5))puts("ERROR load");}else if(!strncmp(line,"text ",5)){uint32_t id;char text[2048];uint16_t wide[2048];double value=0;if(sscanf(line+5,"%u %2047[^\n]",&id,text)!=2){puts("ERROR text syntax");continue;}MultiByteToWideChar(CP_UTF8,0,text,-1,(WCHAR*)wide,2048);r=FN(controller,11,Result(*)(void*,uint32_t,uint16_t*,double*))(controller,id,wide,&value);if(r||!isfinite(value)||value<0||value>1){printf("ERROR text parse %ld %.17g\n",(long)r,value);continue;}r=FN(controller,15,Result(*)(void*,uint32_t,double))(controller,id,value);int32_t index;Queue*q=changes_add(&changes,&id,&index);if(q)q->value=value;printf("SET %u %.17g %ld\n",id,value,(long)r);}else if(!strncmp(line,"set ",4)||!strncmp(line,"plain ",6)){uint32_t id;double value;int plain=line[0]=='p';if(sscanf(line+(plain?6:4),"%u %lf",&id,&value)!=2){puts("ERROR set syntax");continue;}if(plain)value=FN(controller,13,double(*)(void*,uint32_t,double))(controller,id,value);if(!isfinite(value)||value<0||value>1){puts("ERROR normalized range");continue;}r=FN(controller,15,Result(*)(void*,uint32_t,double))(controller,id,value);int32_t index;Queue*q=changes_add(&changes,&id,&index);if(q)q->value=value;printf("SET %u %.17g %ld\n",id,value,(long)r);}else if(!strncmp(line,"render ",7)){char in[4096],out[4096];if(sscanf(line+7,"%4095s %4095s",in,out)!=2||!render(in,out))puts("ERROR render");}else if(!strncmp(line,"block ",6)){int n=atoi(line+6);if(n>=16&&n<=8192)blocksize=n;printf("BLOCK %d\n",blocksize);}else if(!strcmp(line,"latency"))printf("LATENCY %u\n",FN(processor,6,uint32_t(*)(void*))(processor));else if(!strcmp(line,"quit"))break;else puts("ERROR unknown command");pump();}
    flag(processor,8,0);flag(component,11,0);if(pc&&cc){FN(pc,4,Result(*)(void*,Object*))(pc,cc);FN(cc,4,Result(*)(void*,Object*))(cc,pc);}release(pc);release(cc);simple(controller,4);simple(component,4);release(controller);release(processor);release(component);release(factory);uint8_t(*done)(void)=(void*)GetProcAddress(dll,"ExitDll");if(done)done();FreeLibrary(dll);CoUninitialize();return 0;
}
