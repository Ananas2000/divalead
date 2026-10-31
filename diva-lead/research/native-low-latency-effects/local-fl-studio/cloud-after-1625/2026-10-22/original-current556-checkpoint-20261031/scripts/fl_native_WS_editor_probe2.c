/* Own native-plugin diagnostic window, not FL Studio or a user-PC session. */
#define main old_native_probe_main
#include "fl_native_probe.c"
#undef main
static HWND diagnostic_main_window;
static ip editor_host_dispatch(Host*h,ip sender,ip id,ip index,ip value){
 if(id==46)return(ip)diagnostic_main_window;
 return host_dispatch(h,sender,id,index,value);
}
static void pump(Plug*p,int ms){DWORD end=GetTickCount()+ms;do{MSG m;while(PeekMessage(&m,NULL,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessage(&m);}((void(*)(Plug*))p->vt[2])(p);Sleep(10);}while(GetTickCount()<end);}
static int capture_screen(const char*path){
 int width=GetSystemMetrics(SM_CXSCREEN),height=GetSystemMetrics(SM_CYSCREEN);HDC dc=GetDC(NULL),mem=CreateCompatibleDC(dc);HBITMAP bitmap=CreateCompatibleBitmap(dc,width,height);HGDIOBJ old=SelectObject(mem,bitmap);BitBlt(mem,0,0,width,height,dc,0,0,SRCCOPY|CAPTUREBLT);SelectObject(mem,old);
 BITMAPINFO info={0};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=width;info.bmiHeader.biHeight=-height;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;int bytes=width*height*4;void*pixels=malloc(bytes);GetDIBits(mem,bitmap,0,height,pixels,&info,DIB_RGB_COLORS);BITMAPFILEHEADER header={0};header.bfType=0x4d42;header.bfOffBits=sizeof(header)+sizeof(BITMAPINFOHEADER);header.bfSize=header.bfOffBits+bytes;FILE*f=fopen(path,"wb");if(!f)return 0;fwrite(&header,sizeof header,1,f);fwrite(&info.bmiHeader,sizeof(BITMAPINFOHEADER),1,f);fwrite(pixels,bytes,1,f);fclose(f);free(pixels);DeleteObject(bitmap);DeleteDC(mem);ReleaseDC(NULL,dc);return 1;
}
static int state_file(Plug*p,const char*path,int save){
 IStream*s=NULL;if(CreateStreamOnHGlobal(NULL,TRUE,&s)!=S_OK)return 0;
 if(!save){FILE*f=fopen(path,"rb");if(!f)return 0;fseek(f,0,SEEK_END);long bytes=ftell(f);rewind(f);void*b=malloc(bytes);fread(b,bytes,1,f);fclose(f);IStream_Write(s,b,bytes,NULL);free(b);LARGE_INTEGER zero={0};IStream_Seek(s,zero,STREAM_SEEK_SET,NULL);}
 ((void(*)(Plug*,IStream*,BOOL))p->vt[3])(p,s,save);
 if(save){STATSTG st={0};IStream_Stat(s,&st,STATFLAG_NONAME);LARGE_INTEGER zero={0};IStream_Seek(s,zero,STREAM_SEEK_SET,NULL);ULONG size=st.cbSize.LowPart,got;void*b=malloc(size);IStream_Read(s,b,size,&got);FILE*f=fopen(path,"wb");if(!f)return 0;fwrite(b,got,1,f);fclose(f);free(b);}
 IStream_Release(s);return 1;
}
static BOOL CALLBACK show_child(HWND w,LPARAM data){char cls[128]={0},title[256]={0};RECT r;GetClassNameA(w,cls,sizeof cls);GetWindowTextA(w,title,sizeof title);GetWindowRect(w,&r);printf("CHILD class=%s title=%s rect=%ld,%ld,%ld,%ld\n",cls,title,r.left,r.top,r.right,r.bottom);return TRUE;}
int main(int argc,char**argv){
 if(argc!=3)return 2;setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);CoInitializeEx(NULL,COINIT_APARTMENTTHREADED);HMODULE dll=LoadLibraryA(argv[1]);if(!dll)return 3;void*create=GetProcAddress(dll,"CreatePlugInstance");if(!create)return 4;
 static Host h;static void*vt[96];for(int i=0;i<96;i++)vt[i]=noop;vt[0]=editor_host_dispatch;vt[2]=hint;vt[16]=host_mixing_tick;vt[17]=vt[18]=host_mixing_time;h.vt=vt;h.version=21000000;float*waves=calloc(10*16384,4);host_wave_tables(waves);for(int i=0;i<10;i++)h.waves[i]=waves+16384*i;float*tmp=calloc(4*65536*2,4);for(int i=0;i<4;i++)h.temp[i]=tmp+i*65536*2;
 HWND parent=CreateWindowExA(0,"STATIC","Own WaveShaper diagnostic host (not FL Studio)",WS_OVERLAPPEDWINDOW|WS_VISIBLE,40,40,1100,800,NULL,NULL,GetModuleHandle(NULL),NULL);if(!parent)return 6;diagnostic_main_window=parent;h.app=parent;
 Plug*p=((Plug*(*)(Host*,ip))create)(&h,1);dispatch(p,4,0,48000);dispatch(p,3,0,512);dispatch(p,11,0,1);if(!state_file(p,argv[2],0))return 5;
 dispatch(p,0,0,(ip)parent);pump(p,600);printf("EDITOR_READY parent=%p editor=%p\n",parent,p->editor);EnumChildWindows(parent,show_child,0);puts("READY");char line[4096],path[2048];int x,y;
 while(fgets(line,sizeof line,stdin)){
  if(sscanf(line,"CAPTURE %2047[^\r\n]",path)==1){pump(p,200);printf("CAPTURED %d\n",capture_screen(path));}
  else if(sscanf(line,"SAVE %2047[^\r\n]",path)==1){printf("SAVED %d\n",state_file(p,path,1));}
  else if(sscanf(line,"CLICK %d %d",&x,&y)==2){SetCursorPos(x,y);mouse_event(MOUSEEVENTF_LEFTDOWN,0,0,0,0);mouse_event(MOUSEEVENTF_LEFTUP,0,0,0,0);pump(p,250);puts("CLICKED");}
  else if(sscanf(line,"RCLICK %d %d",&x,&y)==2){SetCursorPos(x,y);mouse_event(MOUSEEVENTF_RIGHTDOWN,0,0,0,0);mouse_event(MOUSEEVENTF_RIGHTUP,0,0,0,0);pump(p,250);puts("CLICKED");}
  else if(line[0]=='Q')break;
  else return 7;
 }
 dispatch(p,0,0,0);dispatch(p,11,0,0);((void(*)(Plug*))p->vt[0])(p);DestroyWindow(parent);FreeLibrary(dll);CoUninitialize();puts("CLOSED_OK");return 0;
}
