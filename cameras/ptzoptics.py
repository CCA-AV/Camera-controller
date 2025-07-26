commands = {
    "power_on": {"command": "8101040002ff", "parameters": []},
    "power_off": {"command": "8101040003ff", "parameters": []},
    "zoom_stop": {"command": "8101040700ff", "parameters": []},
    "zoom_tele_std": {"command": "8101040702ff", "parameters": []},
    "zoom_wide_std": {"command": "8101040703ff", "parameters": []},
    "zoom_tele_var": {
        "command": "810104072pff",
        "parameters": [
            {"name": "position", "type": "int", "min": 0, "max": 7, "length": 1}
        ],
    },
    "zoom_wide_var": {
        "command": "810104073pff",
        "parameters": [
            {"name": "position", "type": "int", "min": 0, "max": 7, "length": 1}
        ],
    },
    "zoom_direct": {
        "command": "81010447pff",
        "parameters": [
            {
                "name": "position",
                "type": "int",
                "min": 0,
                "max": 67108864,
                "length": 8,
            }
        ],
    },
    "focus_stop": {"command": "8101040800ff", "parameters": []},
    "focus_far_std": {"command": "8101040802ff", "parameters": []},
    "focus_near_std": {"command": "8101040803ff", "parameters": []},
    "focus_far_var": {
        "command": "810104082pff",
        "parameters": [
            {"name": "position", "type": "int", "min": 0, "max": 7, "length": 1}
        ],
    },
    "focus_near_var": {
        "command": "810104083pff",
        "parameters": [
            {"name": "position", "type": "int", "min": 0, "max": 7, "length": 1}
        ],
    },
    "focus_direct": {
        "command": "810104480p0p0p0pff",
        "parameters": [
            {
                "name": "position",
                "type": "int",
                "min": 0,
                "max": 1770,
                "length": 1,
                "splits": 4,
            }
        ],
    },
    "pan_up": {
        "command": "81010601pp0301ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_down": {
        "command": "81010601pp0302ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_left": {
        "command": "81010601pp0103ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_right": {
        "command": "81010601pp0203ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_up_left": {
        "command": "81010601pp0101ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_up_right": {
        "command": "81010601pp0201ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_down_left": {
        "command": "81010601pp0102ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_down_right": {
        "command": "81010601pp0202ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_stop": {
        "command": "81010601pp0303ff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
        ],
    },
    "pan_direct_abs": {
        "command": "81010602pp0p0p0p0p0p0p0p0pff",  # ABCD Pan Pos, QRST Tilt pos
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {
                "name": "pan_pos",
                "type": "int",
                "min": 0,
                "max": 65535,
                "length": 1,
                "splits": 4,
            },
            {
                "name": "tilt_pos",
                "type": "int",
                "min": 0,
                "max": 65535,
                "length": 1,
                "splits": 4,
            },
        ],
    },
    "pan_direct_rel": {
        "command": "81010603pp0p0p0p0p0p0p0p0pff",
        "parameters": [
            {"name": "pan_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {"name": "tilt_speed", "type": "int", "min": 0, "max": 255, "length": 2},
            {
                "name": "pan_pos",
                "type": "int",
                "min": 0,
                "max": 65535,
                "length": 1,
                "splits": 4,
            },
            {
                "name": "tilt_pos",
                "type": "int",
                "min": 0,
                "max": 65535,
                "length": 1,
                "splits": 4,
            },
        ],
    },
    "pan_home": {"command": "81010604ff", "parameters": []},
    "pan_reset": {"command": "81010605ff", "parameters": []},
    "brightness_direct": {
        "command": "810104A100000p0pff",
        "parameters": [
            {
                "name": "brightness",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },
    "contrast_direct": {
        "command": "810104A200000p0pff",
        "parameters": [
            {
                "name": "contrast",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },
    "color_gain": {
        "command": "810104490000000pff",
        "parameters": [
            {"name": "color_gain", "type": "int", "min": 0, "max": 14, "length": 1},
        ],
    },
    "wb_auto": {"command": "8101043500ff", "parameters": []},
    "wb_auto_sensitivity": {  # P: 0: High, 1: Normal, 2: Low
        "command": "810104A90pff",
        "parameters": [
            {"name": "sensitivity", "type": "int", "min": 0, "max": 2, "length": 1},
        ],
    },
    "wb_indoor": {"command": "8101043501ff", "parameters": []},
    "wb_outdoor": {"command": "8101043502ff", "parameters": []},
    "wb_onepush": {"command": "8101043503ff", "parameters": []},
    "wb_manual": {"command": "8101043505ff", "parameters": []},
    "wb_color_temp": {"command": "8101043520ff", "parameters": []},
    "color_temp_reset": {"command": "8101042000ff", "parameters": []},
    "color_temp_up": {"command": "8101042002ff", "parameters": []},
    "color_temp_down": {"command": "8101042003ff", "parameters": []},
    "color_temp_direct": {
        "command": "810104200p0pff",
        "parameters": [
            {
                "name": "color_temp",
                "type": "int",
                "min": 0,
                "max": 55,
                "length": 1,
                "splits": 2,
            },
        ],
    },
    "wb_onepush_trigger": {"command": "8101041005ff", "parameters": []},
    "ae_full_auto": {"command": "8101043900ff", "parameters": []},  # Auto exposure
    "ae_full_manual": {"command": "8101043900ff", "parameters": []},  # Manual
    "ae_full_shutter_priority": {
        "command": "8101043900ff",
        "parameters": [],
    },  # Auto shutter priority exposure
    "ae_full_iris_priority": {
        "command": "8101043900ff",
        "parameters": [],
    },  # Auto iris priority exposure
    "ae_bright": {
        "command": "8101043900ff",
        "parameters": [],
    },  # Bright mode (manual control)
    "iris_reset": {"command": "8101040B00ff", "parameters": []},
    "iris_up": {"command": "8101040B02ff", "parameters": []},
    "iris_down": {"command": "8101040B03ff", "parameters": []},
    "iris_direct": {
        "command": "8101044B00000p0pff",
        "parameters": [
            {
                "name": "iris_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ iris position
    "shutter_reset": {"command": "8101040A00ff", "parameters": []},
    "shutter_up": {"command": "8101040A02ff", "parameters": []},
    "shutter_down": {"command": "8101040A03ff", "parameters": []},
    "shutter_direct": {
        "command": "8101044A00000p0pff",
        "parameters": [
            {
                "name": "shutter_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ shutter position
    "rgain_reset": {"command": "8101040300ff", "parameters": []},
    "rgain_up": {"command": "8101040302ff", "parameters": []},
    "rgain_down": {"command": "8101040303ff", "parameters": []},
    "rgain_direct": {
        "command": "8101044300000p0pff",
        "parameters": [
            {
                "name": "rgain_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ r gain
    "bgain_reset": {"command": "8101040400ff", "parameters": []},
    "bgain_up": {"command": "8101040402ff", "parameters": []},
    "bgain_down": {"command": "8101040403ff", "parameters": []},
    "bgain_direct": {
        "command": "8101044400000p0pff",
        "parameters": [
            {
                "name": "bgain_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ b gain
    "gain_reset": {"command": "8101040C00ff", "parameters": []},
    "gain_up": {"command": "8101040C02ff", "parameters": []},
    "gain_down": {"command": "8101040C03ff", "parameters": []},
    "gain_direct": {
        "command": "8101044C00000p0pff",
        "parameters": [
            {
                "name": "gain_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ gain position
    "gain_limit": {
        "command": "8101042C0pff",
        "parameters": [
            {"name": "gain_limit", "type": "int", "min": 0, "max": 255, "length": 1},
        ],
    },  # P gain position
    "bright_reset": {"command": "8101040D00ff", "parameters": []},
    "bright_up": {"command": "8101040D02ff", "parameters": []},
    "bright_down": {"command": "8101040D03ff", "parameters": []},
    "bright_direct": {
        "command": "8101044D00000p0pff",
        "parameters": [
            {
                "name": "bright_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ bright position
    "flip_off": {"command": "810104A400ff", "parameters": []},
    "flip_h": {"command": "810104A401ff", "parameters": []},
    "flip_v": {"command": "810104A402ff", "parameters": []},
    "flip_hv": {"command": "810104A403ff", "parameters": []},
    "lr_reverse_on": {"command": "8101046102ff", "parameters": []},  # flip lr
    "lr_reverse_off": {"command": "8101046103ff", "parameters": []},
    "ud_reverse_on": {"command": "8101046602ff", "parameters": []},  # flip vertical
    "ud_reverse_off": {"command": "8101046603ff", "parameters": []},
    "save_settings": {"command": "810104A510ff", "parameters": []},
    "preset_reset": {
        "command": "8101043f00pff",
        "parameters": [
            {"name": "preset_number", "type": "int", "min": 0, "max": 127, "length": 1},
        ],
    },  # PP mem number (0-127)
    "preset_set": {
        "command": "8101043f01pff",
        "parameters": [
            {"name": "preset_number", "type": "int", "min": 0, "max": 127, "length": 1},
        ],
    },  # PP mem number (0-127)
    "preset_recall": {
        "command": "8101043f02pff",
        "parameters": [
            {"name": "preset_number", "type": "int", "min": 0, "max": 127, "length": 1},
        ],
    },  # PP mem number (0-127)
    "preset_recall_speed": {
        "command": "81010601pff",
        "parameters": [
            {"name": "speed_grade", "type": "int", "min": 1, "max": 24, "length": 1},
        ],
    },  # PP speed grade, 0x01~0x18
    "backlight": {
        "command": "810104330pff",
        "parameters": [
            {"name": "backlight", "type": "int", "min": 2, "max": 3, "length": 1}
        ],
    },  # P 2 On, 3 off
    "flicker": {
        "command": "810104230pff",
        "parameters": [
            {"name": "flicker", "type": "int", "min": 0, "max": 2, "length": 1}
        ],
    },  # P flicker settings, (0: Off, 1: 50Hz, 2: 60Hz)
    "aperture_auto": {"command": "8101040502ff", "parameters": []},
    "aperture_manual": {"command": "8101040503ff", "parameters": []},
    "aperture_reset": {"command": "8101040200ff", "parameters": []},
    "aperture_up": {"command": "8101040202ff", "parameters": []},
    "aperture_down": {"command": "8101040203ff", "parameters": []},
    "aperture_direct": {
        "command": "8101044200000p0pff",
        "parameters": [
            {
                "name": "aperture_pos",
                "type": "int",
                "min": 0,
                "max": 255,
                "length": 1,
                "splits": 2,
            },
        ],
    },  # PQ aperture gain
    "picture_effect_off": {"command": "8101046300ff", "parameters": []},
    "picture_effect_bw": {"command": "8101046304ff", "parameters": []},
    "setting_save": {"command": "810104Af10ff", "parameters": []},
    "af_zone_top": {"command": "810104AA00ff", "parameters": []},
    "af_zone_center": {"command": "810104AA01ff", "parameters": []},
    "af_zone_bottom": {"command": "810104AA02ff", "parameters": []},
    "color_hue": {
        "command": "8101044f0000000pff",
        "parameters": [
            {"name": "color_hue", "type": "int", "min": 0, "max": 22, "length": 1}
        ],
    },  # P: 0h (-14deg) to Eh (+14deg)
    "osd_toggle": {"command": "8101043f025fff", "parameters": []},
    "osd_up": {"command": "810106010E0E0301ff", "parameters": []},
    "osd_down": {"command": "810106010E0E0302ff", "parameters": []},
    "osd_left": {"command": "810106010E0E0103ff", "parameters": []},
    "osd_right": {"command": "810106010E0E0203ff", "parameters": []},
    "osd_enter": {"command": "8101060605ff", "parameters": []},
    "osd_return": {"command": "8101060604ff", "parameters": []},
    "af_recalibrate": {"command": "810A010310ff", "parameters": []},
    "tally_light": {
        "command": "810A02020pff",
        "parameters": [
            {"name": "tally_light", "type": "int", "min": 1, "max": 3, "length": 1}
        ],
    },  # P: 1: flashing, 2: on, 3: normal
    "ndi_high": {"command": "810B0101ff", "parameters": []},
    "ndi_medium": {"command": "810B0102ff", "parameters": []},
    "ndi_low": {"command": "810B0103ff", "parameters": []},
    "ndi_off": {"command": "810B0104ff", "parameters": []},
    "multicast_mode": {
        "command": "810B01230pff",
        "parameters": [
            {"name": "multicast_mode", "type": "int", "min": 1, "max": 2, "length": 1}
        ],
    },  # P: 1: on, 2: off
    "motion_sync_on": {"command": "810A111302ff", "parameters": []},
    "motion_sync_off": {"command": "810A111303ff", "parameters": []},
    "motion_sync_max": {
        "command": "810A1114pff",
        "parameters": [
            {"name": "motion_sync_max", "type": "int", "min": 1, "max": 2, "length": 1}
        ],
    },  # P: speed stage
    "motion_sync_min": {"command": "810A1114pff", "parameters": []},
    "usb_audio_toggle": {
        "command": "812A02A0040pff",
        "parameters": [
            {"name": "usb_audio_toggle", "type": "int", "min": 2, "max": 3, "length": 1}
        ],
    },  # P: 2: on, 3: off
    "inq": {
        "zoom_pos": "81090447ff",  # Returns: 90500P0Q0R0Sff PQRS zoom position
        "focus_mode": "81090438ff",  # Returns: 905002ff for af, 905003ff for manual
        "focus_pos": "81090448ff",  # Returns: 90500P0Q0R0Sff PQRS position
        "wb_mode": "81090435ff",  # Returns: 905000ff Auto, 905001ff Indoor, 905002ff Outdoor, 905003ff OnePush, 905005ff Manual, 905020ff Color Temp
        "rgain": "81090443ff",  # Returns: 905000000p0q ff pq: R Gain
        "bgain": "81090444ff",  # Returns: 905000000p0q ff pq: B Gain
        "color_temp": "81090420ff",  # Returns: 9050pqffpq: Color Temperature position
        "auto_exposure": "81090439ff",  # Returns: 905000ff full Auto, 905003ff Manual, 90500Aff Shutter priority (SAE), 90500Bff Iris priority (AAE), 90500Dff Bright
        "shutter_pos": "8109044Aff",  # Returns: 90500p0qff pq: Shutter Position
        "iris_pos": "8109044Bff",  # Returns: 90 50 0p 0q ff pq: Iris Position
        "bright_pos": "8109044Dff",  # Returns: 90 50 0p 0q ff pq: Bright Position
        "exposure_mode": "8109043Eff",  # Returns: 90500Pff, P: 2: On, 3: Off
        "exposure_pos": "8109044Eff",  # Returns: 90 50 00 00 0p 0q ff pq: ExpComp Position
        "backlight_mode": "81090433ff",  # Returns: 90500Pff, P: 2: On, 3: Off
        "aperture_mode": "81090405ff",  # Returns: 90500Pff, P: 2: Auto, 3: Manual
        "aperture_gain": "81090442ff",  # Returns: 905000000p0qff pq: Aperture gain
        "menu_mode": "81090606ff",  # Returns: 90500Pff, P: 2: On, 3: Off
        "picture_effect_mode": "81090463ff",  # Returns: 90500Pff, P: 2: Off, 4: BW
        "lr_reverse": "81090461ff",  # Returns: 90500Pff, P: 2: On, 3: Off
        "picture_flip": "81090466ff",  # Returns: 90500Pff, P: 2: On, 3: Off
        "color_gain": "81090449ff",  # Returns: 90500000000pff p: gain setting from 0 (60%) to E (200%)
        "pan_tilt_pos": "81090612ff",  # Returns: 90500w0w0w0w0z0z0z0zff wwww: pan pos, zzzz: tilt pos
        "gain_limit": "8109042Cff",  # Returns: 90500qff q: gain limit
        "af_sensitivity": "81090458ff",  # Returns: options: 1: high, 2: normal, 3: low
        "brightness": "810904A1ff",  # Returns: 905000000p0qff pq: brightness pos
        "contrast": "810904A2ff",  # Returns: 905000000p0qff pq: brightness pos
        "flip": "810904A4ff",  # Returns: options: 0: off, 1: fliph, 2: flipv, 3 fliphv
        "af_zone": "810904A4ff",  # Returns: options: 0: top, 1: center, 2: bottom
        "color_hue": "8109044fff",  # Returns: 90500000000pff p: color hue
        "awb_sensitivity": "810904A9ff",  # Returns: 0: high, 1: normal, 2: low
        "uac": "",  # Returns: 90500Pff, P: 2: On, 3: Off
        "lens_block": "81097E7E00ff",  # Returns: 90500u0u0u0u00000v0v0v0v000w00ff uuuu: zoom, vvvv: focus, w.bit0: focus mode
        "camera_block": "81097E7E01ff",  # Returns: 90500p0p0q0q0r0stt0uvvww00xx0zff pp: rgain, qq: bgain, r: wbmode, s: aperture, tt: aemode, u.bit2: backlight, u.bit1: exp comp, vv: shutterpos, ww: iris pos, xx: bright pos, z: exp comp pos
        "other_block": "81097E7E02ff",  # Returns: 90500p0q000r000000000000000000ff p.bit0: power 1: on, 0: off, q.bit2: lr reverse 1: on, 0: off, r.bit3~0: picture effect mode
        "enlargement_block": "91097E7E03ff",  # Returns: 90500000000000p0qrr0s0t0uff p: af sens, q.bit0: picture flip, 1 on, 0 off, rr.bit6~3: color gain (0 (60%) to E (200%)), s: flip 0 off, 1 h, 3 v, 3 hv, t.bit2~0: nr2d level, u: gain limit
    },
}

returns = {
    "904yff": {"text": "Command Accepted", "status": 0},
    "905yff": {"text": "Command Completed", "status": 0},
    "906y02ff": {"text": "Syntax Error", "status": 1},
    "906y03ff": {"text": "Command Buffer full Error", "status": 1},
    "906y04ff": {"text": "Command Canceled Error", "status": 1},
    "906y05ff": {"text": "No Socket Error", "status": 1},
    "906y41ff": {"text": "Command Not Executable Error", "status": 1},
}

results = {
    "9050yyff": {"data_digits": [[4, 6]]},
    "90500y0yff": {"data_digits": [[4, 8]]},
    "90500000000yff": {"data_digits": [[11, 12]]},
    "905000000y0yff": {"data_digits": [[8, 12]]},
    "90500y0y0y0yff": {"data_digits": [[5, 12]]},
    "90500y0y0y0y0y0y0y0yff": {"data_digits": [[4, 12], [12, 20]]},
    "90500y0y000y000000000000000000ff": {"data_digits": [[5, 6], [7, 8], [11, 12]]},
    "90500y0y0y0y00000y0y0y0y000y00ff": {"data_digits": [[4, 12], [16, 24], [27, 28]]},
    "90500y0y0y0y0y0yyy0yyyyy0yyy0yff": {
        "data_digits": [
            [4, 8],
            [8, 12],
            [13, 14],
            [15, 16],
            [16, 18],
            [19, 20],
            [20, 22],
            [22, 24],
            [26, 28],
            [29, 30],
        ]
    },
    "9050000000000000000y0yyy0y0y0yff": {
        "data_digits": [[19, 20], [21, 22], [22, 24], [25, 26], [27, 28], [29, 30]]
    },
    "": {"data_digits": [[]]},
    "": {"data_digits": [[]]},
}
