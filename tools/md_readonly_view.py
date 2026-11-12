"""Read-only native RAM view for source-map planners; never injected into a core."""
def md_to_sms_view(raw,sy):
    data=lambda n,k,offset=0:bytes(raw[(sy[n]+offset+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    out=bytearray(8192);out[0xb0:0x300]=data('game_save_state',592)
    out[0xe0:0xf1]=data('hero_items',17)
    for at,name in [(0x1d,'game_state'),(0x37,'world_graphics_class'),(0xd9,'hero_health'),(0xda,'hero_max_health'),(0xdb,'hero_magic'),(0xdc,'hero_max_magic'),(0xdd,'hero_gold'),(0xde,'hero_keys'),(0xdf,'hero_selected_item'),(0xe0,'hero_basic_level'),(0xe1,'hero_weapon_level'),(0xf1,'hero_armor_level'),(0xf2,'hero_shield_level'),(0x301,'hero_state'),(0x304,'hero_counter'),(0x305,'hero_hurt'),(0x318,'hero_health')]:out[at]=word(name)&255
    out[0xb9:0xbb]=word('room_id').to_bytes(2,'little');out[0xbb:0xbd]=word('house_return_room').to_bytes(2,'little')
    out[0x310:0x312]=word('hero_y').to_bytes(2,'little');out[0x312:0x314]=word('hero_x').to_bytes(2,'little')
    scratch=data('scratch',0x8a0);out[0x900:0x1100]=scratch[:2048];out[0x1c00:0x1ca0]=scratch[0x800:0x8a0]
    out[0x1600:0x1c00]=data('sms_vram',1536,0x3800)
    for at,name in ((0x30a,'hero_direction'),(0xa0,'inventory_slot'),(0xac,'ice_bell_state'),(0x41,'hero_terrain_context')):out[at]=word(name)&255
    out[0x330]=data('world_spell_state',1)[0]
    return bytes(out)
