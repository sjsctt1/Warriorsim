import numpy as np
import ctypes
import json
import wowsims

_encoded_settings = None
def Reset():
    wowsims.new(_encoded_settings)
    Auras.register()
    TargetAuras.register()
    Spells.register()

def Load(interactive):
    global _encoded_settings
    f = open('data/feral.json')
    settings = json.load(f)
    settings['simOptions']['interactive'] = interactive
    _encoded_settings = json.dumps(settings).encode('utf-8')
    Reset()



class Spells():
    Berserk = None
    Bite = None
    FFF = None
    Fury = None
    Mangle = None
    Rake = None
    Roar = None
    Rip = None
    Shred = None

    Cooldowns = None
    
    @classmethod
    def register(cls):
        """Map from spell id to spellbook index and stores the result in a global with the spell's name."""
        num_spells = wowsims.getSpellCount()
        spells = np.array([0] * num_spells, dtype=np.int32)
        spells_ptr = (ctypes.c_int * len(spells)).from_buffer(spells)
        wowsims.getSpells(spells_ptr, len(spells))
        for i, spell in enumerate(spells):
            if spell == 50334 and cls.Berserk is None: cls.Berserk = i
            if spell == 48577 and cls.Bite is None: cls.Bite = i
            if spell == 16857 and cls.FFF is None: cls.FFF = i
            if spell == 50213 and cls.Fury is None: cls.Fury = i
            if spell == 48566 and cls.Mangle is None: cls.Mangle = i
            if spell == 48574 and cls.Rake is None: cls.Rake = i
            if spell == 52610 and cls.Roar is None: cls.Roar = i
            if spell == 49800 and cls.Rip is None: cls.Rip = i
            if spell == 48572 and cls.Shred is None: cls.Shred = i
        cls.Cooldowns = np.array([0.0] * len(cls.registered_actions()))
    
    @classmethod
    def registered_actions(cls):
        actions = [
            cls.Berserk, 
            cls.Bite,
            cls.FFF,
            cls.Fury,
            cls.Mangle,
            cls.Rake,
            cls.Roar,
            cls.Rip,
            cls.Shred] 
        return [action for action in actions if action is not None]
    
    @classmethod
    def update(cls):
        actions = np.array(cls.registered_actions(), dtype=np.int32)
        cds_ptr = (ctypes.c_double * len(actions)).from_buffer(cls.Cooldowns)
        actions_ptr = (ctypes.c_int * len(actions)).from_buffer(actions)
        wowsims.getCooldowns(cds_ptr, actions_ptr, len(actions))

class Auras():
    Labels = ["Berserk", "Cat Form", "Clearcasting", "Savage Roar Aura", "Tiger's Fury Aura"]
    Durations = np.array([0.0] * len(Labels), dtype=np.float64)

    @classmethod
    def register(cls):
        ptr = (ctypes.c_char_p * (len(cls.Labels)+1))()
        ptr[:-1] = [label.encode('utf-8') for label in cls.Labels]
        ptr[-1] = None
        wowsims.registerAuras(ptr)
    
    @classmethod
    def update(cls):
        ptr = (ctypes.c_double * len(cls.Durations)).from_buffer(cls.Durations)
        wowsims.getAuras(ptr, len(cls.Durations))
    
    @classmethod
    def get_dur(cls, label):
        return cls.Durations[cls.Labels.index(label)]

class TargetAuras():
    Labels = ["Rake", "Rip", "Mangle"]
    Durations = np.array([0.0] * len(Labels), dtype=np.float64)

    @classmethod
    def register(cls):
        ptr = (ctypes.c_char_p * (len(cls.Labels)+1))()
        ptr[:-1] = [label.encode('utf-8') for label in cls.Labels]
        ptr[-1] = None
        wowsims.registerTargetAuras(ptr)
    
    @classmethod
    def update(cls):
        ptr = (ctypes.c_double * len(cls.Durations)).from_buffer(cls.Durations)
        wowsims.getTargetAuras(ptr, len(cls.Durations))

    @classmethod
    def get_dur(cls, label):
        return cls.Durations[cls.Labels.index(label)]