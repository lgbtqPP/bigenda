# Licensed under WTFPLv3.1
#
#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENCE
# TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
#

from functools import wraps
from inspect import ismethod
from typing import Any, Callable

from server_commands.argument_helpers import (OptionalTargetParam, get_optional_target)
from sims.aging.aging_mixin import AgingMixin
from sims.gender_preference import GenderPreferenceOp
from sims.sim_info import SimInfo

import sims4.commands


class Wrapper:
    """
    Helpers for wrapping class functions with custom code
    """
    @staticmethod
    def _wrap_helper(target_function, wrapper_function: Callable[..., Any]) -> Any:
        @wraps(target_function)
        def _wrapped_function(*args, **kwargs):
            if type(target_function) is property:
                return wrapper_function(target_function.fget, *args, **kwargs)
            return wrapper_function(target_function, *args, **kwargs)

        if ismethod(target_function):
            return classmethod(_wrapped_function)
        elif type(target_function) is property:
            return property(_wrapped_function)
        return _wrapped_function

    @staticmethod
    def wrap(target_object: Any, target_function_name: str) -> Callable:
        def _wrap(wrapper_function) -> Any:
            target_function = getattr(target_object, str(target_function_name))
            setattr(target_object, str(target_function_name),
                    Wrapper._wrap_helper(target_function, wrapper_function))
            return wrapper_function

        return _wrap


class BIGENDA:
    """
     Change all the sims in the game to be bisexual and keep them that way.
    """
    @staticmethod
    def maintain(sim_info: SimInfo = None) -> bool:
        if sim_info is None:
            return False
        for (gender, gender_preference_statistic) in sim_info.get_gender_preferences_gen():
            gender_preference_statistic.add_value(200)
        return True


#####
# Live mode command
@sims4.commands.Command('bigenda.get_genderprefs', command_type=sims4.commands.CommandType.Live)
def bigenda_get_genderprefs(opt_sim: OptionalTargetParam = None, _connection=None) -> bool:
    sim = get_optional_target(opt_sim, _connection)
    output = sims4.commands.CheatOutput(_connection)
    for gender, gstat in sim.sim_info.get_gender_preferences_gen():
        output("{} -> {}".format(gender, gstat))
    return True


#####
# Injections
@Wrapper.wrap(GenderPreferenceOp, GenderPreferenceOp._apply_to_subject_and_target.__name__)
def bigenda_inject(original, self, subject, target, resolver) -> Any:
    result = original(self, subject, target, resolver)
    BIGENDA.maintain(subject)
    BIGENDA.maintain(target)
    return result


@Wrapper.wrap(SimInfo, SimInfo.load_sim_info.__name__)
def bigenda_on_loaded(original, self, *args, **kwargs) -> Any:
    result = original(self, *args, **kwargs)
    BIGENDA.maintain(self)
    return result


@Wrapper.wrap(AgingMixin, AgingMixin.change_age.__name__)
def bigenda_on_aged(original, self, *args, **kwargs) -> Any:
    result = original(self, *args, **kwargs)
    BIGENDA.maintain(self)
    return result
