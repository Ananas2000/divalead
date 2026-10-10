#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct AEffect AEffect;
typedef intptr_t (*AudioMaster)(AEffect*,int32_t,int32_t,intptr_t,void*,float);
typedef intptr_t (*Dispatcher)(AEffect*,int32_t,int32_t,intptr_t,void*,float);
struct AEffect {
    int32_t magic;
    Dispatcher dispatcher;
    void (*process)(AEffect*,float**,float**,int32_t);
    void (*setParameter)(AEffect*,int32_t,float);
    float (*getParameter)(AEffect*,int32_t);
    int32_t numPrograms,numParams,numInputs,numOutputs,flags;
    intptr_t reserved1,reserved2;
    int32_t initialDelay,realQualities,offQualities;
    float ioRatio;
    void *object,*user;
    int32_t uniqueID,version;
    void (*processReplacing)(AEffect*,float**,float**,int32_t);
    void (*processDoubleReplacing)(AEffect*,double**,double**,int32_t);
    char future[56];
};
typedef struct {
    double samplePos,sampleRate,nanoSeconds,ppqPos,tempo,barStartPos,cycleStartPos,cycleEndPos;
    int32_t timeSigNumerator,timeSigDenominator,smpteOffset,smpteFrameRate,samplesToNextClock,flags;
} VstTimeInfo;
typedef struct {
    int32_t type,byteSize,deltaFrames,flags,noteLength,noteOffset;
    char midiData[4],detune,noteOffVelocity,reserved1,reserved2;
} MidiEvent;
typedef struct {
    int32_t numEvents;
    intptr_t reserved;
    void *events[16];
} Events;

static double sample_position=0;
static const double sample_rate=48000;
static const int block_size=512;
static VstTimeInfo time_info;
static int pattern_notes=5,pattern_transpose=0;
static double pattern_repeat=7;
static double step_swing=0,step_gate=1;
static int root_velocities[3]={100,100,100};
static int step_velocities[8]={100,100,100,100,100,100,100,100},use_step_velocities=0;
static double terminal_gate=-1;
static double step_offsets[8]={0},step_gates[8]={1,1,1,1,1,1,1,1};
static int use_step_grid=0;

static intptr_t master(AEffect *effect,int32_t opcode,int32_t index,intptr_t value,void *ptr,float opt) {
    (void)effect; (void)index; (void)value; (void)opt;
    switch(opcode) {
        case 1:return 2400;
        case 7:
            memset(&time_info,0,sizeof(time_info));
            time_info.samplePos=sample_position;time_info.sampleRate=sample_rate;
            time_info.tempo=180;time_info.ppqPos=sample_position/sample_rate*3;
            time_info.barStartPos=floor(time_info.ppqPos/4)*4;
            time_info.timeSigNumerator=4;time_info.timeSigDenominator=4;
            time_info.flags=(sample_position>=0?2:0)|512|1024|2048|8192;
            if(sample_position==0||sample_position==-4096)time_info.flags|=1;
            return (intptr_t)&time_info;
        case 16:return (intptr_t)sample_rate;
        case 17:return block_size;
        case 23:return 4;
        case 24:return 0;
        case 32:if(ptr)strcpy(ptr,"ReferenceHost");return 1;
        case 33:if(ptr)strcpy(ptr,"ReferenceHost");return 1;
        case 34:return 100;
        case 37:
            if(!ptr)return 0;
            return (!strcmp(ptr,"sendVstEvents")||!strcmp(ptr,"sendVstMidiEvent")||!strcmp(ptr,"sendVstTimeInfo"))?1:0;
        case 42:return 1;
        case 48:return 0;
        case 49:return 0;
        default:return 0;
    }
}

static int load_preset(AEffect *effect,const char *path) {
    FILE *file=fopen(path,"rb");
    if(!file){fprintf(stderr,"Preset open failed: %s\n",path);return 0;}
    fseek(file,0,SEEK_END);long size=ftell(file);rewind(file);
    char *data=calloc(1,(size_t)size+1);
    if(!data||fread(data,1,(size_t)size,file)!=(size_t)size){fclose(file);free(data);return 0;}
    fclose(file);
    intptr_t result=effect->dispatcher(effect,24,1,size,data,0);
    free(data);
    printf("PRESET %s dispatcher_result=%lld\n",path,(long long)result);fflush(stdout);
    return 1;
}

