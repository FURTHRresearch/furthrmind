
def getUnitCategory():

    length = ["cm","mm","m","km","um","nm","pm","fm","Ang","in","ft","mi"]
    volume = ["L","mL","nL","uL","pL","fL","kL","ML","GL"]
    time = ["s","ms","us","ns","min","h","day","week","year"]
    frequency = ["Hz","mHz","kHz","MHz","GHz"]
    mass = ["kg","g","mg","ug","ng","pg","fg","t","amu","Da","kDa","lbm"]
    energy = ["J","mJ","uJ","nJ","pJ","fJ","MJ","GJ","eV","keV","meV","MeV","GeV","TeV","cal","kcal","Wh","kWh"]
    concentration = ["M","mM","uM","pM","nM","fM"]
    molar = ["mol","mmol","umol","pmol","nmol","fmol"]
    force = ["N", "mN", "uN", "nN", "pN", "fN", "kN", "MN", "GN", "lbf"]
    pressure = ["Pa", "hPa", "kPa", "MPa", "GPa", "bar", "mbar", "kbar", "Mbar", "atm", "torr", "mtorr", "psi"]
    power = ["W", "mW", "uW", "nW", "pW", "nW", "kW", "MW", "GW", "TW"]
    temperature = ["K", "°C"]
    charge = ["C", "mC", "uC", "nC", "Ah", "mAh"]
    current = ["A", "mA", "uA", "nA", "pA", "fA"]
    voltage = ["V", "mV", "kV", "MV", "GV", "TV"]
    resistence = ["ohm", "mohm", "kohm", "Mohm", "Gohm"]
    conductivity = ["S", "mS", "uS", "nS"]
    magnetic = ["T","mT","uT","nT","G","mG","uG"]
    capacity = ["F","uF","nF","pF","fF","H","mH","uH","nH"]

    return{
        "length":length,
        "volume":volume,
        "time":time,
        "frequency":frequency,
        "mass":mass,
        "energy":energy,
        "concentration":concentration,
        "molar":molar,
        "force":force,
        "pressure":pressure,
        "power":power,
        "temperature":temperature,
        "charge":charge,
        "current":current,
        "voltage":voltage,
        "resistence":resistence,
        "magnetic":magnetic,
        "capacity":capacity,
        "conductivity":conductivity
    }


