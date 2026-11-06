/* Native translation of the pre-title story, Z80 0C98..10BE.
 * All graphics, text, relative sprite frames and color sequences come from ROM. */
extern const u8 intro_bank6[],intro_fixed[],intro_mono_font[],intro_symbols_rle[];
extern const u8 intro_fire_colors[],intro_lightning_colors[];
static u16 intro_scene,intro_counter,intro_abort;
static bool intro_boot_music;
static u16 intro_logic_clock;
static volatile u16 intro_tick_work;
static volatile u16 intro_text_predictions,intro_text_irq_skips;
static volatile u32 intro_text_prediction_total;
static u16 intro_sprite_count,intro_sprite_pending;
static volatile u16 intro_line,intro_running;
static u16 intro_actor_state[16],intro_actor_pose[16];
static const u8 *intro_actor_templates;

/* Each explicit title B95 wait advances C02F; loader audio IRQs do not. */
static void title_wait_frame(void)
{
    u32 before=vtimer;
    /* With display disabled, SGDK may process the current blank again.
     * Source B95 always waits for a new IRQ before returning. */
    do { wait_frame(); } while(vtimer==before);
    intro_logic_clock=(intro_logic_clock+1)&255;
}
static void title_wait_frames(u16 frames)
{
    while(frames-- && !title_requested) title_wait_frame();
}

/* 0AA4: one black full IRQ, then blue/green/red ramps held two IRQs. */
static void intro_font_palette(void)
{
    u16 target[32],n,step;bool changed;
    memcpy(target,sms_palette,sizeof(target));memset(sms_palette,0,sizeof(sms_palette));
    set_palette(sms_palette);draw_map();title_wait_frame();VDP_setEnable(TRUE);
    for(step=16;step;step>>=2)
    {
        do
        {
            changed=FALSE;
            for(n=0;n<32;n++) if((sms_palette[n]&(step*3))!=(target[n]&(step*3)))
            { sms_palette[n]+=step;changed=TRUE; }
            if(changed) { intro_palette_pending=1;title_wait_frames(2); }
        } while(changed);
    }
}

static const u8 *intro_address(u16 address) { return intro_fixed+address-0x0f95; }
static void intro_init_actors(u16 address)
{
    intro_actor_templates=intro_address(address);intro_counter=0;
    memset(intro_actor_state,0,sizeof(intro_actor_state));
    memset(intro_actor_pose,0,sizeof(intro_actor_pose));
}

