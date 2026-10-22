#define COBJMACROS
#include <windows.h>
#include <objidl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef intptr_t ip;
typedef struct {void **vt; int version,flags; void *app,*waves[10],*temp[4]; int reserved[30];} Host;
typedef struct {void **vt; ip tag; void *info,*editor; int mono,reserved[32];} Plug;
#pragma pack(push,4)
typedef struct {int sdk;char *name,*shortname;int flags,numparams,poly,outctrl,outvoice,reserved[30];} Info;
#pragma pack(pop)
static int latency=0,calls[512],node_latency[128];
static double host_sample_position=0,host_sample_rate=48000;
static double host_mixing_time(Host*h){return host_sample_position*288./host_sample_rate;}
static int host_mixing_tick(Host*h){return (int)floor(host_mixing_time(h));}
static void host_wave_tables(float *waves){
 unsigned rng=0x46374a31u;
 for(int i=0;i<16384;i++){
  double phase=2*3.14159265358979323846*i/16384.,s=sin(phase);
  waves[i]=s;waves[16384+i]=2/3.14159265358979323846*asin(s);
  waves[32768+i]=s>=0?1:-1;waves[49152+i]=2.*i/16384.-1;
  waves[65536+i]=waves[49152+i];rng=rng*1664525u+1013904223u;
  waves[81920+i]=(float)((double)rng/2147483648.-1);
 }
}
static LONG WINAPI capture_exception(EXCEPTION_POINTERS *e){
 static int seen=0;
 if(e->ExceptionRecord->ExceptionCode==EXCEPTION_ACCESS_VIOLATION && seen++<4){
  fprintf(stderr,"NATIVE_LOAD_EXCEPTION rip=%p rsp=%p\n",(void*)e->ContextRecord->Rip,(void*)e->ContextRecord->Rsp);
  MEMORY_BASIC_INFORMATION m;
  if(VirtualQuery((void*)e->ContextRecord->Rsp,&m,sizeof m)&&m.State==MEM_COMMIT){
   uintptr_t *stack=(uintptr_t*)e->ContextRecord->Rsp;
   for(int i=0;i<10;i++){
    if(VirtualQuery((void*)stack[i],&m,sizeof m)&&m.Type==MEM_IMAGE){
     char path[MAX_PATH]={0};GetModuleFileNameA((HMODULE)m.AllocationBase,path,sizeof path);
     fprintf(stderr,"NATIVE_EXCEPTION_STACK i=%d address=%p module=%s offset=%llx\n",i,(void*)stack[i],path,(unsigned long long)(stack[i]-(uintptr_t)m.AllocationBase));
    }
   }
  }
 }
 return EXCEPTION_CONTINUE_SEARCH;
}
static ip noop(){return 0;}
static ip host_dispatch(Host *h,ip sender,ip id,ip index,ip value){
 if(id>=0&&id<512&&calls[id]++<4)fprintf(stderr,"HOST id=%lld index=%lld value=%lld\n",(long long)id,(long long)index,(long long)value);
 if(id==24)return (ip)GetModuleHandleA(NULL);
 if(id==30){latency=(int)value;if(sender>=0&&sender<128)node_latency[sender]=(int)value;}
 if(id==29||id==47)return (ip)"C:\\Program Files\\Image-Line\\FL Studio 20\\";
 if(id==39){float v=1;int x;memcpy(&x,&v,4);return x;}
 if((id==36||id==37)&&value){double*t=(double*)value;double frame=host_sample_position;t[0]=index==0?frame*3/host_sample_rate:frame*1000/host_sample_rate;t[1]=t[0];return 1;}
 /* Unknown and product-code requests are deliberately unsupported. */
 return 0;
}
static void hint(Host*h,ip sender,char*t){if(t)fprintf(stderr,"HINT %s\n",t);}
static int readable(void*p){MEMORY_BASIC_INFORMATION m;return p&&VirtualQuery(p,&m,sizeof m)&&m.State==MEM_COMMIT&&!(m.Protect&(PAGE_NOACCESS|PAGE_GUARD));}
static ip dispatch(Plug*p,ip id,ip index,ip value){return ((ip(*)(Plug*,ip,ip,ip))p->vt[1])(p,id,index,value);}
int main(int argc,char**argv){
 setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);
 if(argc<2)return 2;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
 AddVectoredExceptionHandler(1,capture_exception);
 CoInitializeEx(NULL,COINIT_APARTMENTTHREADED);
 HMODULE mod=LoadLibraryA(argv[1]);if(!mod){printf("LOAD_FAILED %lu\n",GetLastError());return 3;}
 void*create=GetProcAddress(mod,"CreatePlugInstance");if(!create){puts("NO_NATIVE_ENTRY");return 4;}
 static Host h;static void* vt[96];for(int i=0;i<96;i++)vt[i]=noop;vt[0]=host_dispatch;vt[2]=hint;vt[16]=host_mixing_tick;vt[17]=vt[18]=host_mixing_time;h.vt=vt;h.version=21000000;
 float* waves=calloc(10*16384,sizeof(float));host_wave_tables(waves);for(int i=0;i<10;i++)h.waves[i]=waves+i*16384;
 float* temp=calloc(4*65536*2,sizeof(float));for(int i=0;i<4;i++)h.temp[i]=temp+i*65536*2;
 puts("CREATE_BEGIN");Plug*p=((Plug*(*)(Host*,ip))create)(&h,123);
 if(!readable(p)||!readable(p->vt)||!readable(p->info)){printf("BAD_NATIVE_OBJECT %p\n",(void*)p);return 5;}
 Info*info=p->info;
 printf("INFO sdk=%d params=%d flags=%d name=%s\n",info->sdk,info->numparams,info->flags,readable(info->name)?info->name:"?");
 fprintf(stderr,"DISPATCH sample rate\n");dispatch(p,4,0,48000);dispatch(p,3,0,512);dispatch(p,11,0,1);dispatch(p,12,0,1);
 if(info->numparams<0||info->numparams>4096)return 6;
 for(int i=0;i<info->numparams;i++){
  char name[256]={0};((void(*)(Plug*,int,int,int,char*))p->vt[4])(p,0,i,0,name);
  int v=((int(*)(Plug*,int,int,int))p->vt[6])(p,i,0,2);
  char display[256]={0};((void(*)(Plug*,int,int,int,char*))p->vt[4])(p,1,i,v,display);
  printf("PARAM\t%d\t%d\t%s\t%s\n",i,v,name,display);
 }
 float in[1024]={0},out[1024]={0};in[0]=.25f;in[1]=.125f;
 puts("RENDER_BEGIN");memcpy(out,in,sizeof in);((void(*)(Plug*,float*,float*,int))p->vt[7])(p,out,out,512);
 int finite=1;double sum=0;for(int i=0;i<1024;i++){finite&=isfinite(out[i]);sum+=out[i]*out[i];}
 printf("RENDER finite=%d energy=%.17g first_L=%.9g first_R=%.9g reported_latency=%d\n",finite,sum,out[0],out[1],latency);
 if(argc>2){IStream*s=NULL;if(CreateStreamOnHGlobal(NULL,TRUE,&s)==S_OK){
  ((void(*)(Plug*,IStream*,BOOL))p->vt[3])(p,s,TRUE);
  STATSTG st={0};IStream_Stat(s,&st,STATFLAG_NONAME);LARGE_INTEGER zero;zero.QuadPart=0;IStream_Seek(s,zero,STREAM_SEEK_SET,NULL);
  ULONG n=st.cbSize.LowPart;void*b=malloc(n);ULONG got=0;IStream_Read(s,b,n,&got);
  FILE*f=fopen(argv[2],"wb");if(f){fwrite(b,1,got,f);fclose(f);}printf("SAVED_NATIVE_STATE %lu bytes\n",got);free(b);IStream_Release(s);
 }}
 dispatch(p,12,0,0);dispatch(p,11,0,0);
 ((void(*)(Plug*))p->vt[0])(p);puts("DESTROY_OK");
 puts("UNLOAD_BEGIN");FreeLibrary(mod);puts("UNLOAD_OK");
 CoUninitialize();return finite?0:7;
}
