/* 669D service3 and79DA..7B30: four original magic teachers. */
#include "source_spell_teacher.h"
extern const u8 *const spell_teacher_portraits_rle[],*const spell_teacher_portraits_map[];
extern const u8 spell_teacher_text[];
extern const u16 spell_teacher_text_index[][2],spell_teacher_text_count;
static volatile u16 spell_teacher_phase,spell_teacher_index;
static const u8 *spell_teacher_message(u16 pc)
{
    u16 n;
    for(n=0;n<spell_teacher_text_count;n++)
        if(spell_teacher_text_index[n][0]==pc) return spell_teacher_text+spell_teacher_text_index[n][1];
    return (const u8 *)"";
}
static void spell_teacher_read(u8 *state)
{
    u16 n;
    for(n=0;n<4;n++) state[n]=hero_items[4+n];
    state[4]=hero_items[8];
    for(n=0;n<3;n++) state[5+n]=game_save_state[0x43+n];
    state[8]=hero_max_health;state[9]=hero_max_magic;state[10]=hero_magic;state[11]=hero_gold;
    for(n=0;n<9;n++) state[12+n]=game_save_state[0x1f+n];
}
static void spell_teacher_apply(const u8 *state)
{
    u16 n;
    for(n=0;n<4;n++) hero_items[4+n]=state[n];
    hero_items[8]=state[4];
    for(n=0;n<3;n++) game_save_state[0x43+n]=state[5+n];
    hero_max_magic=state[9];hero_magic=state[10];
}
static void show_spell_teacher_service(void)
{
    static const u8 towns[]={0xe6,0xa3,0x2c,0xaa};
    u16 teacher,prompt,text,n,cost;u8 state[21],preview[21];bool accepted=TRUE;
    for(teacher=0;teacher<4;teacher++) if(house_return_room==towns[teacher]) break;
    if(teacher==4) return;
    spell_teacher_read(state);memcpy(preview,state,sizeof(state));
    source_spell_teacher(teacher,FALSE,preview,&prompt);
    save_service_phase=8;spell_teacher_phase=1;spell_teacher_index=teacher;
    game_state=22;house_dialogue_active=1;
    service_begin(spell_teacher_portraits_rle[teacher],spell_teacher_portraits_map[teacher]);
    if(prompt)
    {
        /* 7A6D sets the introductory flag before the confirmation window. */
        game_save_state[0x44]=preview[6];house_dialogue_index=prompt;
        render_dialogue_text(spell_teacher_message(prompt),TRUE);
        spell_teacher_phase=2;accepted=save_confirm_yes_no();
    }
    text=source_spell_teacher(teacher,accepted,state,&prompt);
    cost=hero_gold-state[11];spell_teacher_phase=3;
    for(n=0;n<cost;n++)
    {
        hero_gold--;sound_effect(0x95);merchant_number(0x3dd0,hero_gold);draw_map();wait_frame();wait_frame();
    }
    hero_gold_drawn=hero_gold;hero_gold_pending=FALSE;
    spell_teacher_apply(state);house_dialogue_index=text;
    render_dialogue_text(spell_teacher_message(text),TRUE);wait_dialog_end();
    prepare_hero_magic_bar();service_finish();spell_teacher_phase=0;
}