static void intro_tick(void)
{
    u16 clock=(u8)intro_logic_clock,n,count=0;
    intro_tick_work=30; /* 0F32:LD HL,(DCEC),JP(HL),0F36:RET. */
    if(intro_scene==1)
    {
        intro_tick_work=51;
        if(!(clock&7))
        {
            u16 next=(intro_counter+1)&255;
            /* INC/CP6/JR C/XOR clamps any retained actor counter >=6;
             * modulo6 is equivalent only when the old counter was0..5. */
            intro_tick_work=next>=6?235:236;
            intro_counter=next<6?next:0;
            for(n=0;n<3;n++) sms_palette[1+n]=intro_fire_colors[intro_counter*3+n];
        }
    }
    else if(intro_scene>=2)
    {
        const u8 *p=intro_actor_templates,*colors;
        /* 1061 includes all16 actor slots; template slots add the
         * taken CALL cost and their108B branch below. */
        intro_tick_work=intro_scene==2?1793:1702;
        if(!(clock&3)) intro_tick_work+=25;
        if(intro_scene==2) sms_palette[18]=intro_address(0x10bf)[clock&3];
        if(!(clock&3)) intro_counter=(intro_counter+1)&255;
        VDP_resetSprites();
        for(n=0;n<16 && p[0];n++,p+=6)
        {
            u16 descriptor=p[4]|((u16)p[5]<<8),pose=intro_actor_pose[n];
            u16 actor_prefix=intro_actor_state[n]?19:74;
            if(!intro_actor_state[n] && intro_counter==p[2]) intro_actor_state[n]=1;
            if(!intro_actor_state[n]) { intro_tick_work+=64;continue; }
            {
                const u8 *table=intro_address(descriptor)+pose*2;
                u16 address=table[0]|((u16)table[1]<<8);
                const u8 *frame=intro_address(address);
                /* 0A78 costs153+94*SMS sprite count. RST08 table
                 * indices here cannot carry across their low-byte page. */
                intro_tick_work+=7+actor_prefix+296+94*frame[0]+
                    ((clock&3)?31:(pose+1==p[3]?143:97));
                count=add_sms_sprite_frame(count,p[1],(s8)p[0],frame,0);
            }
            if(!(clock&3))
            {
                pose++;
                if(pose==p[3]) { pose=0;intro_actor_state[n]=0; }
                intro_actor_pose[n]=pose;
            }
        }
        if(count) VDP_setSpriteLink(count-1,0);
        /* 1061/108B builds DD40/DD80 after the frame wait. The source IRQ
         * uploads that buffer at 015E..016A on the following VBlank. */
        intro_sprite_count=count;intro_sprite_pending=1;
        /* Only104A calls bank5:BE25 after1061. Callback1055 returns
         * from1061 directly and retains the scene-two picture palette. */
        if(intro_scene==3)
        {
            /*104A bank/JP30T, BE25 empty521T or nonempty584T. */
            intro_tick_work+=30+(count?584:521);
            colors=intro_lightning_colors+(count?6+((clock>>1)&7)*3:0);
            for(n=0;n<3;n++) sms_palette[1+n]=colors[n];
            for(n=0;n<4;n++) { sms_palette[4+n]=colors[3];sms_palette[8+n]=colors[4];sms_palette[12+n]=colors[5]; }
        }
    }
    if(!intro_scene) set_palette(sms_palette);
}

static void intro_wait(u16 frames)
{
    while(frames-- && !intro_abort)
    {
        if(intro_scene) intro_palette_pending=1;
        wait_frame();
        if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1;
        intro_logic_clock=(intro_logic_clock+1)&255;
        intro_tick();
    }
}

/* 0F1E requests its full IRQ before the bitmap work. Preparation on68k
 * can straddle that IRQ; do not force another complete wait afterward. */
static void intro_finish_reveal_wait(u32 requested_frame)
{
    if(vtimer==requested_frame) wait_frame();
    else { SYS_doVBlankProcessEx(IMMEDIATELY);input=JOY_readJoypad(JOY_1); }
    if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1;
    intro_logic_clock=(intro_logic_clock+1)&255;intro_tick();
}

static void intro_upload_patterns(void)
{
    convert_patterns_range_fast(0,288);VDP_loadTileData(md_patterns,16,288,CPU);
}

