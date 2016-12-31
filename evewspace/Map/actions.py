#   Eve W-Space
#   Copyright 2014 Andrew Austin and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import time
from django.dispatch import receiver

from ews_location_agent.signals import character_location_update


from collections import namedtuple

LocationInterface = namedtuple('Location', ('ssytem_id', ''))

def update_character_location(user):
    # step 0: get sytem objects
    # step 1: update character location to system
    # step 2: find maps the old system is part of
    # step 2.1: check permissions per map
    # step 2.2: if new system, add template
    current_location = ...
    old_location = ...
    character_id = ...
    user_cache_key = 'user_{}_locations'.format(user.pk)

    if old_location:
        try:
            old_system = System.objects.get(pk=old_location.id)
            old_system.remove_active_pilot(character.id)
        except System.DoesNotExist:
            logger.warning("Old location system id %d not found", old_location.id)
            pass

    request.user.update_location(
        current_system.pk,
        request.eve_charid, request.eve_charname,
        request.eve_shipname, request.eve_shiptypename)

    current_time = time.time()

    user_locations_dict = cache.get(user_cache_key)
    time_threshold = current_time - (60 * 15)
    location_tuple = (sys_id, charname, shipname, shiptype, current_time)
    if user_locations_dict:
        user_locations_dict.pop(charid, None)
        user_locations_dict[charid] = location_tuple
    else:
        user_locations_dict = {charid: location_tuple}
    # Prune dict to ensure we're not carrying over stale entries
    for charid, location in user_locations_dict.items():
        if location[4] < time_threshold:
            user_locations_dict.pop(charid, None)

    cache.set(user_cache_key, user_locations_dict, 60 * 15)
    return user_locations_dict

    # .......

    can_edit = current_map.get_permission(request.user) == 2
    current_location = (request.eve_systemid, request.eve_charname,
                        request.eve_shipname, request.eve_shiptypename)
    char_cache_key = 'char_%s_location' % request.eve_charid
    old_location = cache.get(char_cache_key)
    result = None
    current_system = get_object_or_404(System, pk=current_location[0])
    silent_map = request.POST.get('silent', 'false') == 'true'
    kspace_map = request.POST.get('kspace', 'false') == 'true'

    if old_location != current_location:
        if old_location:
            old_system = get_object_or_404(System, pk=old_location[0])
            old_system.remove_active_pilot(request.eve_charid)
        request.user.update_location(
            current_system.pk,
            request.eve_charid, request.eve_charname,
            request.eve_shipname, request.eve_shiptypename)
        cache.set(char_cache_key, current_location, 60 * 5)
    # Conditions for the system to be automagically added to the map.
        if (can_edit and
            old_location and
            old_system in current_map and
            current_system not in current_map and
            not _is_moving_from_kspace_to_kspace(
                old_system, current_system, kspace_map)):
            context = {
                'oldsystem':
                    current_map.systems.filter(system=old_system).all()[0],
                'newsystem': current_system,
                'wormholes': utils.get_possible_wh_types(old_system,
                                                         current_system),
            }

            if request.POST.get('silent', 'false') != 'true':
                result = render_to_string(
                    'igb_system_add_dialog.html', context,
                    context_instance=RequestContext(request))
            else:
                new_ms = current_map.add_system(
                    request.user, current_system, '', context['oldsystem'])
                k162_type = WormholeType.objects.get(name="K162")
                new_ms.connect_to(context['oldsystem'], k162_type, k162_type)
                result = 'silent'
    else:
        cache.set(char_cache_key, current_location, 60 * 5)
        # Use add_active_pilot to refresh the user's record in the global
        # location cache
        current_system.add_active_pilot(
            request.user.username, request.eve_charid, request.eve_charname,
            request.eve_shipname, request.eve_shiptypename
        )

    return result

@receiver(character_location_changed)
def on_character_location_change(character, ship, old_location, new_location, **kwargs):
    update_character_location(character, ship, old_location, new_location)
