/* Offline native-FL renderer. Router arithmetic is ordinary mixer routing;
   all EQ, waveshaping, chorus, phase and clipping use the supplied native DLLs. */
#define main standalone_probe_main
#include "fl_native_probe.c"
#undef main
#include <time.h>
#if defined(SIDE_COMMON_PHASE_PAIR)
#define NODES 17
#elif defined(COMMON_PHASE_PAIR)
#define NODES 15
#elif defined(STATIC_COMB_STACK)
#define NODES 14
#elif defined(FL_PRESET_GRAPH)
#define NODES 13
#else
#define NODES 10
#endif
#ifndef BLOCK
#define BLOCK 512
#endif
typedef struct {HMODULE module;Plug *p;int count,bypass;int values[512];} Node;
static Node nodes[NODES];static Host shared;static void*shared_vt[96];
static float *source;static int frames,rate;
static double mixer[5]={1,0,1,1,1};
typedef struct {int frame,node,index,value;} Automation;
static Automation automation[256];static int automation_count=0;
static int automation_order(const void*a,const void*b){return ((Automation*)a)->frame-((Automation*)b)->frame;}
/* Keep an immutable source buffer for conservative native-SDK interoperability.
   M/S-branch gain changes intentionally crossfeed L/R; this is NOT an EQ2 bug. */
