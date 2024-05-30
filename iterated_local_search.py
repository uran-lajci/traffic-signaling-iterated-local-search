import itertools
import random
import time
from copy import deepcopy

from fitness_function import fitness_score
from initial_solution import Schedule
from input_parser import Intersection, Street


def new_home_base(current_home_base: list[Schedule],
                  current_solution: list[Schedule],
                  streets: list[Street],
                  intersections: list[Intersection],
                  paths: list[str],
                  total_duration: int,
                  bonus_points: int
                  ) -> list[Schedule]:
    cs_score = fitness_score(current_solution, streets, intersections, paths, total_duration, bonus_points)
    chb_score = fitness_score(current_home_base, streets, intersections, paths, total_duration, bonus_points)
    if cs_score >= chb_score:
        return deepcopy(current_solution)
    else:
        return deepcopy(current_home_base)


def find_max_value_number(numbers, value_dict):
    max_value_number = None
    max_value = float('-inf')

    for number in numbers:
        if number in value_dict and value_dict[number] > max_value:
            max_value = value_dict[number]
            max_value_number = number

    return max_value_number


def guided_swap_orders(current_solution: list[Schedule],
                       intersection_id_to_car_length
                       ) -> list[Schedule]:
    tweaked_solution = deepcopy(current_solution)
    sorted_schedules = sorted(tweaked_solution, key=lambda x: intersection_id_to_car_length[x.i_intersection],
                              reverse=True)

    num_to_change = max(1, len(tweaked_solution) * 10 // 100)

    selected_schedules = sorted_schedules[:num_to_change]

    for schedule in selected_schedules:
        if not schedule.order:
            continue

        if len(schedule.order) > 1:
            index1, index2 = random.sample(range(len(schedule.order)), 2)
            schedule.order[index1], schedule.order[index2] = schedule.order[index2], schedule.order[index1]

    return tweaked_solution


def guided_change_of_green_time(current_solution: list[Schedule],
                                street_id_to_car_length,
                                intersection_id_to_car_length
                                ) -> list[Schedule]:
    tweaked_solution = deepcopy(current_solution)
    num_to_change = max(1, len(tweaked_solution) * 10 // 100)

    sorted_schedules = sorted(tweaked_solution, key=lambda x: intersection_id_to_car_length[x.i_intersection],
                              reverse=True)

    selected_schedules = sorted_schedules[:num_to_change]

    for schedule in selected_schedules:
        if not schedule.order:
            continue

        orders = schedule.order
        order_key = find_max_value_number(orders, street_id_to_car_length)

        choices = [-3] * 16 + [-2] * 17 + [-1] * 17 + [1] * 17 + [2] * 17 + [3] * 16
        change = random.choice(choices)

        schedule.green_times[order_key] = max(1, schedule.green_times[order_key] + change)

    return tweaked_solution


def change_green_times(current_solution: list[Schedule]) -> list[Schedule]:
    tweaked_solution = deepcopy(current_solution)
    num_to_change = max(1, len(tweaked_solution) * 5 // 100)
    for _ in range(num_to_change):
        schedule = random.choice(tweaked_solution)
        if not schedule.order:
            continue
        order_key = random.choice(schedule.order)
        choices = [-3] * 16 + [-2] * 17 + [-1] * 17 + [1] * 17 + [2] * 17 + [3] * 16
        change = random.choice(choices)
        schedule.green_times[order_key] = max(1, schedule.green_times[order_key] + change)
    return tweaked_solution


def swap_neighbor_orders(current_solution: list[Schedule]) -> list[Schedule]:
    tweaked_solution = deepcopy(current_solution)
    num_to_swap = max(1, len(tweaked_solution) * 5 // 100)
    for _ in range(num_to_swap):
        schedule = random.choice(tweaked_solution)
        if len(schedule.order) > 1:
            index = random.randint(0, len(schedule.order) - 2)
            schedule.order[index], schedule.order[index + 1] = schedule.order[index + 1], schedule.order[index]
    return tweaked_solution


def swap_random_orders(current_solution: list[Schedule]) -> list[Schedule]:
    tweaked_solution = deepcopy(current_solution)
    num_to_swap = max(1, len(tweaked_solution) * 5 // 100)
    for _ in range(num_to_swap):
        schedule = random.choice(tweaked_solution)
        if len(schedule.order) > 1:
            index1, index2 = random.sample(range(len(schedule.order)), 2)
            schedule.order[index1], schedule.order[index2] = schedule.order[index2], schedule.order[index1]
    return tweaked_solution


def optimize_orders_brute_force(current_solution: list[Schedule],
                                streets: list[Street],
                                intersections: list[Intersection],
                                paths: list[str],
                                total_duration: int,
                                bonus_points: int
                                ) -> list[Schedule]:
    best_solution = deepcopy(current_solution)
    best_score = fitness_score(current_solution, streets, intersections, paths, total_duration, bonus_points)

    num_to_optimize = max(1, len(current_solution) * 1 // 100)
    schedules_to_optimize = random.sample(current_solution, num_to_optimize)

    for schedule in schedules_to_optimize:
        original_order = schedule.order
        for i in range(len(original_order) - 2):
            # Extracting 3 continuous elements, or less if not available
            elements_to_permute = original_order[i:i + 3]
            for permuted in itertools.permutations(elements_to_permute):
                schedule.order = original_order[:i] + list(permuted) + original_order[i + 3:]
                temp_score = fitness_score(current_solution, streets, intersections, paths, total_duration,
                                           bonus_points)
                if temp_score > best_score:
                    best_score = temp_score
                    best_solution = deepcopy(current_solution)

        # Resetting the order after optimization
        schedule.order = original_order

    return best_solution


def optimize_green_times_brute_force(current_solution: list[Schedule],
                                     streets: list[Street],
                                     intersections: list[Intersection],
                                     paths: list[str],
                                     total_duration: int,
                                     bonus_points: int
                                     ) -> list[Schedule]:
    best_solution = deepcopy(current_solution)
    best_score = fitness_score(current_solution, streets, intersections, paths, total_duration, bonus_points)

    num_to_optimize = max(1, len(current_solution) * 1 // 100)
    schedules_to_optimize = random.sample(current_solution, num_to_optimize)

    for schedule in schedules_to_optimize:
        for key in schedule.green_times:
            original_value = schedule.green_times[key]
            for change in [-1, 1, 2, 3]:
                schedule.green_times[key] = max(1, original_value + change)
                temp_score = fitness_score(current_solution, streets, intersections, paths, total_duration,
                                           bonus_points)
                if temp_score > best_score:
                    best_score = temp_score
                    best_solution = deepcopy(current_solution)

            # Resetting green_times after optimization
            schedule.green_times[key] = original_value

    return best_solution


def enhanced_tweak(current_solution: list[Schedule],
                   intersection_id_to_intersection,
                   street_name_to_street,
                   street_id_to_street,
                   streets: list[Street],
                   intersections: list[Intersection],
                   paths: list[str],
                   total_duration: int,
                   bonus_points: int,
                   street_id_to_car_length,
                   intersection_id_to_car_length
                   ) -> list[Schedule]:
    options = ([0] * 30) + ([1] * 5) + ([2] * 15) + ([3] * 15) + ([4] * 30)
    tweak_option = random.choice(options)

    if tweak_option == 0:
        return guided_change_of_green_time(current_solution,
                                           street_id_to_car_length,
                                           intersection_id_to_car_length)
    elif tweak_option == 1:
        return change_green_times(current_solution)
    elif tweak_option == 2:
        return swap_neighbor_orders(current_solution)
    elif tweak_option == 3:
        return swap_random_orders(current_solution)
    else:
        return guided_swap_orders(current_solution, intersection_id_to_car_length)


def perturb(current_solution: list[Schedule]) -> list[Schedule]:
    perturbed_solution = deepcopy(current_solution)
    num_to_shuffle = max(1, len(perturbed_solution) * 15 // 100)
    for _ in range(num_to_shuffle):
        schedule = random.choice(perturbed_solution)
        random.shuffle(schedule.order)
    return perturbed_solution


def optimize_solution_with_ils(initial_solution: list[Schedule],
                               streets: list[Street],
                               intersections: list[Intersection],
                               paths: list[str],
                               total_duration: int,
                               bonus_points: int,
                               street_id_to_car_length,
                               intersection_id_to_car_length
                               ) -> list[Schedule]:
    street_id_to_car_length = dict(sorted(street_id_to_car_length.items(), key=lambda item: item[1], reverse=True))
    intersection_id_to_car_length = dict(
        sorted(intersection_id_to_car_length.items(), key=lambda item: item[1], reverse=True))

    intersection_id_to_intersection = {
        intersection.id: intersection
        for intersection in intersections
    }

    street_name_to_street = {
        street.name: street
        for street in streets
    }

    street_id_to_street = {
        street.id: street
        for street in streets
    }

    current_solution = deepcopy(initial_solution)
    current_home_base = deepcopy(initial_solution)
    best_solution = deepcopy(initial_solution)

    duration = 60 * 60

    start_time = time.time()
    iteration = 0

    while time.time() - start_time < duration:
        inner_iteration = 0
        cs_score = fitness_score(current_solution, streets, intersections, paths, total_duration, bonus_points)

        while inner_iteration < 1000 and time.time() - start_time < duration:
            tweak_solution = enhanced_tweak(current_solution,
                                            intersection_id_to_intersection,
                                            street_name_to_street,
                                            street_id_to_street, streets, intersections, paths, total_duration,
                                            bonus_points,
                                            street_id_to_car_length,
                                            intersection_id_to_car_length)

            tw_score = fitness_score(tweak_solution, streets, intersections, paths, total_duration, bonus_points)
            if tw_score > cs_score:
                current_solution = tweak_solution
                cs_score = tw_score
                # print('tw score:', tw_score)

            inner_iteration = inner_iteration + 1

        bs_score = fitness_score(best_solution, streets, intersections, paths, total_duration, bonus_points)
        cs_score = fitness_score(current_solution, streets, intersections, paths, total_duration, bonus_points)
        if cs_score > bs_score:
            best_solution = current_solution

        print('bs score:', bs_score)

        current_home_base = new_home_base(current_home_base, current_solution, streets, intersections, paths,
                                          total_duration, bonus_points)
        current_solution = perturb(current_home_base)
        iteration = iteration + 1

    print(iteration)
    print()

    return best_solution
