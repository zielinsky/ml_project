from enum import Enum


class Champion(Enum):
    ANNIE = 1
    OLAF = 2
    GALIO = 3
    TWISTED_FATE = 4
    XIN_ZHAO = 5
    URGOT = 6
    LEBLANC = 7
    VLADIMIR = 8
    FIDDLESTICKS = 9
    KAYLE = 10
    MASTER_YI = 11
    ALISTAR = 12
    RYZE = 13
    SION = 14
    SIVIR = 15
    SORAKA = 16
    TEEMO = 17
    TRISTANA = 18
    WARWICK = 19
    NUNU_AND_WILLUMP = 20
    MISS_FORTUNE = 21
    ASHE = 22
    TRYNDAMERE = 23
    JAX = 24
    MORGANA = 25
    ZILEAN = 26
    SINGED = 27
    EVELYNN = 28
    TWITCH = 29
    KARTHUS = 30
    CHOGATH = 31
    AMUMU = 32
    RAMMUS = 33
    ANIVIA = 34
    SHACO = 35
    DR_MUNDO = 36
    SONA = 37
    KASSADIN = 38
    IRELIA = 39
    JANNA = 40
    GANGPLANK = 41
    CORKI = 42
    KARMA = 43
    TARIC = 44
    VEIGAR = 45
    TRUNDLE = 48
    SWAIN = 50
    CAITLYN = 51
    BLITZCRANK = 53
    MALPHITE = 54
    KATARINA = 55
    NOCTURNE = 56
    MAOKAI = 57
    RENEKTON = 58
    JARVAN_IV = 59
    ELISE = 60
    ORIANNA = 61
    WUKONG = 62
    BRAND = 63
    LEE_SIN = 64
    VAYNE = 67
    RUMBLE = 68
    CASSIOPEIA = 69
    SKARNER = 72
    HEIMERDINGER = 74
    NASUS = 75
    NIDALEE = 76
    UDYR = 77
    POPPY = 78
    GRAGAS = 79
    PANTHEON = 80
    EZREAL = 81
    MORDEKAISER = 82
    YORICK = 83
    AKALI = 84
    KENNEN = 85
    GAREN = 86
    LEONA = 89
    MALZAHAR = 90
    TALON = 91
    RIVEN = 92
    KOGMAW = 96
    SHEN = 98
    LUX = 99
    XERATH = 101
    SHYVANA = 102
    AHRI = 103
    GRAVES = 104
    FIZZ = 105
    VOLIBEAR = 106
    RENGAR = 107
    VARUS = 110
    NAUTILUS = 111
    VIKTOR = 112
    SEJUANI = 113
    FIORA = 114
    ZIGGS = 115
    LULU = 117
    DRAVEN = 119
    HECARIM = 120
    KHAZIX = 121
    DARIUS = 122
    JAYCE = 126
    LISSANDRA = 127
    DIANA = 131
    QUINN = 133
    SYNDRA = 134
    AURELION_SOL = 136
    KAYN = 141
    ZOE = 142
    ZYRA = 143
    KAISA = 145
    SERAPHINE = 147
    GNAR = 150
    ZAC = 154
    YASUO = 157
    VELKOZ = 161
    TALIYAH = 163
    AKSHAN = 166
    CAMILLE = 164
    BRAUM = 201
    JHIN = 202
    KINDRED = 203
    JINX = 222
    TAHM_KENCH = 223
    VIEGO = 234
    SENNA = 235
    LUCIAN = 236
    ZED = 238
    KLED = 240
    EKKO = 245
    QIYANA = 246
    VI = 254
    AATROX = 266
    NAMI = 267
    AZIR = 268
    YUUMI = 350
    SAMIRA = 360
    THRESH = 412
    ILLAOI = 420
    REKSAI = 421
    IVERN = 427
    KALISTA = 429
    BARD = 432
    RAKAN = 497
    XAYAH = 498
    ORNN = 516
    SYLAS = 517
    RELL = 526
    NEEKO = 518
    APHELIOS = 523
    PYKE = 555
    SETT = 875
    VEX = 711
    YONE = 777
    GWEN = 887
    LILLIA = 876
    HWEI = 910
    BRIAR = 233
    NAAFIRI = 950
    MILIO = 902
    KSANTE = 421
    NILAH = 895
    BELVETH = 200
    RENATAGLASC = 888
    ZERI = 221