static void intro_reveal(void)
{
    u16 mask=127;
    do
    {
        u16 row=0,chunk=0;u32 published_frame=vtimer,requested_frame=vtimer;
        u16 phase;
        u8 masks[4];
        u32 planes[4];
        u8 rotated=(u8)((mask<<2)|(mask>>6));
        if(intro_scene) intro_palette_pending=1;
        for(phase=0;phase<4;phase++)
        {
            rotated=(u8)((rotated>>2)|(rotated<<6));
            masks[phase]=rotated;planes[phase]=plane_spread[rotated]<<3;
        }
        /* 0E8B..0E9D changes only plane 3, at 100 Z80 T-states/row.
         * The first visible slice starts at V-counter 112 (0F21) and ends
         * at line 192. Subsequent slices reserve time for the source IRQ.
         * These slices restore the five-frame pass cadence; exact per-row
         * IRQ contention/scanline equivalence still needs verification. */
        while(row<0x900)
        {
            u16 first=row;
            u16 count=chunk?((SYS_isPAL()?71364UL:59736UL)-3600)/100:
                ((192-112)*228)/100;
            count&=0xfffc;
            if(count>0x900-row) count=0x900-row;
            {
                u8 *sms=sms_vram+row*4+3;
                u32 *md=md_patterns+row;
                u16 groups=count>>2;
                while(groups--)
                {
                    sms[0]=masks[0];sms[4]=masks[1];sms[8]=masks[2];sms[12]=masks[3];
                    md[0]=(md[0]&0x77777777UL)|planes[0];
                    md[1]=(md[1]&0x77777777UL)|planes[1];
                    md[2]=(md[2]&0x77777777UL)|planes[2];
                    md[3]=(md[3]&0x77777777UL)|planes[3];
                    sms+=16;md+=4;
                }
                row+=count;
            }
            DMA_queueDma(DMA_VRAM,md_patterns+first,512+first*4,(row-first)*2,2);
            if(!chunk) intro_finish_reveal_wait(requested_frame);
            else
            {
                /* 0F09 runs actor/palette behavior once per pass, not once
                 * per transfer slice. Music still runs in the VBlank IRQ. */
                /* Conversion may reach the next VBlank before this call.
                 * Count that actual IRQ instead of forcing another one. */
                if(vtimer==published_frame) wait_frame();
                else
                {
                    SYS_doVBlankProcessEx(IMMEDIATELY);
                    input=JOY_readJoypad(JOY_1);
                }
                if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) { intro_abort=1;return; }
            }
            if(intro_abort) return;
            published_frame=vtimer;chunk++;
        }
        /* SRL 01 carries into one final iteration with mask zero. */
        if(!mask) break;
        mask>>=1;
    } while(!intro_abort);
}

static void intro_load_scene(u16 scene)
{
    u16 n,row,column;
    const u8 *src=intro_bank6+(scene==1?0x1d70:scene==2?0x2655:0x2f1f);
    if(scene==2) intro_init_actors(0x0f95);
    intro_scene=scene==3?0:scene;VDP_resetSprites();VDP_updateSprites(0,CPU);
    for(n=0x3800;n<0x3b00;n+=2) { sms_vram[n]=0xfa;sms_vram[n+1]=9; }
    if(scene==3)
    {
        /* 0EFA copies D600..D8FF only; preserve the text rows. */
        source_class0_video_map(sms_vram+0x3800,md_map,12*32);
        VDP_setTileMapDataRect(BG_A,md_map,0,2,32,12,32,CPU);
    }
    else draw_map();
    intro_wait(1);
    if(scene>=2) { wait_frame();intro_wait(1);overview_work_budget=0;overview_pacing=1; }
    else { wait_frame();intro_wait(1); }
    for(n=0;n<16;n++) sms_palette[n]=n<4?*src++:0;
    set_palette(sms_palette);
    if(scene<3)
    {
        src=decode_planes(src,sms_vram,4);
        decode_map(src,title_map);
    }
    else
    {
        src=decode_planes(src,scratch,1);
        /* Scene three contains 2304 monochrome rows per plane. */
        for(n=0;n<0x900;n++) sms_vram[n*4]=scratch[n];
        decode_planes(src,scratch,1);
        for(n=0;n<0x900;n++) sms_vram[n*4+1]=scratch[n];
        for(row=0;row<12;row++) for(column=0;column<24;column++)
        {
            n=row+column*12;title_map[(row*24+column)*2]=n;title_map[(row*24+column)*2+1]=n>>8;
        }
    }
    for(n=3;n<0x2400;n+=4) sms_vram[n]=255;
    intro_upload_patterns();
    for(row=0;row<12;row++) memcpy(sms_vram+0x3808+row*64,title_map+row*48,48);
    draw_map();
    if(scene>=2)
    {
        /* Source E57..E72 costs1005162 foreground T states, excluding
         * IRQ work. Audio IRQ work is debited by the shared work budget. */
        while(overview_work_budget<(scene==2?1005162UL:1195746UL) && !intro_abort)
        { wait_frame();if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1; }
        overview_pacing=0;
    }
    intro_wait(1);
    /* 0EFA falls through into0F09 after its picture copy. */
    wait_frame();intro_wait(1);
    if(scene==1)
    {
        /* First scene69/62 follows first music23/20. Queue the first
         * reveal slice one IRQ before its source hardware publication. */
        u16 ready=SYS_isPAL()?41:45;
        while((u16)((u16)vtimer-sound_track_started_frame)<ready) wait_frame();
    }
    intro_scene=scene==3?0:scene;
    intro_reveal();
}

