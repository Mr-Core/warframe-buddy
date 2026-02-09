from services.fetch_data import fetch_data
from orchestrator import DropOrchestrator
from search_engine import WarframeSearchEngine
from config import DEVELOPMENT_MODE


def _noop(_):
    pass


def rebuild(emit=_noop):
    error_trigger = False

    # Check for dev mode and fetch or skip fetching new html
    if DEVELOPMENT_MODE:
        emit("\nDEVELOPMENT MODE is active!" "\nUsing cached HTML file...")
    else:
        emit("\nFetching latest data...")
        fetch_success, fetch_error = fetch_data()

        if fetch_success:
            emit("✓ Data fetched successfully")
        else:
            emit("✗ Error fetching latest data.")
            if fetch_error:
                emit(f"  ↳ {fetch_error}")
            return False

    # Parse everything
    emit("\nParsing data...")
    orchestrator = DropOrchestrator()
    all_drops, len_all_drops = orchestrator.parse_all()

    # Emit parse details
    emit(
        "✓ Parsing completed:\n"
        f"   Missions: {len_all_drops['mission_drops']} drops\n"
        f"   Relics: {len_all_drops['relic_drops']} drops\n"
        f"   Sorties: {len_all_drops['sortie_drops']} drops\n"
        f"   Cetus bounties: {len_all_drops['cetus_bounty_drops']} drops\n"
        f"   Orb Vallis bounties: {len_all_drops['solaris_bounty_drops']} drops\n"
        f"   Cambion Drift bounties: {len_all_drops['deimos_bounty_drops']} drops\n"
        f"   Zariman bounties: {len_all_drops['zariman_bounty_drops']} drops\n"
        f"   Albrecht's Laboratories bounties: {len_all_drops['entrati_lab_bounty_drops']} drops\n"
        f"   Hex bounties: {len_all_drops['hex_bounty_drops']} drops\n"
        f"   Dynamic Location Rewards: {len_all_drops['transient_drops']} drops\n"
        f"   Total drops: {len_all_drops['total_drops']} drops"
    )

    # Generate a validation report
    report = orchestrator.get_validation_report()

    # Show validation summary
    overall = report["overall"]
    emit(
        f"\nValidation summary:\n"
        f"   Total drops: {overall['total_drops']}\n"
        f"   Data integrity: {overall['data_integrity']:.1%}\n"
        f"   Errors: {overall['error_count']}\n"
        f"   Warnings: {overall['warning_count']}\n"
    )

    # Check if validation report contains any errors
    if report["overall"]["error_count"] > 0 or report["overall"]["warning_count"] > 0:
        error_trigger = True
        emit("   CRITICAL: Errors found in data!\n")

    if error_trigger:
        emit(
            "⚠  Data contains errors and is not safe to use! ⚠\n"
            "Run the program in DEVELOPMENT MODE to diagnose the problems.\n"
        )
        if DEVELOPMENT_MODE:
            orchestrator.print_validation_details()
        return False

    # Save parsed data to file
    emit("Saving parsed data to file...")
    save_response = orchestrator.save_parsed_data()
    emit(save_response)

    # Create search engine with fresh data
    emit("\nCreating search indexes...")
    search_engine = WarframeSearchEngine()
    
    # Create indexes from parsed data
    create_indexes_reponse = search_engine.create_indexes_from_drops(all_drops)
    emit(
        f"✓ Indexed {len(all_drops)} drops\n"
        f"   ↳ Unique items: {create_indexes_reponse}"
    )

    # Save indexes to file
    save_indexes_response = search_engine.save_indexes()
    emit(save_indexes_response)

    # Show index status
    status = search_engine.get_index_status()
    emit(
        f"\nIndex Status:\n"
        f"  - Items indexed: {status['total_items']}\n"
        f"  - Rebuilt at: {status['last_rebuild'] or 'Just now'}"
    )

    emit("\n✓ Rebuilding finished successfully.")
    return True