static int dump(AEffect *effect,const char *path) {
    FILE *file=fopen(path,"wb");
    if(!file)return 0;
    fprintf(file,"index\tnormalized\tname\tdisplay\tlabel\n");
    for(int i=0;i<effect->numParams;i++) {
        char name[1024]={0},display[1024]={0},label[1024]={0};
        effect->dispatcher(effect,8,i,0,name,0);
        effect->dispatcher(effect,7,i,0,display,0);
        effect->dispatcher(effect,6,i,0,label,0);
        name[1023]=display[1023]=label[1023]=0;
        fprintf(file,"%d\t%.9g\t%s\t%s\t%s\n",i,effect->getParameter(effect,i),name,display,label);
    }
    fclose(file);
    return 1;
}

static int save_state(AEffect *effect,const char *path) {
    void *data=NULL;
    intptr_t size=effect->dispatcher(effect,23,1,0,&data,0);
    if(size<=0||!data)return 0;
    FILE *file=fopen(path,"wb");if(!file)return 0;
    size_t written=fwrite(data,1,(size_t)size,file);fclose(file);
    return written==(size_t)size;
}

static void write_u16(FILE *file,uint16_t x){fwrite(&x,2,1,file);}
static void write_u32(FILE *file,uint32_t x){fwrite(&x,4,1,file);}

typedef struct {int frame,status,pitch,velocity;} Note;
static int compare_notes(const void *a,const void *b) {
    const Note *x=a,*y=b;
    if(x->frame!=y->frame)return x->frame-y->frame;
    return x->status-y->status;
}

static int render(AEffect *effect,const char *path) {
    if(!effect->processReplacing||effect->numOutputs>8)return 0;
    FILE *file=fopen(path,"wb");if(!file)return 0;
    int frames=288000;
    fwrite("RIFF",1,4,file);write_u32(file,36+frames*8);fwrite("WAVEfmt ",1,8,file);
    write_u32(file,16);write_u16(file,3);write_u16(file,2);
    write_u32(file,48000);write_u32(file,48000*8);write_u16(file,8);write_u16(file,32);
    fwrite("data",1,4,file);write_u32(file,frames*8);
    Note notes[40];int note_count=0;
    double starts[8]={0,1,1.5,2.5,3},durations[8]={1,.5,1,.5,1};int pitches[8]={41,53,37,49,36};
    if(pattern_notes==3) {
        starts[0]=0;starts[1]=1.5;starts[2]=3;
        durations[0]=1.5;durations[1]=1.5;durations[2]=1;
        if(terminal_gate>=0)durations[2]=terminal_gate;
        pitches[0]=41;pitches[1]=37;pitches[2]=36;
    } else if(pattern_notes==8) {
        int repeated_pitches[8]={41,41,53,37,37,49,36,36};
        for(int i=0;i<8;i++) {
            starts[i]=i*.5+(i%2?step_swing/6:0);
            durations[i]=.5*step_gate;pitches[i]=repeated_pitches[i];
            if(i==7&&terminal_gate>=0)durations[i]=.5*terminal_gate;
            if(use_step_grid){starts[i]+=step_offsets[i];durations[i]=.5*step_gates[i];}
        }
    }
    for(int repetition=0;repetition<2;repetition++)for(int i=0;i<pattern_notes;i++) {
        double beat=repetition*pattern_repeat+starts[i];
        int root=pattern_notes==3?i:pattern_notes==8?(i<3?0:i<6?1:2):(i<2?0:i<4?1:2);
        int velocity=pattern_notes==8&&use_step_velocities?step_velocities[i]:root_velocities[root];
        notes[note_count++]=(Note){(int)llround(beat/3*48000),0x90,pitches[i]+pattern_transpose,velocity};
        notes[note_count++]=(Note){(int)llround((beat+durations[i])/3*48000),0x80,pitches[i]+pattern_transpose,0};
    }
    qsort(notes,note_count,sizeof(Note),compare_notes);
    float zero[512]={0},out[8][512],interleaved[1024];float *inputs[8],*outputs[8];
    for(int i=0;i<8;i++){inputs[i]=zero;outputs[i]=out[i];}
    effect->dispatcher(effect,72,0,0,0,0);
    effect->dispatcher(effect,12,0,0,0,0);
    effect->dispatcher(effect,12,0,1,0,0);
    effect->dispatcher(effect,71,0,0,0,0);
    /* Diva applies loaded preset state at the first DSP callback. Process it
       before the first MIDI note, or that state transition can drop note-on. */
    sample_position=-4096;
    for(int warmup=0;warmup<8;warmup++) {
        memset(out,0,sizeof(out));
        effect->processReplacing(effect,inputs,outputs,block_size);
        sample_position+=block_size;
    }
    /* Reset host MIDI state before starting an independent offline phrase. */
    MidiEvent reset_midi[2];Events reset_events;memset(&reset_events,0,sizeof(reset_events));
    memset(reset_midi,0,sizeof(reset_midi));
    for(int i=0;i<2;i++) {
        reset_midi[i].type=1;reset_midi[i].byteSize=sizeof(MidiEvent);
        reset_midi[i].midiData[0]=(char)0xb0;
        reset_midi[i].midiData[1]=(char)(i==0?123:120);
        reset_events.events[reset_events.numEvents++]=&reset_midi[i];
    }
    effect->dispatcher(effect,25,0,0,&reset_events,0);
    memset(out,0,sizeof(out));
    effect->processReplacing(effect,inputs,outputs,block_size);
    int next_note=0;sample_position=0;
    for(int frame=0;frame<frames;frame+=block_size) {
        int n=frames-frame;if(n>block_size)n=block_size;
        MidiEvent midi[16];Events events;memset(&events,0,sizeof(events));
        while(next_note<note_count&&notes[next_note].frame<frame+n) {
            Note note=notes[next_note++];MidiEvent *event=&midi[events.numEvents];memset(event,0,sizeof(*event));
            event->type=1;event->byteSize=sizeof(*event);event->deltaFrames=note.frame-frame;
            event->midiData[0]=(char)note.status;event->midiData[1]=(char)note.pitch;event->midiData[2]=(char)note.velocity;
            events.events[events.numEvents++]=event;
        }
        if(events.numEvents)effect->dispatcher(effect,25,0,0,&events,0);
        memset(out,0,sizeof(out));
        effect->processReplacing(effect,inputs,outputs,n);
        for(int i=0;i<n;i++){interleaved[2*i]=out[0][i];interleaved[2*i+1]=out[1][i];}
        fwrite(interleaved,sizeof(float),n*2,file);sample_position+=n;
    }
    fclose(file);return 1;
}