static void intro_fade(void)
{
    u16 step,n;bool changed;
    intro_scene=0;
    for(step=1;step<=16;step*=4)
    {
        do
        {
            changed=FALSE;
            for(n=0;n<16;n++) if(sms_palette[n]&(step*3)) { sms_palette[n]-=step;changed=TRUE; }
            if(changed) { intro_palette_pending=1;intro_wait(4); }
        } while(changed && !intro_abort);
    }
}

static void intro_start_third_animation(void)
{
    u16 n,mask=1;
    decode_planes(intro_bank6+0x3595,scratch,2);
    do
    {
        u8 rotated=mask;
        /* Subsequent source passes resume at V112, with80 lines
         * of foreground time before the next V192 IRQ. */
        overview_work_budget=mask==1?0:(192-112)*228;overview_pacing=1;
        for(n=0;n<0x600;n++)
        {
            /* 0DA0..0DBA sends two bytes at DE,DE+1, then DE+=4. */
            sms_vram[n*4+2]=scratch[n*2]&rotated;
            sms_vram[n*4+3]=scratch[n*2+1]&rotated;
            rotated=(u8)((rotated<<2)|(rotated>>6));
        }
        convert_patterns_range_fast(0,192);VDP_loadTileData(md_patterns,16,192,CPU);
        /* 1536 rows,178T/row, final JR shorter by5T, setup31T. */
        while(overview_work_budget<273434UL && !intro_abort)
        { wait_frame();if(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) intro_abort=1; }
        overview_pacing=0;
        intro_wait(1);mask=(mask<<1)|1;
    } while(mask<256 && !intro_abort);
    intro_init_actors(0x0fe4);intro_scene=3;
}

/* 0D59 sends only D900..DBFF to VDP3B00: the12 text rows.
 * Rewriting the picture rows first delays the text transfer into the beam. */
static void intro_upload_text_map(void)
{
    source_class0_video_map(sms_vram+0x3b00,md_map+12*32,12*32);
    VDP_setTileMapDataRect(BG_A,md_map+12*32,0,14,32,12,32,CPU);
}

/* From BB3 to the next F09 after the first text-map copy:
 *149+50+70+18+47+24708+20+17+16193+10+52+46+52=41432T,
 * plus92T/glyph and the current semantic F32 callback work. */
static bool intro_text_misses_irq(u16 glyphs)
{
    u8 state[336]={0};SourceIrqInput entry;SourceIrqOutput output;
    SourceClockWork reader;u32 total;
    state[0x2e]=1;state[0x35]=0xdd;state[0x30]=1;
    entry.raster=193UL*3420+72UL*15;entry.lines=SYS_isPAL()?313:262;
    entry.tile_count=0;entry.joy=0;entry.reset_mask=16;
    entry.compensation=SYS_isPAL()?0:128;
    reader.tstates=sound_source_work.tstates;reader.fetches=sound_source_work.fetches;
    if(!source_irq(state,&entry,&reader,&output)) { sound_unhandled_command=0x502;return FALSE; }
    /* A request needs187T before setting C02E. IRQ palette polling has
     *27T granularity: subtract26T for a lower bound over entry phase,
     * then include the minimum24T B95 polling tail. Only a certain miss
     * inserts an audio-only wait; uncertain boundaries remain unforced. */
    total=output.whole.tstates+intro_tick_work+41432UL+92UL*glyphs+187+24-26;
    intro_text_predictions++;intro_text_prediction_total=total;
    if(total>=(SYS_isPAL()?71364UL:59736UL)) { intro_text_irq_skips++;return TRUE; }
    return FALSE;
}

static void intro_scroll_text(void)
{
    u16 n;
    for(n=0;n<0x2c0;n++) sms_vram[0x3b00+n]=sms_vram[0x3b40+n];
    for(n=0x3dc0;n<0x3e00;n+=2) { sms_vram[n]=0xfa;sms_vram[n+1]=1; }
}

