GAW_CONFIG = {mode="record"}
local dir=debug.getinfo(1,"S").source:sub(2):match("^(.*[/\\])") or "./"
dofile(dir.."gaw_test.lua")
