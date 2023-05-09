import array
import ctypes
import wowsims
import json
import numpy as np

class Settings():
    def __init__(self):
        self._encoded_settings = None

    def Reset(self):
        wowsims.new(self._encoded_settings)
        Auras.register()
        TargetAuras.register()
        Spells.register()

    def Load(self, interactive):
        f = open('data/fury-human-bis-p3.json')
        settings = json.load(f)
        settings['simOptions']['interactive'] = interactive
        self._encoded_settings = json.dumps(settings).encode('utf-8')
        self.Reset()

class Spells():
    Bloodthirst = None
    Whirlwind = None
    Slam = None
    HeroicStrike = None
    Execute = None
    Rend = None
    Overpower = None
    BattleStance = None 
    BerserkerStance = None 
    DeathWish = None 
    Recklessness = None 
    ShatteringThrow = None 
    Bloodrage = None
    # Other CD is here so that the agent could control it
    EngiGlove = None
    Bloodlust = None

    Cooldowns = None


    @classmethod
    def register(cls):
        """Map from spell id to spellbook index and stores the result in a global with the spell's name."""
        num_spells = wowsims.getSpellCount()
        spells = array.array('I', [0] * num_spells)
        spells_ptr = (ctypes.c_int * len(spells)).from_buffer(spells)
        wowsims.getSpells(spells_ptr, len(spells))
        for i, spell in enumerate(spells):
            if spell == 23881 and cls.Bloodthirst is None: cls.Bloodthirst = i
            elif spell == 1680 and cls.Whirlwind is None: cls.Whirlwind = i
            elif spell == 47475 and cls.Slam is None: cls.Slam = i
            elif spell == 47450 and cls.HeroicStrike is None: cls.HeroicStrike = i
            elif spell == 47471 and cls.Execute is None: cls.Execute = i
            # elif spell == 47465 and cls.Rend is None: cls.Rend = i
            # elif spell == 7384 and cls.Overpower is None: cls.Overpower = i
            # elif spell == 2457 and cls.BattleStance is None: cls.BattleStance = i
            # elif spell == 2458 and cls.BerserkerStance is None: cls.BerserkerStance = i
            elif spell == 12292 and cls.DeathWish is None: cls.DeathWish = i
            elif spell == 1719 and cls.Recklessness is None: cls.Recklessness = i
            elif spell == 64382 and cls.ShatteringThrow is None: cls.ShatteringThrow = i
            elif spell == 54758 and cls.EngiGlove is None: cls.EngiGlove = i
            elif spell == 2825 and cls.Bloodlust is None: cls.Bloodlust = i
            elif spell == 2687 and cls.Bloodrage is None: cls.Bloodrage = i
        cls.Cooldowns = np.array([0.0] * len(cls.registered_actions()))
    
    @classmethod
    def registered_actions(cls):
        actions = [
            cls.Bloodthirst, 
            cls.Whirlwind,
            cls.Slam,
            cls.HeroicStrike,
            cls.Execute,
            # cls.Rend,
            # cls.Overpower,
            # cls.BattleStance,
            # cls.BerserkerStance,
            cls.DeathWish,
            cls.Recklessness,
            cls.ShatteringThrow,
            cls.Bloodrage,
            cls.EngiGlove,
            cls.Bloodlust,
            ] 
        return [action for action in actions if action is not None]
    
    @classmethod
    def update(cls):
        actions = np.array(cls.registered_actions(), dtype=np.int32)
        cds_ptr = (ctypes.c_double * len(actions)).from_buffer(cls.Cooldowns)
        actions_ptr = (ctypes.c_int * len(actions)).from_buffer(actions)
        wowsims.getCooldowns(cds_ptr, actions_ptr, len(actions))

class Auras():
    Labels = ["Bloodsurge Proc", "Recklessness", "Death Wish", "Overpower Aura", "HS Queue Aura", "Hyperspeed Acceleration", "Bloodlust"]
    Durations = array.array('d', [0.0] * len(Labels))

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
    Labels = ["Rend", "Shattering Throw"]
    Durations = array.array('d', [0.0] * len(Labels))

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

class AutoAttacks():
    MeleeSwingTime = array.array('d', [0.0] * 2)

    @classmethod
    def get_swing_time(cls):
        ptr = (ctypes.c_double * len(cls.MeleeSwingTime)).from_buffer(cls.MeleeSwingTime)
        wowsims.getMeleeSwingTime(ptr)
        return cls.MeleeSwingTime