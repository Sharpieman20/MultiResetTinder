import settings
import helpers as hlp
from helpers import get_time
import os
import shutil
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path

num_per_state = {}

def assign_to_state(instance, state):
    global num_per_state
    if state not in num_per_state:
        num_per_state[state] = 0
    num_per_state[state] = num_per_state[state] + 1
    instance.state = state
    instance.priority = num_per_state[state]

def has_passed(start_time, duration):
    return (hlp.get_time() - start_time) > duration

class State(Enum):
    DEAD = 0
    BOOTING = 1
    FREE = 2
    PREGEN = 3
    GEN = 4
    PAUSED = 5
    READY = 6
    APPROVED = 7
    ACTIVE = 8

class Process:
    def assign_pid(self, all_processes):
        if settings.is_test_mode():
            self.pid = settings.get_global_test_pid()
            return
        all_pids = hlp.get_pids()
        for pid in all_pids:
            pid_maps_to_instance = False
            for instance in all_processes:
                if instance.pid == pid:
                    pid_maps_to_instance = True
            if not pid_maps_to_instance:
                self.pid = pid

class Suspendable(Process):
    def suspend(self):
        if self.is_suspended():
            return
        self.suspended = True
        hlp.run_ahk("suspendInstance", pid=self.pid)

    def resume(self):
        if not self.is_suspended():
            return
        self.is_suspended = False
        hlp.run_ahk("resumeInstance", pid=self.pid)

    def is_suspended(self):
        return self.suspended

class Stateful(Suspendable):

    def mark_booting(self):
        assign_to_state(self, State.BOOTING)
        self.timestamp = get_time()
    
    def mark_pregen(self):
        self.was_active = False
        assign_to_state(self, State.PREGEN)
    
    def mark_generating(self):
        assign_to_state(self, State.GEN)
        self.timestamp = get_time()
    
    def mark_worldgen_finished(self):
        assign_to_state(self, State.PAUSED)
        self.timestamp = get_time()
    
    def mark_free(self):
        assign_to_state(self, State.FREE)
    
    def release(self):
        if self.is_suspended():
            assign_to_state(self, State.FREE)
        else:
            assign_to_state(self, State.PREGEN)
        self.timestamp = get_time()

    def mark_ready(self):
        assign_to_state(self, State.READY)

    def mark_active(self):
        assign_to_state(self, State.ACTIVE)
        self.was_active = True

    def mark_inactive(self):
        # add to pregen
        self.mark_pregen()

class ConditionalTransitionable(Stateful):

    def is_ready_for_freeze(self):
        duration = 2.0
        if self.state == State.PAUSED:
            duration = 2.0
        return has_passed(self.timestamp, duration)

    def is_done_unfreezing(self):
        duration = 0.5
        return has_passed(self.timestamp, duration)

    def is_ready_for_unfreeze(self):
        duration = 0.5
        return has_passed(self.timestamp, duration)
    
    def is_done_booting(self):
        duration = settings.get_boot_delay()
        return has_passed(self.timestamp, duration)

    def check_should_auto_reset(self):
        duration = 300.0
        if has_passed(self.timestamp, duration):
            self.release()
            return True
            

    def is_active(self):
        return self.state == State.ACTIVE

class Instance(ConditionalTransitionable):

    def __init__(self, num):
        self.num = num
        self.pid = -1
        self.first_reset = True
        self.suspended = False
        self.state = State.DEAD
        assign_to_state(self, self.state)
        self.timestamp = 0
        self.was_active = False
        self.name = '{}{}'.format(settings.get_base_instance_name(), self.num)
        self.mcdir = settings.get_multimc_executable() / "Instances" / self.name
    
    def boot(self):
        hlp.run_ahk("openOfflineInstance", pid=self.pid)
        
    # not yet implemented (not needed in v1)
    def create_multimc_instance(self):
        # probably make some click macro to import instance from zip
        pass

    # not yet implemented (not needed in v1)
    def create_obs_instance(self):
        # create a source with this:
        # https://github.com/Elektordi/obs-websocket-py/blob/master/obswebsocket/requests.py#L551
        # we can create a source that is a copy of a different source returned from
        # https://github.com/Elektordi/obs-websocket-py/blob/master/obswebsocket/requests.py#L524

        # obs1
        #      create a source for when this instance is active
        #   create a source for when this instance is focused
        # obs2
        #   create a source for this instance
        #       tile based on total number of instances
        pass

    def initialize_after_boot(self, all_instances):
        # assign our pid somehow
        self.assign_pid(all_instances)
        # set our title
        hlp.run_ahk("updateTitle", pid=self.pid,
            title="Minecraft* - Instance {}".format(self.num))
        # start generating world w/ duncan mod
        hlp.run_ahk("startDuncanModSession", pid=self.pid)
        # set state to generating
        self.mark_generating()

    def reset_active(self):
        self.pause()
        self.mark_inactive()

    def reset(self):
        hlp.run_ahk("reset", pid=self.pid)

    def pause(self):
        hlp.run_ahk("pauseGame", pid=self.pid)

    # TODO - call this method somewhere
    def move_worlds(self, old_worlds):
        if settings.is_test_mode():
            print("Moving worlds for instance {}".format(self.name))
            return
        for dir_name in os.listdir(self.mcdir + "/saves"):
            # TODO - i think this should be like "Attempt #X" or something cuz of duncan mod
            if dir_name.startswith("New World"):
                try:
                    shutil.move(self.mcdir + "/saves/" + dir_name,
                                old_worlds + f"/{uuid.uuid1()}")
                except:
                    continue

    # TODO - call this method somewhere
    def copy_logs(self):
        # we should copy all relevant logs out of the instance probably since we want to dynamically create instances
        pass

    def read_logs(self, func_check, lines_from_bottom=2):
        if settings.is_test_mode():
            print("Reading logs for instance {}".format(self.name))
            if has_passed(self.timestamp, 5.0):
                return True
            return False
        # this could be a lot faster quite easily. if it's a performance issue, we can check latest modification time on world or something
        # something besides this which is quite slow.

        # also we can try just like, not doing this. since we can try removing pause after creating world and just use the auto-pause on non-focused feature of MC.
        log_file = self.mcdir / "logs" / "latest.log"
        with open(log_file, "r") as logs:
            lines = logs.readlines()
            for i in range(len(lines)):
                if (len(lines) - i <= lines_from_bottom):
                    if (func_check(lines[i])):
                        return True
        return False

    def is_in_world(self, lines_from_bottom=2):
        # Read logs and see if is done world gen
        return self.read_logs(lambda x: "Saving chunks for level 'ServerLevel" in x and "minecraft:the_end" in x, lines_from_bottom)

    def __str__(self):
        return self.name