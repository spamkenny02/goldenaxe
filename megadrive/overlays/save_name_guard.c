/* Non-destructive guard for uninitialized/mixed SRAM bytes, not just allFF. */
typedef unsigned char u8;
typedef unsigned short u16;
u16 save_name_valid(const volatile u8*name,u16 stride){
 u16 n;
 if(!*name)return 0;
 for(n=0;n<8;n++,name+=stride){
  u8 c=*name;
  if(!c)return 1;
  if(!((c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='&'||c=='.'||c=='-'||c==' '))return 0;
 }
 return 1;
}
