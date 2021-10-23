import json
from pathlib import Path
import sys

custom_settings_file = Path.cwd() / sys.argv[1]

print(custom_settings_file)

settings = {}

if custom_settings_file.exists():
    with open(custom_settings_file, "r") as custom_settings_readable:
        settings = json.load(custom_settings_readable)

default_settings_file = Path.cwd() / "defaults" / "settings.json"
default_settings = {}

if default_settings_file.parent.exists() and default_settings_file.exists():
    with open(default_settings_file, "r") as default_settings_readable:
        default_settings = json.load(default_settings_readable)

for key in default_settings.keys():
    if key not in settings.keys():
        settings[key] = default_settings[key]

def is_test_mode():
    return settings['test-mode']

def get_num_instances():
    return int(settings['num-instances'])

def get_max_concurrent():
    return int(settings['max-concurrent'])

def get_max_concurrent_boot():
    return int(settings['max-concurrent-boot'])

def get_unfreeze_delay():
    return float(settings['unfreeze-delay']) / 1000.0

def get_freeze_delay():
    return float(settings['freeze-delay']) / 1000.0

def get_unfrozen_queue_size():
    return int(settings['unfrozen-queue-size'])

def get_hotkeys():
    return settings['hotkeys']

def should_use_tts():
    return not settings['disable-tts']

def get_loop_delay():
    return float(settings['loop-delay']) / 1000.0

def get_lines_from_bottom():
    return int(settings['lines-from-bottom'])

def get_multimc_path():
    return Path(settings['multi-mc-path'])

def get_base_instance_name():
    return settings['template-instance']

def get_boot_delay():
    return float(settings['boot-delay'])

def get_switch_delay():
    return int(settings['switch-delay'])

def get_obs_delay():
    return float(settings['obs-delay'])

def is_fullscreen_enabled():
    return settings['fullscreen']

def get_debug_interval():
    return 2.0

def get_test_worldgen_time():
    return 5.0

def should_auto_launch():
    return settings['auto-launch']

def get_stream_obs_web_host():
    return settings['stream-obs-settings']['web-host']

def get_stream_obs_port():
    return settings['stream-obs-settings']['port']

def get_stream_obs_password():
    return settings['stream-obs-settings']['password']

def get_recording_obs_web_host():
    return settings['recording-obs-settings']['web-host']

def get_recording_obs_port():
    return settings['recording-obs-settings']['port']

def get_recording_obs_password():
    return settings['recording-obs-settings']['password']

def get_obs_source_type():
    if settings['use-game-capture']:
        return 'game_capture'
    return 'window_capture'

def should_auto_pause():
    return settings['auto-pause']

def is_ahk_enabled():
    return settings['ahk-enabled']

def is_obs_enabled():
    return settings['obs-enabled']

def only_focus_ready():
    return True

def get_max_unpaused_time():
    return settings['max-unpaused-time']

def prioritize_booting_over_worldgen():
    return settings['prio-booting-over-worldgen']

def minimum_time_for_settings_reset():
    return settings['min-time-for-settings-reset']

def get_load_chunk_time():
    return settings['chunk-load-time']

def get_obs_path():
    return settings['obs-path']

def get_livesplit_path():
    return settings['livesplit-path']

def get_start_create_world_delay():
    return settings['min-time-from-reset-to-world-entry']

def should_parallelize_ahk():
    return settings['parallelize-ahk']

def get_key_delay():
    return int(settings['key-delay'])

def get_max_concurrent_in_run():
    return int(settings['max-concurrent-in-run']) 

def should_auto_pause_active():
    return False

def get_recording_instance_height():
    return 180

def get_recording_instance_width():
    return 320

def use_prioritization():
    return True

def launch_java_test_processes():
    return True

