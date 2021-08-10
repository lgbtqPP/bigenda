# Licensed under WTFPL

import sims4.commands
import sims.gender_preference

from sims.sim_info import SimInfo

from server_commands.argument_helpers import (OptionalTargetParam,
                                              get_optional_target)

from sims4communitylib.mod_support.common_mod_info import CommonModInfo

from sims4communitylib.utils.common_injection_utils import CommonInjectionUtils

from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.sim.events.sim_loaded import S4CLSimLoadedEvent
from sims4communitylib.events.sim.events.sim_changed_age import S4CLSimChangedAgeEvent


#####
# Setup mod information
class ModInfo(CommonModInfo):
    _FILE_PATH: str = str(__file__)

    @property
    def _name(self) -> str:
        return 'bigenda'

    @property
    def _author(self) -> str:
        return 'lgbtqPP'

    @property
    def _base_namespace(self) -> str:
        return 'bigenda'

    @property
    def _file_path(self) -> str:
        return ModInfo._FILE_PATH

    @property
    def _version(self) -> str:
        return '1.2'


#####
# Maintenance helper function
def BIGENDA_maintain(sim_info: SimInfo = None) -> bool:
    if sim_info is None:
        return False
    for (gender,
         gender_preference_statistic) in sim_info.get_gender_preferences_gen():
        gender_preference_statistic.add_value(200)
    return True


#####
# Live mode command
@sims4.commands.Command('bigenda.get_genderprefs',
                        command_type=sims4.commands.CommandType.Live)
def BIGENDA_get_genderprefs(opt_sim: OptionalTargetParam = None,
                            _connection=None) -> bool:
    sim = get_optional_target(opt_sim, _connection)
    output = sims4.commands.CheatOutput(_connection)
    for gender, gstat in sim.sim_info.get_gender_preferences_gen():
        output("{} -> {}".format(gender, gstat))
    return True


#####
# Injections
@CommonInjectionUtils.inject_safely_into(
    ModInfo.get_identity(), sims.gender_preference.GenderPreferenceOp, sims.
    gender_preference.GenderPreferenceOp._apply_to_subject_and_target.__name__)
def BIGENDA_inject(original, self, subject, target, resolver):
    original(self, subject, target, resolver)
    BIGENDA_maintain(subject)
    BIGENDA_maintain(target)


#####
# Event handlers
@CommonEventRegistry.handle_events(ModInfo.get_identity())
def BIGENDA_on_loaded(event_data: S4CLSimLoadedEvent) -> bool:
    return BIGENDA_maintain(event_data.sim_info)


@CommonEventRegistry.handle_events(ModInfo.get_identity())
def BIGENDA_on_aged(event_data: S4CLSimChangedAgeEvent) -> bool:
    return BIGENDA_maintain(event_data.sim_info)