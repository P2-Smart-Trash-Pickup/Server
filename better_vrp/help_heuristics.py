from vehicle import Vehicle


class Heuristic:
    def __init__(self, heuristic_solver, implement_heuristic) -> None:

        self.heuristic_solver = heuristic_solver
        self.implement_heuristic = implement_heuristic
        self.best_cost = 0
        self.best_i = 0
        self.best_j = 0

        self.best_route_i = 0
        self.best_route_j = 0

        self.best_day_i = 0
        self.best_day_j = 0

    def solve(
        self,
        day_plan: list[list[list[int]]],
        distance_matrix: list[list[float]],
        time_matrix: list[list[float]],
        day_penalty_matrix: list[list[list[int]]],
        penalty: float,
        vehicles: list[Vehicle],
        stop_delay: float,
        weight_matrix: list[list[float]],
        days_in: list[list[int]],
        empty_intervals: list[int],
    ):
        (
            self.best_cost,
            self.best_i,
            self.best_j,
            self.best_route_i,
            self.best_route_j,
            self.best_day_i,
            self.best_day_j,
        ) = self.heuristic_solver(
            day_plan=day_plan,
            days_in=days_in,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            vehicles=vehicles,
            weight_matrix=weight_matrix,
            day_penalty_matrix=day_penalty_matrix,
            penalty=penalty,
            stop_delay=stop_delay,
            empty_interval=empty_intervals,
        )

    def implement(
        self,
        day_plan: list[list[list[int]]],
        days_in: list[list[int]],
        weight_matrix: list[list[float]],
        fill_rates: list[float],
    ):
        self.implement_heuristic(
            day_plan=day_plan,
            days_in=days_in,
            best_i=self.best_i,
            best_j=self.best_j,
            best_route_i=self.best_route_i,
            best_route_j=self.best_route_j,
            best_day_i=self.best_day_i,
            best_day_j=self.best_day_j,
            weight_matrix=weight_matrix,
            fill_rates=fill_rates,
        )


class EnergyHeuristic:
    def __init__(self, heuristic_solver, implement_heuristic) -> None:

        self.heuristic_solver = heuristic_solver
        self.implement_heuristic = implement_heuristic
        self.best_cost = 0
        self.best_i = 0
        self.best_j = 0

        self.best_route_i = 0
        self.best_route_j = 0

        self.best_day_i = 0
        self.best_day_j = 0

    def solve(
        self,
        day_plan: list[list[list[int]]],
        elevation_matrix: list[list[list[list[float]]]],
        time_matrix: list[list[float]],
        day_penalty_matrix: list[list[list[int]]],
        penalty: float,
        vehicles: list[Vehicle],
        stop_delay: float,
        weight_matrix: list[list[float]],
        volume_matrix: list[list[float]],
        days_in: list[list[int]],
        empty_intervals: list[int],
    ):
        (
            self.best_cost,
            self.best_i,
            self.best_j,
            self.best_route_i,
            self.best_route_j,
            self.best_day_i,
            self.best_day_j,
        ) = self.heuristic_solver(
            elevation_matrix=elevation_matrix,
            day_plan=day_plan,
            days_in=days_in,
            time_matrix=time_matrix,
            vehicles=vehicles,
            weight_matrix=weight_matrix,
            day_penalty_matrix=day_penalty_matrix,
            penalty=penalty,
            stop_delay=stop_delay,
            empty_interval=empty_intervals,
            day_volume_matrix=volume_matrix,
        )

    def implement(
        self,
        day_plan: list[list[list[int]]],
        days_in: list[list[int]],
        weight_matrix: list[list[float]],
        volume_matrix: list[list[float]],
        fill_rates: list[float],
    ):
        self.implement_heuristic(
            day_plan=day_plan,
            days_in=days_in,
            best_i=self.best_i,
            best_j=self.best_j,
            best_route_i=self.best_route_i,
            best_route_j=self.best_route_j,
            best_day_i=self.best_day_i,
            best_day_j=self.best_day_j,
            weight_matrix=weight_matrix,
            fill_rates=fill_rates,
            volume_matrix=volume_matrix,
        )


def sum_route_weight_volume(route: list[int], weights: list[float]) -> float:
    total_weight = sum([weights[i] for i in route])
    return total_weight


def sum_route_time(
    route: list[int], time_matrix: list[list[float]], stop_time: float = 0
) -> float:
    total_time = 0
    for index, point in enumerate(route[:-1]):
        next_point = route[index + 1]
        total_time += time_matrix[point][next_point]
        total_time += stop_time
    total_time -= stop_time
    return total_time


def sum_route_dist(route: list[int], distance_matrix: list[list[float]]) -> float:
    total_dist = 0
    for index, point in enumerate(route[:-1]):
        next_point = route[index + 1]
        total_dist += distance_matrix[point][next_point]
    return total_dist


def get_penalty(
    i: int,
    j: int,
    distance_matrix: list[list[float]],
    penalty_matrix: list[list[int]],
    penalty: float,
) -> float:
    org_distance = distance_matrix[i][j]
    return org_distance + penalty * penalty_matrix[i][j] * org_distance


def get_max_empty(days_in: list[int], day_period: int) -> int:
    diffs = []
    for day_i in range(len(days_in)):
        day = days_in[day_i]
        pre_day = days_in[day_i - 1]
        diff = 0
        if pre_day >= day:
            diff = day_period - abs(day - pre_day)
        else:
            diff = day - pre_day
        diffs.append(diff)
    max_diff = max(diffs)

    return max_diff


def gen_weight_day_matrix(
    inital_fill: list[float],
    fill_rates: list[float],
    day_period: int,
    days_in: list[list[int]],
) -> list[list[float]]:
    weight_matrix = [[] for _ in range(day_period)]

    for idx, ini_fl in enumerate(inital_fill):
        in_days = days_in[idx]
        current_fill = ini_fl
        fil_r = fill_rates[idx]
        for day_idx in range(day_period):
            weight_matrix[day_idx].append(current_fill)
            if day_idx in in_days:
                current_fill = 0
            current_fill += fil_r
    return weight_matrix


def update_weight_matrix(
    day_period: int,
    weight_matrix: list[list[float]],
    fill_rates: list[float],
    days_in: list[list[int]],
    point: int,
):
    current_weight = weight_matrix[0][point]
    for day_idx in range(day_period):
        if day_idx in days_in[point]:
            current_weight = 0
        weight_matrix[day_idx][point] = current_weight
        current_weight += fill_rates[point]


def is_weekend(due_date: int) -> bool:
    is_weekend = due_date == 5 or due_date == 6 or due_date == 12 or due_date == 13
    return is_weekend


def volume_to_weight(volume: float) -> float:
    return volume * 0.129
