"""
Breadup — 100 Music Gear SKUs for initial collection.

Manually curated. Each has:
- canonical_id
- search_query (for eBay)
- category
- brand
- expected_price_range (rough)
"""

MUSIC_GEAR_SKUS = [
    # Synthesizers (20)
    {"id": "ROLAND_SP404_MKII", "query": "Roland SP-404 MK2 sampler", "category": "sampler", "brand": "Roland", "price_range": (150, 350)},
    {"id": "KORG_MINILOGUE", "query": "Korg Minilogue synth", "category": "synthesizer", "brand": "Korg", "price_range": (200, 400)},
    {"id": "KORG_MINILOGUE_XD", "query": "Korg Minilogue XD", "category": "synthesizer", "brand": "Korg", "price_range": (350, 600)},
    {"id": "YAMAHA_REFACE_CS", "query": "Yamaha Reface CS synth", "category": "synthesizer", "brand": "Yamaha", "price_range": (150, 300)},
    {"id": "ARTURIA_MINIBRUTE_2S", "query": "Arturia MiniBrute 2S", "category": "synthesizer", "brand": "Arturia", "price_range": (300, 500)},
    {"id": "ROLAND_JUNO_DS61", "query": "Roland Juno-DS 61", "category": "synthesizer", "brand": "Roland", "price_range": (250, 450)},
    {"id": "NOVATION_LAUNCHKEY_49", "query": "Novation Launchkey 49 MK3", "category": "midi_controller", "brand": "Novation", "price_range": (100, 200)},
    {"id": "AKAI_MPK_MINI", "query": "Akai MPK Mini MK3", "category": "midi_controller", "brand": "Akai", "price_range": (50, 100)},
    {"id": "SYNTHESIA_BETTER", "query": "Teenage Engineering OP-1", "category": "synthesizer", "brand": "Teenage Engineering", "price_range": (800, 1500)},
    {"id": "MOOG_SUB37", "query": "Moog Sub 37 synth", "category": "synthesizer", "brand": "Moog", "price_range": (800, 1400)},
    {"id": "SEQUENTIAL_PRO3", "query": "Sequential Pro 3 synth", "category": "synthesizer", "brand": "Sequential", "price_range": (1200, 2000)},
    {"id": "NORD_LEAD_A1", "query": "Nord Lead A1 synth", "category": "synthesizer", "brand": "Nord", "price_range": (800, 1500)},
    {"id": "ASM_HYDRASYNTH", "query": "ASM Hydrasynth synth", "category": "synthesizer", "brand": "ASM", "price_range": (500, 800)},
    {"id": "KORG_PROLOGUE8", "query": "Korg Prologue 8 synth", "category": "synthesizer", "brand": "Korg", "price_range": (400, 700)},
    {"id": "YAMAHA_MODX6", "query": "Yamaha MODX6 synth", "category": "synthesizer", "brand": "Yamaha", "price_range": (400, 700)},
    {"id": "ROLAND_FANTOM_06", "query": "Roland Fantom-06 synth", "category": "synthesizer", "brand": "Roland", "price_range": (800, 1400)},
    {"id": "DREADBOX_NYX", "query": "Dreadbox Nyx synth", "category": "synthesizer", "brand": "Dreadbox", "price_range": (300, 500)},
    {"id": "BEHRINGER_PRO_800", "query": "Behringer Pro-800 synth", "category": "synthesizer", "brand": "Behringer", "price_range": (200, 350)},
    {"id": "IK_MULTIMEDIA_SYNTH_2", "query": "IK Multimedia Uno Synth Pro", "category": "synthesizer", "brand": "IK Multimedia", "price_range": (150, 300)},
    {"id": "WALDORF_BLOFELD", "query": "Waldorf Blofeld synth", "category": "synthesizer", "brand": "Waldorf", "price_range": (250, 450)},

    # Guitar Pedals (20)
    {"id": "BOSS_DS1", "query": "Boss DS-1 distortion pedal", "category": "pedal", "brand": "Boss", "price_range": (30, 60)},
    {"id": "BOSS_SD1", "query": "Boss SD-1 super overdrive", "category": "pedal", "brand": "Boss", "price_range": (30, 60)},
    {"id": "BOSS_RC505", "query": "Boss RC-505 loop station", "category": "pedal", "brand": "Boss", "price_range": (250, 400)},
    {"id": "TC_ELECTRONIC_FLASHBACK2", "query": "TC Electronic Flashback 2 delay", "category": "pedal", "brand": "TC Electronic", "price_range": (80, 150)},
    {"id": "MXR_PHASE90", "query": "MXR Phase 90 phaser", "category": "pedal", "brand": "MXR", "price_range": (50, 90)},
    {"id": "JHS_MOONSHINE", "query": "JHS Moonshine overdrive", "category": "pedal", "brand": "JHS", "price_range": (100, 180)},
    {"id": "ELECTRO_HARMONIX_POG2", "query": "Electro-Harmonix POG2", "category": "pedal", "brand": "Electro-Harmonix", "price_range": (150, 250)},
    {"id": "STRYMON_BLUE_SKY", "query": "Strymon BlueSky reverb", "category": "pedal", "brand": "Strymon", "price_range": (200, 350)},
    {"id": "STRYMON_TIMELINE", "query": "Strymon Timeline delay", "category": "pedal", "brand": "Strymon", "price_range": (350, 550)},
    {"id": "WAHR_PEDAL_V847", "query": "Dunlop Cry Baby wah", "category": "pedal", "brand": "Dunlop", "price_range": (50, 100)},
    {"id": "FULLTONE_OCD", "query": "Fulltone OCD overdrive", "category": "pedal", "brand": "Fulltone", "price_range": (80, 150)},
    {"id": "KORG_TREMOLO", "query": "Korg Tremolo pedal", "category": "pedal", "brand": "Korg", "price_range": (40, 80)},
    {"id": "EMPRESS_REVERB", "query": "Empress Reverb pedal", "category": "pedal", "brand": "Empress", "price_range": (250, 400)},
    {"id": "MERIS_ENZO", "query": "Meris Enzo synth pedal", "category": "pedal", "brand": "Meris", "price_range": (200, 350)},
    {"id": "CHASE_BLISS_MOOD", "query": "Chase Bliss MOOD pedal", "category": "pedal", "brand": "Chase Bliss", "price_range": (300, 500)},
    {"id": "CBA_THERMAE", "query": "Chase Bliss Thermae delay", "category": "pedal", "brand": "Chase Bliss", "price_range": (350, 550)},
    {"id": "BOSS_DM2W", "query": "Boss DM-2W delay", "category": "pedal", "brand": "Boss", "price_range": (80, 150)},
    {"id": "EVENTIDE_H9_MAX", "query": "Eventide H9 Max effects", "category": "pedal", "brand": "Eventide", "price_range": (350, 550)},
    {"id": "MOOG_MINIMOOG_MODEL_D", "query": "Moog MF-101 filter", "category": "pedal", "brand": "Moog", "price_range": (150, 250)},
    {"id": "SOURCE_AUDIO_VERTEX", "query": "Source Audio Ventris reverb", "category": "pedal", "brand": "Source Audio", "price_range": (200, 350)},

    # Turntables (20)
    {"id": "TECHNICS_SL1200_MK2", "query": "Technics SL-1200 MK2 turntable", "category": "turntable", "brand": "Technics", "price_range": (200, 500)},
    {"id": "TECHNICS_SL1200_MK5", "query": "Technics SL-1200 MK5 turntable", "category": "turntable", "brand": "Technics", "price_range": (300, 600)},
    {"id": "TECHNICS_SL1500C", "query": "Technics SL-1500C turntable", "category": "turntable", "brand": "Technics", "price_range": (500, 900)},
    {"id": "REGA_PLANAR_3", "query": "Rega Planar 3 turntable", "category": "turntable", "brand": "Rega", "price_range": (400, 700)},
    {"id": "PRO_JECT_DEBUT_CARBON", "query": "Pro-Ject Debut Carbon turntable", "category": "turntable", "brand": "Pro-Ject", "price_range": (200, 400)},
    {"id": "AUDIO_TECHNICA_LP120", "query": "Audio-Technica AT-LP120 turntable", "category": "turntable", "brand": "Audio-Technica", "price_range": (150, 300)},
    {"id": "PIONEER_PLX1000", "query": "Pioneer PLX-1000 turntable", "category": "turntable", "brand": "Pioneer", "price_range": (400, 700)},
    {"id": "DENON_DP3000F", "query": "Denon DP-3000F turntable", "category": "turntable", "brand": "Denon", "price_range": (200, 400)},
    {"id": "CROSS_1200", "query": "Stanton STR8-150 turntable", "category": "turntable", "brand": "Stanton", "price_range": (150, 300)},
    {"id": "ORTOPHONE_2M_BLUE", "query": "Ortofon 2M Blue cartridge", "category": "cartridge", "brand": "Ortofon", "price_range": (80, 150)},
    {"id": "SHURE_M97XE", "query": "Shure M97xE cartridge", "category": "cartridge", "brand": "Shure", "price_range": (60, 120)},
    {"id": "AUDIO_TECHNICA_VM540ML", "query": "Audio-Technica VM540ML cartridge", "category": "cartridge", "brand": "Audio-Technica", "price_range": (80, 150)},
    {"id": "CLEARAUDIO_CONCEPT", "query": "Clearaudio Concept turntable", "category": "turntable", "brand": "Clearaudio", "price_range": (300, 600)},
    {"id": "THORENS_TD160", "query": "Thorens TD-160 turntable", "category": "turntable", "brand": "Thorens", "price_range": (300, 600)},
    {"id": "LUSICANT_LP12", "query": "Linn Sondek LP12 turntable", "category": "turntable", "brand": "Linn", "price_range": (500, 1500)},
    {"id": "AR_TT2", "query": "Audio Research TT2 turntable", "category": "turntable", "brand": "Audio Research", "price_range": (1500, 3000)},
    {"id": "VPI_PRIME", "query": "VPI Prime turntable", "category": "turntable", "brand": "VPI", "price_range": (1000, 2000)},
    {"id": "REGA_PLANAR_6", "query": "Rega Planar 6 turntable", "category": "turntable", "brand": "Rega", "price_range": (700, 1200)},
    {"id": "PRO_JECT_XP2", "query": "Pro-Ject Xtension 10 turntable", "category": "turntable", "brand": "Pro-Ject", "price_range": (800, 1500)},
    {"id": "CREEK_OBSESSION", "query": "Creek OBi-21SE turntable", "category": "turntable", "brand": "Creek", "price_range": (200, 400)},

    # Amplifiers (20)
    {"id": "FENDER_BLUES_JR", "query": "Fender Blues Junior amplifier", "category": "amplifier", "brand": "Fender", "price_range": (300, 550)},
    {"id": "FENDER_TWIN_REVERB", "query": "Fender Twin Reverb amplifier", "category": "amplifier", "brand": "Fender", "price_range": (600, 1200)},
    {"id": "MARSHALL_JCM800", "query": "Marshall JCM800 amp", "category": "amplifier", "brand": "Marshall", "price_range": (800, 1500)},
    {"id": "MARSHALL_MS2Z", "query": "Marshall MS2 micro amp", "category": "amplifier", "brand": "Marshall", "price_range": (30, 60)},
    {"id": "VOX_AC30", "query": "Vox AC30 amplifier", "category": "amplifier", "brand": "Vox", "price_range": (500, 1000)},
    {"id": "MESABOOGIE_MARK5", "query": "Mesa Boogie Mark Five amplifier", "category": "amplifier", "brand": "Mesa Boogie", "price_range": (1500, 2500)},
    {"id": "BLACKSTAR_HT1", "query": "Blackstar HT-1 amplifier", "category": "amplifier", "brand": "Blackstar", "price_range": (80, 150)},
    {"id": "ORANGE_CR120", "query": "Orange CR120 amplifier", "category": "amplifier", "brand": "Orange", "price_range": (200, 350)},
    {"id": "ROLAND_CUBE_10GX", "query": "Roland Cube 10GX amplifier", "category": "amplifier", "brand": "Roland", "price_range": (80, 150)},
    {"id": "YAMAHA THR10II", "query": "Yamaha THR10II amplifier", "category": "amplifier", "brand": "Yamaha", "price_range": (150, 280)},
    {"id": "SUNN_MODEL_T", "query": "Sunn Model T amplifier", "category": "amplifier", "brand": "Sunn", "price_range": (1500, 3000)},
    {"id": "FENDER_PLAYER_STUDIO", "query": "Fender Bassman 500 amp", "category": "amplifier", "brand": "Fender", "price_range": (400, 700)},
    {"id": "AMPEG_SVT4PRO", "query": "Ampeg SVT-4PRO bass amp", "category": "amplifier", "brand": "Ampeg", "price_range": (500, 900)},
    {"id": "MARKBASS_CMD102P", "query": "Markbass CMD 102P amp", "category": "amplifier", "brand": "Markbass", "price_range": (300, 550)},
    {"id": "HIWATT_DR504", "query": "Hiwatt DR504 amplifier", "category": "amplifier", "brand": "Hiwatt", "price_range": (800, 1500)},
    {"id": "FRIEDMAN_BE100", "query": "Friedman BE-100 amplifier", "category": "amplifier", "brand": "Friedman", "price_range": (1500, 2500)},
    {"id": "DR_Z_MAZ18", "query": "Dr Z Maz 18 amplifier", "category": "amplifier", "brand": "Dr Z", "price_range": (800, 1400)},
    {"id": "THD_UNICOMP", "query": "THD Univalve amplifier", "category": "amplifier", "brand": "THD", "price_range": (800, 1500)},
    {"id": "AXIS_AMPS_SAT", "query": "Two-Rock Studio Pro amplifier", "category": "amplifier", "brand": "Two-Rock", "price_range": (1000, 2000)},
    {"id": "ENGL_FIREBALL", "query": "ENGL Fireball amplifier", "category": "amplifier", "brand": "ENGL", "price_range": (600, 1000)},

    # Audio Interfaces (20)
    {"id": "FOCUSRITE_2I2_4GEN", "query": "Focusrite Scarlett 2i2 4th gen interface", "category": "interface", "brand": "Focusrite", "price_range": (80, 150)},
    {"id": "FOCUSRITE_4I4_4GEN", "query": "Focusrite Scarlett 4i4 4th gen interface", "category": "interface", "brand": "Focusrite", "price_range": (150, 250)},
    {"id": "UNIVERSAL_AUDIO_APOLLO_TWIN", "query": "Universal Audio Apollo Twin interface", "category": "interface", "brand": "Universal Audio", "price_range": (500, 900)},
    {"id": "RME_BABYFACE_PRO", "query": "RME Babyface Pro interface", "category": "interface", "brand": "RME", "price_range": (500, 800)},
    {"id": "MOTU_M4", "query": "MOTU M4 audio interface", "category": "interface", "brand": "MOTU", "price_range": (200, 350)},
    {"id": "PRESONUS_AUDIOBOX_USB96", "query": "PreSonus AudioBox USB 96", "category": "interface", "brand": "PreSonus", "price_range": (50, 100)},
    {"id": "STEINBERG_UR22C", "query": "Steinberg UR22C interface", "category": "interface", "brand": "Steinberg", "price_range": (100, 180)},
    {"id": "BEHRINGER_UMC202HD", "query": "Behringer UMC202HD interface", "category": "interface", "brand": "Behringer", "price_range": (50, 100)},
    {"id": "APOLLO_X4", "query": "Universal Audio Apollo x4 interface", "category": "interface", "brand": "Universal Audio", "price_range": (800, 1400)},
    {"id": "APOLLO_X8P", "query": "Universal Audio Apollo x8p interface", "category": "interface", "brand": "Universal Audio", "price_range": (2000, 3500)},
    {"id": "RME_FIREFACE_UCX2", "query": "RME Fireface UCX II interface", "category": "interface", "brand": "RME", "price_range": (800, 1400)},
    {"id": "MOTU_828ES", "query": "MOTU 828es interface", "category": "interface", "brand": "MOTU", "price_range": (500, 800)},
    {"id": "FOCUSRITE_CLARETTO_4PRE", "query": "Focusrite Clarett+ 4Pre interface", "category": "interface", "brand": "Focusrite", "price_range": (300, 500)},
    {"id": "ANTARIS_SOLO", "query": "Audient iD14 MKII interface", "category": "interface", "brand": "Audient", "price_range": (150, 250)},
    {"id": "Native_Instruments_Complete_Audio_2", "query": "Native Instruments Complete Audio 2", "category": "interface", "brand": "Native Instruments", "price_range": (80, 150)},
    {"id": "Presonus_Studio_1810c", "query": "PreSonus Studio 1810c interface", "category": "interface", "brand": "PreSonus", "price_range": (200, 350)},
    {"id": "MOTU_ultralite_mk5", "query": "MOTU UltraLite mk5 interface", "category": "interface", "brand": "MOTU", "price_range": (350, 550)},
    {"id": "Roland_Rubix44", "query": "Roland Rubix44 interface", "category": "interface", "brand": "Roland", "price_range": (150, 250)},
    {"id": "Zoom_F4", "query": "Zoom F4 field recorder", "category": "interface", "brand": "Zoom", "price_range": (250, 400)},
    {"id": "Sound_Devices_MixPre3", "query": "Sound Devices MixPre-3 recorder", "category": "interface", "brand": "Sound Devices", "price_range": (300, 500)},
]


def get_sku_list():
    """Return the full SKU list."""
    return MUSIC_GEAR_SKUS


def get_search_queries():
    """Return all eBay search queries."""
    return [sku['query'] for sku in MUSIC_GEAR_SKUS]


def get_categories():
    """Return unique categories."""
    return list(set(sku['category'] for sku in MUSIC_GEAR_SKUS))


if __name__ == '__main__':
    skus = get_sku_list()
    print(f"Total SKUs: {len(skus)}")
    print(f"Categories: {get_categories()}")
    print(f"\nFirst 5 queries:")
    for q in get_search_queries()[:5]:
        print(f"  - {q}")