champion_name_to_enum = {
    "annie": Champion.ANNIE,
    "olaf": Champion.OLAF,
    "galio": Champion.GALIO,
    "twistedfate": Champion.TWISTED_FATE,
    "xinzhao": Champion.XIN_ZHAO,
    "urgot": Champion.URGOT,
    "leblanc": Champion.LEBLANC,
    "vladimir": Champion.VLADIMIR,
    "fiddlesticks": Champion.FIDDLESTICKS,
    "kayle": Champion.KAYLE,
    "masteryi": Champion.MASTER_YI,
    "alistar": Champion.ALISTAR,
    "ryze": Champion.RYZE,
    "sion": Champion.SION,
    "sivir": Champion.SIVIR,
    "soraka": Champion.SORAKA,
    "teemo": Champion.TEEMO,
    "tristana": Champion.TRISTANA,
    "warwick": Champion.WARWICK,
    "nunuandwillump": Champion.NUNU_AND_WILLUMP,
    "nunu": Champion.NUNU_AND_WILLUMP,
    "missfortune": Champion.MISS_FORTUNE,
    "ashe": Champion.ASHE,
    "tryndamere": Champion.TRYNDAMERE,
    "jax": Champion.JAX,
    "morgana": Champion.MORGANA,
    "zilean": Champion.ZILEAN,
    "singed": Champion.SINGED,
    "evelynn": Champion.EVELYNN,
    "twitch": Champion.TWITCH,
    "karthus": Champion.KARTHUS,
    "chogath": Champion.CHOGATH,
    "amumu": Champion.AMUMU,
    "rammus": Champion.RAMMUS,
    "anivia": Champion.ANIVIA,
    "shaco": Champion.SHACO,
    "drmundo": Champion.DR_MUNDO,
    "sona": Champion.SONA,
    "kassadin": Champion.KASSADIN,
    "irelia": Champion.IRELIA,
    "janna": Champion.JANNA,
    "gangplank": Champion.GANGPLANK,
    "corki": Champion.CORKI,
    "karma": Champion.KARMA,
    "taric": Champion.TARIC,
    "veigar": Champion.VEIGAR,
    "trundle": Champion.TRUNDLE,
    "swain": Champion.SWAIN,
    "caitlyn": Champion.CAITLYN,
    "blitzcrank": Champion.BLITZCRANK,
    "malphite": Champion.MALPHITE,
    "katarina": Champion.KATARINA,
    "nocturne": Champion.NOCTURNE,
    "maokai": Champion.MAOKAI,
    "renekton": Champion.RENEKTON,
    "jarvaniv": Champion.JARVAN_IV,
    "elise": Champion.ELISE,
    "orianna": Champion.ORIANNA,
    "wukong": Champion.WUKONG,
    "brand": Champion.BRAND,
    "leesin": Champion.LEE_SIN,
    "vayne": Champion.VAYNE,
    "rumble": Champion.RUMBLE,
    "cassiopeia": Champion.CASSIOPEIA,
    "skarner": Champion.SKARNER,
    "heimerdinger": Champion.HEIMERDINGER,
    "nasus": Champion.NASUS,
    "nidalee": Champion.NIDALEE,
    "udyr": Champion.UDYR,
    "poppy": Champion.POPPY,
    "gragas": Champion.GRAGAS,
    "pantheon": Champion.PANTHEON,
    "ezreal": Champion.EZREAL,
    "mordekaiser": Champion.MORDEKAISER,
    "yorick": Champion.YORICK,
    "akali": Champion.AKALI,
    "kennen": Champion.KENNEN,
    "garen": Champion.GAREN,
    "leona": Champion.LEONA,
    "malzahar": Champion.MALZAHAR,
    "talon": Champion.TALON,
    "riven": Champion.RIVEN,
    "kogmaw": Champion.KOGMAW,
    "shen": Champion.SHEN,
    "lux": Champion.LUX,
    "xerath": Champion.XERATH,
    "shyvana": Champion.SHYVANA,
    "ahri": Champion.AHRI,
    "graves": Champion.GRAVES,
    "fizz": Champion.FIZZ,
    "volibear": Champion.VOLIBEAR,
    "rengar": Champion.RENGAR,
    "varus": Champion.VARUS,
    "nautilus": Champion.NAUTILUS,
    "viktor": Champion.VIKTOR,
    "sejuani": Champion.SEJUANI,
    "fiora": Champion.FIORA,
    "ziggs": Champion.ZIGGS,
    "lulu": Champion.LULU,
    "draven": Champion.DRAVEN,
    "hecarim": Champion.HECARIM,
    "khazix": Champion.KHAZIX,
    "darius": Champion.DARIUS,
    "jayce": Champion.JAYCE,
    "lissandra": Champion.LISSANDRA,
    "diana": Champion.DIANA,
    "quinn": Champion.QUINN,
    "syndra": Champion.SYNDRA,
    "aurelionsol": Champion.AURELION_SOL,
    "kayn": Champion.KAYN,
    "zoe": Champion.ZOE,
    "zyra": Champion.ZYRA,
    "kaisa": Champion.KAISA,
    "seraphine": Champion.SERAPHINE,
    "gnar": Champion.GNAR,
    "zac": Champion.ZAC,
    "yasuo": Champion.YASUO,
    "velkoz": Champion.VELKOZ,
    "taliyah": Champion.TALIYAH,
    "akshan": Champion.AKSHAN,
    "camille": Champion.CAMILLE,
    "braum": Champion.BRAUM,
    "jhin": Champion.JHIN,
    "kindred": Champion.KINDRED,
    "jinx": Champion.JINX,
    "tahmkench": Champion.TAHM_KENCH,
    "viego": Champion.VIEGO,
    "senna": Champion.SENNA,
    "lucian": Champion.LUCIAN,
    "zed": Champion.ZED,
    "kled": Champion.KLED,
    "ekko": Champion.EKKO,
    "qiyana": Champion.QIYANA,
    "vi": Champion.VI,
    "aatrox": Champion.AATROX,
    "nami": Champion.NAMI,
    "azir": Champion.AZIR,
    "yuumi": Champion.YUUMI,
    "samira": Champion.SAMIRA,
    "thresh": Champion.THRESH,
    "illaoi": Champion.ILLAOI,
    "reksai": Champion.REKSAI,
    "ivern": Champion.IVERN,
    "kalista": Champion.KALISTA,
    "bard": Champion.BARD,
    "rakan": Champion.RAKAN,
    "xayah": Champion.XAYAH,
    "ornn": Champion.ORNN,
    "sylas": Champion.SYLAS,
    "rell": Champion.RELL,
    "neeko": Champion.NEEKO,
    "aphelios": Champion.APHELIOS,
    "pyke": Champion.PYKE,
    "sett": Champion.SETT,
    "vex": Champion.VEX,
    "yone": Champion.YONE,
    "gwen": Champion.GWEN,
    "lillia": Champion.LILLIA,
    "hwei": Champion.HWEI,
    "briar": Champion.BRIAR,
    "naafiri": Champion.NAAFIRI,
    "milio": Champion.MILIO,
    "ksante": Champion.KSANTE,
    "nilah": Champion.NILAH,
    "belveth": Champion.BELVETH,
    "renataglasc": Champion.RENATAGLASC,
    "renata": Champion.RENATAGLASC,
    "zeri": Champion.ZERI,
}

champion_enum_to_name = {value: key for key, value in champion_name_to_enum.items()}
