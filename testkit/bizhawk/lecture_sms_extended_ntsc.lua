-- Adaptation non validee dans BizHawk ; route validee uniquement sous libretro GX.
GAW_CONFIG = {mode="replay",route="sms_extended_ntsc",assistance=true}
local dir=debug.getinfo(1,"S").source:sub(2):match("^(.*[/\\])") or "./"
dofile(dir.."gaw_test.lua")
