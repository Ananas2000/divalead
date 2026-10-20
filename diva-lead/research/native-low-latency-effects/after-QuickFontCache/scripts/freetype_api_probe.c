#include <windows.h>
#include <stdio.h>
#include <ft2build.h>
#include FT_FREETYPE_H
int main(int argc,char**argv){
 if(argc!=3)return 2;
 HMODULE module=LoadLibraryA(argv[1]);if(!module){printf("LOAD_FAILED %lu\n",GetLastError());return 3;}
 const char*required[]={"FT_Attach_File","FT_Done_Face","FT_Done_FreeType","FT_Get_Char_Index","FT_Get_Kerning","FT_Init_FreeType","FT_Load_Glyph","FT_New_Face","FT_New_Memory_Face","FT_Render_Glyph","FT_Select_Charmap","FT_Set_Char_Size","FT_Set_Charmap","FT_Set_Pixel_Sizes"};
 for(int i=0;i<14;i++)if(!GetProcAddress(module,required[i])){printf("MISSING_EXPORT %s\n",required[i]);return 4;}
 FT_Error (*init)(FT_Library*)=(void*)GetProcAddress(module,"FT_Init_FreeType");
 FT_Error (*newface)(FT_Library,const char*,FT_Long,FT_Face*)=(void*)GetProcAddress(module,"FT_New_Face");
 FT_Error (*pixels)(FT_Face,FT_UInt,FT_UInt)=(void*)GetProcAddress(module,"FT_Set_Pixel_Sizes");
 FT_UInt (*index)(FT_Face,FT_ULong)=(void*)GetProcAddress(module,"FT_Get_Char_Index");
 FT_Error (*load)(FT_Face,FT_UInt,FT_Int32)=(void*)GetProcAddress(module,"FT_Load_Glyph");
 FT_Error (*render)(FT_GlyphSlot,FT_Render_Mode)=(void*)GetProcAddress(module,"FT_Render_Glyph");
 FT_Error (*doneface)(FT_Face)=(void*)GetProcAddress(module,"FT_Done_Face");
 FT_Error (*done)(FT_Library)=(void*)GetProcAddress(module,"FT_Done_FreeType");
 FT_Library library;FT_Face face;
 int e=init(&library);if(e){printf("INIT_FAILED %d\n",e);return 5;}
 e=newface(library,argv[2],0,&face);if(e){printf("FONT_FAILED %d\n",e);return 6;}
 e=pixels(face,0,24);if(e)return 7;
 unsigned glyph=index(face,'A');if(!glyph)return 8;
 if(load(face,glyph,FT_LOAD_DEFAULT))return 9;
 if(render(face->glyph,FT_RENDER_MODE_NORMAL))return 10;
 printf("FREETYPE_FONT_RENDER_OK exports=14 glyph=%u bitmap_width=%u bitmap_rows=%u\n",glyph,face->glyph->bitmap.width,face->glyph->bitmap.rows);
 doneface(face);done(library);FreeLibrary(module);return 0;
}