static void pp(Node*n,float*x,int count){if(!n->bypass){
 float original[BLOCK*2];memcpy(original,x,count*8);
 ((void(*)(Plug*,float*,float*,int))n->p->vt[7])(n->p,original,x,count);
}}
static int param(Node*n,int index,int value,int flags){return ((int(*)(Plug*,int,int,int))n->p->vt[6])(n->p,index,value,flags);}
static int load_wave(const char*path){
 FILE*f=fopen(path,"rb");if(!f)return 0;char tag[4];uint32_t length,size=0,sr=0;uint16_t fmt=0,channels=0,bits=0;
 if(fread(tag,4,1,f)!=1||memcmp(tag,"RIFF",4))return 0;fread(&length,4,1,f);fread(tag,4,1,f);if(memcmp(tag,"WAVE",4))return 0;
 long start=0;
 while(fread(tag,4,1,f)==1&&fread(&length,4,1,f)==1){long next=ftell(f)+length+(length&1);
  if(!memcmp(tag,"fmt ",4)){uint32_t d;uint16_t d16;fread(&fmt,2,1,f);fread(&channels,2,1,f);fread(&sr,4,1,f);fread(&d,4,1,f);fread(&d16,2,1,f);fread(&bits,2,1,f);}
  if(!memcmp(tag,"data",4)){start=ftell(f);size=length;break;}fseek(f,next,SEEK_SET);
 }
 if(!start||fmt!=3||channels!=2||bits!=32||size%8)return 0;
 frames=size/8;rate=sr;source=malloc(size);fseek(f,start,SEEK_SET);int good=fread(source,1,size,f)==size;fclose(f);return good;
}
static int save_wave(const char*path,float*data,int n){FILE*f=fopen(path,"wb");if(!f)return 0;uint32_t size=n*8,x;uint16_t h;
 fwrite("RIFF",1,4,f);x=size+36;fwrite(&x,4,1,f);fwrite("WAVEfmt ",1,8,f);x=16;fwrite(&x,4,1,f);h=3;fwrite(&h,2,1,f);h=2;fwrite(&h,2,1,f);x=rate;fwrite(&x,4,1,f);x=rate*8;fwrite(&x,4,1,f);h=8;fwrite(&h,2,1,f);h=32;fwrite(&h,2,1,f);fwrite("data",1,4,f);fwrite(&size,4,1,f);fwrite(data,1,size,f);fclose(f);return 1;
}
static void process(float*data,int n){
 float dry[BLOCK*2],wet[BLOCK*2],mid[BLOCK*2],side[BLOCK*2];
 pp(&nodes[0],data,n);pp(&nodes[1],data,n);pp(&nodes[2],data,n);
 memcpy(dry,data,n*8);memcpy(wet,data,n*8);pp(&nodes[3],wet,n);
 for(int i=0;i<n;i++){
  float l=mixer[0]*dry[2*i]+mixer[1]*wet[2*i];float r=mixer[0]*dry[2*i+1]+mixer[1]*wet[2*i+1];
#ifdef FL_PRESET_GRAPH
  mid[2*i]=side[2*i]=l;mid[2*i+1]=side[2*i+1]=r;
#else
  mid[2*i]=mid[2*i+1]=.5f*(l+r);side[2*i]=side[2*i+1]=.5f*(l-r);
#endif
 }
#ifdef FL_PRESET_GRAPH
#ifdef COMMON_PHASE_PAIR
 pp(&nodes[13],mid,n);pp(&nodes[14],mid,n);memcpy(side,mid,n*8);
#endif
#ifdef STATIC_COMB_STACK
 pp(&nodes[13],mid,n);memcpy(side,mid,n*8);
#endif
 pp(&nodes[10],mid,n);pp(&nodes[11],side,n);
#endif
 pp(&nodes[4],mid,n);pp(&nodes[5],mid,n);pp(&nodes[6],side,n);pp(&nodes[7],side,n);
#ifdef FL_PRESET_GRAPH
#ifdef SIDE_COMMON_PHASE_PAIR
 pp(&nodes[15],side,n);pp(&nodes[16],side,n);
#endif
 pp(&nodes[12],side,n);
 for(int i=0;i<n;i++){data[2*i]=mixer[3]*mid[2*i]+mixer[4]*side[2*i];data[2*i+1]=mixer[3]*mid[2*i+1]+mixer[4]*side[2*i+1];}
#else
 for(int i=0;i<n;i++){data[2*i]=mixer[3]*mid[2*i]+mixer[4]*side[2*i];data[2*i+1]=mixer[3]*mid[2*i+1]-mixer[4]*side[2*i+1];}
#endif
 pp(&nodes[8],data,n);pp(&nodes[9],data,n);
 for(int i=0;i<n*2;i++)data[i]*=mixer[2];
}
static int state_file(Node*n,const char*path,int save){
 IStream*s=NULL;if(CreateStreamOnHGlobal(NULL,TRUE,&s)!=S_OK)return 0;
 if(!save){FILE*f=fopen(path,"rb");if(!f)return 0;fseek(f,0,SEEK_END);long bytes=ftell(f);fseek(f,0,SEEK_SET);void*b=malloc(bytes);fread(b,1,bytes,f);fclose(f);IStream_Write(s,b,bytes,NULL);free(b);LARGE_INTEGER zero;zero.QuadPart=0;IStream_Seek(s,zero,STREAM_SEEK_SET,NULL);}
 ((void(*)(Plug*,IStream*,BOOL))n->p->vt[3])(n->p,s,save);
 if(save){STATSTG st={0};IStream_Stat(s,&st,STATFLAG_NONAME);LARGE_INTEGER zero;zero.QuadPart=0;IStream_Seek(s,zero,STREAM_SEEK_SET,NULL);ULONG bytes=st.cbSize.LowPart,got;void*b=malloc(bytes);IStream_Read(s,b,bytes,&got);FILE*f=fopen(path,"wb");if(!f)return 0;fwrite(b,1,got,f);fclose(f);free(b);}
 IStream_Release(s);return 1;
}
int main(int argc,char**argv){
 setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);if(argc!=NODES+3){fprintf(stderr,"Need input, output, %d native plugin paths\n",NODES);return 2;}
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);AddVectoredExceptionHandler(1,capture_exception);CoInitializeEx(NULL,COINIT_APARTMENTTHREADED);
 if(!load_wave(argv[1]))return 3;
 for(int i=0;i<96;i++)shared_vt[i]=noop;shared_vt[0]=host_dispatch;shared_vt[2]=hint;shared_vt[16]=host_mixing_tick;shared_vt[17]=shared_vt[18]=host_mixing_time;shared.vt=shared_vt;shared.version=21000000;host_sample_rate=rate;
 float*waves=calloc(10*16384,4);host_wave_tables(waves);for(int i=0;i<10;i++)shared.waves[i]=waves+i*16384;
 float*tmp=calloc(4*65536*2,4);for(int i=0;i<4;i++)shared.temp[i]=tmp+i*65536*2;
 for(int i=0;i<NODES;i++){
  Node*n=&nodes[i];n->module=LoadLibraryA(argv[i+3]);if(!n->module){fprintf(stderr,"LOAD_FAIL node=%d error=%lu\n",i,GetLastError());return 4;}
  void*create=GetProcAddress(n->module,"CreatePlugInstance");if(!create)return 5;n->p=((Plug*(*)(Host*,ip))create)(&shared,i+1);
  Info*info=n->p->info;n->count=info->numparams;if(n->count<0||n->count>512)return 6;
  dispatch(n->p,4,0,rate);dispatch(n->p,3,0,BLOCK);dispatch(n->p,11,0,1);
  for(int j=0;j<n->count;j++)n->values[j]=param(n,j,0,2);
  fprintf(stderr,"NODE_READY %d %s params=%d flags=%d\n",i,info->name,n->count,info->flags);
 }
 float*out=malloc(frames*8);printf("READY frames=%d rate=%d nodes=%d\n",frames,rate,NODES);
 char line[4096];
 while(fgets(line,sizeof line,stdin)){
  int node,index,value,at_frame,at_value;double amount;char path[2048];
  if(sscanf(line,"S %d %d %d",&node,&index,&value)==3){if(node<0||node>=NODES||index<0||index>=nodes[node].count)return 7;param(&nodes[node],index,value,1|1024);nodes[node].values[index]=param(&nodes[node],index,0,2);}
  else if(sscanf(line,"G %d %lf",&index,&amount)==2){if(index<0||index>=5||!isfinite(amount))return 8;mixer[index]=amount;}
  else if(sscanf(line,"B %d %d",&node,&value)==2){if(node<0||node>=NODES)return 11;nodes[node].bypass=value!=0;}
  else if(sscanf(line,"H %d %d %d",&node,&index,&value)==3){param(&nodes[node],index,value,1|32|1024);int mapped=param(&nodes[node],index,0,2);nodes[node].values[index]=mapped;param(&nodes[node],index,mapped,4);printf("MAPPED %d %d %d\n",node,index,mapped);}
  else if(sscanf(line,"V %d %d",&node,&index)==2){
   if(node<0||node>=NODES||index<0||index>=nodes[node].count)return 18;
   int actual=param(&nodes[node],index,0,2);param(&nodes[node],index,actual,4);printf("VALUE %d %d %d\n",node,index,actual);
  }
  else if(sscanf(line,"D %d %2047[^\r\n]",&node,path)==2){printf("STATE_SAVED %d %d\n",node,state_file(&nodes[node],path,1));}
  else if(sscanf(line,"L %d %2047[^\r\n]",&node,path)==2){
   int loaded=state_file(&nodes[node],path,0);
   if(loaded)for(int j=0;j<nodes[node].count;j++)nodes[node].values[j]=param(&nodes[node],j,0,2);
   printf("STATE_LOADED %d %d\n",node,loaded);
  }
  else if(sscanf(line,"I %2047[^\r\n]",path)==1){
   float*old=source;int oldrate=rate;
   if(!load_wave(path)||rate!=oldrate)return 14;
   free(old);out=realloc(out,frames*8);if(!out)return 15;
   printf("INPUT_LOADED frames=%d rate=%d\n",frames,rate);
  }
  else if(!strncmp(line,"TCLEAR",6)){automation_count=0;}
  else if(sscanf(line,"T %d %d %d %d",&at_frame,&node,&index,&at_value)==4){
   if(automation_count>=256||at_frame<0||at_frame>=frames||node<0||node>=NODES||index<0||index>=nodes[node].count)return 16;
   automation[automation_count++]=(Automation){at_frame,node,index,at_value};
  }
  else if(line[0]=='R'){
   clock_t start=clock();host_sample_position=0;
   /* Recreate Chorus between trials, without patching DLLs. Native free-running
      LFOs can still vary; Chorus is excluded from deterministic transfer fits. */
   Node*ch=&nodes[3];dispatch(ch->p,12,0,0);dispatch(ch->p,11,0,0);((void(*)(Plug*))ch->p->vt[0])(ch->p);
   void*create=GetProcAddress(ch->module,"CreatePlugInstance");ch->p=((Plug*(*)(Host*,ip))create)(&shared,4);
   dispatch(ch->p,4,0,rate);dispatch(ch->p,3,0,BLOCK);dispatch(ch->p,11,0,1);
   for(int j=0;j<ch->count;j++)param(ch,j,ch->values[j],1|1024);
   for(int i=0;i<NODES;i++){dispatch(nodes[i].p,12,0,0);dispatch(nodes[i].p,2,0,0);dispatch(nodes[i].p,13,0,0);dispatch(nodes[i].p,12,0,1);}
   float zero[BLOCK*2];for(int block=0;block<128;block++){memset(zero,0,sizeof zero);process(zero,BLOCK);}
   qsort(automation,automation_count,sizeof(Automation),automation_order);int next_event=0;
   memcpy(out,source,frames*8);for(int pos=0;pos<frames;){
    while(next_event<automation_count&&automation[next_event].frame==pos){Automation*a=&automation[next_event++];param(&nodes[a->node],a->index,a->value,1|1024);nodes[a->node].values[a->index]=param(&nodes[a->node],a->index,0,2);}
    int n=frames-pos;if(n>BLOCK)n=BLOCK;
    if(next_event<automation_count&&automation[next_event].frame-pos<n)n=automation[next_event].frame-pos;
    if(n<=0)return 17;host_sample_position=pos;process(out+2*pos,n);pos+=n;
   }
   double peak=0,energy=0;int finite=1;for(int i=0;i<frames*2;i++){finite&=isfinite(out[i]);peak=fmax(peak,fabs(out[i]));energy+=(double)out[i]*out[i];}
   if(!finite||!save_wave(argv[2],out,frames))return 9;
   int total=0;for(int i=1;i<=NODES;i++)total+=node_latency[i];
   printf("DONE frames=%d peak=%.12g rms=%.12g latency=%d cpu=%.6g\n",frames,peak,sqrt(energy/(2*frames)),total,(double)(clock()-start)/CLOCKS_PER_SEC);
  }
  else if(line[0]=='Q')break;
  else {fprintf(stderr,"UNKNOWN_COMMAND %s",line);return 10;}
 }
 for(int i=NODES-1;i>=0;i--){dispatch(nodes[i].p,12,0,0);dispatch(nodes[i].p,11,0,0);((void(*)(Plug*))nodes[i].p->vt[0])(nodes[i].p);FreeLibrary(nodes[i].module);}
 CoUninitialize();puts("CLOSED_OK");return 0;
}