static void intro_sequence(void)
{
    u16 n,destination,glyphs;bool missed,boot=intro_boot_music;u32 map_frame;const u8 *scan;const u8 *text=intro_bank6+0x39ce,*patch=intro_address(0x10c3);
    /* CE0 resets the line/timer, but preserves DCE2 across attract loops. */
    intro_scene=intro_abort=intro_timer=intro_line=0;intro_running=1;
    intro_palette_pending=intro_sprite_pending=intro_sprite_count=0;
    title_phase=FALSE;
    if(intro_boot_music) intro_boot_music=FALSE;
    else
    {
        /* 0C98 calls the same0B48 audio/video fade as1470. */
        sound_ram[12]=sound_ram[13]=4;sound_ram[11]=12;
        fade_before_title();overview_work_budget=0;overview_pacing=1;
    }
    title_phase=FALSE;VDP_setEnable(FALSE);map_origin=0x3800;
    memset(sms_vram,0,sizeof(sms_vram));
    decode_planes(number_font_rle,sms_vram+0x2600,4);
    load_mono(0x2820,intro_mono_font,256,3,TRUE);
    decode_planes(intro_symbols_rle,sms_vram+0x3400,4);
    for(n=0;n<7;n++)
    {
        u16 address=(patch[0]|((u16)patch[1]<<8))&0x3fff;patch+=2;
        while(*patch) { load_mono(address,intro_mono_font+(*patch++-65)*8,8,3,TRUE);address+=32; }
        patch++;
    }
    for(n=0x3800;n<0x3e00;n+=2) { sms_vram[n]=0xfa;sms_vram[n+1]=1; }
    for(n=0;n<16;n++) { sms_palette[n]=0;sms_palette[16+n]=menu_palette[n]; }
    sms_palette[22]=0x2a;sms_palette[23]=0;sms_palette[31]=1;
    convert_patterns_range_fast(0,512);VDP_loadTileData(md_patterns,16,512,CPU);
    if(!boot)
    {
        /* Original B56..CDA font/setup foreground work, excluding IRQs. */
        while(overview_work_budget<691750UL) wait_frame();
        overview_pacing=0;sound_music(0x85);intro_font_palette();
    }
    else { set_palette(sms_palette);draw_map();VDP_setEnable(TRUE); }
    /* Cold CE0 has C02F=20. Later loops retain the live full-IRQ clock.
     * All four source map waits now run their actual callbacks, including
     * a fire counter wrap before the scene header overwrites its colors. */
    if(boot) intro_logic_clock=20;
    intro_load_scene(1);
    while(*text && !intro_abort)
    {
        do { intro_wait(1); } while(intro_timer && !intro_abort);
        intro_timer=90;intro_scroll_text();intro_wait(2);
        glyphs=0;for(scan=text;*scan && *scan!=255;scan++) glyphs++;
        missed=intro_text_misses_irq(glyphs);map_frame=vtimer;intro_upload_text_map();
        intro_scroll_text();destination=0x3dc2;
        while(*text!=255 && *text) { sms_vram[destination++]=*text++;sms_vram[destination++]=9; }
        if(*text==255) text++;
        intro_line++;
        if(missed && vtimer==map_frame) wait_frame();
        intro_wait(2);intro_upload_text_map();
        if(intro_line==18 || intro_line==39) intro_fade();
        else if(intro_line==19) intro_load_scene(2);
        else if(intro_line==40) intro_load_scene(3);
        else if(intro_line==44) intro_start_third_animation();
    }
    /* 0D10 checks the terminating zero only after the final 90-IRQ timer. */
    while(intro_timer && !intro_abort) intro_wait(1);
    VDP_resetSprites();VDP_updateSprites(0,CPU);
    /* A press skips only the intro; release before accepting a title press. */
    while(input&(BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_START)) wait_frame();
    intro_palette_pending=intro_sprite_pending=intro_sprite_count=0;
    intro_running=0;title_phase=TRUE;title_requested=FALSE;
}
