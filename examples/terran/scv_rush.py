""" 
Bot that stays on 1base, goes 4 rax mass reaper
This bot is one of the first examples that are micro intensive
Bot has a chance to win against elite (=Difficulty.VeryHard) zerg AI

Bot made by Burny
"""

import os
import sys

from sc2.constants import IS_COLLECTING

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import random
from typing import Set

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units


class SCVRushBot(BotAI):
    def __init__(self):
        # Select distance calculation method 0, which is the pure python distance calculation without caching or indexing, using math.hypot(), for more info see distances.py _distances_override_functions() function
        self.distance_calculation_method = 3


    async def on_step(self, iteration):

        attack_scvs:Units = self.units(UnitTypeId.SCV)
        attack_scvs=attack_scvs.sorted(lambda x: x.tag)
        mining_scv:Unit=attack_scvs[0]
        attack_scvs=attack_scvs[1:]


        for r in attack_scvs:

            # Move to range 5 of closest unit if scv is below 20 hp and not regenerating
            enemyThreatsClose: Units = self.all_enemy_units.filter(
                lambda unit: unit.distance_to(r) < 2
            )  # Threats that can attack the scv

            enemySCVs: Units = self.enemy_units(UnitTypeId.DRONE)


            if r.health_percentage < 2 / 5:
                # is in bad health

                if not r.is_repairing and not r.is_moving:

                    if enemyThreatsClose:
                        # Move back
                        retreatPoints: Set[Point2] = self.neighbors8(r.position,
                                                                    distance=3) | self.neighbors8(r.position, distance=5)
                        # Filter points that are pathable
                        retreatPoints: Set[Point2] = {x for x in retreatPoints if self.in_pathing_grid(x)}
                        if retreatPoints:
                            closestEnemy: Unit = enemyThreatsClose.closest_to(r)
                            retreatPoint: Unit = closestEnemy.position.furthest(retreatPoints)
                            r.move(retreatPoint)
                            continue  # Continue for loop, dont execute any of the following

                    # Start repairing
                    svcs=self.units(UnitTypeId.SCV)
                    lower_health_scvs:Units=svcs.filter(lambda unit: unit.health_percentage < 1)
                    a_other_attack_scv: Unit=lower_health_scvs.closest_to(r)
                    r.repair(a_other_attack_scv)

            else:
                # Scv is ready to attack, attack nearest ground unit
                if r.weapon_cooldown == 0 and enemySCVs:
                    enemySCVs: Units = enemySCVs.sorted(lambda x: x.distance_to(r))
                    closestEnemy: Unit = enemySCVs[0]
                    r.attack(closestEnemy)
                    continue  # Continue for loop, dont execute any of the following


            # Move to random enemy start location if no enemy buildings have been seen
            r.move(random.choice(self.enemy_start_locations))


    # Helper functions

    # Stolen and modified from position.py
    def neighbors4(self, position, distance=1) -> Set[Point2]:
        p = position
        d = distance
        return {Point2((p.x - d, p.y)), Point2((p.x + d, p.y)), Point2((p.x, p.y - d)), Point2((p.x, p.y + d))}

    # Stolen and modified from position.py
    def neighbors8(self, position, distance=1) -> Set[Point2]:
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }



def main():
    # Multiple difficulties for enemy bots available https://github.com/Blizzard/s2client-api/blob/ce2b3c5ac5d0c85ede96cef38ee7ee55714eeb2f/include/sc2api/sc2_gametypes.h#L30
    run_game(
        maps.get("AcropolisLE"),
        [Bot(Race.Terran, SCVRushBot()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=True,
    )


if __name__ == "__main__":
    main()
