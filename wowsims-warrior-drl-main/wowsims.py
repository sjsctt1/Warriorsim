import ctypes
import json
import platform

lib_file_path = './wowsimwotlk-'
if platform.system() == 'Linux':
    lib_file_path = lib_file_path + 'linux.so' 
elif platform.system() == 'Darwin':
    lib_file_path = lib_file_path + 'mac.so' 
else:
    lib_file_path = lib_file_path + 'windows.dll' 

library = ctypes.cdll.LoadLibrary(lib_file_path)

# new
new = library.new
new.argtypes = [ctypes.c_char_p]

# runSim
_runSim = library.runSim
_runSim.argtypes = [ctypes.c_char_p]
_runSim.restype = ctypes.POINTER(ctypes.c_char)
def runSim(requestJson):
    char_ptr = _runSim(json.dumps(requestJson).encode('utf-8'))
    string_ptr = ctypes.cast(char_ptr, ctypes.c_char_p)
    result = json.loads(string_ptr.value)
    FreeCString(char_ptr)
    return result

# trySpell
trySpell = library.trySpell
trySpell.argtypes = [ctypes.c_int]
trySpell.restype = ctypes.c_bool

# doNothing
doNothing = library.doNothing
doNothing.restype = ctypes.c_bool

# step
step = library.step
step.restype = ctypes.c_bool

# needsInput
needsInput = library.needsInput
needsInput.restype = ctypes.c_bool

# registerAuras
registerAuras = library.registerAuras
registerAuras.argtypes = [ctypes.POINTER(ctypes.c_char_p)]

# registerTargetAuras
registerTargetAuras = library.registerTargetAuras
registerTargetAuras.argtypes = [ctypes.POINTER(ctypes.c_char_p)]

# getAuras
getAuras = library.getAuras
getAuras.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]

# getTargetAuras
getTargetAuras = library.getTargetAuras
getTargetAuras.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]

# getMeleeSwingTime
getMeleeSwingTime = library.getMeleeSwingTime
getMeleeSwingTime.argtypes = [ctypes.POINTER(ctypes.c_double)]

# getUnits
getUnitCount = library.getUnitCount
getUnitCount.restype = ctypes.c_int

# getRemainingDuration
getRemainingDuration = library.getRemainingDuration
getRemainingDuration.restype = ctypes.c_double

# getIterationDuration
getIterationDuration = library.getIterationDuration
getIterationDuration.restype = ctypes.c_double

# getCurrentTime
getCurrentTime = library.getCurrentTime
getCurrentTime.restype = ctypes.c_double

#getGcdReadyTime
getGcdReadyTime = library.getGcdReadyTime
getGcdReadyTime.restype = ctypes.c_double

# getRage
getRage = library.getRage
getRage.restype = ctypes.c_double

# getEnergy
getEnergy = library.getEnergy
getEnergy.restype = ctypes.c_double

# getComboPoints
getComboPoints = library.getComboPoints
getComboPoints.restype = ctypes.c_int

# getDamageDone
getDamageDone = library.getDamageDone
getDamageDone.restype = ctypes.c_double

# cleanup
cleanup = library.cleanup

# getSpells
getSpells = library.getSpells
getSpells.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]

# getSpellCount
getSpellCount = library.getSpellCount
getSpellCount.restype = ctypes.c_int

# getCooldowns
getCooldowns = library.getCooldowns
getCooldowns.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int), ctypes.c_int]

# getSpellMetrics
_getSpellMetrics = library.getSpellMetrics
_getSpellMetrics.restype = ctypes.POINTER(ctypes.c_char)

# FreeCString
FreeCString = library.FreeCString
FreeCString.argtypes = [ctypes.POINTER(ctypes.c_char)]

def getSpellMetrics():
    char_ptr = _getSpellMetrics()
    string_ptr = ctypes.cast(char_ptr, ctypes.c_char_p)
    cast_metrics = json.loads(string_ptr.value)
    FreeCString(char_ptr)
    return cast_metrics