# Copyright 2018-2022 The glTF-Blender-IO authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import bpy
import typing
from ......io.com import gltf2_io
from ......io.exp.gltf2_io_user_extensions import export_user_extensions
from .....com.gltf2_blender_conversion import get_target, get_channel_from_target
from ....gltf2_blender_gather_cache import cached
from ...fcurves.gltf2_blender_gather_fcurves_channels import get_channel_groups
from .gltf2_blender_gather_object_sampler import gather_object_sampled_animation_sampler
from .gltf2_blender_gather_object_channel_target import gather_object_sampled_channel_target

def gather_object_sampled_channels(object_uuid: str, blender_action_name: str, export_settings)  -> typing.List[gltf2_io.AnimationChannel]:
    channels = []

    list_of_animated_channels = []
    if object_uuid != blender_action_name and blender_action_name in bpy.data.actions:
        # Not bake situation
        channels_animated, to_be_sampled = get_channel_groups(object_uuid, bpy.data.actions[blender_action_name], export_settings)
        for chan in [chan for chan in channels_animated.values() if chan['bone'] is None]:
            for prop in chan['properties'].keys():
                list_of_animated_channels.append(get_channel_from_target(get_target(prop)))

        for _, _, chan_prop, _ in [chan for chan in to_be_sampled if chan[1] == "OBJECT"]:
            list_of_animated_channels.append(chan_prop)

    for p in ["location", "rotation_quaternion", "scale"]:
        channel = gather_sampled_object_channel(
            object_uuid,
            p,
            blender_action_name,
            p in list_of_animated_channels,
            export_settings
            )
        if channel is not None:
            channels.append(channel)

    blender_object = export_settings['vtree'].nodes[object_uuid].blender_object
    export_user_extensions('animation_gather_object_channel', export_settings, blender_object, blender_action_name)


    return channels if len(channels) > 0 else None

@cached
def gather_sampled_object_channel(
        obj_uuid: str,
        channel: str,
        action_name: str,
        node_channel_is_animated: bool,
        export_settings
        ):

    __target= __gather_target(obj_uuid, channel, export_settings)
    if __target.path is not None:
        sampler = __gather_sampler(obj_uuid, channel, action_name, node_channel_is_animated, export_settings)

        if sampler is None:
            # After check, no need to animate this node for this channel
            return None

        animation_channel = gltf2_io.AnimationChannel(
            extensions=None,
            extras=None,
            sampler=sampler,
            target=__target
        )

        export_user_extensions('gather_animation_channel_hook',
                               export_settings,
                               animation_channel,
                               channel,
                               export_settings['vtree'].nodes[obj_uuid].blender_object,
                               node_channel_is_animated
                               )

        return animation_channel
    return None


def __gather_target(
        obj_uuid: str,
        channel: str,
        export_settings
        ):

    return gather_object_sampled_channel_target(
        obj_uuid, channel, export_settings)

def __gather_sampler(
        obj_uuid: str,
        channel: str,
        action_name: str,
        node_channel_is_animated: bool,
        export_settings):


    return gather_object_sampled_animation_sampler(
        obj_uuid,
        channel,
        action_name,
        node_channel_is_animated,
        export_settings
        )
