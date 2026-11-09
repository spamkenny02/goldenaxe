-- Adaptation BizHawk creee pour ce kit. Les campagnes d'origine utilisent
-- le lecteur libretro Python fourni, pas BizHawk. Voir README_FR.md.
-- Modes: monitor (jouer librement), record, replay (route CSV).
local cfg = GAW_CONFIG or { mode = "monitor", route = "md_ntsc", assistance = true }
local script = debug.getinfo(1, "S").source:sub(2)
local dir = script:match("^(.*[/\\])") or "./"
local base = dir .. "../"
local system = emu.getsystemid()
local md = system == "GEN"
assert(md or system == "SMS", "Charger une ROM SMS ou Mega Drive avant le script.")
local mode = cfg.mode or "monitor"
assert(mode == "monitor" or mode == "record" or mode == "replay", "Mode inconnu")
local sha = gameinfo.getromhash():lower():gsub("^sha1:", "")
local known = md and {
  ["65dbbd5c318a5dc8fad9cfcd369a051a48fa39eb"] = true, -- V320
  ["9a42e3283d7b10035924636f56dbb9ad67b4303c"] = true  -- V321
} or { ["5dc6988b6592a61c8a66f744e9701bfc1494d5b1"] = true }
assert(known[sha], "ROM inconnue : adresses RAM du kit non garanties. Ne pas reutiliser sur une autre compilation.")
local domain = cfg.domain
if not domain then
  local names = memory.getmemorydomainlist()
  for _, name in pairs(names) do
    if (md and name == "68K RAM") or (not md and name == "RAM") then domain = name end
  end
  if not domain then
    local matches = {}
    for _, name in pairs(names) do
      if name:lower():find("ram") and memory.getmemorydomainsize(name) == (md and 65536 or 8192) then
        matches[#matches + 1] = name
      end
    end
    if #matches == 1 then domain = matches[1] end
  end
end
assert(domain and memory.getmemorydomainsize(domain) == (md and 65536 or 8192),
  "Domaine RAM ambigu. Renseigner GAW_CONFIG.domain avec le domaine RAM principal.")
local function byte(n) return memory.read_u8(n, domain) end
local function word(n)
  if md then return memory.read_u16_be(n, domain) end
  return memory.read_u16_le(n, domain)
end
local function state()
  local crystals = 0
  for n = 0, 8 do
    if byte((md and 0x28be or 0xb0) + 0x1f + n) >= 128 then crystals = crystals + 1 end
  end
  return {
    room = word(md and 0x28b4 or 0xb9),
    health = md and word(0x2b16) or byte(0x318),
    game = md and word(0x74c) or -1,
    audio_error = md and word(0x2d12) or -1,
    crystals = crystals
  }
end
-- libretro IDs verified in the actual GX libretro.c: Y->A, B->B, A->C.
local mapping = md and {
  [0]="P1 B", [1]="P1 A", [2]="P1 Mode", [3]="P1 Start",
  [4]="P1 Up", [5]="P1 Down", [6]="P1 Left", [7]="P1 Right", [8]="P1 C"
} or {
  [0]="P1 B1", [3]="Pause", [4]="P1 Up", [5]="P1 Down",
  [6]="P1 Left", [7]="P1 Right", [8]="P1 B2"
}
local available = joypad.get()
for _, name in pairs(mapping) do
  if name ~= "P1 Mode" then assert(available[name] ~= nil, "Bouton absent : " .. name .. ". Verifier la manette configuree.") end
end
local function mask_from_input(pad)
  local mask = 0
  for bit, name in pairs(mapping) do if pad[name] then mask = mask + 2 ^ bit end end
  return mask
end
local function apply(mask)
  local pad = {}
  for name, _ in pairs(available) do pad[name] = false end
  for bit, name in pairs(mapping) do
    if available[name] ~= nil then pad[name] = math.floor(mask / 2 ^ bit) % 2 == 1 end
  end
  joypad.set(pad)
end
local rows, position, total = {}, 1, cfg.frames
if mode == "replay" then
  assert(emu.framecount() == 0, "Reouvrir la ROM a froid, sans sauvegarde, et lancer a l'image0.")
  local route = cfg.route or "md_ntsc"
  assert((route:sub(1,3) == "md_") == md, "Route d'un autre systeme")
  local want_pal = route:sub(-3) == "pal"
  assert((emu.getdisplaytype():upper():find("PAL") ~= nil) == want_pal, "Region de la route differente du coeur")
  for line in io.lines(base .. "routes/" .. route .. ".csv") do
    local a,b,m,g = line:match("^(%d+),(%d+),(%d+),(-?%d+)$")
    if a then
      a,b,m,g = tonumber(a),tonumber(b),tonumber(m),tonumber(g)
      assert(a == (#rows == 0 and 1 or rows[#rows][2] + 1) and b >= a, "CSV non continu")
      assert(g == -1 or g == 0 or g == 129, "Valeur de protection inconnue")
      rows[#rows+1] = {a,b,m,g}
    end
  end
  assert(#rows > 0, "Route vide")
  total = math.min(total or rows[#rows][2], rows[#rows][2])
end
local suffix = os.date("%Y%m%d-%H%M%S") .. "-" .. system .. "-" .. mode
local function fresh(path)
  local old = io.open(path, "rb")
  if old then old:close();error("Le fichier existe deja : " .. path) end
  return assert(io.open(path, "w"))
end
local log = fresh(base .. "logs/" .. suffix .. ".csv")
log:write("frame,room,game,health,crystals,audio_error,guard\n")
local record = mode == "record" and fresh(base .. "logs/" .. suffix .. "-route.csv") or nil
if record then record:write("start,end,mask,guard\n") end
local closed, seen_ending = false, false
local function close()
  if closed then return end
  closed = true
  if log then log:flush();log:close() end
  if record then record:flush();record:close() end
end
event.onexit(close, "gaw testkit close")
console.log("GAW " .. mode .. " / " .. system .. " / " .. domain .. " / " .. sha)
console.log("Adaptation BizHawk non certifiee A-Z ; arreter en cas de desynchronisation.")
local frame, previous, guard_writes = 0, nil, 0
local initial_frame = emu.framecount()
while not total or frame < total do
  assert(emu.framecount() == initial_frame + frame, "Rewind/reset/savestate detecte : reprendre depuis le debut")
  frame = frame + 1
  local guard = -1
  if mode == "replay" then
    while rows[position][2] < frame do position = position + 1 end
    local row = rows[position]
    apply(row[3]);guard = row[4]
    if guard ~= -1 and cfg.assistance then
      assert(md, "Aucune injection SMS prevue par les routes fournies")
      memory.write_u16_be(0x2b1a, guard, domain);guard_writes = guard_writes + 1
    end
  elseif record then
    local mask = mask_from_input(joypad.getimmediate())
    record:write(string.format("%d,%d,%d,-1\n",frame,frame,mask))
  end
  emu.frameadvance()
  local s = state()
  seen_ending = seen_ending or s.game == 14
  local key = s.room .. ":" .. s.game .. ":" .. s.health .. ":" .. s.crystals
  if key ~= previous or frame % 60 == 0 then
    log:write(string.format("%d,%d,%d,%d,%d,%d,%d\n",frame,s.room,s.game,s.health,s.crystals,s.audio_error,guard))
    log:flush();previous = key
  end
  gui.text(2,2,string.format("GAW %s f%d R%03X HP%d C%d/9",mode,frame,s.room,s.health,s.crystals))
  if md then assert(s.audio_error == 0, "Erreur lecteur audio : " .. s.audio_error) end
end
apply(0)
local final = state()
console.log(string.format("Fin : %d images, salle%03X, cristaux%d/9, credits observes=%s, ecritures protection%d",
  frame,final.room,final.crystals,tostring(seen_ending),guard_writes))
if mode == "replay" and md and total == rows[#rows][2] and cfg.assistance then
  assert(seen_ending and final.room == 332 and final.game == 0 and final.crystals == 9,
    "Fin attendue non atteinte : route desynchronisee. Ce n'est pas un test reussi.")
end
close();client.pause()