int main(int argc,char **argv) {
    setvbuf(stdout,NULL,_IONBF,0);
    if(argc<2){fprintf(stderr,"Usage: host.exe plugin_path [preset_path]\n");return 2;}
    HMODULE library=LoadLibraryA(argv[1]);
    if(!library){fprintf(stderr,"LoadLibrary failed error=%lu\n",GetLastError());return 3;}
    AEffect *(*entry)(AudioMaster)=(void*)GetProcAddress(library,"VSTPluginMain");
    if(!entry){fprintf(stderr,"VSTPluginMain missing\n");return 4;}
    AEffect *effect=entry(master);
    if(!effect||effect->magic!=0x56737450){fprintf(stderr,"Invalid AEffect\n");return 5;}
    printf("LOADED params=%d inputs=%d outputs=%d programs=%d\n",effect->numParams,effect->numInputs,effect->numOutputs,effect->numPrograms);
    effect->dispatcher(effect,0,0,0,0,0);
    effect->dispatcher(effect,10,0,0,0,(float)sample_rate);
    effect->dispatcher(effect,11,0,block_size,0,0);
    if(argc>2&&!load_preset(effect,argv[2]))return 6;
    printf("READY\n");
    char line[4096];
    while(fgets(line,sizeof(line),stdin)) {
        line[strcspn(line,"\r\n")]=0;
        if(!strncmp(line,"set ",4)) {
            int index;float normalized;
            if(sscanf(line+4,"%d %f",&index,&normalized)==2&&index>=0&&index<effect->numParams&&normalized>=0&&normalized<=1) {
                effect->setParameter(effect,index,normalized);printf("SET %d %.9g\n",index,effect->getParameter(effect,index));
            } else printf("ERROR set\n");
        } else if(!strncmp(line,"stepvel ",8)) {
            int values[8];int valid=sscanf(line+8,"%d %d %d %d %d %d %d %d",values,values+1,values+2,values+3,values+4,values+5,values+6,values+7)==8;
            for(int i=0;i<8&&valid;i++)if(values[i]<1||values[i]>127)valid=0;
            if(valid){memcpy(step_velocities,values,sizeof(values));use_step_velocities=1;printf("STEPVEL 1\n");}else printf("ERROR stepvel\n");
        } else if(!strncmp(line,"stepgrid ",9)) {
            double offsets[8],gates[8];
            int n=sscanf(line+9,"%lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf",offsets,offsets+1,offsets+2,offsets+3,offsets+4,offsets+5,offsets+6,offsets+7,gates,gates+1,gates+2,gates+3,gates+4,gates+5,gates+6,gates+7);
            int valid=n==16;
            for(int i=0;i<8&&valid;i++)if(!isfinite(offsets[i])||!isfinite(gates[i])||offsets[i]<-.06||offsets[i]>.06||gates[i]<.2||gates[i]>1.1)valid=0;
            if(valid&&offsets[0]>=0){memcpy(step_offsets,offsets,sizeof(offsets));memcpy(step_gates,gates,sizeof(gates));use_step_grid=1;printf("STEPGRID 1\n");}else printf("ERROR stepgrid\n");
        } else if(!strncmp(line,"lastgate ",9)) {
            double gate;
            if(sscanf(line+9,"%lf",&gate)==1&&gate>=.2&&gate<=1){terminal_gate=gate;printf("LASTGATE %.9g\n",gate);}else printf("ERROR lastgate\n");
        } else if(!strncmp(line,"velocities ",11)) {
            int a,b,c;
            if(sscanf(line+11,"%d %d %d",&a,&b,&c)==3&&a>0&&a<128&&b>0&&b<128&&c>0&&c<128) {
                root_velocities[0]=a;root_velocities[1]=b;root_velocities[2]=c;
                printf("VELOCITIES %d %d %d\n",a,b,c);
            } else printf("ERROR velocities\n");
        } else if(!strncmp(line,"timing ",7)) {
            double swing,gate;
            if(sscanf(line+7,"%lf %lf",&swing,&gate)==2&&swing>=0&&swing<=1&&gate>=.2&&gate<=1) {
                step_swing=swing;step_gate=gate;printf("TIMING %.9g %.9g\n",swing,gate);
            } else printf("ERROR timing\n");
        } else if(!strncmp(line,"pattern ",8)) {
            int count=5,transpose=0;double repeat=7;
            if(sscanf(line+8,"%d %d %lf",&count,&transpose,&repeat)==3 &&
               (count==3||count==5||count==8)&&transpose>=-24&&transpose<=24&&repeat>=4&&repeat<=8) {
                pattern_notes=count;pattern_transpose=transpose;pattern_repeat=repeat;
                printf("PATTERN %d %d %.9g\n",count,transpose,repeat);
            } else printf("ERROR pattern\n");
        } else if(!strncmp(line,"get ",4)) {
            int index;
            if(sscanf(line+4,"%d",&index)==1&&index>=0&&index<effect->numParams) {
                char display[1024]={0};effect->dispatcher(effect,7,index,0,display,0);
                display[1023]=0;
                printf("GET %d %.9g %s\n",index,effect->getParameter(effect,index),display);
            } else printf("ERROR get\n");
        } else if(!strncmp(line,"dump ",5))printf("DUMP %s %d\n",line+5,dump(effect,line+5));
        else if(!strncmp(line,"render ",7))printf("RENDER %s %d\n",line+7,render(effect,line+7));
        else if(!strncmp(line,"save ",5))printf("SAVE %s %d\n",line+5,save_state(effect,line+5));
        else if(!strncmp(line,"load ",5))load_preset(effect,line+5);
        else if(!strcmp(line,"quit"))break;
        else printf("ERROR command\n");
    }
    effect->dispatcher(effect,72,0,0,0,0);effect->dispatcher(effect,12,0,0,0,0);
    effect->dispatcher(effect,1,0,0,0,0);FreeLibrary(library);return 0;
}
