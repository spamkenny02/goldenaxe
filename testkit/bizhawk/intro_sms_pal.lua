GAW_CONFIG = {mode="replay",route="sms_intro_pal",assistance=false}
local dir=debug.getinfo(1,"S").source:sub(2):match("^(.*[/\\])") or "./"
dofile(dir.."gaw_test.lua")
