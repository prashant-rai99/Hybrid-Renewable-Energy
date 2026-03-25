def optimize_energy(solar, wind, demand, battery_soc):

    total_generation = solar + wind

    result = {}

    # Case 1: Extra energy
    if total_generation > demand:

        surplus = total_generation - demand

        charge = min(surplus, 100 - battery_soc)

        result["status"] = "SURPLUS"
        result["battery_action"] = f"Charge {charge:.2f}"
        result["grid_usage"] = 0
        result["energy_used"] = demand

    # Case 2: Deficit
    else:

        deficit = demand - total_generation

        discharge = min(deficit, battery_soc)

        remaining = deficit - discharge

        result["status"] = "DEFICIT"
        result["battery_action"] = f"Discharge {discharge:.2f}"
        result["grid_usage"] = max(0, remaining)
        result["energy_used"] = total_generation + discharge

    return result