def getUnitList():
    # Unit
    # Length

    unitList = [
        {"ShortName": "cm",
        "LongName": "centimeter",
        "Definition": "cm"},
    {"ShortName": "mm",
        "LongName": "millimeter",
        "Definition": "mm"},
    {"ShortName": "m",
        "LongName": "meter",
        "Definition": "m"},
    {"ShortName": "km",
        "LongName": "kilometer",
        "Definition": "km"},
    {"ShortName": "um",
        "LongName": "micrometer",
        "Definition": "um"},
    {"ShortName": "nm",
        "LongName": "nanometer",
        "Definition": "nm"},
    {"ShortName": "pm",
        "LongName": "picometer",
        "Definition": "pm"},
    {"ShortName": "fm",
        "LongName": "femtometer",
        "Definition": "fm"},
    {"ShortName": "Ang",
        "LongName": "angstrom",
        "Definition": "angstrom"},
    {"ShortName": "in",
        "LongName": "inch",
        "Definition": "inch"},
    {"ShortName": "ft",
        "LongName": "foot",
        "Definition": "foot"},
    {"ShortName": "mi",
        "LongName": "mile",
        "Definition": "mile"},
        ]

    # Volume
    unitList.append({"ShortName": "L",
                "LongName": "liter",
                "Definition": "L"})

    unitList.append({"ShortName": "mL",
                "LongName": "milliliter",
                "Definition": "mL"})
    unitList.append({"ShortName": "uL",
                "LongName": "microliter",
                "Definition": "uL"})
    unitList.append({"ShortName": "nL",
                "LongName": "nanoliter",
                "Definition": "nL"})
    unitList.append({"ShortName": "pL",
                "LongName": "picoliter",
                "Definition": "pL"})
    unitList.append({"ShortName": "fL",
                "LongName": "femtoliter",
                "Definition": "pL"})


    unitList.append({"ShortName": "kL",
                "LongName": "kiloliter",
                "Definition": "kL"})
    unitList.append({"ShortName": "ML",
                "LongName": "megaliter",
                "Definition": "ML"})
    unitList.append({"ShortName": "GL",
                "LongName": "gigaliter",
                "Definition": "GL"})


    # Time
    unitList.append({"ShortName": "s",
                "LongName": "second",
                "Definition": "s"})
    unitList.append({"ShortName": "ms",
                "LongName": "millisecond",
                "Definition": "ms"})
    unitList.append({"ShortName": "us",
                "LongName": "microsecond",
                "Definition": "us"})
    unitList.append({"ShortName": "ns",
                "LongName": "nanosecond",
                "Definition": "ns"})
    unitList.append({"ShortName": "min",
                "LongName": "minute",
                "Definition": "minute"})
    unitList.append({"ShortName": "h",
                "LongName": "hour",
                "Definition": "hour"})
    unitList.append({"ShortName": "day",
                "LongName": "",
                "Definition": "day"})
    unitList.append({"ShortName": "week",
                "LongName": "",
                "Definition": "s"})
    unitList.append({"ShortName": "year",
                "LongName": "",
                "Definition": "year"})


    # Frequency
    unitList.append({"ShortName": "Hz",
                "LongName": "hertz",
                "Definition": "Hz"})
    unitList.append({"ShortName": "mHz",
                "LongName": "millihertz",
                "Definition": "mHz"})
    unitList.append({"ShortName": "kHz",
                "LongName": "kilohertz",
                "Definition": "kHz"})
    unitList.append({"ShortName": "MHz",
                "LongName": "megahertz",
                "Definition": "MHz"})
    unitList.append({"ShortName": "GHz",
                "LongName": "gigahertz",
                "Definition": "hour"})

    # Mass
    unitList.append({"ShortName": "kg",
                "LongName": "kilogram",
                "Definition": "kg"})
    unitList.append({"ShortName": "g",
                "LongName": "gram",
                "Definition": "g"})
    unitList.append({"ShortName": "mg",
                "LongName": "milligram",
                "Definition": "mg"})
    unitList.append({"ShortName": "ug",
                "LongName": "microgram",
                "Definition": "ug"})
    unitList.append({"ShortName": "ng",
                "LongName": "nanogram",
                "Definition": "ng"})
    unitList.append({"ShortName": "pg",
                "LongName": "picogram",
                "Definition": "pg"})
    unitList.append({"ShortName": "fg",
                "LongName": "femtogram",
                "Definition": "fg"})
    unitList.append({"ShortName": "t",
                "LongName": "ton",
                "Definition": "tonne"})
    unitList.append({"ShortName": "amu",
                "LongName": "atmic mass unit",
                "Definition": "amu"})
    unitList.append({"ShortName": "Da",
                "LongName": "dalton",
                "Definition": "Da"})
    unitList.append({"ShortName": "kDa",
                "LongName": "kilodalton",
                "Definition": "kDa"})
    unitList.append({"ShortName": "lbm",
                "LongName": "pound",
                "Definition": "lbm"})

    # Energy

    unitList.append({"ShortName": "J",
                "LongName": "joule",
                "Definition": "J"})
    unitList.append({"ShortName": "mJ",
                "LongName": "millijoule",
                "Definition": "mJ"})
    unitList.append({"ShortName": "uJ",
                "LongName": "micorjoule",
                "Definition": "uJ"})
    unitList.append({"ShortName": "nJ",
                "LongName": "nanojoule",
                "Definition": "nJ"})
    unitList.append({"ShortName": "pJ",
                "LongName": "picojoule",
                "Definition": "pJ"})
    unitList.append({"ShortName": "fJ",
                "LongName": "femtojoule",
                "Definition": "fJ"})
    unitList.append({"ShortName": "kJ",
                "LongName": "kilojoule",
                "Definition": "kJ"})
    unitList.append({"ShortName": "MJ",
                "LongName": "megajoule",
                "Definition": "MJ"})
    unitList.append({"ShortName": "GJ",
                "LongName": "gigjoule",
                "Definition": "GJ"})
    unitList.append({"ShortName": "eV",
                "LongName": "electron volt",
                "Definition": "eV"})
    unitList.append({"ShortName": "keV",
                "LongName": "kilo electron volt",
                "Definition": "keV"})
    unitList.append({"ShortName": "meV",
                "LongName": "mili electron volt",
                "Definition": "meV"})
    unitList.append({"ShortName": "MeV",
                "LongName": "mega electron volt",
                "Definition": "MeV"})
    unitList.append({"ShortName": "GeV",
                "LongName": "giga electron volt",
                "Definition": "GeV"})
    unitList.append({"ShortName": "TeV",
                "LongName": "terra electron volt",
                "Definition": "TeV"})
    unitList.append({"ShortName": "cal",
                "LongName": "calorie",
                "Definition": "smallcal"})
    unitList.append({"ShortName": "kcal",
                "LongName": "kilocalorie",
                "Definition": "kcal"})
    unitList.append({"ShortName": "Wh",
                "LongName": "watthour",
                "Definition": "Wh"})
    unitList.append({"ShortName": "kWh",
                "LongName": "kilowatt hour",
                "Definition": "kWh"})

    # Moles, concentration / molarity
    unitList.append({"ShortName": "mol",
                "LongName": "mole",
                "Definition": "mol"})
    unitList.append({"ShortName": "mmol",
                "LongName": "millimole",
                "Definition": "mmol"})
    unitList.append({"ShortName": "umol",
                "LongName": "micromole",
                "Definition": "umol"})
    unitList.append({"ShortName": "nmol",
                "LongName": "nanomole",
                "Definition": "nmol"})
    unitList.append({"ShortName": "pmol",
                "LongName": "picomole",
                "Definition": "pmol"})
    unitList.append({"ShortName": "fmol",
                "LongName": "femtomole",
                "Definition": "fmol"})
    unitList.append({"ShortName": "M",
                "LongName": "molar (mol/L)",
                "Definition": "M"})
    unitList.append({"ShortName": "mM",
                "LongName": "millimolar",
                "Definition": "mM"})
    unitList.append({"ShortName": "uM",
                "LongName": "micromolar",
                "Definition": "uM"})
    unitList.append({"ShortName": "nM",
                "LongName": "nanomolar",
                "Definition": "nM"})
    unitList.append({"ShortName": "pM",
                "LongName": "picomolar",
                "Definition": "pM"})
    unitList.append({"ShortName": "fM",
                "LongName": "femtomolar",
                "Definition": "fM"})

    # Force

    unitList.append({"ShortName": "N",
                "LongName": "newton",
                "Definition": "N"})
    unitList.append({"ShortName": "mN",
                "LongName": "millinewton",
                "Definition": "mN"})
    unitList.append({"ShortName": "uN",
                "LongName": "micronewton",
                "Definition": "uN"})
    unitList.append({"ShortName": "nN",
                "LongName": "nanonewton",
                "Definition": "nN"})
    unitList.append({"ShortName": "pN",
                "LongName": "piconewton",
                "Definition": "pN"})
    unitList.append({"ShortName": "fN",
                "LongName": "femtonewton",
                "Definition": "fN"})
    unitList.append({"ShortName": "kN",
                "LongName": "kilonewton",
                "Definition": "kN"})
    unitList.append({"ShortName": "MN",
                "LongName": "meganewton",
                "Definition": "MN"})
    unitList.append({"ShortName": "GN",
                "LongName": "giganewton",
                "Definition": "GN"})
    unitList.append({"ShortName": "lbf",
                "LongName": "pound force",
                "Definition": "lbf"})

    # Pressure
    unitList.append({"ShortName": "Pa",
                "LongName": "pascal",
                "Definition": "Pa"})
    unitList.append({"ShortName": "hPa",
                "LongName": "hectopascal",
                "Definition": "hPa"})
    unitList.append({"ShortName": "kPa",
                "LongName": "kilopascal",
                "Definition": "kPa"})
    unitList.append({"ShortName": "MPa",
                "LongName": "megapascal",
                "Definition": "MPa"})
    unitList.append({"ShortName": "GPa",
                "LongName": "gigapascal",
                "Definition": "GPa"})
    unitList.append({"ShortName": "bar",
                "LongName": "bar",
                "Definition": "bar"})
    unitList.append({"ShortName": "mbar",
                "LongName": "millibar",
                "Definition": "mbar"})
    unitList.append({"ShortName": "kbar",
                "LongName": "kilobar",
                "Definition": "kbar"})
    unitList.append({"ShortName": "Mbar",
                "LongName": "megabar",
                "Definition": "Mbar"})
    unitList.append({"ShortName": "atm",
                "LongName": "atmosphere",
                "Definition": "atm"})
    unitList.append({"ShortName": "torr",
                "LongName": "torr",
                "Definition": "torr"})
    unitList.append({"ShortName": "mtorr",
                "LongName": "millitorr",
                "Definition": "mtorr"})
    unitList.append({"ShortName": "psi",
                "LongName": "pound per square inch",
                "Definition": "psi"})

    # Power

    unitList.append({"ShortName": "W",
                "LongName": "watt",
                "Definition": "W"})
    unitList.append({"ShortName": "mW",
                "LongName": "milliwatt",
                "Definition": "mW"})
    unitList.append({"ShortName": "uW",
                "LongName": "microwatt",
                "Definition": "uW"})
    unitList.append({"ShortName": "nW",
                "LongName": "nanowatt",
                "Definition": "nW"})
    unitList.append({"ShortName": "pW",
                "LongName": "picowatt",
                "Definition": "pW"})
    unitList.append({"ShortName": "kW",
                "LongName": "kilowatt",
                "Definition": "kW"})
    unitList.append({"ShortName": "MW",
                "LongName": "megawatt",
                "Definition": "MW"})
    unitList.append({"ShortName": "GW",
                "LongName": "gigawatt",
                "Definition": "GW"})
    unitList.append({"ShortName": "TW",
                "LongName": "terrawatt",
                "Definition": "TW"})

    # Temperature



    unitList.append({"ShortName": "K",
                "LongName": "kelvin",
                "Definition": "K"})

    unitList.append({"ShortName": "°C",
                "LongName": "degree celcius",
                "Definition": "degC"})

    # Charge


    unitList.append({"ShortName": "C",
                "LongName": "coulomb",
                "Definition": "C"})

    unitList.append({"ShortName": "mC",
                "LongName": "millicoulomb",
                "Definition": "mC"})

    unitList.append({"ShortName": "uC",
                "LongName": "microcoulomb",
                "Definition": "uC"})

    unitList.append({"ShortName": "nC",
                "LongName": "nanocoulomb",
                "Definition": "nc"})

    unitList.append({"ShortName": "Ah",
                "LongName": "ampere hour",
                "Definition": "Ah"})

    unitList.append({"ShortName": "mAh",
                "LongName": "milli ampere hour",
                "Definition": "mAh"})

    # Current


    unitList.append({"ShortName": "A",
                "LongName": "ampere",
                "Definition": "A"})

    unitList.append({"ShortName": "mA",
                "LongName": "milliampere",
                "Definition": "mA"})

    unitList.append({"ShortName": "uA",
                "LongName": "microampere",
                "Definition": "uA"})

    unitList.append({"ShortName": "nA",
                "LongName": "nanoampere",
                "Definition": "nA"})

    unitList.append({"ShortName": "pA",
                "LongName": "picoampere",
                "Definition": "pA"})

    unitList.append({"ShortName": "fA",
                "LongName": "femtoampere",
                "Definition": "fA"})
    # Voltage

    unitList.append({"ShortName": "V",
                "LongName": "volt",
                "Definition": "V"})

    unitList.append({"ShortName": "mV",
                "LongName": "millivolt",
                "Definition": "mV"})

    unitList.append({"ShortName": "nV",
                "LongName": "nanovolt",
                "Definition": "nV"})

    unitList.append({"ShortName": "kV",
                "LongName": "kilovolt",
                "Definition": "kV"})

    unitList.append({"ShortName": "MV",
                "LongName": "megavolt",
                "Definition": "MV"})

    unitList.append({"ShortName": "GV",
                "LongName": "gigavolt",
                "Definition": "GV"})

    unitList.append({"ShortName": "TV",
                "LongName": "terravolt",
                "Definition": "TV"})

    # Resistance and conductivity


    unitList.append({"ShortName": "ohm",
                "LongName": "ohm",
                "Definition": "ohm"})
    unitList.append({"ShortName": "mohm",
                "LongName": "milliohm",
                "Definition": "mohm"})
    unitList.append({"ShortName": "kohm",
                "LongName": "kiloohm",
                "Definition": "kohm"})
    unitList.append({"ShortName": "Mohm",
                "LongName": "megaohm",
                "Definition": "Mohm"})
    unitList.append({"ShortName": "Gohm",
                "LongName": "gigaohm",
                "Definition": "Gohm"})
    unitList.append({"ShortName": "S",
                "LongName": "siemens",
                "Definition": "S"})
    unitList.append({"ShortName": "mS",
                "LongName": "millisiemens",
                "Definition": "mS"})
    unitList.append({"ShortName": "uS",
                "LongName": "microsiemens",
                "Definition": "uS"})
    unitList.append({"ShortName": "nS",
                "LongName": "nanosiemens",
                "Definition": "nS"})

    # Magnetic fields and fluxes


    unitList.append({"ShortName": "T",
                "LongName": "tesla",
                "Definition": "T"})
    unitList.append({"ShortName": "mT",
                "LongName": "millitesla",
                "Definition": "mT"})
    unitList.append({"ShortName": "uT",
                "LongName": "microtesla",
                "Definition": "uT"})
    unitList.append({"ShortName": "nT",
                "LongName": "nanotesla",
                "Definition": "nT"})
    unitList.append({"ShortName": "G",
                "LongName": "gauss",
                "Definition": "G"})
    unitList.append({"ShortName": "mG",
                "LongName": "milligauss",
                "Definition": "mG"})
    unitList.append({"ShortName": "uG",
                "LongName": "microgauss",
                "Definition": "uG"})



    # Capacitance and inductance
    unitList.append({"ShortName": "F",
                "LongName": "farad",
                "Definition": "F"})
    unitList.append({"ShortName": "uF",
                "LongName": "microfarad",
                "Definition": "uF"})
    unitList.append({"ShortName": "nF",
                "LongName": "nanofarad",
                "Definition": "nF"})
    unitList.append({"ShortName": "pF",
                "LongName": "picofarad",
                "Definition": "pF"})
    unitList.append({"ShortName": "fF",
                "LongName": "femtofarad",
                "Definition": "fF"})
    unitList.append({"ShortName": "H",
                "LongName": "henry",
                "Definition": "H"})
    unitList.append({"ShortName": "mH",
                "LongName": "millihenry",
                "Definition": "mH"})
    unitList.append({"ShortName": "uH",
                "LongName": "microhenry",
                "Definition": "uH"})
    unitList.append({"ShortName": "nH",
                "LongName": "nanohenry",
                "Definition": "nH"})

    # unit
    unitDictExtension = {
        "ProjectID": None,
        "Predefined": True,
        "FileIDList": [],
        "UnitCategoryIDList": []
    }
    for unit in unitList:
        unit.update(unitDictExtension)
    return unitList
