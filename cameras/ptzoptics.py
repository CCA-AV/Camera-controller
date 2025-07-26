commands = {
    "power_on": "8101040002ff",
    "power_off": "8101040003ff",
    "zoom_stop": "8101040700ff",
    "zoom_tele_std": "8101040702ff",
    "zoom_wide_std": "8101040703ff",
    "zoom_tele_var": "810104072pff",
    "zoom_wide_var": "810104073pff",
    "zoom_direct": "81010447pff",
    "focus_stop": "8101040800ff",
    "focus_far_std": "8101040802ff",
    "focus_near_std": "8101040803ff",
    "focus_far_var": "810104082pff",
    "focus_near_var": "810104083pff",
    "focus_direct": "810104480p0q0r0sff",
    "pan_up": "81010601VW0301ff",  # VV: Pan speed, WW: Tilt speed
    "pan_down": "81010601VW0302ff",
    "pan_left": "81010601VW0103ff",
    "pan_right": "81010601VW0203ff",
    "pan_up_left": "81010601VW0101ff",
    "pan_up_right": "81010601VW0201ff",
    "pan_down_left": "81010601VW0102ff",
    "pan_down_right": "81010601VW0202ff",
    "pan_stop": "81010601VW0303ff",
    "pan_direct_abs": "81010602VW0A0B0C0D0Q0R0S0Tff",  # ABCD Pan Pos, QRST Tilt pos
    "pan_direct_rel": "81010603VW0A0B0C0D0Q0R0S0Tff",
    "pan_home": "81010604ff",
    "pan_reset": "81010605ff",
    "brightness_direct": "810104A100000P0Qff",  # PQ Brightness pos
    "contrast_direct": "810104A200000P0Qff",  # PQ Contrast pos
    "color_gain": "810104490000000Pff",  # Color gain setting 0h (60%) to Eh (200%)
    "wb_auto": "8101043500ff",
    "wb_auto_sensitivity": "810104A90Pff",  # P: 0: High, 1: Normal, 2: Low
    "wb_indoor": "8101043501ff",
    "wb_outdoor": "8101043502ff",
    "wb_onepush": "8101043503ff",
    "wb_manual": "8101043505ff",
    "wb_color_temp": "8101043520ff",
    "color_temp_reset": "8101042000ff",
    "color_temp_up": "8101042002ff",
    "color_temp_down": "8101042003ff",
    "color_temp_direct": "810104200P0Qff",  # PQ Color temp position: 0x00:2500K ~ 0x37: 8000K
    "wb_onepush_trigger": "8101041005ff",
    "ae_full_auto": "8101043900ff",  # Auto exposure
    "ae_full_manual": "8101043900ff",  # Manual
    "ae_full_shutter_priority": "8101043900ff",  # Auto shutter priority exposure
    "ae_full_iris_priority": "8101043900ff",  # Auto iris priority exposure
    "ae_bright": "8101043900ff",  # Bright mode (manual control)
    "iris_reset": "8101040B00ff",
    "iris_up": "8101040B02ff",
    "iris_down": "8101040B03ff",
    "iris_direct": "8101044B00000P0Qff",  # PQ iris position
    "shutter_reset": "8101040A00ff",
    "shutter_up": "8101040A02ff",
    "shutter_down": "8101040A03ff",
    "shutter_direct": "8101044A00000P0Qff",  # PQ shutter position
    "rgain_reset": "8101040300ff",
    "rgain_up": "8101040302ff",
    "rgain_down": "8101040303ff",
    "rgain_direct": "8101044300000P0Qff",  # PQ r gain
    "bgain_reset": "8101040400ff",
    "bgain_up": "8101040402ff",
    "bgain_down": "8101040403ff",
    "bgain_direct": "8101044400000P0Qff",  # PQ b gain
    "gain_reset": "8101040C00ff",
    "gain_up": "8101040C02ff",
    "gain_down": "8101040C03ff",
    "gain_direct": "8101044C00000P0Qff",  # PQ gain position
    "gain_limit": "8101042C0Pff",  # P gain position
    "bright_reset": "8101040D00ff",
    "bright_up": "8101040D02ff",
    "bright_down": "8101040D03ff",
    "bright_direct": "8101044D00000P0Qff",  # PQ bright position
    "flip_off": "810104A400ff",
    "flip_h": "810104A401ff",
    "flip_v": "810104A402ff",
    "flip_hv": "810104A403ff",
    "lr_reverse_on": "8101046102ff",  # flip lr
    "lr_reverse_off": "8101046103ff",
    "ud_reverse_on": "8101046602ff",  # flip vertical
    "ud_reverse_off": "8101046603ff",
    "save_settings": "810104A510ff",
    "preset_reset": "8101043f00Pff",  # PP mem number (0-127)
    "preset_set": "8101043f01Pff",  # PP mem number (0-127)
    "preset_recall": "8101043f02Pff",  # PP mem number (0-127)
    "preset_recall_speed": "81010601Pff",  # PP speed grade, 0x01~0x18
    "backlight": "810104330Pff",  # P 2 On, 3 off
    "flicker": "810104230Pff",  # P flicker settings, (0: Off, 1: 50Hz, 2: 60Hz)
    "aperture_auto": "8101040502ff",
    "aperture_manual": "8101040503ff",
    "aperture_reset": "8101040200ff",
    "aperture_up": "8101040202ff",
    "aperture_down": "8101040203ff",
    "aperture_direct": "8101044200000P0Qff",  # PQ aperture gain
    "picture_effect_off": "8101046300ff",
    "picture_effect_bw": "8101046304ff",
    "setting_save": "810104Af10ff",
    "af_zone_top": "810104AA00ff",
    "af_zone_center": "810104AA01ff",
    "af_zone_bottom": "810104AA02ff",
    "color_hue": "8101044f0000000Pff",  # P: 0h (-14deg) to Eh (+14deg)
    "osd_toggle": "8101043f025fff",
    "osd_up": "810106010E0E0301ff",
    "osd_down": "810106010E0E0302ff",
    "osd_left": "810106010E0E0103ff",
    "osd_right": "810106010E0E0203ff",
    "osd_enter": "8101060605ff",
    "osd_return": "8101060604ff",
    "af_recalibrate": "810A010310ff",
    "tally_light": "810A02020Pff",  # P: 1: flashing, 2: on, 3: normal
    "ndi_high": "810B0101ff",
    "ndi_medium": "810B0102ff",
    "ndi_low": "810B0103ff",
    "ndi_off": "810B0104ff",
    "multicast_mode": "810B01230Pff",  # P: 1: on, 2: off
    "motion_sync_on": "810A111302ff",
    "motion_sync_off": "810A111303ff",
    "motion_sync_max": "810A1114Pff",  # P: speed stage
    "motion_sync_min": "810A1114Pff",
    "usb_audio_toggle": "812A02A0040Pff",  # P: 2: on, 3: off
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
