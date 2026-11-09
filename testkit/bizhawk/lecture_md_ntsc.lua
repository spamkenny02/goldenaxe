GAW_CONFIG = {mode="replay",route="md_ntsc",assistance=true}
local dir=debug.getinfo(1,"S").source:sub(2):match("^(.*[/\\])") or "./"
dofile(dir.."gaw_test.lua")
