#ifndef GAW_SOURCE_SPELL_TEACHER_H
#define GAW_SOURCE_SPELL_TEACHER_H
#include <types.h>
/* 7A09..7B30. state: levels[4],apple,intro[2],final flag,max HP,
 * max magic,current magic,gold,nine crystal bytes. Returns text PC;
 * prompt is nonzero only for the second teacher's confirmation. */
u16 source_spell_teacher(u8 teacher,u8 accepted,u8 *state,u16 *prompt);
#endif
